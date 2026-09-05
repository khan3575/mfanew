# Repository Triage — converting this repo into a clean starting point

**Created:** 2026-09-06
**Purpose:** Classify everything currently in this repository before anything is deleted, so the repo becomes a clean foundation for a new, valid ZKP + MFA project — and so we have a permanent record of what was removed and why.

**Status: Stages 1, 3 and 4 executed 2026-09-06; `MFA/` removed per decision. Stage 2 (claim-level fixes) still outstanding.** See the removal log in §6.

---

## 0. The governing rule

> **The old project is a guardrail, not an input.**
> It records mistakes we must not repeat. Its numbers, claims, comparisons and figures must never flow into the new work as source material.

Practically, this splits everything in the repo into two very different kinds of "keep":

- **KEEP (active)** — clean material the new project builds on.
- **ARCHIVE (evidence)** — material we retain as a historical record of what went wrong, deliberately quarantined so it cannot be mistaken for input.

The distinction matters. Deleting the evidence would destroy our ability to explain what changed and why; leaving it loose in the repo root invites exactly the contamination we're trying to end.

### Classification codes

| Code | Meaning |
|---|---|
| ✅ **KEEP** | Clean, correct, part of the new project |
| 📦 **ARCHIVE** | Contaminated as data, but valuable as evidence — quarantine, never cite as input |
| 🔧 **FIX** | Keep, but has identified defects that must be corrected first |
| ❌ **REMOVE** | No value to the new project; delete |
| ❓ **DECIDE** | Needs your judgement — listed in §7 |

---

## 1. File-by-file inventory

### Root

| Item | Class | Reasoning |
|---|---|---|
| `RESEARCH_STUDY.md` | ✅ **KEEP** | Built from scratch under strict provenance rules. 9 papers, 8 read in full. No old-project data used as input. **This is the foundation of the new project.** |
| `papers/` (8 PDFs + README) | ✅ **KEEP** | Primary sources, each verified against its title page. Clean. |
| `PROJECT_DRAFT_HardwareBound_ZKP.md` | 🔧 **FIX** | The new design, and largely sound — but still contains three imports from the old project and several unsupported claims. Claim-level triage in §2. |
| `PROJECT_DRAFT_HardwareBound_ZKP.pdf` | ❌ **REMOVE** | Generated 22 Jul from a `.md` that has changed substantially since. A stale PDF that contradicts the live document is a hazard, not a backup. Regenerate when the draft stabilises. |
| `redesign_proof_of_concept/hardware_bound_schnorr_poc.py` | 🔧 **FIX** | Ed25519 maths is correct and the self-check passes. But §2 defects: the "OLD" comparison is fabricated, the honeypot test is vacuous, and replay/tamper tests are missing. |
| `PAPER_VS_CODE_AUDIT.md` | 📦 **ARCHIVE** | Accurate and well-evidenced — but it is *about* the old project, and its §E recommendations (RFC5114, 160-bit subgroup, keep biometrics) were superseded by the Ed25519 redesign. Keeping it in the root implies it is the live plan. |
| `CamScanner 27-2-26 23.17.pdf` | 📦 **ARCHIVE** | **Now identified** (was previously uninspected): the full rejected paper, scanned, with the supervisor's handwritten annotations, plus the reviewer comments screenshot. Every technical claim in it is contradicted. **But it is the only primary record of the rejection and the supervisor's requirements** — see §4. Rename on archive; the current filename tells you nothing. |
| `README.md` | 🔧 **FIX** | Currently the single line `# mfanew`. Must become the entry point describing the new project. |
| `MFA/` | ❓ **DECIDE** | 47 MB, 173 files, the entire old codebase. Also a **broken submodule** — see §3. Detailed breakdown below. |

### Inside `MFA/` — not uniform, do not treat as one blob

| Subtree | Class | Reasoning |
|---|---|---|
| `src/zkp/` | ❌ **REMOVE** | The core defect. `g = 2` not in the subgroup, malformed 1039-bit `q` larger than `p`, `x = int(pin)`. Nothing here is salvageable; the new design uses Ed25519. |
| `paper/`, `overleaf/` | 📦 **ARCHIVE** | The rejected manuscript's LaTeX sources, figures and the stale `SUBMISSION_CHECKLIST.md` (still describing QPAIN 2025, 7.4 ms, 9 subjects). Contaminated as content. |
| `esp32/interface_controller/` | ❓ **DECIDE** | Keypad + LCD driver. Contains the cleartext-PIN line (`PASSWORD:%s`) that must die, but the surrounding I/O scaffolding is ordinary working hardware code you may want to build Phase 1 on. |
| `esp32/face_auth_demo/` | ❌ **REMOVE** | Biometrics are dropped from the new design. |
| `src/server.py`, `database_manager.py`, `config.py` | ❓ **DECIDE** | Flask + DB scaffolding. Reusable *engineering* for Phase 2 — but `server.py` carries the bogus 2051-bit composite modulus in its logging path. Salvage selectively or rewrite clean. |
| `src/face_processor.py`, `models/`, `tests/`, `database/photos` | ❌ **REMOVE** | Biometrics, dropped. `models/` is also most of the 47 MB. |
| `static/`, `templates/` | ❓ **DECIDE** | Generic web UI. Low value, low harm. |
| `generate_proof_logs.py`, `latency_comparison.png`, `generate_latency_chart.py` | ❌ **REMOVE** | These produced the contradicted figures. Actively dangerous to keep. |

---

## 2. Claim-level triage inside the files we are keeping

Files can be clean overall and still carry contaminated passages. These are the specific items.

### `PROJECT_DRAFT_HardwareBound_ZKP.md`

| Location | Issue | Action |
|---|---|---|
| §2 | *"The old design stored `Y = PIN·B`"* — false. The old system used `g^PIN mod p`, not a curve. | ❌ Remove the old-design comparison. Motivate the honeypot problem generically: *any* scheme storing a verifier derived from a ~13-bit secret is brute-forceable. |
| §2, §6.4, §11 | *"leaks the PIN in ~7 ms"* — a number produced by the PoC re-implementing a system that never existed. | ❌ Remove all three instances. |
| §3, §6.4 | Search space stated as `10⁴ × 2²⁵⁶` ≈ 2²⁶⁹ | 🔧 Wrong, and contradicts §11's own "~128-bit security". The real bound is the Ed25519 DLP, ≈2¹²⁶. Correct to ~128-bit. |
| §7, §9, Appendix | *"Every security claim in §6 is matched by a passing check"* / *"The PoC already passes the logic versions of these"* | ✅ **Already fixed in §9.** Still to fix in §7 and the Appendix line — §6.5 (replay) has no test. |
| §3 vs §8 Phase 3 | `device_key` "generated at manufacturing" vs generated during provisioning | 🔧 Pick one; they are different trust models. |
| §4 | Architecture diagram shows one chip; the real hardware is two boards with a UART between them | 🔧 Either move to a single board or show the bus and state what crosses it. |
| §10 | Assumes the eFuse key store is honest | 🔧 Keep the assumption, but state it explicitly and cite P4 (EUROCRYPT 2026), which designs for a *subverted* secure element. |
| §8 Phases 4–5 | — | ✅ **Clean, rewritten today.** Per-operation table, `n` and spread, ProVerif. |

### `redesign_proof_of_concept/hardware_bound_schnorr_poc.py`

| Location | Issue | Action |
|---|---|---|
| Lines 104–110 | The "OLD" brute-force attack — Ed25519 `x = int(PIN)`, a system that never existed | ❌ **Delete this block.** It is the single most contaminated thing in otherwise clean code. |
| Lines 111–118 | Honeypot test draws a **fresh random device key each iteration** and tries only 2,000 of 10,000 PINs | 🔧 Rewrite: fix the device key, sweep all 10,000 PINs, report zero matches. |
| — | No replay test, no tampered-`s` test | 🔧 Add both. §6.5 is the draft's weakest claim. |
| Lines 78–80 | Wrong-PIN check reuses `r` and `c` from the successful run | 🔧 Minor; draw fresh values so it resembles a real failed login. |
| Lines 9–101 | Ed25519 arithmetic, completeness, soundness, ZK simulator | ✅ **Correct.** Self-check `L·B = identity` passes. Keep as is. |

---

## 3. The broken submodule — fix this regardless of what you decide about `MFA/`

`MFA/` is recorded in git as a **gitlink** (mode 160000, commit `c183db9`) but there is **no `.gitmodules` file**. A fresh clone of this repo produces an empty `MFA/` directory with no way to fetch its contents. The history is not actually captured here.

Whatever you choose in §7, this must be resolved — either properly registered as a submodule, or removed from tracking, or vendored in as plain files. Leaving it as-is means the repo does not reproduce.

---

## 4. What is genuinely worth carrying forward from the old work

Short list, deliberately. Everything here is a *requirement or lesson*, not data.

**From the reviewer comments** (page 6 of the scan — primary source, QPAIN 2026 paper #4879, status **Reject**):

> **Reviewer 1:** (1) Move Figure 1 into single column. (2) Make the Conclusion more research-oriented and informative. (3) Add more relevant references matching the paper's topic and scope.
> **Reviewer 2:** (1) The manuscript is not well written. (2) The methodology and results are insufficient to support the conclusions. (3) The work does not show a clear or significant contribution to the field.

Reviewer 1's points are all mechanical and easy. Reviewer 2's are the real ones — and R2(3) is addressed directly by `RESEARCH_STUDY.md` §4, which now identifies a specific unclaimed gap.

**From the supervisor's handwritten annotations on the scan** — these are structural requirements for the new paper and remain valid:

- Add a zero-knowledge **explanation** (the concept, spelled out)
- Add **mathematical expression with figure**
- Discuss the **use case**
- Add **implementation circuit diagram** and **experimental setup**
- Add **circuitry output picture**
- Theory section goes **before** implementation
- Add more references
- Emphasise **privacy preserving** framing and the **hash storage / ZKP relation**

**From the codebase:** the Flask/DB/UI scaffolding and the keypad/LCD I/O code — as engineering only, never as results.

**Everything else from the old project carries forward as nothing.**

---

## 5. What the clean repo should look like

```
PaperWithRupokSir/
├── README.md                   ← entry point for the NEW project
├── RESEARCH_STUDY.md           ← literature foundation (clean)
├── papers/                     ← 8 source PDFs (clean)
├── PROJECT_DRAFT_HardwareBound_ZKP.md   ← after §2 fixes
├── proof_of_concept/           ← after §2 fixes
├── REPO_TRIAGE.md              ← this file: the record of what changed
└── archive/                    ← quarantined evidence, never an input
    ├── README.md               ← "nothing in here is a source for the new work"
    ├── rejected_paper_QPAIN2026_4879_annotated.pdf
    ├── PAPER_VS_CODE_AUDIT.md
    └── old_codebase/           ← if retained at all
```

---

## 6. Removal log

*Each stage is executed only after sign-off, and recorded here with the date and reason. Nothing is deleted silently.*

| Date | Item | Action | Reason | Recoverable? |
|---|---|---|---|---|
| 2026-09-06 | `CamScanner 27-2-26 23.17.pdf` | Moved → `archive/rejected_paper_QPAIN2026_4879_annotated.pdf` | Contaminated as data, essential as evidence. Renamed because the original filename said nothing. Annotations transcribed to `SUPERVISOR_AND_REVIEWER_REQUIREMENTS.md` first | Yes — in repo |
| 2026-09-06 | `PAPER_VS_CODE_AUDIT.md` | Moved → `archive/` | About the old project; its §E recommendations were superseded by the Ed25519 redesign. Root placement implied it was the live plan | Yes — in repo |
| 2026-09-06 | `MFA/` (173 files, 47 MB) + its gitlink | **Deleted** | Decision: no code reused. `src/zkp/` unsalvageable; `paper/`+`overleaf/` contaminated; biometrics dropped from the new design. Also fixes the broken-submodule problem (§3) | **Yes — `git@github.com:jannatul-musruk/MFA.git` @ `c183db9`, verified in sync before deletion** |
| 2026-09-06 | `PROJECT_DRAFT_HardwareBound_ZKP.pdf` | **Deleted** | Generated 22 Jul from a `.md` since substantially rewritten. A stale PDF contradicting the live document is a hazard | Regenerate from the `.md` |

**Recommended order** — safest first, so nothing irreversible happens early:

1. ✅ **Stage 1 — `archive/` created, evidence moved.** Done 2026-09-06.
2. ⬜ **Stage 2 — Fix the claim-level contamination** in the draft and PoC (§2). **Still outstanding — this is the next task.**
3. ✅ **Stage 3 — `README.md` rewritten** as the new project's entry point. Done.
4. ✅ **Stage 4 — Stale draft PDF removed.** Done. (The figure-generating scripts went with `MFA/`.)
5. ✅ **Stage 5 — `MFA/` deleted**, submodule breakage resolved by removal. Done.

---

## 7. Decisions — RESOLVED 2026-09-06

1. **`MFA/`** → **Removed entirely.** No code reused; Phases 1–2 built clean. Recoverable from GitHub.
2. **Git history** → **Not preserved as history.** Documented instead in `PAST_WORK_AND_DESCRIPTION.md`.
3. **Repo** → **New project stays here.** Continuity kept; contamination handled by `archive/` plus this document.
4. **Sir's annotations** → **This scan is the only copy.** Transcribed into `SUPERVISOR_AND_REVIEWER_REQUIREMENTS.md`.

### Original framing of these decisions

1. **`MFA/` — what happens to the old codebase?** Options: (a) archive the whole thing as a reference; (b) salvage only the Flask/DB scaffolding and the keypad I/O, delete the rest; (c) delete entirely and rebuild Phase 1–2 clean. *My view: (b), but you know how much of that engineering you actually want to reuse.*
2. **Is the old work's history worth preserving in git at all?** If yes, the submodule must be properly registered. If it is only a reference, vendoring the useful files and dropping the gitlink is simpler.
3. **Does the new project stay in this repo, or start in a fresh one** with this repo archived whole? Staying here preserves continuity and the record; starting fresh guarantees no contamination. *My view: stay here — this document plus `archive/` gives the same guarantee without losing the trail.*
4. **Are Rupok Sir's annotations already reflected anywhere else** — a supervision email, meeting notes — or is this scan the only copy? If it is the only copy, it should be transcribed into a plain-text requirements list rather than left as an image.
