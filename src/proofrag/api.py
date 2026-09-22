from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Annotated, Any

import pymupdf
from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from proofrag.answering import build_answer_generator
from proofrag.config import Settings, get_settings
from proofrag.database import Database
from proofrag.embeddings import HashingEmbedder
from proofrag.ingestion import DocumentIngestor, IngestionError
from proofrag.models import (
    AnswerResponse,
    AskRequest,
    DocumentSummary,
    DocumentType,
    HealthResponse,
    IngestionResponse,
)
from proofrag.retrieval import HybridRetriever
from proofrag.safety import SafetyPolicy
from proofrag.service import GroundedAnswerService

pymupdf_any: Any = pymupdf


@dataclass(slots=True)
class Container:
    settings: Settings
    database: Database
    ingestor: DocumentIngestor
    answer_service: GroundedAnswerService


def build_container(settings: Settings) -> Container:
    settings.ensure_directories()
    database = Database(settings.database_path)
    database.initialize()
    embedder = HashingEmbedder(settings.embedding_dimensions)
    retriever = HybridRetriever(database=database, settings=settings, embedder=embedder)
    ingestor = DocumentIngestor(database=database, settings=settings, embedder=embedder)
    answer_service = GroundedAnswerService(
        database=database,
        retriever=retriever,
        generator=build_answer_generator(settings),
        safety_policy=SafetyPolicy(),
    )
    return Container(
        settings=settings,
        database=database,
        ingestor=ingestor,
        answer_service=answer_service,
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
        app.state.container = build_container(resolved_settings)
        yield

    app = FastAPI(
        title=resolved_settings.app_name,
        version="0.1.0",
        description="Evidence-first multimodal maintenance intelligence",
        lifespan=lifespan,
    )
    app.mount(
        "/static",
        StaticFiles(directory=resolved_settings.static_dir),
        name="static",
    )

    def container(request: Request) -> Container:
        return request.app.state.container  # type: ignore[no-any-return]

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(resolved_settings.static_dir / "index.html")

    @app.get("/api/health", response_model=HealthResponse)
    async def health(request: Request) -> HealthResponse:
        dependencies = container(request)
        documents, chunks = await run_in_threadpool(dependencies.database.counts)
        return HealthResponse(
            status="ok",
            documents=documents,
            chunks=chunks,
            answer_provider=dependencies.settings.answer_provider,
        )

    @app.get("/api/documents", response_model=list[DocumentSummary])
    async def list_documents(request: Request) -> list[DocumentSummary]:
        return await run_in_threadpool(container(request).database.list_documents)

    @app.post(
        "/api/documents",
        response_model=IngestionResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_document(
        request: Request,
        file: Annotated[UploadFile, File()],
        title: Annotated[str | None, Form()] = None,
        version: Annotated[str | None, Form()] = None,
        equipment_model: Annotated[str | None, Form()] = None,
        document_type: Annotated[DocumentType, Form()] = DocumentType.MANUAL,
    ) -> IngestionResponse:
        maximum = container(request).settings.max_upload_mb * 1024 * 1024
        payload = bytearray()
        while chunk := await file.read(1024 * 1024):
            payload.extend(chunk)
            if len(payload) > maximum:
                raise HTTPException(
                    status_code=413,
                    detail=(
                        f"Document exceeds the {container(request).settings.max_upload_mb} MB "
                        "upload limit"
                    ),
                )
        try:
            return await run_in_threadpool(
                container(request).ingestor.ingest_bytes,
                filename=file.filename or "document",
                data=bytes(payload),
                title=title,
                version=version,
                equipment_model=equipment_model,
                document_type=document_type,
            )
        except IngestionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/ask", response_model=AnswerResponse)
    async def ask(request: Request, payload: AskRequest) -> AnswerResponse:
        return await container(request).answer_service.answer(payload)

    @app.get("/api/documents/{document_id}/pages/{page_number}/image")
    async def page_image(
        request: Request,
        document_id: str,
        page_number: int,
        x0: float | None = Query(default=None),
        y0: float | None = Query(default=None),
        x1: float | None = Query(default=None),
        y1: float | None = Query(default=None),
    ) -> Response:
        record = await run_in_threadpool(
            container(request).database.get_document_record, document_id
        )
        if record is None:
            raise HTTPException(status_code=404, detail="Document not found")
        if record.local_path.suffix.casefold() != ".pdf":
            raise HTTPException(status_code=415, detail="Page preview is available for PDF files")
        if page_number < 1 or page_number > record.page_count:
            raise HTTPException(status_code=404, detail="Page not found")

        coordinates = (x0, y0, x1, y1)
        supplied = [value is not None for value in coordinates]
        if any(supplied) and not all(supplied):
            raise HTTPException(status_code=422, detail="Provide all four bounding-box coordinates")
        if all(supplied):
            numeric = tuple(float(value) for value in coordinates if value is not None)
            if not all(isfinite(value) for value in numeric) or not (
                numeric[0] < numeric[2] and numeric[1] < numeric[3]
            ):
                raise HTTPException(status_code=422, detail="Invalid bounding-box coordinates")
        try:
            image = await run_in_threadpool(
                _render_page_image,
                record.local_path,
                page_number,
                coordinates,
            )
        except (ValueError, RuntimeError, pymupdf.FileDataError) as exc:
            raise HTTPException(
                status_code=422, detail="Source page could not be rendered"
            ) from exc
        return Response(content=image, media_type="image/png")

    return app


app = create_app()


def _render_page_image(
    path: Path,
    page_number: int,
    coordinates: tuple[float | None, float | None, float | None, float | None],
) -> bytes:
    pdf = pymupdf_any.open(path)
    try:
        page = pdf[page_number - 1]
        if all(value is not None for value in coordinates):
            values = tuple(float(value) for value in coordinates if value is not None)
            rectangle = pymupdf_any.Rect(*values)
            if not page.rect.contains(rectangle):
                raise ValueError("Bounding box is outside the source page")
            page.draw_rect(rectangle, color=(0.95, 0.1, 0.1), width=3, overlay=True)
        pixmap = page.get_pixmap(matrix=pymupdf_any.Matrix(1.6, 1.6), alpha=False)
        return bytes(pixmap.tobytes("png"))
    finally:
        pdf.close()
