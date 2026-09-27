from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from starlette.concurrency import run_in_threadpool

from proofrag.answering import AnswerDraft, AnswerGenerator, EvidenceGate
from proofrag.database import Database
from proofrag.models import (
    AnswerResponse,
    AskRequest,
    Citation,
    DocumentType,
    EvidenceDecision,
    EvidenceReason,
    SearchHit,
)
from proofrag.retrieval import HybridRetriever
from proofrag.safety import SafetyPolicy
from proofrag.text import concise_quote


class GroundedAnswerService:
    def __init__(
        self,
        *,
        database: Database,
        retriever: HybridRetriever,
        generator: AnswerGenerator,
        safety_policy: SafetyPolicy,
    ) -> None:
        self.database = database
        self.retriever = retriever
        self.generator = generator
        self.safety_policy = safety_policy
        self.evidence_gate = EvidenceGate(retriever.settings)

    async def answer(self, request: AskRequest) -> AnswerResponse:
        if self.safety_policy.is_safeguard_bypass(request.question):
            decision = EvidenceDecision(
                accepted=False,
                reason=EvidenceReason.SAFEGUARD_REFUSAL,
                explanation=(
                    "The request asks for a safeguard, guard, or protective interlock to be "
                    "bypassed or disabled."
                ),
                support=0,
                query_token_coverage=0,
            )
            draft = AnswerDraft(
                answer=(
                    "I cannot provide instructions to bypass or disable a safeguard. Keep the "
                    "protection in service, place the equipment in a safe state under site "
                    "procedure, and escalate to authorized personnel."
                ),
                evidence_support=0,
                abstained=True,
            )
            return await self._response(request, [], decision, draft)

        hits = await run_in_threadpool(
            self.retriever.search,
            request.question,
            top_k=request.top_k or max(self.retriever.settings.default_top_k, 8),
            document_ids=request.document_ids,
            equipment_model=request.equipment_model,
            manual_version=request.manual_version,
        )
        empty_reason = await run_in_threadpool(self._empty_reason, request)
        relevant_hits = self._prune_hits(hits)
        decision = self.evidence_gate.decide(
            request.question,
            relevant_hits,
            empty_reason=empty_reason,
        )
        draft = await self.generator.generate(request.question, relevant_hits, decision)
        return await self._response(request, relevant_hits, decision, draft)

    def _empty_reason(self, request: AskRequest) -> EvidenceReason:
        if request.document_ids == []:
            return EvidenceReason.NO_DOCUMENT_SELECTED
        documents = self.database.list_documents()
        if request.equipment_model and not any(
            (document.equipment_model or "").casefold() == request.equipment_model.casefold()
            for document in documents
        ):
            return EvidenceReason.MODEL_MISMATCH
        if request.manual_version and not any(
            (document.version or "").casefold() == request.manual_version.casefold()
            and (
                not request.equipment_model
                or (document.equipment_model or "").casefold()
                == request.equipment_model.casefold()
            )
            for document in documents
        ):
            return EvidenceReason.VERSION_MISMATCH
        return EvidenceReason.NO_APPLICABLE_DOCUMENT

    @staticmethod
    def _prune_hits(hits: list[SearchHit]) -> list[SearchHit]:
        if not hits:
            return []
        selected = [
            hit
            for hit in hits
            if hit.raw_bm25_score > 0 or hit.vector_score >= 0.12
        ][:4]
        return selected or hits[:1]

    async def _response(
        self,
        request: AskRequest,
        hits: list[SearchHit],
        decision: EvidenceDecision,
        draft: AnswerDraft,
    ) -> AnswerResponse:
        citation_hits = [
            (index, hits[index - 1])
            for index in draft.referenced_indices
            if 0 < index <= len(hits)
        ]
        citations = [] if draft.abstained else self._citations(citation_hits)
        warnings = self.safety_policy.warnings_for(request.question)
        if draft.abstained:
            warnings.append("No procedural action should be taken from this response.")
        applicability_warnings = self._applicability_warnings(request.question, citation_hits)

        query_id = uuid4().hex
        response = AnswerResponse(
            answer=draft.answer,
            citations=citations,
            confidence=draft.evidence_support,
            evidence_support=draft.evidence_support,
            evidence_decision=decision,
            abstained=draft.abstained,
            warnings=warnings,
            applicability_warnings=applicability_warnings,
            query_id=query_id,
        )
        await run_in_threadpool(
            self.database.log_query,
            query_id=query_id,
            question=request.question,
            answer=response.answer,
            confidence=response.evidence_support,
            abstained=response.abstained,
            citation_chunk_ids=[citation.chunk_id for citation in response.citations],
            created_at=datetime.now(UTC),
        )
        return response

    @staticmethod
    def _applicability_warnings(
        question: str,
        indexed_hits: list[tuple[int, SearchHit]],
    ) -> list[str]:
        warnings: list[str] = []
        hits = [hit for _, hit in indexed_hits]
        versions = {hit.document_version for hit in hits if hit.document_version}
        if len(versions) > 1:
            warnings.append(
                "Evidence spans document versions "
                + ", ".join(sorted(versions))
                + "; verify applicability rather than assuming generic version precedence."
            )
        types = {hit.document_type for hit in hits}
        if DocumentType.BULLETIN in types and DocumentType.MANUAL in types:
            warnings.append(
                "A service bulletin and base manual are both cited; the bulletin applies only "
                "under its stated conditions."
            )
        if DocumentType.BULLETIN in types and not any(
            term in question.casefold()
            for term in ("dust", "fiber", "woodwork", "textile", "aggregate")
        ):
            warnings.append(
                "Bulletin applicability depends on dusty or fiber-rich conditions not established "
                "by this question."
            )
        return warnings

    @staticmethod
    def _citations(indexed_hits: list[tuple[int, SearchHit]]) -> list[Citation]:
        return [
            Citation(
                index=index,
                chunk_id=hit.chunk.id,
                document_id=hit.chunk.document_id,
                document_title=hit.document_title,
                document_version=hit.document_version,
                equipment_model=hit.equipment_model,
                document_type=hit.document_type,
                page_number=hit.chunk.page_number,
                quote=concise_quote(hit.chunk.content),
                source_type=hit.chunk.source_type,
                bbox=hit.chunk.bbox.as_list() if hit.chunk.bbox else None,
                score=round(hit.score, 4),
            )
            for index, hit in indexed_hits
        ]
