from __future__ import annotations

from pathlib import Path

import pymupdf
from fastapi.testclient import TestClient

from proofrag.api import create_app
from proofrag.config import Settings
from proofrag.ingestion import DocumentIngestor, IngestionError


def settings_for(tmp_path: Path, *, max_upload_mb: int = 2) -> Settings:
    return Settings(
        environment="test",
        data_dir=tmp_path,
        database_path=tmp_path / "api.db",
        embedding_dimensions=128,
        max_upload_mb=max_upload_mb,
    )


def pdf_bytes() -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "PX-200 E-17 lockout/tagout and connector J4 evidence")
    payload = document.tobytes()
    document.close()
    return payload


def test_health_upload_list_ask_and_page_preview(tmp_path: Path) -> None:
    with TestClient(create_app(settings_for(tmp_path))) as client:
        assert client.get("/api/health").status_code == 200
        upload = client.post(
            "/api/documents",
            files={"file": ("synthetic.pdf", pdf_bytes(), "application/pdf")},
            data={
                "title": "Synthetic PX-200",
                "version": "1.0",
                "equipment_model": "PX-200",
                "document_type": "manual",
            },
        )
        assert upload.status_code == 201
        document = upload.json()["document"]
        assert document["equipment_model"] == "PX-200"
        assert client.get("/api/documents").json()[0]["document_type"] == "manual"
        ask = client.post(
            "/api/ask",
            json={"question": "What evidence covers E-17 connector J4?"},
        )
        assert ask.status_code == 200
        preview = client.get(
            f"/api/documents/{document['id']}/pages/1/image",
            params={"x0": 70, "y0": 60, "x1": 400, "y1": 90},
        )
        assert preview.status_code == 200
        assert preview.headers["content-type"] == "image/png"


def test_mislabeled_and_malformed_pdfs_are_safe_422(tmp_path: Path) -> None:
    with TestClient(create_app(settings_for(tmp_path))) as client:
        mislabeled = client.post(
            "/api/documents",
            files={"file": ("fake.pdf", b"plain text", "application/pdf")},
        )
        malformed = client.post(
            "/api/documents",
            files={"file": ("broken.pdf", b"%PDF-not-a-document", "application/pdf")},
        )
    assert mislabeled.status_code == 422
    assert malformed.status_code == 422
    assert list((tmp_path / "uploads").iterdir()) == []


def test_empty_unsupported_and_oversized_uploads(tmp_path: Path) -> None:
    with TestClient(create_app(settings_for(tmp_path, max_upload_mb=1))) as client:
        empty = client.post(
            "/api/documents", files={"file": ("empty.txt", b"", "text/plain")}
        )
        unsupported = client.post(
            "/api/documents", files={"file": ("data.csv", b"a,b", "text/csv")}
        )
        oversized = client.post(
            "/api/documents",
            files={"file": ("large.txt", b"x" * (1024 * 1024 + 1), "text/plain")},
        )
    assert empty.status_code == 422
    assert unsupported.status_code == 422
    assert oversized.status_code == 413


def test_invalid_page_and_bounding_boxes_are_rejected(tmp_path: Path) -> None:
    with TestClient(create_app(settings_for(tmp_path))) as client:
        upload = client.post(
            "/api/documents",
            files={"file": ("synthetic.pdf", pdf_bytes(), "application/pdf")},
        ).json()
        document_id = upload["document"]["id"]
        assert client.get(f"/api/documents/{document_id}/pages/2/image").status_code == 404
        partial = client.get(
            f"/api/documents/{document_id}/pages/1/image", params={"x0": 1}
        )
        reversed_box = client.get(
            f"/api/documents/{document_id}/pages/1/image",
            params={"x0": 10, "y0": 10, "x1": 2, "y1": 2},
        )
        outside = client.get(
            f"/api/documents/{document_id}/pages/1/image",
            params={"x0": 10, "y0": 10, "x1": 9000, "y1": 9000},
        )
    assert partial.status_code == 422
    assert reversed_box.status_code == 422
    assert outside.status_code == 422


def test_unicode_text_and_filename_are_supported(tmp_path: Path) -> None:
    with TestClient(create_app(settings_for(tmp_path))) as client:
        response = client.post(
            "/api/documents",
            files={
                "file": (
                    "sécurité.md",
                    "# Sécurité\n\nVérifier l’absence de tension.".encode(),
                    "text/markdown",
                )
            },
        )
    assert response.status_code == 201
    assert response.json()["document"]["filename"] == "sécurité.md"


def test_pdf_signature_validation_happens_before_artifact_creation(tmp_path: Path) -> None:
    settings = settings_for(tmp_path)
    from proofrag.api import build_container

    ingestor: DocumentIngestor = build_container(settings).ingestor
    try:
        ingestor.ingest_bytes(filename="bad.pdf", data=b"not pdf")
    except IngestionError:
        pass
    else:  # pragma: no cover
        raise AssertionError("Expected invalid PDF to be rejected")
    assert list(settings.upload_dir.iterdir()) == []
