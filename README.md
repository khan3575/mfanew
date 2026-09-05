# Hardware-Bound Zero-Knowledge Authentication for IoT Devices

Research project toward a publishable paper on **zero-knowledge proof based multi-factor authentication** for low-cost microcontrollers.

**Status:** design complete, literature foundation complete, software proof-of-concept working. **No hardware implementation yet.** No performance numbers exist, and none will be claimed until they are measured on the chip.

---

## The idea in one paragraph

A user logs into a ~$5 ESP32 with a 4-digit PIN. The PIN never crosses the network, and stealing the server's database is useless to an attacker. This works because the login secret is not the PIN alone — it is the PIN mixed with a 256-bit key burned into the chip's eFuse:

```
x = H(device_key ‖ PIN) mod L        Y = x·B  (stored on the server)
```

The device proves knowledge of `x` with an Ed25519 Schnorr protocol. Because `device_key` never leaves the chip, a stolen `Y` cannot be brute-forced against 10,000 PIN guesses. The chip is the possession factor and the PIN is the knowledge factor, so it is genuine multi-factor authentication without a camera or a biometric dataset.

---

## Where things stand

| | |
|---|---|
| ✅ Literature foundation | 9 papers, 8 read in full, gap identified |
| ✅ Protocol design + written proofs | completeness, soundness, zero-knowledge, honeypot resistance |
| ✅ Software proof-of-concept | real Ed25519, all properties demonstrated |
| ⬜ Phase 1 — ESP32 firmware prover | **the actual contribution; not started** |
| ⬜ Phase 2 — server verifier | |
| ⬜ Phase 3 — provisioning / eFuse burn | |
| ⬜ Phase 4 — measurement on hardware | |
| ⬜ Phase 5 — ProVerif verification | |
| ⬜ Paper | |

---

## Files

| Path | What it is |
|---|---|
| [`PROJECT_DRAFT_HardwareBound_ZKP.md`](PROJECT_DRAFT_HardwareBound_ZKP.md) | The design: protocol, security proofs, threat model, phased implementation plan |
| [`RESEARCH_STUDY.md`](RESEARCH_STUDY.md) | Literature review — 9 papers with strict provenance, per-paper reading depth, and the gap analysis this project targets |
| [`papers/`](papers/) | The source PDFs |
| [`redesign_proof_of_concept/`](redesign_proof_of_concept/) | Runnable Python PoC over real Ed25519 |
| [`SUPERVISOR_AND_REVIEWER_REQUIREMENTS.md`](SUPERVISOR_AND_REVIEWER_REQUIREMENTS.md) | Rupok Sir's annotations and the reviewer comments, transcribed, as a checklist |
| [`REPO_TRIAGE.md`](REPO_TRIAGE.md) | What was kept, fixed, archived or removed when this repo was cleaned, and why |
| [`PAST_WORK_AND_DESCRIPTION.md`](PAST_WORK_AND_DESCRIPTION.md) | Description of the previous project and where to recover its code |
| [`archive/`](archive/) | Historical evidence — **not source material for this work** |

Run the proof-of-concept:

```bash
python3 redesign_proof_of_concept/hardware_bound_schnorr_poc.py
```

---

## The rule this project runs on

An earlier version of this work was rejected because the numbers in the paper did not come from the system the paper described. That failure is the reason for the following, which is non-negotiable:

> **Every claim must be traceable to a measurement taken on the platform being claimed.**
> No projected numbers. No figures inherited from previous work. No simulated result presented as an embedded one. Where something is unmeasured or unverified, it is written down as unmeasured.

The previous project is a guardrail, not a source. Its material lives in [`archive/`](archive/) and is quarantined there deliberately.
