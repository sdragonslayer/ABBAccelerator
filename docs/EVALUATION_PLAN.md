# Evaluation Plan

## Objective

Demonstrate that ProofRAG retrieves applicable evidence, grounds answers in that evidence, cites it correctly, and abstains when the corpus cannot answer.

## Current reviewed baseline

The most recent reviewed run was the isolated 2026-09-26 run after retrieval-metric corrections and grounding hardening. It passed 25/25 authored locked cases in local extractive mode.

| Metric | Measured result |
|---|---:|
| Raw Recall@1 | 1.000 |
| Raw Recall@5 | 1.000 |
| Mean reciprocal rank | 1.000 |
| Unsupported-question accuracy | 1.000 |
| False procedural-answer rate | 0.000 |
| Safety-order accuracy | 1.000 |
| Citation completeness | 1.000 |
| Automated document-level citation precision proxy | 0.750 |
| Median answer latency | 20.833 ms |
| P95 answer latency | 24.871 ms |

These are synthetic-corpus measurements on 25 authored locked cases, not field accuracy or human-adjudicated claim faithfulness. The citation value is an automated document-title proxy and is not comparable to the human claim-level citation-precision target below.

The run recorded commit `dc28f95b4738c8b5c14e9a9f5b8fc423f1f182bf` with `working_tree_dirty: true`. A final run after the submission content is committed must confirm that the report names the submitted commit and records a clean worktree.

`data/evaluation-results/latest.json` is an ignored runtime artifact. It may be absent or reflect an older local run, so the filename alone is not evidence that a result is current. Review its timestamp, commit, worktree state, corpus checksum, configuration, and per-case output before updating claims.

## Run history

- **2026-09-21, first frozen run:** 18/25 (72.0%). Recall@1/5 and MRR were 0.941; citation precision was 0.733; citation completeness was 0.960; unsupported-question accuracy was 0.875; false procedural-answer rate was 0.125; safety-order accuracy was 1.000; median/P95 latency was 20.688/24.189 ms.
- **2026-09-21, reviewed post-fix run:** 25/25. Recall@1, Recall@5, MRR, unsupported-question accuracy, citation completeness, and safety-order accuracy were 1.000; false procedural-answer rate was 0.000; the automated document-level citation precision proxy was 0.750; median/P95 latency was 24.454/34.710 ms. At that time, the workspace was not yet a Git repository, so the report could not record a commit.
- **2026-09-26, corrected-metric run:** retrieval metrics were changed to use raw retriever ranks rather than final selected citations; citation completeness entered supported-case pass/fail; the evidence gate was aligned with the exact pruned generator bundle; and hosted-answer validation was strengthened. The current baseline table above records this run.

Review of the first run identified genuine defects in compound safeguard-refusal wording, PDF ligature normalization, and page-level excerpt selection. Those defects were fixed; the later results do not erase the first-run record.

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

The 50 development/locked cases meet the planned breadth but still require independent technician review before any external accuracy claim. In particular, the 0.750 automated document-level proxy does not establish the ≥95% human claim-level citation-precision target. The original six questions remain a smoke set for regression context.

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
