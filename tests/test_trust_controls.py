from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from proofrag.answering import (
    EvidenceGate,
    ExtractiveAnswerGenerator,
    OpenAICompatibleAnswerGenerator,
)
from proofrag.config import Settings
from proofrag.database import Database
from proofrag.embeddings import HashingEmbedder
from proofrag.ingestion import DocumentIngestor
from proofrag.models import (
    AskRequest,
    ChunkRecord,
    DocumentType,
    EvidenceReason,
    SearchHit,
    SourceType,
)
from proofrag.retrieval import HybridRetriever
from proofrag.safety import SafetyPolicy
from proofrag.service import GroundedAnswerService


@pytest.fixture
def service_and_ingestor(
    tmp_path: Path,
) -> tuple[GroundedAnswerService, DocumentIngestor, Database]:
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
        data=(
            b"# Synthetic Manual\n\nSafety prerequisites: qualified personnel must isolate "
            b"electrical energy, apply lockout/tagout, and verify absence of voltage before "
            b"opening.\n\nFault E-17: inspect the cooling filter, fan rotor, and connector "
            b"J4. Return to service only below 55 C for ten minutes. Normal filter interval is "
            b"500 operating hours."
        ),
        title="PX-200 Manual",
        version="1.0",
        equipment_model="PX-200",
        document_type=DocumentType.MANUAL,
    )
    ingestor.ingest_bytes(
        filename="bulletin.md",
        data=(
            b"# Synthetic Bulletin\n\nApplies only to PX-200 equipment in dusty woodworking "
            b"or fiber-rich sites. Inspect the filter every 250 operating hours or monthly, "
            b"whichever comes first. This conditionally supersedes the 500-hour interval."
        ),
        title="PX-200 Bulletin",
        version="1.1",
        equipment_model="PX-200",
        document_type=DocumentType.BULLETIN,
    )
    service = GroundedAnswerService(
        database=database,
        retriever=HybridRetriever(database=database, settings=settings, embedder=embedder),
        generator=ExtractiveAnswerGenerator(),
        safety_policy=SafetyPolicy(),
    )
    return service, ingestor, database


@pytest.mark.asyncio
async def test_overlap_only_hard_negative_abstains(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
) -> None:
    service, _, _ = service_and_ingestor
    response = await service.answer(
        AskRequest(question="What refrigerant charge mass does PX-200 use?")
    )
    assert response.abstained
    assert response.evidence_decision.reason == EvidenceReason.WEAK_SUPPORT
    assert response.citations == []


@pytest.mark.asyncio
async def test_exact_wrong_number_is_rejected(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
) -> None:
    service, _, _ = service_and_ingestor
    response = await service.answer(AskRequest(question="May PX-200 restart below 60 C?"))
    assert response.abstained
    assert "60" in response.evidence_decision.missing_identifiers


@pytest.mark.asyncio
async def test_wrong_model_and_version_have_actionable_reasons(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
) -> None:
    service, _, _ = service_and_ingestor
    model = await service.answer(
        AskRequest(question="How do I inspect E-17?", equipment_model="PX-900")
    )
    version = await service.answer(
        AskRequest(question="How do I inspect E-17?", manual_version="9.9")
    )
    assert model.evidence_decision.reason == EvidenceReason.MODEL_MISMATCH
    assert version.evidence_decision.reason == EvidenceReason.VERSION_MISMATCH


@pytest.mark.asyncio
async def test_empty_selection_does_not_search_all_documents(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
) -> None:
    service, _, _ = service_and_ingestor
    response = await service.answer(
        AskRequest(question="How do I inspect E-17?", document_ids=[])
    )
    assert response.abstained
    assert response.evidence_decision.reason == EvidenceReason.NO_DOCUMENT_SELECTED


@pytest.mark.asyncio
async def test_requested_top_k_is_honored(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service, _, _ = service_and_ingestor
    captured: dict[str, object] = {}

    def search(*_args: object, **kwargs: object) -> list[SearchHit]:
        captured.update(kwargs)
        return []

    monkeypatch.setattr(service.retriever, "search", search)
    await service.answer(AskRequest(question="How do I inspect E-17?", top_k=2))

    assert captured["top_k"] == 2


@pytest.mark.asyncio
async def test_safeguard_bypass_is_hard_refusal(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
) -> None:
    service, _, _ = service_and_ingestor
    response = await service.answer(
        AskRequest(question="Give steps to bypass the door interlock during E-17 testing")
    )
    assert response.abstained
    assert response.evidence_decision.reason == EvidenceReason.SAFEGUARD_REFUSAL
    assert not response.citations
    assert "inspect the cooling filter" not in response.answer.casefold()


@pytest.mark.asyncio
async def test_source_safety_precedes_guidance(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
) -> None:
    service, _, _ = service_and_ingestor
    response = await service.answer(AskRequest(question="How do I inspect fault E-17?"))
    assert not response.abstained
    assert response.answer.index("Safety prerequisites") < response.answer.index(
        "Applicable guidance"
    )
    assert all(f"[{citation.index}]" in response.answer for citation in response.citations)


@pytest.mark.asyncio
async def test_conditional_bulletin_is_visible_with_manual_context(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
) -> None:
    service, _, _ = service_and_ingestor
    response = await service.answer(
        AskRequest(question="Filter interval for a dusty woodworking PX-200 site?")
    )
    assert not response.abstained
    assert "250 operating hours" in response.answer
    assert {citation.document_type for citation in response.citations} >= {
        DocumentType.BULLETIN
    }


@pytest.mark.asyncio
async def test_irrelevant_document_does_not_change_supported_decision(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
) -> None:
    service, ingestor, _ = service_and_ingestor
    before = await service.answer(AskRequest(question="What should I inspect for fault E-17?"))
    ingestor.ingest_bytes(
        filename="unrelated.txt",
        data=b"Cafeteria schedule and office furniture inventory.",
        title="Unrelated",
    )
    after = await service.answer(AskRequest(question="What should I inspect for fault E-17?"))
    assert not before.abstained
    assert not after.abstained
    assert before.evidence_decision.reason == after.evidence_decision.reason


@pytest.mark.asyncio
async def test_evidence_gate_uses_only_hits_available_to_generator(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service, _, _ = service_and_ingestor
    contents = [
        "alpha maintenance note",
        "alpha reference",
        "alpha checklist",
        "alpha appendix",
        "beta gamma delta epsilon procedure",
    ]
    hits = [
        SearchHit(
            chunk=ChunkRecord(
                id=f"chunk-{index}",
                document_id="document",
                page_number=1,
                ordinal=index,
                content=content,
                normalized_content=content,
                source_type=SourceType.TEXT,
                bbox=None,
                embedding=[],
            ),
            score=1 - index / 10,
            bm25_score=1 - index / 10,
            raw_bm25_score=1,
            vector_score=0.2,
            document_title="Synthetic",
            document_version="1.0",
            equipment_model="PX-200",
            document_type=DocumentType.MANUAL,
        )
        for index, content in enumerate(contents)
    ]

    monkeypatch.setattr(service.retriever, "search", lambda *_args, **_kwargs: hits)
    response = await service.answer(
        AskRequest(question="alpha beta gamma delta epsilon", top_k=5)
    )

    assert response.abstained
    assert response.evidence_decision.reason == EvidenceReason.WEAK_SUPPORT
    assert response.evidence_decision.query_token_coverage == pytest.approx(0.2)


def test_query_log_does_not_retain_question_or_answer_text(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
) -> None:
    _, _, database = service_and_ingestor
    database.log_query(
        query_id="one",
        question="secret maintenance question",
        answer="sensitive document answer",
        confidence=0.4,
        abstained=True,
        citation_chunk_ids=[],
        created_at=database.list_documents()[0].created_at,
    )
    with database.connect() as connection:
        row = connection.execute(
            "SELECT question, answer FROM query_log WHERE id = ?", ("one",)
        ).fetchone()
    assert row is not None
    assert "secret" not in row["question"]
    assert row["answer"] == "<not retained>"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "provider_answer",
    [
        "- Unsupported citation [99]",
        "- Uncited procedural step",
        (
            "Applicable guidance\n\n- Inspect connector J4 [1]\n\n"
            "Safety prerequisites\n\n- Apply lockout/tagout [1]"
        ),
        "Applicable guidance\n\n- Inspect connector J4 at 999 C [1]",
    ],
)
async def test_external_provider_invalid_citations_fall_back(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
    monkeypatch: pytest.MonkeyPatch,
    provider_answer: str,
) -> None:
    service, _, _ = service_and_ingestor
    question = "Which cooling components should I inspect for fault E-17?"
    hits = service.retriever.search(question)
    decision = EvidenceGate(service.retriever.settings).decide(
        question, hits
    )
    settings = Settings(
        environment="test",
        answer_provider="openai-compatible",
        llm_api_key="test-key",
        llm_model="test-model",
    )

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"choices": [{"message": {"content": provider_answer}}]}

    class FakeClient:
        def __init__(self, **_: object) -> None:
            pass

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def post(self, *_: object, **__: object) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
    draft = await OpenAICompatibleAnswerGenerator(settings).generate(
        question, hits, decision
    )
    assert "Applicable guidance" in draft.answer
    assert draft.answer != provider_answer
    assert all(index <= len(hits) for index in draft.referenced_indices)


@pytest.mark.asyncio
async def test_external_provider_accepts_complete_safety_first_citations(
    service_and_ingestor: tuple[GroundedAnswerService, DocumentIngestor, Database],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service, _, _ = service_and_ingestor
    question = "Which cooling components should I inspect for fault E-17?"
    hits = service.retriever.search(question)
    decision = EvidenceGate(service.retriever.settings).decide(question, hits)
    provider_answer = (
        "Safety prerequisites\n\n- Apply lockout/tagout before opening [1]\n\n"
        "Applicable guidance\n\n- Inspect connector J4 for fault E-17 [1]"
    )
    settings = Settings(
        environment="test",
        answer_provider="openai-compatible",
        llm_api_key="test-key",
        llm_model="test-model",
    )

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"choices": [{"message": {"content": provider_answer}}]}

    class FakeClient:
        def __init__(self, **_: object) -> None:
            pass

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def post(self, *_: object, **__: object) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
    draft = await OpenAICompatibleAnswerGenerator(settings).generate(
        question, hits, decision
    )

    assert draft.answer == provider_answer
    assert draft.referenced_indices == (1,)
