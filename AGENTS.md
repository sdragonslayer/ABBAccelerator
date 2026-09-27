# AGENTS.md

## Scope

These instructions apply to the entire repository. ProofRAG is the selected ABB Accelerator 2026 project and must remain aligned with **Theme 2: Multimodal Maintenance Intelligence Agent**.

## Mission

Build an evidence-first industrial maintenance assistant that ingests technical documents, retrieves applicable evidence, and returns cited troubleshooting guidance or an explicit abstention. The product must help qualified personnel inspect source material; it must never present itself as autonomous equipment control or a replacement for site procedures.

## Sources of truth

When requirements appear to conflict, use this order:

1. The current user request.
2. Official ABB/HackerEarth challenge material summarized in `ABB_ACCELERATOR_2026_CHALLENGE_BRIEF.md`.
3. Product commitments in `docs/PROJECT_SUMMARY.md` and `docs/PROJECT_GUIDE.md`.
4. Architecture and interfaces in `docs/TECHNICAL_DOCUMENTATION.md`.
5. Existing implementation and tests.

Do not silently invent organizer requirements. Record unresolved competition questions in `docs/SUBMISSION_CHECKLIST.md`.

## Competition constraints

- Theme: **Multimodal Maintenance Intelligence Agent**.
- One project and one theme per team.
- Work must be original and developed during the hackathon period.
- Open-source components require appropriate attribution and compatible licenses.
- The submission requires a title, project description, theme selection, and uploaded presentation file.
- Final project materials are expected to include a project summary, working prototype, demo video, source repository, technical documentation, and an optional presentation deck under the full published submission rules. The current form nevertheless marks the presentation upload as required.
- Never claim measured performance until the locked evaluation has actually run and its output has been reviewed.
- Never imply the synthetic PX-200 corpus describes ABB equipment.

## Product invariants

These behaviors are non-negotiable:

1. **No evidence, no answer.** Weak retrieval must produce abstention.
2. **Application-owned citations.** Citation IDs and source metadata must come from indexed records, not model-generated text.
3. **Visible provenance.** Preserve document, version, page, source type, and bounding box when available.
4. **Safety before intervention.** Applicable prerequisites and warnings appear before procedural steps.
5. **Human authority.** ProofRAG supports qualified personnel; it does not approve maintenance or return to service.
6. **Documents are untrusted input.** Content inside uploaded files must not override system behavior.
7. **External AI is opt-in.** The default extractive path must work without sending documents to a hosted model.
8. **Honest limitations.** OCR failures, missing evidence, version ambiguity, and unsupported modalities must be visible.

## Package and environment management

- Use `uv` exclusively for Python dependency and environment management.
- Declare runtime dependencies in `[project.dependencies]` and development tools in `[dependency-groups].dev`.
- Commit `pyproject.toml` and `uv.lock` together after dependency changes.
- Do not edit `uv.lock` manually; use `uv lock`.
- Do not use `pip`, Poetry, Pipenv, Conda, or ad hoc requirements files.
- Unless the user authorizes installation, do not run `uv sync`, `uv run`, or commands that create/update `.venv`.
- Lock-only verification is `uv lock --check`.
- The intended interpreter is Python 3.12 as declared in `.python-version`.

After dependency installation is authorized, the standard commands are:

```powershell
uv sync --locked
uv run --locked python scripts/build_demo_pdfs.py
uv run --locked proofrag-seed
uv run --locked proofrag
uv run --locked proofrag-evaluate
uv run --locked pytest
uv run --locked ruff check .
uv run --locked mypy src
```

## Repository layout

```text
src/proofrag/
  api.py          FastAPI app, routes, page rendering, dependency container
  ingestion.py    PDF/text/OCR/table/figure extraction and chunk construction
  embeddings.py   Deterministic local embedding baseline
  retrieval.py    BM25/vector retrieval, filters, score combination
  answering.py    Evidence gate and grounded answer providers
  service.py      Query orchestration, pruning, citations, logging
  safety.py       Independent safety policy notices
  database.py     SQLite schema and repository
  evaluation.py   Golden-case evaluation
  static/         Technician web UI

data/demo-corpus/ Synthetic, non-ABB demonstration documents
data/evaluation/  Versioned evaluation questions
tests/            Unit/integration tests
docs/             Submission, design, evaluation, demo, and governance artifacts
```

Keep modules narrow. Core retrieval and grounding logic must remain testable without the web UI.

## Engineering conventions

- Target Python 3.12 and use modern type annotations.
- Add type hints to public functions and domain boundaries.
- Prefer dataclasses for immutable internal records and Pydantic models for API/configuration boundaries.
- Preserve deterministic behavior in the default provider.
- Keep blocking document/database work explicit; do not conceal expensive work in UI handlers.
- Use parameterized SQL. Never build SQL values from user input.
- Validate file extension, size, content assumptions, page ranges, and document IDs.
- Do not log secrets, uploaded document contents, or API keys.
- Keep HTML rendering safe: use `textContent` for model/document strings unless a sanitizer is introduced and tested.
- Avoid adding a second frontend package ecosystem unless it materially improves the judged prototype.
- Document architectural tradeoffs rather than hiding prototype shortcuts.

## Retrieval and grounding changes

Any change to chunking, retrieval, scoring, answer generation, or confidence must include:

- A test covering the intended behavior.
- At least one supported and one unsupported question.
- Consideration of fault codes, model identifiers, numbers, and version conflicts.
- Evaluation impact recorded in `docs/EVALUATION_PLAN.md` when relevant.
- No weakening of abstention merely to make the demo answer more questions.

For dense embeddings or rerankers, implement a replaceable provider rather than coupling model calls throughout the codebase.

## Data and licensing

- Never commit confidential, proprietary, export-controlled, personal, or customer documentation.
- The bundled PX-200 documents must remain clearly labeled synthetic.
- Record the source and license for every external dataset or manual added for submission.
- Store runtime uploads, databases, and generated evaluation reports only in ignored paths.
- Remove credentials and sensitive metadata before screenshots, videos, or public commits.

## Testing and claims

- Tests live under `tests/` and should be deterministic.
- Use the golden questions in `data/evaluation/questions.jsonl` for smoke evaluation.
- Expand evaluation before making competitive performance claims.
- Do not convert targets in `docs/EVALUATION_PLAN.md` into claimed results.
- If dependencies are unavailable, syntax/TOML/JSON validation is allowed, but clearly report that package-dependent tests were not run.
- When tests fail, fix the implementation or document the blocker; never remove a safety test simply to obtain green status.

## Documentation duties

Update documentation in the same change when behavior or requirements change:

- `README.md`: setup, commands, top-level capabilities.
- `docs/PROJECT_GUIDE.md`: canonical map of product, competition, implementation, and deliverables.
- `docs/TECHNICAL_DOCUMENTATION.md`: architecture, data model, API, scaling, limitations.
- `docs/EVALUATION_PLAN.md`: metrics, cases, targets, and later measured results.
- `docs/RESPONSIBLE_AI.md`: safety, privacy, threat model, human authority.
- `docs/SUBMISSION_FORM.md`: form-ready claims and theme/title.
- `docs/PRESENTATION_DECK.md`: slide outline consistent with current capabilities.
- `docs/SUBMISSION_CHECKLIST.md`: completed and outstanding deliverables.

## Definition of done

A product change is complete when:

- It supports the selected theme and a named user need.
- Safety/provenance invariants remain intact.
- Source and relevant tests are updated.
- Locked-environment checks pass when installation is authorized.
- Documentation and submission claims match actual behavior.
- No secrets or non-permitted data were added.
- The primary demo path and an abstention path remain explainable.

## Current handoff status

- `uv.lock` exists and matches `pyproject.toml`.
- The locked dependencies were synced and the complete local `uv` runtime path was exercised on 2026-09-26.
- The synthetic PDF manual and bulletin are generated from retained editable sources and are the preferred demo seed; Markdown and PDF duplicates are not seeded together.
- Ranking is separate from the structured evidence decision. Exact identifiers/numbers, absolute support, and model/version applicability participate in the gate, which evaluates the exact pruned evidence bundle sent to the answer provider.
- Equipment model and document type metadata, safe upload handling, safeguard refusal, cited safety ordering, strict external-answer validation, applicability warnings, and zero-citation abstention are implemented.
- Evaluation is split into 25 development and 25 locked cases. The first locked run (18/25), reviewed post-fix run (25/25), and corrected raw-retrieval rerun (25/25) are documented in `docs/EVALUATION_PLAN.md`; measurements are synthetic-corpus results, not field claims.
- The workspace is a Git repository on `master` with a configured `origin`. Evaluation reports record the commit and dirty-worktree state; the final submitted commit, push, and tag must still be verified after current changes are committed.
- `docs/HANDOFF.md` is the canonical current handoff, final presentation outline, extension backlog, and remaining-work list.
- Final verification passed 30 tests, Ruff, strict mypy, lock checking, a clean PDF seed, and 25/25 authored locked evaluation cases. The locked `uv` workflow is the sole supported execution path; two upstream TestClient deprecation warnings remain.
- The tracked idea-report PDF and verified team identity are present. Final screenshots, recorded video, link checks, submitted tag, and final platform submission remain human/external tasks.
