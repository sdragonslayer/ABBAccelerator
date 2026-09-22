# ProofRAG Competition Handoff

## Handoff snapshot

ProofRAG is an evidence-first prototype for **ABB Accelerator 2026 — Theme 2: Multimodal Maintenance Intelligence Agent**. The primary local demo path is implemented around a clearly labeled synthetic PX-200 manual and service bulletin. It supports qualified personnel in inspecting evidence; it does not control equipment, authorize work, or approve return to service.

Verified implementation work includes:

- A separate evidence-sufficiency decision based on discriminative term coverage, exact identifiers/numbers, absolute vector support, and model/version applicability.
- Structured abstention reasons including weak support, wrong model, wrong version, missing applicable documents, and empty document selection.
- Source-derived safety prerequisites before guidance and hard refusal of safeguard/interlock bypass requests.
- Application-owned citations restricted to evidence indices actually referenced by the answer.
- Validation and extractive fallback for missing, out-of-range, or incomplete external-provider citations.
- Equipment model and document type metadata with additive SQLite migration.
- Exact model/version/document filters plus visible mixed-version and bulletin-applicability warnings.
- Streamed upload limits, PDF signature/parser validation, failed-upload cleanup, and validated preview bounding boxes.
- Blocking parsing, rendering, and database work moved outside asynchronous request handlers.
- Persistent ingestion/OCR warnings, three demo prompts, empty-selection behavior, and a permanent synthetic/non-ABB label.
- Editable Markdown sources and generated citation-ready PDFs with tables, an E-17 procedure, connector reference, figure caption, page numbers, versions, and disclaimers.
- Separate 25-case development and 25-case locked evaluation sets, retaining the original six-case smoke file.

## Honest capability boundary

Use the phrase **version-visible, applicability-aware retrieval**. ProofRAG does not implement a general version-precedence engine. The synthetic bulletin explicitly changes the 500-hour interval to 250 hours or monthly only for its stated dusty/fiber-rich environments.

Figure support means figure-region and caption indexing. It is not full diagram understanding. OCR is optional and depends on a working host Tesseract installation. The deterministic hashing embedder is a reproducible baseline, not a production semantic model.

“Evidence support” is a retrieval/support signal, not a probability that an answer is correct. Raw ranking scores remain diagnostic information.

## Evaluation record

The first frozen locked run on 2026-09-21 passed 18/25 cases. Review found genuine defects in compound safeguard refusal, ligature normalization, and evidence excerpt selection. That history is intentionally retained in `docs/EVALUATION_PLAN.md`.

The post-fix locked synthetic run passed 25/25 authored cases with:

| Metric | Measured result |
|---|---:|
| Recall@1 | 1.000 |
| Recall@5 | 1.000 |
| Mean reciprocal rank | 1.000 |
| Unsupported-question accuracy | 1.000 |
| False procedural-answer rate | 0.000 |
| Safety-order accuracy | 1.000 |
| Citation completeness | 1.000 |
| Automated document-level citation precision proxy | 0.750 |
| Median query latency | 23.641 ms |
| P95 query latency | 27.874 ms |

These results apply only to the synthetic PX-200 corpus and 25 authored locked cases in local extractive mode. The citation metric is an automated document-title proxy, not human-adjudicated claim-level faithfulness. Independent maintenance-domain review remains required before external accuracy claims.

The runtime report is written to ignored path `data/evaluation-results/latest.json`. It includes per-case results, configuration, timestamp, and corpus checksum. Its commit field truthfully reports that no commit identifier is available because this workspace is not currently a Git repository.

## Reproducible local path

Use `uv` exclusively:

```powershell
uv lock --check
uv sync --locked
uv run --locked python scripts/build_demo_pdfs.py
uv run --locked proofrag-seed
uv run --locked pytest
uv run --locked ruff check .
uv run --locked mypy src
uv run --locked proofrag-evaluate
uv run --locked proofrag
```

Open `http://127.0.0.1:8000`. The three intended demo prompts are available as buttons in the UI:

1. E-17 safety and inspection with cited prerequisites.
2. Dusty woodworking applicability with the conditional 250-hour/monthly bulletin interval.
3. Unsupported PX-200 refrigerant question with explicit abstention and zero citations.

## Final presentation outline

Target: 10 slides, 5–7 minutes. Use a 16:9 layout, large type, restrained industrial styling, and a visible `Synthetic PX-200 — not ABB equipment` footer on all evidence/demo slides.

### Slide 1 — ProofRAG: maintenance answers you can verify

- Evidence-first multimodal maintenance intelligence.
- “No evidence, no answer.”
- ABB Accelerator 2026, Theme 2.
- Add verified team names and roles only.

Visual: one document region flowing into a numbered citation and technician-facing answer.

### Slide 2 — The problem is applicability and proof

- Maintenance answers are fragmented across manuals, scans, tables, figures, and bulletins.
- The wrong model, revision, or operating condition can make a technically correct excerpt unsafe.
- Keyword search lacks procedural context; generic generation may sound plausible without support.

Visual: fragmented sources converging on one technician question.

### Slide 3 — Design principle: no evidence, no answer

- Ranking finds candidates; a separate evidence decision permits or rejects the answer.
- Exact fault/model/connector/number checks protect against incidental vocabulary overlap.
- Safety prerequisites come first.
- Weak or inapplicable support produces an actionable abstention.
- Qualified personnel and site procedures remain authoritative.

Visual: evidence gate branching equally to `CITED GUIDANCE` and `ABSTAIN`.

### Slide 4 — Product workflow

1. Validate and ingest permitted technical documents.
2. Preserve document/model/version/type/page/region provenance.
3. Retrieve with BM25 and a deterministic local vector signal.
4. Check evidence support and applicability.
5. Return cited extractive guidance or abstain.
6. Inspect the highlighted original PDF region.

Visual: six-step horizontal flow with the optional hosted provider downstream of the gate.

### Slide 5 — Demo path 1: E-17 with safety first

- Ask which checks apply to E-17.
- Show source-derived lockout/tagout and absence-of-voltage prerequisites before inspection.
- Show filter, fan, and J4 guidance.
- Open the PDF citation and highlighted evidence region.

Visual: actual product screenshot captured after the final clean seed.

### Slide 6 — Demo paths 2 and 3: applicability and abstention

- Dusty woodworking question cites the later bulletin and its 250-hour/monthly condition.
- Base-manual and bulletin versions/types remain visible.
- Explain that this is conditional applicability, not generic automatic precedence.
- Refrigerant question demonstrates overlap-resistant abstention, zero citations, and no-action warning.

Visual: side-by-side applicability warning and abstention state.

### Slide 7 — Architecture and trust controls

- Local PDF/text ingestion with optional OCR.
- Structured text/table/figure-caption chunks in SQLite.
- Hybrid ranking separated from evidence sufficiency.
- Application-owned citation records and external-citation validation.
- Documents treated as untrusted input.
- Hard safeguard-bypass refusal; no equipment-control path.
- Raw question/answer text not retained in audit rows.

Visual: five-layer architecture with citations and safety outside the optional model box.

### Slide 8 — Measured synthetic-corpus evidence

- Post-fix locked cases: 25/25.
- Recall@1 / Recall@5 / MRR: 1.000 / 1.000 / 1.000.
- Unsupported accuracy: 1.000; false procedural-answer rate: 0.000.
- Safety-order accuracy: 1.000.
- Automated document-level citation precision proxy: 0.750.
- Median/P95 latency: 23.641/27.874 ms on the final verification run.
- Retain the first-run 18/25 → defect review → post-fix rerun timeline.

Qualifier: authored synthetic cases, not independently adjudicated and not a field-performance claim.

### Slide 9 — From prototype to bounded pilot

- Start with one approved equipment family and immutable documents.
- Add technician-authored cases and independent claim/citation review.
- Introduce authentication, tenant isolation, encryption, malware scanning, and approved retention.
- Evaluate trained embeddings/reranking and structured applicability rules only after the trust baseline.

Visual: prototype → reviewed pilot → production hardening → controlled expansion.

### Slide 10 — Impact and ask

- Faster navigation to applicable source material.
- Fewer unsupported troubleshooting suggestions.
- Better knowledge transfer and evidence auditability.
- Visibility into missing, conflicting, or ambiguous documentation.

Ask: pilot ProofRAG on a bounded equipment family with approved manuals and technician-authored evaluation questions.

Close: **“ProofRAG — because the source is part of the answer.”**

## Presentation production checklist

- Add real screenshots only; do not mock unimplemented behavior.
- Add team, repository, demo, and contact details only after verification.
- Keep measured synthetic results visually separate from targets and expected impact.
- Include license/source attribution and the synthetic/non-ABB disclaimer.
- Export the required accepted format, verify it opens, and keep it under 50 MB.
- Rehearse the live path and retain a PDF backup and backup recording.

## Prioritized extension brainstorm

These are future extensions, not current capabilities.

### 1. Domain-reviewed pilot workflow

- Import one approved equipment family with immutable document approvals.
- Add dual-review adjudication for claim faithfulness, applicability, and citation precision.
- Record reviewer corrections without silently rewriting historical evaluation reports.

Why first: it converts a synthetic technical proof into trustworthy domain evidence.

### 2. Structured applicability and precedence engine

- Model effective dates, serial-number ranges, equipment variants, site conditions, and explicit supersession links.
- Return a trace explaining why one procedure applies and another does not.
- Treat unresolved ambiguity as abstention.

### 3. Table-cell and procedure-step provenance

- Preserve cell-level and list-step bounding boxes rather than broad table/page regions.
- Link answer claims to the smallest sufficient source region.
- Add citation-completeness validation at claim level.

### 4. Reviewed diagram intelligence

- Introduce a replaceable vision provider that produces bounded figure descriptions with region provenance.
- Require reviewer approval for stored descriptions and keep original captions visible.
- Never infer control logic from diagrams without explicit evidence and evaluation.

### 5. Retrieval upgrades behind stable interfaces

- Evaluate domain embeddings, cross-encoder reranking, query expansion, and identifier-aware scoring.
- Compare against the deterministic baseline on frozen sets.
- Retain abstention calibration instead of optimizing only answered-question rate.

### 6. OCR quality and document-health reporting

- Add per-page OCR confidence, deskew/orientation checks, language detection, and extraction quality dashboards.
- Route low-quality pages to review rather than silently indexing weak text.

### 7. Enterprise security and governance

- Authentication, role-based corpus access, tenant/facility isolation, encryption, malware/content-disarm scanning, and immutable audit events.
- Configurable retention with privacy-preserving analytics.
- Approved outbound model gateways with redaction and residency controls.

### 8. Human feedback and evidence correction

- Allow technicians to flag unsupported claims, wrong applicability, or imprecise citation regions.
- Require reviewer approval before feedback changes indexed evidence or evaluation labels.
- Track correction lineage by document version.

### 9. CMMS/EAM integration with a read-only boundary

- Link cited guidance to equipment records, work orders, and approved document sets.
- Keep ProofRAG advisory/read-only; do not issue control commands or approve return to service.

### 10. Multilingual and edge deployment

- Evaluate multilingual retrieval while preserving the original-language quote beside translations.
- Package an offline field-laptop mode with signed corpus updates and local inference.

## Remaining work requiring human or external coordination

- Initialize and push the approved source repository; the current workspace is not a Git repository.
- Add verified team identity and repository/demo links.
- Capture desktop and narrow-viewport screenshots after a clean seed.
- Produce the accepted presentation upload file from the outline above.
- Record primary and backup videos, add captions, and verify playback/access privately.
- Obtain independent maintenance-domain review of the evaluation cases and citations.
- Confirm unresolved organizer questions in `docs/SUBMISSION_CHECKLIST.md`.
- Submit before the internal four-hour safety buffer.

## Final verification — 2026-09-21

- `uv sync --locked --offline`: passed (38 packages checked).
- Synthetic PDF build and clean seed: passed; manual 7 blocks in 326.2 ms, bulletin 1 block in 148.5 ms.
- `pytest`: 23 passed; two upstream TestClient deprecation warnings remain.
- `ruff check .`: passed.
- `mypy src`: passed in strict mode.
- Locked evaluation: 25/25 passed; latest report median/P95 latency 23.641/27.874 ms.
- `uv lock --check`: passed.
- Secret-pattern review found only documentation placeholders, a test-only key, and source configuration/authorization code; no credential candidate was found.
- Docker build was not run because the Docker CLI is not installed on this machine.
- Runtime database, uploads, evaluation output, environments, and caches are covered by `.gitignore`. The workspace is not a Git repository, so committed-file and commit-ID checks are impossible here.

## Repository hygiene

Runtime databases, uploads, evaluation reports, environments, caches, and credentials must remain ignored. The bundled PDFs and Markdown files are synthetic; do not add confidential, proprietary, export-controlled, personal, or customer documents.
