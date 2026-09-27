# ProofRAG Project and Competition Guide

## 1. Purpose of this guide

This is the canonical orientation document for the ProofRAG submission. It explains the competition requirements, selected idea, repository implementation, documentation set, form content, completion status, and remaining work.

## 2. Competition understanding

### Selected challenge

- **Competition:** ABB Accelerator 2026
- **Selected theme:** Theme 2 — Multimodal Maintenance Intelligence Agent
- **Core ask:** Build a grounded AI assistant that can understand technical text, scans, tables, diagrams, and images and return accurate, citation-backed troubleshooting answers.
- **Team size:** HackerEarth is configured for 1–5 members.
- **Eligibility:** Current students at accredited U.S. colleges or universities, according to the formal eligibility block.
- **Submission rule:** One project in one selected theme.

The complete competition research, dates, rules, judging weights, ambiguities, and ranked concepts are in [`../ABB_ACCELERATOR_2026_CHALLENGE_BRIEF.md`](../ABB_ACCELERATOR_2026_CHALLENGE_BRIEF.md).

### Judging weights

| Criterion | Weight | How ProofRAG addresses it |
|---|---:|---|
| Technical Excellence | 25% | Typed service architecture, structured ingestion, hybrid retrieval, citations, evaluation, reproducible packaging |
| Innovation & Creativity | 20% | Evidence-first design, region citations, abstention, version-aware evidence, local-first mode |
| Problem–Solution Fit | 20% | Direct implementation of the multimodal maintenance-assistant brief |
| Scalability & Feasibility | 15% | Practical MVP and documented path to PostgreSQL/Qdrant/object storage/model gateway |
| User Experience | 10% | Technician-oriented query flow and evidence viewer |
| Presentation & Demo | 10% | Supported answer, bulletin conflict, and unsupported-question narrative |

### Timeline caution

The published timeline image and live metadata disagree by several hours/date labeling near the Prototype Phase deadline. The challenge brief records both. Always submit against the earlier live platform cutoff.

## 3. Submission form answers

The ready-to-paste title, description, theme, presentation requirement, and pre-submission checks are in [`SUBMISSION_FORM.md`](SUBMISSION_FORM.md).

Recommended title:

> ProofRAG: Evidence-First Multimodal Maintenance Intelligence

Selected theme:

> Theme 2: Multimodal Maintenance Intelligence Agent

## 4. Product definition

### User problem

Maintenance knowledge is fragmented across manuals, scanned bulletins, tables, drawings, and versions. Technicians need quick answers but cannot safely rely on text that lacks provenance.

### Product promise

ProofRAG returns a cited answer that the user can inspect, or it explicitly says that the corpus cannot support an answer.

### Primary demonstration

The synthetic PX-200 base manual and service bulletin create three clear scenes:

1. **Supported troubleshooting:** E-17 returns safety prerequisites and cooling-system checks.
2. **Version/bulletin reasoning:** a dusty-site filter interval changes from 500 to 250 hours/monthly.
3. **Safe abstention:** a refrigerant question has no support and returns no procedural answer.

### Boundaries

- Not an autonomous control system.
- Not a replacement for qualified technicians or site safety procedures.
- Not evidence that the synthetic equipment or results apply to ABB products.
- Not yet a production semantic-search platform.

## 5. What has been built

### Application source

| Area | File(s) | Responsibility |
|---|---|---|
| Configuration | `src/proofrag/config.py` | Typed environment configuration and validation |
| Domain models | `src/proofrag/models.py` | Documents, chunks, answers, citations, evaluation records |
| Storage | `src/proofrag/database.py` | SQLite schema, transactional persistence, audit log |
| Ingestion | `src/proofrag/ingestion.py` | PDF/text extraction, OCR hooks, tables, figures, chunks |
| Embeddings | `src/proofrag/embeddings.py` | Deterministic local vector baseline |
| Retrieval | `src/proofrag/retrieval.py` | BM25/vector scoring, filters, ranking |
| Answering | `src/proofrag/answering.py` | Evidence gate, extractive and OpenAI-compatible providers |
| Orchestration | `src/proofrag/service.py` | Pruning, citations, safety warnings, query logging |
| Safety | `src/proofrag/safety.py` | Visible independent safety policy notices |
| API | `src/proofrag/api.py` | FastAPI routes, uploads, questions, PDF page highlights |
| CLI | `src/proofrag/cli.py` | Demo seeding and evaluation commands |
| Evaluation | `src/proofrag/evaluation.py` | Golden-case evaluation and report generation |
| Web interface | `src/proofrag/static/` | Uploads, corpus selection, query, answer, citation viewer |

### Demo and evaluation assets

| Asset | Purpose |
|---|---|
| `data/demo-corpus/sentinel_px200_manual_v1.md` | Synthetic base manual |
| `data/demo-corpus/sentinel_px200_service_bulletin_v1_1.md` | Synthetic superseding bulletin |
| `data/evaluation/development.jsonl` | 25 calibration/development cases |
| `data/evaluation/locked.jsonl` | 25 frozen test cases used by the evaluation command |
| `data/evaluation/questions.jsonl` | Original six-case smoke fixture retained for context |
| `tests/` | Embedding, ingestion, retrieval, duplicate, grounding, and abstention tests |

### Packaging and deployment

- `pyproject.toml`: project metadata and dependency declarations.
- `uv.lock`: exact cross-platform dependency resolution.
- `.python-version`: intended Python 3.12 interpreter.
- `.env.example`: safe configuration template.
- `uv` and `uv.lock`: the sole supported local packaging and execution path.
- `LICENSE`: MIT project license.

## 6. Requirements traceability

| Challenge/submission requirement | Implementation or artifact | Status |
|---|---|---|
| Multimodal document ingestion | PDF blocks, OCR hook, tables, figure/caption regions | Implemented and exercised with the synthetic PDF pack |
| Hybrid semantic/keyword search | BM25 + hashing-vector baseline | Implemented and evaluated on synthetic cases |
| Citation-backed answers | App-owned `Citation` records and UI cards | Implemented and covered by API/grounding tests |
| Source highlighting/evidence viewer | Bounding boxes and rendered PDF page endpoint | Implemented and API-tested with PDF evidence |
| Technician-friendly interface | Responsive static UI with demo prompts and states | Implemented; final screenshots still pending |
| Multi-document reasoning | Retrieval across base manual and conditional bulletin | Implemented as version-visible, applicability-aware retrieval |
| Safe unsupported behavior | Absolute evidence decision and zero-citation abstention | Implemented and adversarially tested |
| Project summary | `docs/PROJECT_SUMMARY.md` | Draft complete |
| Working prototype | `src/proofrag/` | Locked runtime and automated paths verified |
| Demo video | `docs/DEMO_VIDEO_SCRIPT.md` | Script complete; recording pending |
| Source repository | Tracked `origin` on `master` | Initialized and pushed locally; public/private-browser access check and submission tag pending |
| Technical documentation | `docs/TECHNICAL_DOCUMENTATION.md` | Draft complete |
| Presentation upload | `ProofRAG_Idea_Report.pdf` and `docs/PRESENTATION_DECK.md` | Three-page PDF opens and is under 50 MB, but page 3 has stale pre-verification evaluation copy and no link annotations/screenshots; regenerate before submission |
| Evaluation evidence | `docs/EVALUATION_PLAN.md` and evaluation runner | First run and post-fix locked run recorded |
| Responsible AI | `docs/RESPONSIBLE_AI.md` | Draft complete |

## 7. Documentation index

| Document | Read when… |
|---|---|
| [`../README.md`](../README.md) | Setting up, running, or understanding top-level capabilities |
| [`SUBMISSION_FORM.md`](SUBMISSION_FORM.md) | Filling the current HackerEarth form |
| [`PROJECT_SUMMARY.md`](PROJECT_SUMMARY.md) | Preparing the written project narrative |
| [`PRESENTATION_DECK.md`](PRESENTATION_DECK.md) | Building the required deck upload |
| [`DESIGN_AI_REPORT_BRIEF.md`](DESIGN_AI_REPORT_BRIEF.md) | Generating the complete ABB-style idea report or slide deck in a design AI |
| [`DEMO_VIDEO_SCRIPT.md`](DEMO_VIDEO_SCRIPT.md) | Recording the final demonstration |
| [`TECHNICAL_DOCUMENTATION.md`](TECHNICAL_DOCUMENTATION.md) | Reviewing architecture, APIs, storage, and scaling |
| [`EVALUATION_PLAN.md`](EVALUATION_PLAN.md) | Measuring retrieval, grounding, citations, and abstention |
| [`RESPONSIBLE_AI.md`](RESPONSIBLE_AI.md) | Reviewing safety, privacy, security, and human authority |
| [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) | Tracking what is complete and still required |
| [`../ABB_ACCELERATOR_2026_CHALLENGE_BRIEF.md`](../ABB_ACCELERATOR_2026_CHALLENGE_BRIEF.md) | Reviewing official competition research and concept ranking |
| [`../AGENTS.md`](../AGENTS.md) | Making future code or documentation changes |

## 8. Verified locked run

Dependencies were synced on 2026-09-21. On 2026-09-26, 30 tests, Ruff, strict mypy, lock checking, and a fresh 25/25 isolated locked evaluation passed. The repeatable startup path is:

```powershell
uv sync --locked
uv run --locked python scripts/build_demo_pdfs.py
uv run --locked proofrag-seed
uv run --locked proofrag
```

Open `http://127.0.0.1:8000` and manually exercise:

1. Health endpoint and document list.
2. Seeded evidence count.
3. E-17 supported question.
4. Dusty-site bulletin question.
5. Refrigerant abstention question.
6. Upload of a permitted PDF.
7. Citation page rendering and bounding-box highlight.
8. Manual-version filter.

Then run:

```powershell
uv lock --check
uv run --locked pytest
uv run --locked ruff check .
uv run --locked mypy src
uv run --locked proofrag-evaluate
```

Record actual results and defects. Do not edit claims to imply that targets were achieved unless the outputs support them.

## 9. Required work before submission

### Critical

1. Create and upload the required presentation file from the outline.
2. Capture screenshots and record the primary and backup demo videos.
3. Verify the configured repository is accessible as intended, then tag the submitted commit.
4. Have an independent domain reviewer adjudicate the 50 authored evaluation cases.
5. Verify final repository, video, deck, and submission links in a private browser.

### Organizer confirmations

- Exact Idea Phase deliverable expectations.
- Whether ABB supplies documents or datasets after registration.
- Finalist count and onsite travel/lodging policy.
- Prize distribution per team or member.
- IP ownership and usage terms.
- Solo participation, if applicable.

### Polish

- Add team names and roles.
- Add a public repository/demo link after verification.
- Replace slide targets with measured results.
- Attribute all third-party assets and licensed source documents.
- Export a PDF deck under 50 MB and verify it opens.

## 10. Claims policy

Safe claims now:

- ProofRAG is designed around evidence gating and application-owned citations.
- The source implements PDF/text ingestion, hybrid retrieval, abstention, and an evidence UI.
- The default design can operate without an external model.
- The bundled corpus is synthetic.

Claims that remain bounded or require further review:

- The recorded locked metrics apply only to the synthetic PX-200 corpus and authored cases; they are not field accuracy claims.
- Citation precision is an automated document-level proxy until a qualified reviewer adjudicates claim-level support.
- Production scalability or security certification.
- Compatibility with specific ABB manuals or equipment.
- Proven downtime reduction or cost savings.

## 11. Recommended pitch framing

Lead with trust, not “chat with PDFs”:

> Generic AI optimizes for producing an answer. ProofRAG optimizes for proving whether an answer is supported.

Then demonstrate the difference:

- Exact fault code and safety steps.
- Later bulletin that changes the applicable value.
- Unsupported question that the system refuses.

Close with the adoption path:

> Pilot on one approved equipment family, evaluate with technician-authored questions, then scale only after citation and abstention targets are met.
