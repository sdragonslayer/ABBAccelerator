from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from starlette.concurrency import run_in_threadpool

from proofrag.models import AskRequest, EvaluationCase, EvaluationResult
from proofrag.service import GroundedAnswerService


def load_cases(path: Path) -> list[EvaluationCase]:
    cases: list[EvaluationCase] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            cases.append(EvaluationCase.model_validate_json(line))
        except Exception as exc:
            raise ValueError(f"Invalid evaluation case on line {line_number}: {exc}") from exc
    return cases


async def evaluate_cases(
    service: GroundedAnswerService, cases: list[EvaluationCase]
) -> list[EvaluationResult]:
    results: list[EvaluationResult] = []
    for case in cases:
        retrieval_hits = await run_in_threadpool(
            service.retriever.search,
            case.question,
            top_k=5,
            equipment_model=case.equipment_model,
            manual_version=case.manual_version,
        )
        matching_ranks = [
            index
            for index, hit in enumerate(retrieval_hits, start=1)
            if case.expected_document
            and case.expected_document.casefold() in hit.document_title.casefold()
        ]
        retrieval_rank = matching_ranks[0] if matching_ranks else None
        retrieval_hit = case.expected_document is None or retrieval_rank is not None

        started = perf_counter()
        response = await service.answer(
            AskRequest(
                question=case.question,
                equipment_model=case.equipment_model,
                manual_version=case.manual_version,
            )
        )
        latency_ms = (perf_counter() - started) * 1000
        answer_folded = response.answer.casefold()
        matched_terms = sum(term.casefold() in answer_folded for term in case.expected_terms)
        term_coverage = matched_terms / len(case.expected_terms) if case.expected_terms else 1.0
        citation_documents = [citation.document_title for citation in response.citations]
        abstention_correct = response.abstained == case.should_abstain
        expected_citations = 0 if case.should_abstain else 1
        correct_citations = sum(
            case.expected_document is not None
            and case.expected_document.casefold() in citation.document_title.casefold()
            and (
                case.expected_version is None
                or citation.document_version == case.expected_version
            )
            and (
                case.expected_source_type is None
                or citation.source_type == case.expected_source_type
            )
            for citation in response.citations
        )
        citation_precision = (
            correct_citations / len(response.citations) if response.citations else 1.0
        )
        citation_completeness = (
            min(1.0, correct_citations / expected_citations)
            if expected_citations
            else 1.0
        )
        version_model_correct = all(
            (case.expected_version is None or citation.document_version == case.expected_version)
            and (case.equipment_model is None or citation.equipment_model == case.equipment_model)
            for citation in response.citations
        )
        safety_position = response.answer.casefold().find("safety prerequisites")
        guidance_position = response.answer.casefold().find("applicable guidance")
        safety_order_correct = not case.safety_order_required or (
            safety_position >= 0 and guidance_position >= 0 and safety_position < guidance_position
        )
        forbidden_absent = all(
            term.casefold() not in answer_folded for term in case.forbidden_terms
        )
        passed = (
            retrieval_hit
            and abstention_correct
            and term_coverage >= 0.75
            and version_model_correct
            and citation_completeness == 1.0
            and safety_order_correct
            and forbidden_absent
        )
        results.append(
            EvaluationResult(
                case_id=case.id,
                expected_document=case.expected_document,
                expected_abstain=case.should_abstain,
                passed=passed,
                retrieval_hit=retrieval_hit,
                term_coverage=round(term_coverage, 3),
                abstention_correct=abstention_correct,
                version_model_correct=version_model_correct,
                citation_precision=round(citation_precision, 3),
                citation_completeness=round(citation_completeness, 3),
                safety_order_correct=safety_order_correct,
                latency_ms=round(latency_ms, 3),
                retrieval_rank=retrieval_rank,
                evidence_reason=response.evidence_decision.reason,
                answer=response.answer,
                citation_documents=citation_documents,
            )
        )
    return results


def write_report(
    path: Path,
    results: list[EvaluationResult],
    *,
    metadata: dict[str, object] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(result.passed for result in results)
    latencies = sorted(result.latency_ms for result in results)
    median = latencies[len(latencies) // 2] if latencies else 0
    p95 = latencies[min(len(latencies) - 1, int(len(latencies) * 0.95))] if latencies else 0
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "metadata": metadata or {},
        "summary": {
            "passed": passed,
            "total": len(results),
            "pass_rate": round(passed / len(results), 3) if results else 0,
            "citation_precision": round(
                sum(result.citation_precision for result in results) / len(results), 3
            ) if results else 0,
            "citation_completeness": round(
                sum(result.citation_completeness for result in results) / len(results), 3
            ) if results else 0,
            "median_query_latency_ms": median,
            "p95_query_latency_ms": p95,
            "recall_at_1": _ratio(
                sum(result.retrieval_rank == 1 for result in results if result.expected_document),
                sum(bool(result.expected_document) for result in results),
            ),
            "recall_at_5": _ratio(
                sum(
                    result.retrieval_rank is not None and result.retrieval_rank <= 5
                    for result in results
                    if result.expected_document
                ),
                sum(bool(result.expected_document) for result in results),
            ),
            "mean_reciprocal_rank": round(
                sum(
                    1 / result.retrieval_rank
                    for result in results
                    if result.expected_document and result.retrieval_rank
                )
                / max(1, sum(bool(result.expected_document) for result in results)),
                3,
            ),
            "unsupported_question_accuracy": _ratio(
                sum(
                    result.abstention_correct
                    for result in results
                    if result.expected_abstain
                ),
                sum(result.expected_abstain for result in results),
            ),
            "false_procedural_answer_rate": _ratio(
                sum(
                    not result.abstention_correct
                    for result in results
                    if result.expected_abstain
                ),
                sum(result.expected_abstain for result in results),
            ),
            "safety_order_accuracy": _ratio(
                sum(result.safety_order_correct for result in results), len(results)
            ),
        },
        "results": [result.model_dump() for result in results],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 3) if denominator else 0.0
