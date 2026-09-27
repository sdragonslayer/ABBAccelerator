# Evaluation Plan

## Objective

Demonstrate that ProofRAG retrieves applicable evidence, grounds answers in that evidence, cites it correctly, and abstains when the corpus cannot answer.

The locked environment was first executed on 2026-09-21. The first frozen 25-case locked run passed 18/25 (72.0%). Its reviewed summary was Recall@1/5 0.941, MRR 0.941, citation precision 0.733, citation completeness 0.960, unsupported-question accuracy 0.875, false procedural-answer rate 0.125, safety-order accuracy 1.000, median latency 20.688 ms, and P95 latency 24.189 ms. This is a synthetic-corpus prototype measurement, not a field-performance claim.

Review of that run identified genuine defects in compound safeguard-refusal wording, PDF ligature normalization, and page-level excerpt selection. Those defects were fixed; any later rerun is reported separately and does not erase this first-run record.

The reviewed post-fix rerun on 2026-09-21 passed 25/25 authored locked cases. Recall@1, Recall@5, MRR, unsupported-question accuracy, citation completeness, and safety-order accuracy were 1.000; false procedural-answer rate was 0.000; the automated document-level citation precision proxy was 0.750; median/P95 query latency was 24.454/34.710 ms. The report records the threshold configuration, timestamp, corpus SHA-256, and the absence of a commit identifier because this workspace is not yet a Git repository. These are local synthetic-corpus measurements, not field accuracy or human-adjudicated faithfulness.

On 2026-09-26, retrieval metrics were corrected to use the retriever's ranked hits rather than the final answer's selected citations. Citation completeness was also made part of supported-case pass/fail, the evidence gate was aligned with the exact pruned bundle sent to the generator, and hosted-answer validation was strengthened. A fresh isolated run still passed 25/25. Raw Recall@1/5 and MRR were 1.000; unsupported accuracy, citation completeness, and safety-order accuracy were 1.000; false procedural-answer rate was 0.000; the document-level citation precision proxy was 0.750; median/P95 answer latency was 20.833/24.871 ms. The report recorded commit `dc28f95b4738c8b5c14e9a9f5b8fc423f1f182bf` and `working_tree_dirty: true`; rerun after committing to bind final results to the submitted revision.

## Evaluation dimensions

### 1. Retrieval quality

- **Recall@1/5:** Proportion of questions for which a supporting evidence block appears in the first one/five raw retrieval results, before answer citation selection.
- **Mean reciprocal rank:** Rewards placing the first correct evidence block earlier.
- **Version accuracy:** Proportion of version-filtered questions citing only the requested version.
- **Source-type recall:** Separate recall for ordinary text, tables, figures, and OCR blocks.

### 2. Answer quality

- **Expected-term coverage:** Required procedural facts present in the answer.
- **Faithfulness:** Every answer claim supported by at least one cited excerpt.
- **Citation precision:** Each citation actually supports the nearby claim.
- **Citation completeness:** Material claims are not left uncited.

### 3. Safety and abstention

- **Unanswerable accuracy:** Unsupported questions produce abstention.
- **False-answer rate:** Unsupported questions that receive a procedural answer.
- **Safety ordering:** Safety prerequisites appear before intervention steps when the sources require them.
- **Safeguard policy:** Requests to bypass interlocks are visibly rejected.

### 4. System quality

- Median and P95 end-to-end latency.
- Indexing throughput per page.
- OCR warning and failure rate.
- API error rate.
- Duplicate-document behavior.

## Bundled evaluation set

The repository retains the original six-case smoke file and now has two manually authored 25-case sets:

- `data/evaluation/development.jsonl` for calibration and development.
- `data/evaluation/locked.jsonl` for the locked test run used by `proofrag-evaluate`.

Together they cover supported procedures, tables/numbers, figure captions, version/applicability, overlapping-vocabulary hard negatives, and safety/safeguard cases.

- Safety prerequisite for E-17.
- E-17 component and connector checks.
- Superseding inspection interval from a service bulletin.
- Evidence against premature fan replacement.
- Numeric return-to-service threshold.
- Unsupported refrigerant question requiring abstention.

The corpus is synthetic, so these cases validate system behavior rather than real equipment expertise.

## Commands

After installing the locked environment:

```powershell
uv run --locked proofrag-seed
uv run --locked proofrag-evaluate
uv run --locked pytest
```

The evaluation command creates `data/evaluation-results/latest.json` and records the Git commit plus whether the working tree was dirty.

## Prototype acceptance targets

| Metric | Target |
|---|---:|
| Retrieval Recall@5 | ≥ 90% on a 50-question set |
| Citation precision | ≥ 95% |
| Expected-term coverage | ≥ 85% |
| Unanswerable accuracy | ≥ 90% |
| Unsupported procedural answer rate | ≤ 5% |
| Median local retrieval latency | < 500 ms at 10,000 chunks |

The 50 development/locked cases meet the planned breadth but still require independent technician review before any external accuracy claim. The original six questions remain a smoke set for regression context.

## Human review protocol

For each answer, two reviewers independently label:

1. Correct / partially correct / incorrect.
2. Fully supported / partially supported / unsupported.
3. Citations correct / mixed / incorrect.
4. Safety prerequisite correctly ordered / not applicable / incorrect.
5. Applicable manual/version selected / ambiguous / incorrect.

Disagreements are adjudicated and retained as evaluation notes. Reviewers must not be the developer who authored the corresponding golden case.

## Adversarial cases

- Prompt injection embedded in a manual.
- A question using the wrong model number.
- Conflicting base manual and later bulletin.
- Blurry scanned page with low OCR confidence.
- Numerically similar but incorrect thresholds.
- Request to bypass a protective interlock.
- Question for a component absent from the corpus.
