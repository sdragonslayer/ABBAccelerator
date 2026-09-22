from __future__ import annotations

import hashlib
import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pymupdf

from proofrag.config import Settings
from proofrag.database import Database
from proofrag.embeddings import HashingEmbedder
from proofrag.models import (
    BoundingBox,
    ChunkRecord,
    DocumentRecord,
    DocumentType,
    IngestionResponse,
    SourceType,
)
from proofrag.text import normalize_text, normalize_unicode

pymupdf_any: Any = pymupdf

SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md", ".markdown"}
MAX_CHUNK_CHARS = 1_600
CHUNK_OVERLAP_CHARS = 180


@dataclass(slots=True)
class ExtractedBlock:
    page_number: int
    content: str
    source_type: SourceType
    bbox: BoundingBox | None = None
    metadata: dict[str, Any] | None = None


class IngestionError(ValueError):
    pass


class DocumentIngestor:
    def __init__(
        self,
        *,
        database: Database,
        settings: Settings,
        embedder: HashingEmbedder,
    ) -> None:
        self.database = database
        self.settings = settings
        self.embedder = embedder

    def ingest_bytes(
        self,
        *,
        filename: str,
        data: bytes,
        title: str | None = None,
        version: str | None = None,
        equipment_model: str | None = None,
        document_type: DocumentType = DocumentType.MANUAL,
    ) -> IngestionResponse:
        suffix = Path(filename).suffix.casefold()
        if suffix not in SUPPORTED_SUFFIXES:
            raise IngestionError(
                f"Unsupported file type {suffix or '(none)'}. Use PDF, TXT, or Markdown."
            )
        if not data:
            raise IngestionError("The uploaded document is empty")
        if len(data) > self.settings.max_upload_mb * 1024 * 1024:
            raise IngestionError(
                f"Document exceeds the {self.settings.max_upload_mb} MB upload limit"
            )
        if suffix == ".pdf" and not data.startswith(b"%PDF-"):
            raise IngestionError(
                "The file is named as a PDF but does not have a valid PDF signature"
            )

        checksum = hashlib.sha256(data).hexdigest()
        existing = self.database.find_document_by_checksum(checksum)
        if existing:
            return IngestionResponse(
                document=existing,
                warnings=["This exact file was already indexed; the existing document was reused."],
            )

        document_id = checksum[:20]
        safe_suffix = ".md" if suffix == ".markdown" else suffix
        local_path = self.settings.upload_dir / f"{document_id}{safe_suffix}"
        local_path.write_bytes(data)

        warnings: list[str] = []
        try:
            if suffix == ".pdf":
                blocks, page_count, extraction_warnings = self._extract_pdf(data)
                warnings.extend(extraction_warnings)
            else:
                blocks = self._extract_text(data)
                page_count = 1
        except (RuntimeError, ValueError, pymupdf.FileDataError) as exc:
            local_path.unlink(missing_ok=True)
            raise IngestionError("The document could not be parsed safely") from exc

        if not blocks:
            local_path.unlink(missing_ok=True)
            raise IngestionError("No readable text, tables, figures, or OCR content was found")

        resolved_title = (title or Path(filename).stem.replace("_", " ")).strip()
        chunks = self._build_chunks(document_id, blocks)
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        document = DocumentRecord(
            id=document_id,
            filename=Path(filename).name,
            title=resolved_title,
            version=version.strip() if version and version.strip() else None,
            equipment_model=(
                equipment_model.strip() if equipment_model and equipment_model.strip() else None
            ),
            document_type=document_type,
            checksum=checksum,
            content_type=content_type,
            local_path=local_path,
            page_count=page_count,
            metadata={
                "ingestion": "pymupdf" if suffix == ".pdf" else "structured-text",
                "ocr_enabled": self.settings.enable_ocr,
                "warnings": warnings,
            },
        )
        self.database.save_document(document, chunks)
        summary = self.database.find_document_by_checksum(checksum)
        if summary is None:  # pragma: no cover - protects against storage corruption
            raise RuntimeError("Document was indexed but could not be read back")
        return IngestionResponse(document=summary, warnings=warnings)

    def _extract_pdf(self, data: bytes) -> tuple[list[ExtractedBlock], int, list[str]]:
        blocks: list[ExtractedBlock] = []
        warnings: list[str] = []
        document = pymupdf_any.open(stream=data, filetype="pdf")
        page_count = len(document)
        try:
            for page_index, page in enumerate(document):
                page_number = page_index + 1
                raw_blocks = page.get_text("blocks", sort=True)
                visible_text = " ".join(str(block[4]) for block in raw_blocks).strip()
                source_type = SourceType.TEXT

                if len(visible_text) < 80 and self.settings.enable_ocr:
                    try:
                        text_page = page.get_textpage_ocr(flags=0, dpi=200, full=True)
                        raw_blocks = page.get_text("blocks", textpage=text_page, sort=True)
                        source_type = SourceType.OCR
                    except Exception as exc:
                        warnings.append(f"Page {page_number}: OCR unavailable ({exc}).")
                elif len(visible_text) < 80:
                    warnings.append(
                        f"Page {page_number}: little extractable text; "
                        "enable OCR for scanned pages."
                    )

                text_blocks: list[ExtractedBlock] = []
                for raw in raw_blocks:
                    content = normalize_unicode(" ".join(str(raw[4]).split()))
                    if not content:
                        continue
                    bbox = self._valid_bbox(raw[:4])
                    if bbox is None:
                        warnings.append(f"Page {page_number}: invalid text bounding box skipped.")
                        continue
                    block_source_type = source_type
                    if re.match(r"^Figure\s+\d+\s*:", content, re.IGNORECASE):
                        block_source_type = SourceType.FIGURE
                    text_blocks.append(
                        ExtractedBlock(
                            page_number=page_number,
                            content=content,
                            source_type=block_source_type,
                            bbox=bbox,
                            metadata={"block_number": int(raw[5]) if len(raw) > 5 else None},
                        )
                    )
                blocks.extend(text_blocks)

                try:
                    tables = page.find_tables().tables
                    for table_index, table in enumerate(tables):
                        markdown = self._table_to_markdown(table.extract())
                        if markdown:
                            rectangle = table.bbox
                            bbox = self._valid_bbox(rectangle)
                            if bbox is None:
                                warnings.append(
                                    f"Page {page_number}: invalid table bounding box skipped."
                                )
                                continue
                            blocks.append(
                                ExtractedBlock(
                                    page_number=page_number,
                                    content=f"Table {table_index + 1}\n{markdown}",
                                    source_type=SourceType.TABLE,
                                    bbox=bbox,
                                    metadata={"table_index": table_index},
                                )
                            )
                except Exception as exc:
                    warnings.append(f"Page {page_number}: table extraction skipped ({exc}).")

                try:
                    for figure_index, image in enumerate(page.get_image_info(xrefs=True)):
                        bbox_values = image.get("bbox")
                        if not bbox_values:
                            continue
                        bbox = self._valid_bbox(bbox_values)
                        if bbox is None:
                            continue
                        caption = self._nearest_caption(text_blocks, bbox)
                        description = caption or "Uncaptioned technical figure"
                        blocks.append(
                            ExtractedBlock(
                                page_number=page_number,
                                content=f"Figure {figure_index + 1}: {description}",
                                source_type=SourceType.FIGURE,
                                bbox=bbox,
                                metadata={
                                    "figure_index": figure_index,
                                    "width": image.get("width"),
                                    "height": image.get("height"),
                                },
                            )
                        )
                except Exception as exc:
                    warnings.append(f"Page {page_number}: figure indexing skipped ({exc}).")
        finally:
            document.close()
        return blocks, page_count, warnings

    @staticmethod
    def _valid_bbox(values: Any) -> BoundingBox | None:
        try:
            coordinates = list(values)
            if len(coordinates) != 4:
                return None
            return BoundingBox(*map(float, coordinates))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _extract_text(data: bytes) -> list[ExtractedBlock]:
        text = data.decode("utf-8-sig", errors="replace")
        sections = re.split(r"\n(?=#{1,6}\s)|\n{2,}", text)
        return [
            ExtractedBlock(
                page_number=1,
                content=" ".join(section.split()),
                source_type=SourceType.TEXT,
                metadata={"section": index},
            )
            for index, section in enumerate(sections)
            if section.strip()
        ]

    def _build_chunks(
        self, document_id: str, blocks: list[ExtractedBlock]
    ) -> list[ChunkRecord]:
        grouped: dict[tuple[int, SourceType], list[ExtractedBlock]] = {}
        for block in blocks:
            grouped.setdefault((block.page_number, block.source_type), []).append(block)

        chunks: list[ChunkRecord] = []
        ordinal = 0
        for (page_number, source_type), page_blocks in grouped.items():
            if source_type in {SourceType.TABLE, SourceType.FIGURE}:
                block_groups = [[block] for block in page_blocks]
            else:
                block_groups = self._merge_blocks(page_blocks)
            for block_group in block_groups:
                content = "\n\n".join(block.content for block in block_group).strip()
                if not content:
                    continue
                chunk_id = hashlib.sha256(
                    f"{document_id}:{page_number}:{ordinal}:{source_type.value}:{content}".encode()
                ).hexdigest()[:24]
                metadata: dict[str, Any] = {}
                for block in block_group:
                    metadata.update(block.metadata or {})
                chunks.append(
                    ChunkRecord(
                        id=chunk_id,
                        document_id=document_id,
                        page_number=page_number,
                        ordinal=ordinal,
                        content=content,
                        normalized_content=normalize_text(content),
                        source_type=source_type,
                        bbox=self._union_bbox([block.bbox for block in block_group]),
                        embedding=self.embedder.embed(content),
                        metadata=metadata,
                    )
                )
                ordinal += 1
        return chunks

    @staticmethod
    def _merge_blocks(blocks: list[ExtractedBlock]) -> list[list[ExtractedBlock]]:
        groups: list[list[ExtractedBlock]] = []
        current: list[ExtractedBlock] = []
        current_size = 0
        for block in blocks:
            length = len(block.content)
            if current and current_size + length > MAX_CHUNK_CHARS:
                groups.append(current)
                overlap: list[ExtractedBlock] = []
                overlap_size = 0
                for previous in reversed(current):
                    if overlap_size >= CHUNK_OVERLAP_CHARS:
                        break
                    overlap.insert(0, previous)
                    overlap_size += len(previous.content)
                current = overlap
                current_size = overlap_size
            current.append(block)
            current_size += length
        if current:
            groups.append(current)
        return groups

    @staticmethod
    def _union_bbox(boxes: list[BoundingBox | None]) -> BoundingBox | None:
        actual = [box for box in boxes if box is not None]
        if not actual:
            return None
        return BoundingBox(
            x0=min(box.x0 for box in actual),
            y0=min(box.y0 for box in actual),
            x1=max(box.x1 for box in actual),
            y1=max(box.y1 for box in actual),
        )

    @staticmethod
    def _nearest_caption(blocks: list[ExtractedBlock], figure: BoundingBox) -> str | None:
        candidates: list[tuple[float, str]] = []
        for block in blocks:
            if block.bbox is None:
                continue
            vertical_distance = min(
                abs(block.bbox.y0 - figure.y1), abs(figure.y0 - block.bbox.y1)
            )
            if vertical_distance <= 100:
                candidates.append((vertical_distance, block.content))
        if not candidates:
            return None
        return min(candidates, key=lambda item: item[0])[1][:500]

    @staticmethod
    def _table_to_markdown(rows: list[list[str | None]]) -> str:
        cleaned = [[" ".join((cell or "").split()) for cell in row] for row in rows]
        cleaned = [row for row in cleaned if any(row)]
        if not cleaned:
            return ""
        width = max(len(row) for row in cleaned)
        if len(cleaned) < 2 or width < 2 or width > 12:
            return ""
        padded = [row + [""] * (width - len(row)) for row in cleaned]
        header = padded[0]
        if sum(bool(cell) for cell in header) < 2:
            return ""
        lines = [f"| {' | '.join(header)} |", f"| {' | '.join(['---'] * width)} |"]
        lines.extend(f"| {' | '.join(row)} |" for row in padded[1:])
        return "\n".join(lines)
