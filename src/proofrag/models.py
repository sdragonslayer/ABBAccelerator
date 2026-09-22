from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from math import isfinite
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SourceType(StrEnum):
    TEXT = "text"
    TABLE = "table"
    FIGURE = "figure"
    OCR = "ocr"


class DocumentType(StrEnum):
    MANUAL = "manual"
    BULLETIN = "bulletin"
    PROCEDURE = "procedure"


class EvidenceReason(StrEnum):
    SUPPORTED = "supported"
    WEAK_SUPPORT = "weak_support"
    MODEL_MISMATCH = "model_mismatch"
    VERSION_MISMATCH = "version_mismatch"
    NO_APPLICABLE_DOCUMENT = "no_applicable_document"
    NO_DOCUMENT_SELECTED = "no_document_selected"
    SAFEGUARD_REFUSAL = "safeguard_refusal"


@dataclass(frozen=True, slots=True)
class BoundingBox:
    x0: float
    y0: float
    x1: float
    y1: float

    def __post_init__(self) -> None:
        values = (self.x0, self.y0, self.x1, self.y1)
        if not all(isfinite(value) for value in values):
            raise ValueError("Bounding-box coordinates must be finite")
        if self.x0 >= self.x1 or self.y0 >= self.y1:
            raise ValueError("Bounding-box coordinates must be ordered")

    def as_list(self) -> list[float]:
        return [self.x0, self.y0, self.x1, self.y1]

    @classmethod
    def from_list(cls, values: list[float] | None) -> BoundingBox | None:
        if values is None or len(values) != 4:
            return None
        try:
            return cls(*map(float, values))
        except (TypeError, ValueError):
            return None


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    id: str
    filename: str
    title: str
    version: str | None
    equipment_model: str | None
    document_type: DocumentType
    checksum: str
    content_type: str
    local_path: Path
    page_count: int
    status: str = "ready"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ChunkRecord:
    id: str
    document_id: str
    page_number: int
    ordinal: int
    content: str
    normalized_content: str
    source_type: SourceType
    bbox: BoundingBox | None
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SearchHit:
    chunk: ChunkRecord
    score: float
    bm25_score: float
    raw_bm25_score: float
    vector_score: float
    document_title: str
    document_version: str | None
    equipment_model: str | None
    document_type: DocumentType


class DocumentSummary(BaseModel):
    id: str
    filename: str
    title: str
    version: str | None = None
    equipment_model: str | None = None
    document_type: DocumentType = DocumentType.MANUAL
    content_type: str
    page_count: int
    chunk_count: int = 0
    status: str
    created_at: datetime
    ingestion_warnings: list[str] = Field(default_factory=list)


class IngestionResponse(BaseModel):
    document: DocumentSummary
    warnings: list[str] = Field(default_factory=list)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)
    document_ids: list[str] | None = None
    equipment_model: str | None = Field(default=None, max_length=120)
    manual_version: str | None = Field(default=None, max_length=80)

    @field_validator("question")
    @classmethod
    def clean_question(cls, value: str) -> str:
        return " ".join(value.split())


class Citation(BaseModel):
    index: int
    chunk_id: str
    document_id: str
    document_title: str
    document_version: str | None = None
    equipment_model: str | None = None
    document_type: DocumentType
    page_number: int
    quote: str
    source_type: SourceType
    bbox: list[float] | None = None
    score: float = Field(ge=0, le=1)


class EvidenceDecision(BaseModel):
    accepted: bool
    reason: EvidenceReason
    explanation: str
    support: float = Field(ge=0, le=1)
    query_token_coverage: float = Field(ge=0, le=1)
    matched_identifiers: list[str] = Field(default_factory=list)
    missing_identifiers: list[str] = Field(default_factory=list)


class AnswerResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float = Field(ge=0, le=1)
    evidence_support: float = Field(ge=0, le=1)
    evidence_decision: EvidenceDecision
    abstained: bool
    warnings: list[str] = Field(default_factory=list)
    applicability_warnings: list[str] = Field(default_factory=list)
    query_id: str


class HealthResponse(BaseModel):
    status: str
    documents: int
    chunks: int
    answer_provider: str


class EvaluationCase(BaseModel):
    id: str
    question: str
    expected_terms: list[str] = Field(default_factory=list)
    expected_document: str | None = None
    split: str = "locked"
    expected_version: str | None = None
    expected_source_type: SourceType | None = None
    expected_evidence: str | None = None
    forbidden_terms: list[str] = Field(default_factory=list)
    safety_order_required: bool = False
    equipment_model: str | None = None
    manual_version: str | None = None
    should_abstain: bool = False
    notes: str = ""


class EvaluationResult(BaseModel):
    case_id: str
    expected_document: str | None
    expected_abstain: bool
    passed: bool
    retrieval_hit: bool
    term_coverage: float
    abstention_correct: bool
    version_model_correct: bool
    citation_precision: float
    citation_completeness: float
    safety_order_correct: bool
    latency_ms: float
    retrieval_rank: int | None
    evidence_reason: EvidenceReason
    answer: str
    citation_documents: list[str]
