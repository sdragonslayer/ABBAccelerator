from __future__ import annotations

import asyncio
import hashlib
import subprocess
from pathlib import Path
from time import perf_counter

from proofrag.api import build_container
from proofrag.config import get_settings
from proofrag.evaluation import evaluate_cases, load_cases, write_report
from proofrag.models import DocumentType

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEMO_CORPUS = PROJECT_ROOT / "data" / "demo-corpus"
EVALUATION_CASES = PROJECT_ROOT / "data" / "evaluation" / "locked.jsonl"


def git_metadata() -> dict[str, object]:
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return {"commit": "unavailable", "working_tree_dirty": None}
    return {
        "commit": revision.stdout.strip() or "unavailable",
        "working_tree_dirty": bool(status.stdout.strip()),
    }


def seed() -> None:
    settings = get_settings()
    container = build_container(settings)
    documents = sorted(DEMO_CORPUS.glob("*.pdf"))
    if not documents:
        documents = sorted(DEMO_CORPUS.glob("*.md"))
    if not documents:
        raise SystemExit(f"No demo documents found in {DEMO_CORPUS}")
    for path in documents:
        started = perf_counter()
        version = "1.1" if "v1_1" in path.stem else "1.0"
        if path.suffix.casefold() == ".pdf":
            title = (
                "Service Bulletin SB-PX200-04"
                if "bulletin" in path.stem
                else "Sentinel PX-200 Pump Controller"
            )
        else:
            title = path.read_text(encoding="utf-8").splitlines()[0].removeprefix("# ").strip()
        result = container.ingestor.ingest_bytes(
            filename=path.name,
            data=path.read_bytes(),
            title=title,
            version=version,
            equipment_model="PX-200",
            document_type=(
                DocumentType.BULLETIN if "bulletin" in path.stem else DocumentType.MANUAL
            ),
        )
        elapsed_ms = (perf_counter() - started) * 1000
        print(
            f"Indexed {result.document.title}: {result.document.chunk_count} blocks "
            f"in {elapsed_ms:.1f} ms"
        )
        for warning in result.warnings:
            print(f"  warning: {warning}")


async def _evaluate() -> None:
    settings = get_settings()
    container = build_container(settings)
    if not container.database.list_documents():
        seed()
        container = build_container(settings)
    cases = load_cases(EVALUATION_CASES)
    results = await evaluate_cases(container.answer_service, cases)
    output = settings.data_dir / "evaluation-results" / "latest.json"
    corpus_hash = hashlib.sha256()
    for path in sorted(DEMO_CORPUS.glob("*.pdf")):
        corpus_hash.update(path.name.encode("utf-8"))
        corpus_hash.update(path.read_bytes())
    metadata: dict[str, object] = {
        "case_file": str(EVALUATION_CASES.relative_to(PROJECT_ROOT)),
        "corpus_sha256": corpus_hash.hexdigest(),
        "answer_provider": settings.answer_provider,
        "embedding_dimensions": settings.embedding_dimensions,
        "min_query_coverage": settings.min_query_coverage,
        "min_absolute_similarity": settings.min_absolute_similarity,
    }
    metadata.update(git_metadata())
    write_report(
        output,
        results,
        metadata=metadata,
    )
    passed = sum(result.passed for result in results)
    print(f"Evaluation: {passed}/{len(results)} passed")
    print(f"Report: {output}")
    for result in results:
        marker = "PASS" if result.passed else "FAIL"
        print(f"  {marker} {result.case_id}")


def evaluate() -> None:
    asyncio.run(_evaluate())
