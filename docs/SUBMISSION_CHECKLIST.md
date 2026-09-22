# Submission Checklist

## 1. Project summary

- [x] Problem, solution, innovation, users, and impact documented.
- [x] ABB judging alignment documented.
- [ ] Add final team name and member details.
- [ ] Confirm exact Idea Phase form/format with the organizer.

Artifact: `docs/PROJECT_SUMMARY.md`

## 2. Working prototype

- [x] Ingestion and evidence storage implemented.
- [x] Hybrid retrieval implemented.
- [x] Grounded extractive and optional external answer providers implemented.
- [x] Abstention, safety warnings, and citations implemented.
- [x] PDF highlighted evidence endpoint implemented.
- [x] Responsive web interface implemented.
- [x] Synthetic demonstration corpus included.
- [x] Run `uv sync --locked`.
- [x] Seed and exercise the automated API/demo paths.
- [x] Fix and document defects found during the first locked run.

Artifact: source under `src/proofrag/`

## 3. Demo video

- [x] Script and storyboard completed.
- [x] Supported, version-conflict, and abstention scenes defined.
- [ ] Record primary demo.
- [ ] Record backup demo.
- [ ] Add captions and verify audio.
- [ ] Upload to the permitted host and verify access permissions.

Artifact: `docs/DEMO_VIDEO_SCRIPT.md`

## 4. Source repository

- [x] `pyproject.toml` present.
- [x] `uv.lock` present.
- [x] `.env.example` present with no credentials.
- [x] README and license present.
- [x] Tests and evaluation fixtures present.
- [x] Runtime data ignored.
- [ ] Initialize/push the approved Git repository.
- [ ] Run secret scanning before making it public.
- [ ] Tag the submitted commit.

## 5. Technical documentation

- [x] Architecture and component design.
- [x] Data model and API examples.
- [x] Setup and configuration.
- [x] Production scaling path.
- [x] Limitations and future work.
- [x] Responsible AI and threat model.
- [ ] Add screenshots after the first run.
- [x] Add actual locked evaluation results and retain the first-run defect record.

Artifacts: `docs/TECHNICAL_DOCUMENTATION.md`, `docs/EVALUATION_PLAN.md`, and `docs/RESPONSIBLE_AI.md`

## 6. Presentation deck

- [x] Ten-slide narrative drafted.
- [x] Complete ABB-style report layout and design-AI prompt drafted.
- [x] Final presentation outline frozen in `docs/HANDOFF.md`.
- [ ] Add team, real screenshots, and verified links in the final slide file.
- [ ] Rehearse to the allotted pitch duration.
- [ ] Export PDF backup.

Artifacts: `docs/PRESENTATION_DECK.md`, `docs/DESIGN_AI_REPORT_BRIEF.md`

## Organizer confirmations

- [ ] Exact Idea Phase deliverable.
- [ ] Official or permitted dataset/document sources.
- [ ] Solo-team eligibility if applicable.
- [ ] Finalist count and onsite travel/lodging policy.
- [ ] Prize distribution per team/member.
- [ ] IP ownership and usage terms.

## Final quality gate

- [x] `uv lock --check`
- [x] `uv sync --locked`
- [x] `uv run --locked pytest` (23 passed; two upstream deprecation warnings)
- [x] `uv run --locked ruff check .`
- [x] `uv run --locked mypy src`
- [x] `uv run --locked proofrag-evaluate` (25/25 authored locked cases)
- [x] All current Markdown claims distinguish measured synthetic evidence from targets.
- [ ] Build/smoke-test Docker (Docker CLI unavailable on verification machine).
- [ ] All third-party sources and licenses are attributed.
- [ ] No proprietary or personal data is committed.
- [ ] Submission links work in a private browser window.
- [ ] Upload is complete before the earlier platform deadline.
