from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from proofrag.models import (
    BoundingBox,
    ChunkRecord,
    DocumentRecord,
    DocumentSummary,
    DocumentType,
    SourceType,
)

SCHEMA = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    title TEXT NOT NULL,
    version TEXT,
    equipment_model TEXT,
    document_type TEXT NOT NULL DEFAULT 'manual',
    checksum TEXT NOT NULL UNIQUE,
    content_type TEXT NOT NULL,
    local_path TEXT NOT NULL,
    page_count INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    ordinal INTEGER NOT NULL,
    content TEXT NOT NULL,
    normalized_content TEXT NOT NULL,
    source_type TEXT NOT NULL,
    bbox_json TEXT,
    embedding_json TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_page ON chunks(document_id, page_number);

CREATE TABLE IF NOT EXISTS query_log (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    confidence REAL NOT NULL,
    abstained INTEGER NOT NULL,
    citation_chunk_ids_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


class Database:
    """Small SQLite repository suitable for a hackathon-scale document corpus."""

    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA)
            columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(documents)").fetchall()
            }
            if "equipment_model" not in columns:
                connection.execute("ALTER TABLE documents ADD COLUMN equipment_model TEXT")
            if "document_type" not in columns:
                connection.execute(
                    "ALTER TABLE documents ADD COLUMN document_type TEXT NOT NULL DEFAULT 'manual'"
                )

    def find_document_by_checksum(self, checksum: str) -> DocumentSummary | None:
        query = """
            SELECT d.*, COUNT(c.id) AS chunk_count
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            WHERE d.checksum = ?
            GROUP BY d.id
        """
        with self.connect() as connection:
            row = connection.execute(query, (checksum,)).fetchone()
        return self._summary_from_row(row) if row else None

    def save_document(self, document: DocumentRecord, chunks: Sequence[ChunkRecord]) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    id, filename, title, version, equipment_model, document_type, checksum,
                    content_type, local_path, page_count, status, created_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    filename = excluded.filename,
                    title = excluded.title,
                    version = excluded.version,
                    equipment_model = excluded.equipment_model,
                    document_type = excluded.document_type,
                    content_type = excluded.content_type,
                    local_path = excluded.local_path,
                    page_count = excluded.page_count,
                    status = excluded.status,
                    metadata_json = excluded.metadata_json
                """,
                (
                    document.id,
                    document.filename,
                    document.title,
                    document.version,
                    document.equipment_model,
                    document.document_type.value,
                    document.checksum,
                    document.content_type,
                    str(document.local_path),
                    document.page_count,
                    document.status,
                    document.created_at.isoformat(),
                    json.dumps(document.metadata),
                ),
            )
            connection.execute("DELETE FROM chunks WHERE document_id = ?", (document.id,))
            connection.executemany(
                """
                INSERT INTO chunks (
                    id, document_id, page_number, ordinal, content, normalized_content,
                    source_type, bbox_json, embedding_json, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk.id,
                        chunk.document_id,
                        chunk.page_number,
                        chunk.ordinal,
                        chunk.content,
                        chunk.normalized_content,
                        chunk.source_type.value,
                        json.dumps(chunk.bbox.as_list()) if chunk.bbox else None,
                        json.dumps(chunk.embedding),
                        json.dumps(chunk.metadata),
                    )
                    for chunk in chunks
                ],
            )

    def list_documents(self) -> list[DocumentSummary]:
        query = """
            SELECT d.*, COUNT(c.id) AS chunk_count
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            GROUP BY d.id
            ORDER BY d.created_at DESC
        """
        with self.connect() as connection:
            rows = connection.execute(query).fetchall()
        return [self._summary_from_row(row) for row in rows]

    def get_document_record(self, document_id: str) -> DocumentRecord | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
        if row is None:
            return None
        return DocumentRecord(
            id=row["id"],
            filename=row["filename"],
            title=row["title"],
            version=row["version"],
            equipment_model=row["equipment_model"],
            document_type=DocumentType(row["document_type"]),
            checksum=row["checksum"],
            content_type=row["content_type"],
            local_path=Path(row["local_path"]),
            page_count=row["page_count"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            metadata=json.loads(row["metadata_json"]),
        )

    def get_chunks(self, document_ids: Sequence[str] | None = None) -> list[ChunkRecord]:
        query = "SELECT * FROM chunks"
        parameters: tuple[str, ...] = ()
        if document_ids is not None:
            if not document_ids:
                return []
            placeholders = ",".join("?" for _ in document_ids)
            query += f" WHERE document_id IN ({placeholders})"
            parameters = tuple(document_ids)
        query += " ORDER BY document_id, page_number, ordinal"
        with self.connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self._chunk_from_row(row) for row in rows]

    def document_descriptors(
        self,
    ) -> dict[str, tuple[str, str | None, str | None, DocumentType]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT id, title, version, equipment_model, document_type FROM documents"
            ).fetchall()
        return {
            row["id"]: (
                row["title"],
                row["version"],
                row["equipment_model"],
                DocumentType(row["document_type"]),
            )
            for row in rows
        }

    def counts(self) -> tuple[int, int]:
        with self.connect() as connection:
            document_count = connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            chunk_count = connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        return int(document_count), int(chunk_count)

    def log_query(
        self,
        *,
        query_id: str,
        question: str,
        answer: str,
        confidence: float,
        abstained: bool,
        citation_chunk_ids: Sequence[str],
        created_at: datetime,
    ) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO query_log (
                    id, question, answer, confidence, abstained,
                    citation_chunk_ids_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    query_id,
                    "sha256:" + hashlib.sha256(question.encode("utf-8")).hexdigest(),
                    "<not retained>",
                    confidence,
                    int(abstained),
                    json.dumps(list(citation_chunk_ids)),
                    created_at.isoformat(),
                ),
            )

    @staticmethod
    def _summary_from_row(row: sqlite3.Row) -> DocumentSummary:
        return DocumentSummary(
            id=row["id"],
            filename=row["filename"],
            title=row["title"],
            version=row["version"],
            equipment_model=row["equipment_model"],
            document_type=DocumentType(row["document_type"]),
            content_type=row["content_type"],
            page_count=row["page_count"],
            chunk_count=row["chunk_count"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            ingestion_warnings=json.loads(row["metadata_json"]).get("warnings", []),
        )

    @staticmethod
    def _chunk_from_row(row: sqlite3.Row) -> ChunkRecord:
        bbox_values = json.loads(row["bbox_json"]) if row["bbox_json"] else None
        return ChunkRecord(
            id=row["id"],
            document_id=row["document_id"],
            page_number=row["page_number"],
            ordinal=row["ordinal"],
            content=row["content"],
            normalized_content=row["normalized_content"],
            source_type=SourceType(row["source_type"]),
            bbox=BoundingBox.from_list(bbox_values),
            embedding=[float(value) for value in json.loads(row["embedding_json"])],
            metadata=json.loads(row["metadata_json"]),
        )
