# Supervisor Annotations and Reviewer Comments — Requirements for the New Paper

**Transcribed:** 2026-09-06, from the only existing copy.

**Source:** a 6-page scan of the rejected QPAIN 2026 submission (#4879), carrying Rupok Sir's handwritten margin notes, with the PROCONF reviewer-comments page as the final page. Archived as `archive/rejected_paper_QPAIN2026_4879_annotated.pdf`.

> ⚠️ **This scan is the only copy of the supervisor's annotations.** They exist nowhere else — no email, no meeting notes. They are transcribed here so they survive independently of a single image file, and so they can be worked from as a checklist.
>
> Unlike the rest of the old project, **the contents of this file ARE valid inputs to the new work.** They are requirements and criticism, not contaminated data.

---

## 1. Rupok Sir's handwritten annotations

Transcribed from the margins, with the page each appeared on and the section it sat beside.

| # | Annotation | Where it appears | What it asks for |
|---|---|---|---|
| 1 | *"Add Zero knowledge Explanation"* | p.1, beside the Introduction | The concept of zero-knowledge itself must be explained, not assumed. A reader outside cryptography should understand what is being proved and why it reveals nothing. |
| 2 | *"Privacy Preserving"* | p.1, beside the Abstract | Frame the contribution in privacy-preserving terms explicitly. |
| 3 | *"Hash Storage / Relation ZKP"* | p.1, margin | Make the relationship between what is stored (the hash / public key) and the ZKP explicit. |
| 4 | *"Use case discuss"* | p.1, top | A concrete use-case discussion is missing — who deploys this, where, and why. |
| 5 | *"Mathematical Expression with figure"* | p.2, beside Operational Modes | The mathematics must be presented with an accompanying figure, not as prose or bare equations. |
| 6 | *"It will go before implementation"* | p.3, beside Protocol Execution Flow | **Ordering requirement:** theory and protocol come *before* the implementation section. |
| 7 | *"Implementation circuit diagram"* | p.3 | A circuit diagram of the implementation is required. |
| 8 | *"Experimental setup"* | p.3 | The experimental setup must be described as its own component. |
| 9 | *"Add Circuitry Output picture"* | p.4, beside Performance Analysis | Photographic evidence of the working hardware and its output. |
| 10 | *"Add more reference"* | p.5, beside References | More references — matching Reviewer 1's point 3. |

### How these map onto the new work

| Annotation | Status | Where it lands |
|---|---|---|
| 1 — ZK explanation | ✅ Largely done | `PROJECT_DRAFT_HardwareBound_ZKP.md` §1 glossary and §6 proofs are written for a non-specialist reader |
| 2 — Privacy-preserving framing | 🔧 Partly | The draft argues it; the *framing* should lead |
| 3 — Hash storage / ZKP relation | ✅ Done | This is now the core contribution: `x = H(device_key ‖ PIN)`, server stores only `Y` |
| 4 — Use-case discussion | ❌ Not written | New section needed. Who is the user, what device, what deployment |
| 5 — Maths with figure | 🔧 Partly | §5.2 has the protocol table; needs a proper protocol-flow figure |
| 6 — Theory before implementation | ✅ Structurally correct | §5–6 (protocol, proofs) precede §8 (implementation plan) |
| 7 — Circuit diagram | ❌ Blocked on Phase 1 | Requires the hardware to exist |
| 8 — Experimental setup | 🔧 Specified, not executed | Phase 4 now specifies the setup in detail; the numbers do not exist yet |
| 9 — Circuitry output photo | ❌ Blocked on Phase 1 | Requires working hardware |
| 10 — More references | ✅ Substantially addressed | `RESEARCH_STUDY.md` provides 9 verified sources with full metadata |

**Four items (4, 5, 7, 9) remain genuinely outstanding.** Three of them depend on the firmware existing, so they are naturally Phase 1 deliverables. Item 4 — the use-case discussion — can be written now and should be, since it also speaks to Reviewer 2's "no clear contribution."

---

## 2. Reviewer comments — verbatim

From the PROCONF review system, page 6 of the scan.

> **Paper ID:** 4879
> **Title:** Zero-Knowledge Proof Based Multi-Factor Authentication System for IoT Devices
> **Status:** Reject

**Reviewer 1:**
> 1. Move Figure 1 into single column.
> 2. Make the Conclusion section more research-oriented and informative.
> 3. Add more relevant references that match the paper's topic and scope.

**Reviewer 2:**
> 1. The manuscript is not well written.
> 2. The methodology and results are insufficient to support the conclusions.
> 3. The work does not show a clear or significant contribution to the field.

### Reading them honestly

**Reviewer 1's points are all mechanical** — formatting, a stronger conclusion, better references. None required rethinking the work. All three are cheap to satisfy.

**Reviewer 2's points are the ones that mattered, and R2 was right.**

- *R2(2) — "methodology and results are insufficient"* is the terse version of what `archive/PAPER_VS_CODE_AUDIT.md` found in detail: the described system had not been built, and the reported numbers could not have come from it. **Addressed by** the code-first order of work (Phases 1–3 before any measurement) and Phase 4's measurement discipline.
- *R2(3) — "no clear or significant contribution"* was fair. "We combined ZKP with MFA on an ESP32" is not a contribution when the ZKP wasn't on the ESP32. **Addressed by** `RESEARCH_STUDY.md` §4, which identifies a specific gap no retrieved paper fills: hardware-bound low-entropy PIN authentication with a real sigma protocol, and isolated on-device proof-generation cost — which no paper in the set reports for a microcontroller.
- *R2(1) — "not well written"* is the least specific and easiest to underestimate. It should be treated as real: budget time for writing, and have Rupok Sir read a full draft before submission rather than at the end.

---

## 3. Consolidated checklist for the new paper

Carry this into the submission.

**Structure**
- [ ] Theory and protocol precede implementation *(Sir #6)*
- [ ] Concrete use-case discussion *(Sir #4)*
- [ ] Conclusion is research-oriented, not a summary *(R1 #2)*
- [ ] Figures fit a single column *(R1 #1)*

**Content**
- [ ] Zero-knowledge explained accessibly *(Sir #1)*
- [ ] Privacy-preserving framing leads *(Sir #2)*
- [ ] Stored-value ↔ ZKP relationship made explicit *(Sir #3)*
- [ ] Mathematics presented with a figure *(Sir #5)*
- [ ] References broad and on-topic *(Sir #10, R1 #3)*

**Evidence**
- [ ] Implementation circuit diagram *(Sir #7)*
- [ ] Experimental setup described *(Sir #8)*
- [ ] Photograph of working hardware and its output *(Sir #9)*
- [ ] Every number traceable to a measurement on the platform claimed *(R2 #2)*
- [ ] A contribution stated in one sentence, defensible against the literature *(R2 #3)*

**Process**
- [ ] Full draft read by Rupok Sir before submission, not at the deadline *(R2 #1)*
