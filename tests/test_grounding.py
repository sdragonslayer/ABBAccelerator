from pathlib import Path

import pytest

from proofrag.answering import ExtractiveAnswerGenerator
from proofrag.config import Settings
from proofrag.database import Database
from proofrag.embeddings import HashingEmbedder
from proofrag.ingestion import DocumentIngestor
from proofrag.models import AskRequest
from proofrag.retrieval import HybridRetriever
from proofrag.safety import SafetyPolicy
from proofrag.service import GroundedAnswerService


@pytest.fixture
def service(tmp_path: Path) -> GroundedAnswerService:
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
    ingestor = DocumentIngestor(database=database, settings=settings, embedder=embedder)
    ingestor.ingest_bytes(
        filename="manual.md",
        data=b"# Fault E-17\n\nApply lockout/tagout, then inspect the filter and connector J4.",
        title="Synthetic Manual",
    )
    return GroundedAnswerService(
        database=database,
        retriever=HybridRetriever(database=database, settings=settings, embedder=embedder),
        generator=ExtractiveAnswerGenerator(settings),
        safety_policy=SafetyPolicy(),
    )


@pytest.mark.asyncio
async def test_supported_answer_contains_citation(service: GroundedAnswerService) -> None:
    response = await service.answer(AskRequest(question="How do I inspect fault E-17?"))

    assert not response.abstained
    assert response.citations
    assert "[1]" in response.answer


@pytest.mark.asyncio
async def test_unsupported_question_abstains(service: GroundedAnswerService) -> None:
    response = await service.answer(
        AskRequest(question="What refrigerant charge mass is required?")
    )

    assert response.abstained
    assert not response.citations
