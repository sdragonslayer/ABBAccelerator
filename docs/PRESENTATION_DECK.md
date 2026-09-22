# Required Presentation: Slide Outline

The HackerEarth form requires an uploaded presentation file (`.key`, `.odp`, `.odt`, `.pdf`, `.pps`, `.ppt`, or `.pptx`) under 50 MB. This file is the content outline; it is not itself an accepted upload. Build the final deck in the preferred slide tool and export a PDF backup.

Recommended length: **10 slides / 5–7 minutes**. For a shorter Idea Phase pitch, combine Slides 7–8 and Slides 9–10.

## Slide 1 — ProofRAG

**Maintenance answers you can verify**

- Evidence-first multimodal troubleshooting
- ABB Accelerator 2026
- Team name and members

Speaker note: Industrial AI earns trust through evidence, not confidence alone.

Visual: product name, one-line promise, team names, and a clean source-document/citation motif.

## Slide 2 — The maintenance information problem

- Procedures are spread across manuals, scans, tables, drawings, and bulletins.
- Equipment downtime makes search time expensive.
- Keyword search misses context and cross-document relationships.
- Generic AI may hallucinate or cite the wrong version.

Visual: fragmented documents leading to a technician under time pressure.

Speaker goal: establish that the problem is applicability and trust, not merely document search.

## Slide 3 — Design principle

> No evidence, no answer.

- Retrieve before generating.
- Preserve page and region provenance.
- Put safety prerequisites first.
- Abstain when support is weak.
- Keep the technician in control.

Visual: a simple evidence gate—question → evidence → answer, with “insufficient” branching to abstention.

## Slide 4 — Product workflow

1. Ingest manuals, scans, tables, and figures.
2. Ask a natural-language fault question.
3. Retrieve with lexical and vector signals.
4. Gate on evidence strength and applicability.
5. Return cited guidance or abstain.
6. Inspect the original highlighted source.

Visual: six-step horizontal workflow using one sentence per step.

## Slide 5 — Live scenario

**Fault E-17**

- Base manual supplies safety and inspection steps.
- Service bulletin changes the filter interval for dusty sites.
- ProofRAG exposes version-visible, applicability-aware evidence without claiming a generic precedence engine.
- Unsupported refrigerant question is refused.

This slide transitions into the live demo.

Speaker goal: use one base-manual answer, one superseding bulletin, and one unsupported question to show all key differentiators.

## Slide 6 — Technical architecture

- PyMuPDF layout, OCR hooks, table and figure extraction
- SQLite evidence/audit store
- BM25 + embedding retrieval
- Evidence sufficiency and safety gates
- Extractive or approved OpenAI-compatible provider
- FastAPI and technician web interface

Visual: use the Mermaid architecture from the technical documentation.

Speaker goal: emphasize that citations and abstention are application-controlled rather than optional model behaviors.

## Slide 7 — Trust, safety, and governance

- Application-owned citations
- Region-level source inspection
- Prompt-injection-resistant evidence boundary
- Explicit abstention
- Local/offline default
- Query audit trail
- No equipment-control capability

Visual: shield with six compact trust controls. Include the synthetic-corpus disclaimer in the footer.

## Slide 8 — Measured synthetic-corpus evidence

- Post-fix locked cases passed: **25/25**
- Recall@1 / Recall@5 / MRR: **1.000 / 1.000 / 1.000**
- Unsupported-question accuracy: **1.000**
- False procedural-answer rate: **0.000**
- Safety-order accuracy: **1.000**
- Automated document-level citation precision proxy: **0.750**
- Median / P95 query latency: **23.641 / 27.874 ms** on the final verification run

Footer qualifier: synthetic PX-200 corpus, 25 authored locked cases, local extractive mode; not independently adjudicated and not a field-performance claim. Preserve the documented first run (18/25) and explain that the rerun followed fixes for genuine control defects.

Visual: a compact scorecard plus a small “first run → defect review → post-fix rerun” timeline. Do not present the citation proxy as human-reviewed faithfulness.

## Slide 9 — Scale and adoption

Prototype → production:

- SQLite → PostgreSQL
- JSON vectors → Qdrant/pgvector
- Local files → encrypted object storage
- Hashing baseline → evaluated industrial embeddings
- Single service → authenticated, queue-backed deployment

Deployment stages: documentation search → guided troubleshooting → technician feedback loop.

Visual: prototype-to-pilot-to-production roadmap with approval gates.

## Slide 10 — Impact and ask

- Faster navigation from fault to applicable procedure.
- Fewer unsupported troubleshooting suggestions.
- Better knowledge transfer and auditability.
- Visibility into missing or contradictory documentation.

**Ask:** Pilot ProofRAG on a bounded equipment family with approved manuals and technician-authored evaluation questions.

Closing line: **ProofRAG — because the source is part of the answer.**

Visual: three impact outcomes and a single pilot request. Add repository/demo links only after verifying access.

## Deck production checklist

- Use a 16:9 layout and large type readable on a projector.
- Prefer diagrams and screenshots over paragraphs.
- Keep ABB branding references factual; do not imply endorsement beyond hackathon participation.
- Add team names, roles, university, and contact details.
- Include source/license attribution in small footer text or an appendix.
- Keep measured synthetic results separate from targets and future field-validation claims.
- Export to `ProofRAG_ABB_Accelerator_2026_Pitch.pdf`.
- Verify the PDF opens, links work, fonts are embedded, and size is below 50 MB.
