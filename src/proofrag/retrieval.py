from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence

from proofrag.config import Settings
from proofrag.database import Database
from proofrag.embeddings import HashingEmbedder
from proofrag.models import ChunkRecord, SearchHit
from proofrag.text import tokenize


class HybridRetriever:
    """BM25 + deterministic embedding retrieval with transparent score components."""

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

    def search(
        self,
        question: str,
        *,
        top_k: int | None = None,
        document_ids: Sequence[str] | None = None,
        equipment_model: str | None = None,
        manual_version: str | None = None,
    ) -> list[SearchHit]:
        chunks = self.database.get_chunks(document_ids)
        if not chunks:
            return []

        descriptors = self.database.document_descriptors()
        if equipment_model:
            desired_model = equipment_model.casefold()
            chunks = [
                chunk
                for chunk in chunks
                if (descriptors[chunk.document_id][2] or "").casefold() == desired_model
            ]
        if manual_version:
            desired = manual_version.casefold()
            chunks = [
                chunk
                for chunk in chunks
                if (descriptors[chunk.document_id][1] or "").casefold() == desired
            ]
        if not chunks:
            return []

        bm25_scores = self._bm25(question, chunks)
        query_embedding = self.embedder.embed(question)
        vector_scores = [
            self.embedder.cosine(query_embedding, chunk.embedding) for chunk in chunks
        ]
        normalized_bm25 = self._normalize(bm25_scores)
        # Cosine similarity already has a stable 0..1 range. Renormalizing it per
        # query would make an unrelated corpus match look artificially perfect.
        normalized_vector = [max(0.0, min(1.0, score)) for score in vector_scores]
        weight_total = self.settings.bm25_weight + self.settings.vector_weight

        hits: list[SearchHit] = []
        for index, chunk in enumerate(chunks):
            combined = (
                self.settings.bm25_weight * normalized_bm25[index]
                + self.settings.vector_weight * normalized_vector[index]
            ) / weight_total
            title, version, model, document_type = descriptors[chunk.document_id]
            hits.append(
                SearchHit(
                    chunk=chunk,
                    score=combined,
                    bm25_score=normalized_bm25[index],
                    raw_bm25_score=bm25_scores[index],
                    vector_score=normalized_vector[index],
                    document_title=title,
                    document_version=version,
                    equipment_model=model,
                    document_type=document_type,
                )
            )
        hits.sort(key=lambda hit: (hit.score, hit.bm25_score), reverse=True)
        return hits[: top_k or self.settings.default_top_k]

    @staticmethod
    def _bm25(question: str, chunks: list[ChunkRecord]) -> list[float]:
        query_terms = tokenize(question)
        tokenized = [tokenize(chunk.normalized_content) for chunk in chunks]
        if not query_terms or not tokenized:
            return [0.0] * len(chunks)
        document_count = len(tokenized)
        average_length = sum(map(len, tokenized)) / document_count or 1.0
        document_frequency: Counter[str] = Counter()
        for tokens in tokenized:
            document_frequency.update(set(tokens))

        k1 = 1.5
        b = 0.75
        scores: list[float] = []
        for tokens in tokenized:
            frequencies = Counter(tokens)
            length = len(tokens)
            score = 0.0
            for term in query_terms:
                frequency = frequencies[term]
                if not frequency:
                    continue
                df = document_frequency[term]
                inverse_document_frequency = math.log(
                    1 + (document_count - df + 0.5) / (df + 0.5)
                )
                denominator = frequency + k1 * (1 - b + b * length / average_length)
                score += inverse_document_frequency * (frequency * (k1 + 1)) / denominator
            scores.append(score)
        return scores

    @staticmethod
    def _normalize(values: list[float]) -> list[float]:
        if not values:
            return []
        largest = max(values)
        if largest <= 0:
            return [0.0] * len(values)
        return [max(0.0, min(1.0, value / largest)) for value in values]
