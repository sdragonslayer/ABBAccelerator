# Responsible AI and Threat Model

## Intended use

ProofRAG assists qualified personnel in locating and understanding approved maintenance documentation. It is a decision-support and navigation tool, not an autonomous control system, safety instrument, or substitute for training and authorization.

## Non-goals

- Operating or controlling industrial equipment.
- Approving return to service.
- Replacing lockout/tagout, PPE, permit, or site procedures.
- Diagnosing equipment without applicable evidence.
- Inventing a procedure when documentation is incomplete.

## Primary risks and controls

| Risk | Control |
|---|---|
| Hallucinated procedure | Evidence threshold, extractive default, citation requirement, abstention |
| Wrong model/manual version | User-visible filters, version metadata, source title/version on every citation |
| Prompt injection inside documents | Source content is marked as untrusted evidence; system behavior is not derived from it |
| Citation laundering | Citation objects come from database records, not model-generated identifiers |
| Unsafe action ordering | Safety notices and source prerequisites are displayed before intervention steps |
| Outdated bulletin | Preserve document versions; future effective-date policy is documented |
| Sensitive document leakage | Local default; external provider is opt-in; production needs access control and encryption |
| Malicious upload | Streamed size limit, PDF signature/parser validation, and cleanup now; production still requires antivirus, content disarm, and sandboxed parsing |
| Over-trust in support score | Label as evidence support, not correctness probability; expose sources and limitations; calibrate on reviewed data |
| Audit/privacy conflict | Local audit rows retain a question hash, not raw question/answer text; deployments still need retention policy |

## Human-in-the-loop boundary

- A technician chooses the corpus/equipment context.
- The technician inspects citations before acting.
- Site policies and qualified-person requirements remain authoritative.
- Escalation is required when sources conflict or the assistant abstains.

## Security considerations

- Add authentication and role-based corpus access before multi-user deployment.
- Encrypt data at rest and in transit.
- Use immutable source versions and record who approved each document.
- Extend signature/content validation beyond the implemented PDF signature and parser checks.
- Run parsers in resource-limited workers.
- Redact secrets and personal information before external model calls.
- Restrict outbound model endpoints through an approved gateway.
- Log administrative changes separately from technician queries.

## Transparency statement

The bundled corpus is synthetic and does not describe real ABB equipment. The local embedding technique is a baseline. OCR, table extraction, and evidence support may fail; warnings and original sources must remain visible. Locked synthetic-corpus measurements are not evidence of performance on ABB or field documentation.
