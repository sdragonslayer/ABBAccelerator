# Project Summary: ProofRAG Maintenance Intelligence

## One-line pitch

ProofRAG is an evidence-first multimodal maintenance assistant that turns manuals, scans, tables, and diagrams into trustworthy troubleshooting guidance with inspectable citations and safe abstention.

## Problem

Industrial technicians must search across long technical manuals, service bulletins, drawings, tables, and scanned records while equipment is unavailable and time is expensive. Keyword search misses relationships, generic AI assistants can hallucinate, and a plausible answer without verifiable evidence is unsafe in an industrial environment.

The core problem is therefore not merely finding text. It is delivering the correct procedure for the correct equipment and manual version, showing the exact supporting evidence, and refusing to answer when that evidence is inadequate.

## Solution

ProofRAG provides a technician-oriented workflow:

1. Upload PDF, scanned, Markdown, or text documentation.
2. Extract page-aware text, tables, figures, captions, and optional OCR content.
3. Ask a natural-language troubleshooting question and optionally specify equipment/version.
4. Combine keyword and vector retrieval to collect the strongest evidence.
5. Pass evidence through a sufficiency and safety gate.
6. Produce a concise answer with numbered citations, or abstain when support is weak.
7. Open any citation to inspect the original page and highlighted evidence region.

## Innovation

- **Evidence-first generation:** Retrieval records, rather than model prose, own the citations.
- **Region-level verification:** PDF coordinates are retained so technicians can inspect the precise source area.
- **Safe abstention:** The product explicitly refuses unsupported questions.
- **Version-visible, applicability-aware retrieval:** Users can filter exact metadata and see manual/bulletin relationships and conditional warnings; generic automatic precedence is not claimed.
- **Multimodal evidence units:** Text, tables, figures, captions, and OCR blocks share one retrieval and citation model.
- **Transparent scoring:** Hybrid retrieval retains its keyword, vector, and combined scores.
- **Offline baseline:** The default path works without sending industrial documents to an external model.

## User and business impact

### Primary users

- Field-service technicians
- Maintenance engineers
- Control-room and operations personnel
- Technical-support teams

### Expected impact

- Reduce time spent locating applicable procedures.
- Reduce unsupported or hallucinated troubleshooting advice.
- Improve auditability and knowledge transfer.
- Help less-experienced technicians navigate documentation without hiding the source.
- Capture recurring information gaps through abstention and query logs.

## Prototype scope

The current MVP includes ingestion, structured evidence extraction, hybrid retrieval, grounded answers, abstention, safety notices, citations, highlighted PDF previews, a web UI, an API, a synthetic corpus, and a repeatable evaluation harness.

The prototype does not control equipment and does not replace qualified personnel. Figure understanding currently uses region/caption indexing; a vision-language model is a future extension.

## Demonstration scenario

The bundled synthetic PX-200 corpus contains a base manual and a later service bulletin. A technician asks about fault E-17. ProofRAG identifies safety prerequisites, cooling components, connector J4, and the relevant restart condition. A second question about dusty environments retrieves the bulletin's superseding 250-hour interval. An unsupported refrigerant question demonstrates abstention.

## Architecture summary

- FastAPI service and static technician UI
- PyMuPDF layout, table, figure, and OCR hooks
- SQLite evidence and audit store
- BM25 plus deterministic local embedding retrieval
- Extractive offline answer provider
- Optional OpenAI-compatible grounded provider
- `uv` dependency management and cross-platform lockfile

## Alignment with ABB judging criteria

| Criterion | Evidence in ProofRAG |
|---|---|
| Innovation & Creativity | Region citations, explicit evidence decision, applicability visibility, offline mode |
| Technical Excellence | Typed service boundaries, hybrid retrieval, structured storage, evaluation harness, Docker packaging |
| Problem–Solution Fit | Direct implementation of multimodal manual troubleshooting with cited answers |
| Scalability & Feasibility | Swappable embedding/generation providers and documented production migration path |
| User Experience | Technician-oriented query flow and side-by-side evidence inspection |
| Presentation & Demo | Clear supported, superseded, and unsupported scenarios |
