from pathlib import Path

from proofrag.config import Settings
from proofrag.database import Database
from proofrag.embeddings import HashingEmbedder
from proofrag.ingestion import DocumentIngestor
from proofrag.retrieval import HybridRetriever


def build_components(tmp_path: Path) -> tuple[Database, DocumentIngestor, HybridRetriever]:
    settings = Settings(
        environment="test",
        data_dir=tmp_path,
        database_path=tmp_path / "test.db",
        embedding_dimensions=128,
    )
    settings.ensure_directories()
    database = Database(settings.database_path)
    database.initialize()
    embedder = HashingEmbedder(settings.embedding_dimensions)
    return (
        database,
        DocumentIngestor(database=database, settings=settings, embedder=embedder),
        HybridRetriever(database=database, settings=settings, embedder=embedder),
    )


def test_markdown_ingestion_and_fault_retrieval(tmp_path: Path) -> None:
    database, ingestor, retriever = build_components(tmp_path)
    result = ingestor.ingest_bytes(
        filename="manual.md",
        data=(
            b"# Manual\n\nE-17 means cooling airflow is restricted. "
            b"Inspect the filter, fan, and J4 connector after lockout."
        ),
        title="Test Manual",
        version="1.0",
    )

    assert result.document.chunk_count > 0
    hits = retriever.search("What should I inspect for E-17?")
    assert hits
    assert "J4" in hits[0].chunk.content
    assert database.counts()[0] == 1


def test_duplicate_document_is_reused(tmp_path: Path) -> None:
    _, ingestor, _ = build_components(tmp_path)
    payload = b"# Manual\n\nA unique maintenance procedure."

    first = ingestor.ingest_bytes(filename="one.md", data=payload)
    second = ingestor.ingest_bytes(filename="copy.md", data=payload)

    assert first.document.id == second.document.id
    assert second.warnings

