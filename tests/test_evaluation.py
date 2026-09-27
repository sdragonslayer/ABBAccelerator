from __future__ import annotations

import pytest

from proofrag.evaluation import evaluate_cases
from proofrag.models import (
    AnswerResponse,
    ChunkRecord,
    DocumentType,
    EvaluationCase,
    EvidenceDecision,
    EvidenceReason,
    SearchHit,
    SourceType,
)


@pytest.mark.asyncio
async def test_retrieval_rank_is_measured_before_answer_citation_selection() -> None:
    hit = SearchHit(
        chunk=ChunkRecord(
            id="chunk",
            document_id="document",
            page_number=1,
            ordinal=0,
            content="E-17 filter inspection",
            normalized_content="e-17 filter inspection",
            source_type=SourceType.TEXT,
            bbox=None,
            embedding=[],
        ),
        score=1,
        bm25_score=1,
        raw_bm25_score=1,
        vector_score=1,
        document_title="Expected Manual",
        document_version="1.0",
        equipment_model="PX-200",
        document_type=DocumentType.MANUAL,
    )

    class Retriever:
        def search(self, *_args: object, **_kwargs: object) -> list[SearchHit]:
            return [hit]

    class Service:
        retriever = Retriever()

        async def answer(self, _request: object) -> AnswerResponse:
            return AnswerResponse(
                answer="No citation was selected.",
                citations=[],
                confidence=0,
                evidence_support=0,
                evidence_decision=EvidenceDecision(
                    accepted=False,
                    reason=EvidenceReason.WEAK_SUPPORT,
                    explanation="Insufficient support.",
                    support=0,
                    query_token_coverage=0,
                ),
                abstained=True,
                query_id="query",
            )

    case = EvaluationCase(
        id="retrieval-independent-of-citations",
        question="What does E-17 require?",
        expected_document="Expected Manual",
        should_abstain=False,
    )
    result = (await evaluate_cases(Service(), [case]))[0]  # type: ignore[arg-type]

    assert result.retrieval_hit
    assert result.retrieval_rank == 1
    assert result.citation_completeness == 0
    assert not result.passed
