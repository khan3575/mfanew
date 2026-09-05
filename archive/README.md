# Archive — historical evidence, NOT source material

> ## Nothing in this folder is an input to the new project.
>
> No number, claim, figure, table or comparison in these files may be reused, cited as a baseline, or carried into the new paper. They are kept as a record of what was done before and why it failed — nothing more.

## Contents

| File | What it is |
|---|---|
| `rejected_paper_QPAIN2026_4879_annotated.pdf` | The rejected QPAIN 2026 submission (#4879), scanned, with Rupok Sir's handwritten margin notes and the PROCONF reviewer-comments page. **Every technical claim in it is contradicted** — see the audit. |
| `PAPER_VS_CODE_AUDIT.md` | The 2026-07-22 audit comparing that paper's claims against the code that produced its numbers. Accurate, and the reason the project restarted. |

## Two things were extracted from here and DO carry forward

Because they are requirements and criticism, not contaminated data:

- **`../SUPERVISOR_AND_REVIEWER_REQUIREMENTS.md`** — Sir's annotations and the reviewer comments, transcribed. The scan is the only copy of the handwritten notes, so they were lifted into text.
- **`../PAST_WORK_AND_DESCRIPTION.md`** — description of the deleted codebase and where to recover it.

## One caveat about the audit

`PAPER_VS_CODE_AUDIT.md` §E recommends fixing the old design in place — real RFC5114 generator, 160-bit `q`, keep biometrics as a feasibility note. **That plan was superseded.** The project moved to Ed25519 and dropped biometrics entirely. Read §A–D (the findings, which stand) rather than §E (the recommendations, which do not).
