# Past Work — Description and Record

**Written:** 2026-09-06, immediately before the old codebase was removed from this repository.

**Why this file exists.** The previous project's code has been deleted from this repo. Deleting it without a record would leave a gap no one could later explain — what was built, what it actually did, and why none of it carries forward. This file is that record.

> ⚠️ **This is a historical description, not a source.**
> Nothing here is an input to the new project. No number, claim, figure or comparison in this document may be reused, cited, or treated as a baseline. It exists so we can say *what happened*, not so we can build on it.

---

## 1. What the old project was

**"Zero-Knowledge Proof Based Multi-Factor Authentication System for IoT Devices"**
Authors: Sakib Khan, Jannatul Masruk Mukta, Rifa Sanjida, Humayan Kabir Rupok.
Submitted to **QPAIN 2026** as paper **#4879**. **Status: Reject.**

The intended claim was an interactive Schnorr zero-knowledge proof running directly on an ESP32-CAM, with a 160-bit-subgroup optimisation giving 7.4 ms proof generation, "honeypot elimination" (a stolen database revealing nothing), and a multimodal PIN + face + OTP authentication system.

---

## 2. Where the code lived, and how to get it back

The codebase was a nested git repository at `MFA/`, tracked in this repo as a gitlink (mode 160000) at commit `c183db9` — but with **no `.gitmodules` file**, so it was never a working submodule and a fresh clone produced an empty directory.

> ### The code is NOT lost. It is on GitHub.
> **`git@github.com:jannatul-musruk/MFA.git`** — branch `main`, HEAD `c183db9`.
>
> At the time of deletion the local copy was **fully in sync with `origin/main`, with nothing unpushed**. Deletion here removed a redundant local copy only.

**13 commits, 24 Oct 2025 → 26 Feb 2026.** Final commit: `c183db9 chore: clean and organize project, remove bloat and PDFs`.

---

## 3. What was in it

Roughly 173 files, 47 MB.

| Subtree | Size | Contents |
|---|---|---|
| `tests/` | 22 MB | Test scripts and fixtures, incl. registration simulation |
| `database/` | 788 KB | `embeddings.json`, enrolled subject photos |
| `overleaf/` | 476 KB | The submitted manuscript: `main.tex`, `references.bib`, figures (`verification_log.png`, `registration_log.png`, `latency_comparison.png`), `Results.docx` |
| `models/` | 204 KB | Face-recognition model files, Arduino files |
| `src/` | 172 KB | `server.py` (Flask), `database_manager.py`, `face_processor.py`, `config.py`, `zkp/` |
| `paper/` | 152 KB | Sectioned LaTeX drafts and `SUBMISSION_CHECKLIST.md` |
| `templates/`, `static/` | 96 KB | Web UI |
| `esp32/` | 80 KB | `interface_controller/` (keypad + LCD), `face_auth_demo/`, wiring and UART protocol guides |

Plus root scripts: `generate_proof_logs.py`, `generate_latency_chart.py`, `migrate_database.py`.

**Stack:** Python 3.12 + Flask server; InsightFace `buffalo_l` / ArcFace with ONNX for face recognition; Arduino sketches on an ESP32-CAM (AI-Thinker) plus a separate interface controller; SQLite-backed storage; SMTP for OTP delivery.

---

## 4. What it actually did — and why nothing carries forward

The full evidence is in `archive/PAPER_VS_CODE_AUDIT.md`. In summary, the system that produced the paper's numbers was not the system the paper described:

| The paper said | The code did |
|---|---|
| Schnorr ZKP runs on the ESP32 | Firmware sent the **PIN in cleartext** (`Serial2.printf("PASSWORD:%s\n", ...)`). `grep -ri schnorr esp32/` returned **nothing** — no prover on the device at all |
| 160-bit RFC5114 subgroup → 7.4 ms | `g = 2`, not in that subgroup; `q` malformed at **1039 bits — larger than the 1024-bit `p`**; exponents drawn at full width. The optimisation did not exist |
| DB theft needs a discrete-log break | Secret was `x = int(pin)` — a 4-digit integer, ~13 bits. PIN recovered from the stored public key in **under a millisecond** |
| Verification transcript (Fig. 3) | Log previews computed against a hardcoded **2051-bit composite** modulus — the printed sides could never match |
| 75.6% / 77.8% accuracy | Real code, but **9 subjects** — far too few to support the stated figures |

What *was* correct: the verification equation `g^z ≟ T·Y^c mod p` was textbook Schnorr, and completeness and functional soundness held in the Python simulation. That is the entire salvageable technical content, and the new design re-derives it correctly over Ed25519 anyway.

**Per your decision, none of the code is being reused** — not the Flask scaffolding, not the keypad I/O. Phase 1 and Phase 2 are built clean. The old repo remains on GitHub if any of it is ever wanted as a reference.

---

## 5. Why it was rejected

Reviewer comments are recorded verbatim in `SUPERVISOR_AND_REVIEWER_REQUIREMENTS.md` §2. The short version: Reviewer 2 wrote that *"the methodology and results are insufficient to support the conclusions"* and that the work showed no clear contribution. On inspection that was not a presentation problem — the described system had not been built or measured.

**The lesson, which is the only thing that carries forward:** every claim must be traceable to a measurement taken on the platform being claimed. That principle is now enforced in `RESEARCH_STUDY.md` §0 and `PROJECT_DRAFT_HardwareBound_ZKP.md` §8 Phase 4.

---

## 6. Removal record

| Date | Item | Action | Recoverable from |
|---|---|---|---|
| 2026-09-06 | `MFA/` (173 files, 47 MB) and its gitlink | Deleted from this repo | `git@github.com:jannatul-musruk/MFA.git` @ `c183db9` |
