# HackerEarth Submission Form Copy

## Title

**ProofRAG: Evidence-First Multimodal Maintenance Intelligence**

## Description

### The problem

Industrial technicians often troubleshoot equipment by searching across long manuals, scanned service bulletins, tables, diagrams, and operating procedures. Traditional keyword search misses context, while generic AI assistants can return plausible but unsupported instructions. In a maintenance environment, an answer is only useful when the technician can verify where it came from and whether it applies to the correct equipment and manual version.

### Our solution

**ProofRAG** is an evidence-first multimodal maintenance assistant. It transforms technical documentation into grounded troubleshooting guidance with inspectable citations—and explicitly refuses to answer when the available evidence is insufficient.

The workflow is designed for maintenance and field-service teams:

1. Upload PDF, scanned, Markdown, or text documentation.
2. Extract page-aware text, tables, figures, captions, and optional OCR content.
3. Ask a natural-language troubleshooting question and optionally select the equipment or manual version.
4. Combine exact keyword retrieval with vector similarity to locate the strongest evidence.
5. Apply an evidence-sufficiency and safety gate.
6. Return concise guidance with numbered citations, or safely abstain.
7. Open any citation to inspect the original page and highlighted source region.

### What makes ProofRAG different

- **No evidence, no answer:** weak or missing support produces a visible abstention rather than a guess.
- **Application-owned citations:** citations are generated from indexed source records, not invented by an AI model.
- **Region-level verification:** PDF page coordinates are preserved so users can inspect the exact supporting area.
- **Version-visible, applicability-aware evidence:** model/version/type metadata remain visible and filterable, with conditional bulletin warnings rather than a claimed generic precedence engine.
- **Multimodal evidence model:** text, OCR, tables, and figure/caption regions participate in one retrieval pipeline.
- **Local-first operation:** the default extractive mode works without sending industrial documents to an external model.
- **Human-in-the-loop safety:** ProofRAG supports qualified personnel and never controls equipment or approves return to service.

### Prototype and technical approach

The current prototype includes document ingestion, structured evidence extraction, deterministic hybrid retrieval, grounded answering, safe abstention, safety notices, query auditing, highlighted PDF citations, a responsive technician interface, a synthetic demonstration corpus, and a repeatable evaluation harness.

It is built with Python, FastAPI, PyMuPDF, SQLite, BM25, a replaceable embedding layer, and a lightweight web interface. The project is reproducibly packaged with `uv` and a cross-platform lockfile. The answer layer can remain fully extractive or use an approved OpenAI-compatible model endpoint without surrendering citation control.

### Expected impact

ProofRAG can reduce time spent locating applicable procedures, improve maintenance knowledge transfer, expose conflicting or missing documentation, and reduce unsupported AI guidance. Our goal is not to replace technicians; it is to give them faster access to answers they can verify.

> The bundled PX-200 demonstration corpus is synthetic and does not describe real ABB equipment.

## Theme

**Theme 2: Multimodal Maintenance Intelligence Agent**

If the form shortens the option label, select the choice containing **Multimodal Maintenance Intelligence Agent** or **Grounded AI Assistant for Industrial Troubleshooting**.

## Presentation

The form requires an uploaded `.key`, `.odp`, `.odt`, `.pdf`, `.pps`, `.ppt`, or `.pptx` file under 50 MB. Use the outline in [`PRESENTATION_DECK.md`](PRESENTATION_DECK.md) to create the final deck.

Do not upload the currently tracked `ProofRAG_Idea_Report.pdf` unchanged: its third page still contains pre-verification evaluation copy and it lacks final screenshots and verified links.

Recommended filename:

```text
ProofRAG_ABB_Accelerator_2026_Pitch.pdf
```

## Before pasting into the form

- Keep measured results explicitly scoped to the synthetic PX-200 corpus and authored locked cases.
- Add a public source/demo link only after permissions and access have been verified.
- Add team member names where the platform requests them.
- Do not turn the automated citation proxy into a human-reviewed faithfulness claim or add unmeasured impact numbers.
- Confirm the presentation file opens and remains below 50 MB.
