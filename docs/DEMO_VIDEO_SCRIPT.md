# Demo Video Script and Storyboard

Target duration: **3 minutes 15 seconds**.

## Pre-recording checklist

- Run `uv sync --locked`.
- Run `uv run --locked proofrag-seed`.
- Run `uv run --locked proofrag-evaluate` and capture the measured result.
- Start `uv run --locked proofrag`.
- Confirm both synthetic documents appear in the evidence library.
- Prepare a PDF version of the synthetic manual if highlighted page rendering will be shown.
- Close notifications and hide API keys or unrelated browser tabs.
- Record a clean backup in addition to the final take.

## 0:00–0:20 — Problem

**Visual:** Title slide, then a collage of a manual, table, wiring diagram, and error display.

**Narration:**

> When industrial equipment fails, the answer may be spread across a 400-page manual, a scanned service bulletin, a table, and a diagram. Generic AI can produce a confident response, but maintenance teams need something more important: proof.

## 0:20–0:40 — Product

**Visual:** ProofRAG home screen and the “Evidence gated” badge.

**Narration:**

> ProofRAG is a multimodal maintenance assistant that answers only from indexed technical evidence. Every answer includes inspectable citations. When the evidence is insufficient, it refuses to guess.

## 0:40–1:05 — Ingestion

**Visual:** Open the upload form, show the base manual and later service bulletin already indexed, then briefly show evidence-block counts.

**Narration:**

> Documents are parsed into page-aware text, tables, figures, captions, and optional OCR content. ProofRAG retains each source page and bounding box, detects duplicate files, and records manual versions so later bulletins do not disappear inside a generic vector index.

## 1:05–1:45 — Supported troubleshooting question

**Action:** Ask:

> What should I inspect when fault E-17 appears, and what safety step comes first?

**Visual:** Show the answer, safety warning, confidence, and citation cards. Open the base-manual citation.

**Narration:**

> Hybrid retrieval combines exact fault-code search with vector similarity. The evidence gate accepts the result, safety prerequisites appear before intervention, and the response identifies the filter, fan, and J4 connector. Selecting a citation returns to the original source location instead of asking the technician to trust generated prose.

## 1:45–2:20 — Version conflict

**Action:** Ask:

> How often should the cooling filter be inspected in a dusty woodworking site?

**Visual:** Open the service-bulletin citation and point to the superseding 250-hour/monthly interval.

**Narration:**

> The base manual specifies 500 hours under normal conditions. The later bulletin changes that interval to 250 hours or monthly for dusty sites. ProofRAG surfaces the applicable bulletin and exposes the conflict instead of blending the values.

## 2:20–2:42 — Safe abstention

**Action:** Ask:

> What refrigerant type and charge mass does the PX-200 use?

**Visual:** Show “Insufficient evidence,” zero citations, and the no-action warning.

**Narration:**

> The corpus contains no refrigeration system. ProofRAG finds no adequate support, returns no citations, and explicitly says that no procedural action should be taken from the response.

## 2:42–3:02 — Engineering evidence

**Visual:** Architecture diagram, evaluation JSON, and API/docs briefly.

**Narration:**

> The prototype runs locally by default, uses deterministic retrieval, preserves an audit trail, and includes a repeatable evaluation suite for retrieval, citation correctness, expected facts, and abstention. The answer provider can remain fully extractive or use an approved model gateway without surrendering citation control.

## 3:02–3:15 — Close

**Visual:** Product screen and final tagline.

**Narration:**

> ProofRAG turns industrial documentation into answers technicians can verify—because in maintenance, knowing where an answer came from is part of knowing whether it is safe.

## Backup plan

- If the external model endpoint is unavailable, use the default extractive provider.
- If live upload fails, keep the seeded corpus.
- If page preview fails, show citation excerpts and a prerecorded highlighted-page clip.
- If the network is unavailable, the core seeded demonstration remains local.

