# Paper vs. Code Audit — "Zero-Knowledge Proof Based Multi-Factor Authentication System for IoT Devices"

**Paper ID:** QPAIN 2026 #4879 (Status: Reject)
**Audit date:** 2026-07-22
**Scope:** Compare every load-bearing claim in the paper against the cloned project in `MFA/`.
**Method:** Read the ZKP modules, the Flask server endpoints, and the ESP32 firmware; ran the protocol; measured timings and an offline attack directly.

> **One-line finding:** The protocol *equation* is correct textbook Schnorr, but the system the paper *describes* — on-device Schnorr on the ESP32, a 160-bit-subgroup speed optimization, and "honeypot" storage security — **does not exist in the code that produced the paper's numbers.** The device sends the PIN in cleartext; the ZKP is a Python simulation with broken parameters.

---

## A. What the paper CLAIMS

1. **On-device ZKP.** "Executing the Interactive Schnorr ZKP protocol directly on an ESP32-CAM." "We ported the Schnorr identification scheme to the ESP32 firmware using hardware-accelerated math libraries" (bare-metal contribution).
2. **160-bit subgroup optimization → 7.4 ms.** "By manually mapping the modular exponentiation logic to the Xtensa LX6 hardware accelerator and restricting operations to a 160-bit subgroup order (q) as defined in RFC5114, rather than the full 1024-bit modulus, we cut proof generation time down to 7.4 ms."
3. **Honeypot elimination.** "A SQL injection attack reveals no usable secrets, as recovering the PIN from Y requires solving the Discrete Logarithm Problem." Server stores only the public key Y.
4. **Zero-knowledge / MITM security.** The transcript (T, c, z) reveals nothing about x; PIN never leaves device RAM; verified by simulator indistinguishability.
5. **Empirical benchmarks.** ZKP-PIN 7.4 ms / 100% accuracy; Face 168.9 ms / 75.6%; PIN+Face 147.6 ms / 77.8%; 90 auth cycles, 9 subjects. Memory table includes a "ZKP Computation" state at 47.6% PSRAM on the ESP32.
6. **Verification log evidence (Fig. 3).** Server-side transcript showing `g^z` vs `T·Y^c` as proof the verifier works.

---

## B. What the CODE actually HAS

### B1. The ESP32 does **no** cryptography — it sends the PIN in cleartext
- On PIN entry, the firmware transmits the raw PIN: `Serial2.printf("PASSWORD:%s\n", password.c_str())` — [`esp32/interface_controller/interface_controller.ino:526`](MFA/esp32/interface_controller/interface_controller.ino#L526).
- The firmware labels this mode **"Password"** throughout (`MODE_PASSWORD_ONLY`, `MODE_MFA_PASSWORD`) — it is a password check, not a proof of knowledge.
- `grep` across both `.ino` files finds **zero** occurrences of Schnorr / commitment / modexp / BigNum. No prover exists on the device.

### B2. The Schnorr "prover" is a Python simulation, not wired into the live flow
- File header: *"Schnorr Protocol - Prover Side (ESP32 Simulation) … In real deployment, this code would run on ESP32 hardware. For testing, we simulate it in Python."* — [`src/zkp/schnorr_prover.py:2-6`](MFA/src/zkp/schnorr_prover.py#L2-L6).
- `SchnorrProver` is instantiated **only** in `tests/register_users_simulation.py` and the module's own self-test — never by the server's authentication path or the device. So the "7.4 ms on ESP32" number cannot have come from an ESP32; there is no on-device Schnorr code to time.

### B3. The "160-bit subgroup" optimization is not implemented (parameters are broken)
Verified numerically:
- `g = 2` ([`zkp_params.py:31`](MFA/src/zkp/zkp_params.py#L31)) is **not** the RFC5114 generator, and `2` is **not** in the RFC5114 160-bit subgroup (`2^q₁₆₀ mod p ≠ 1`).
- The `q` constant ([`zkp_params.py:43-50`](MFA/src/zkp/zkp_params.py#L43-L50)) is **malformed: 1039 bits — larger than `p` (1024 bits)**. It is neither the 160-bit RFC value nor `(p−1)/2`.
- The commitment exponent actually drawn is **~1033 bits** (full width), not 160.
- **Measured:** a real 160-bit-subgroup modexp is **~7× faster** than what the code runs (0.59 ms vs 4.15 ms per op on this machine). The mechanism the paper credits for its speed is absent — and would change the number if present.
- `p` itself **is** the genuine RFC5114 group-22 prime (that part checks out), but it is **not** a safe prime, despite the code comment calling it one.

### B4. "Honeypot elimination" is false — broken in 0.8 ms
- The secret is `x = int(pin)` — the literal 4-digit integer, 0–9999 (~13 bits) — [`schnorr_prover.py:54`](MFA/src/zkp/schnorr_prover.py#L54), [`:82`](MFA/src/zkp/schnorr_prover.py#L82).
- **Measured:** given the stored public key `Y`, the PIN is recovered by brute force in **0.8 ms** (try all 10,000 candidates). No discrete-log break required. The central security claim does not hold.

### B5. The verification-log evidence uses a bogus modulus
- The live accept/reject ([`server.py:555`](MFA/src/server.py#L555)) uses the correct verifier. **But** the `g^z` / `T·Y^c` values *printed to the logs* ([`server.py:570-575`](MFA/src/server.py#L570-L575)) are computed with a hardcoded `zkp_p` that is a **2051-bit composite number** — a different, non-prime modulus. Those two printed sides will not match even for a valid proof. Any figure built from these logs (e.g., Fig. 3) is mathematically meaningless.

### B6. What is actually correct
- The verification equation `g^z ≟ T·Y^c mod p` ([`schnorr_verifier.py:75-82`](MFA/src/zkp/schnorr_verifier.py#L75-L82)) is textbook Schnorr.
- Completeness holds (correct PIN → `True`) and functional soundness holds (wrong PIN → `False`); both were run.
- In the *simulation*, the PIN is never transmitted (only T, c, z), so the in-transit-privacy idea is sound **in principle** — it is just not what the device does.

---

## C. Side-by-side summary

| # | Paper claims | Code reality | Verdict |
|---|---|---|---|
| 1 | Schnorr runs **on the ESP32** (bare metal, HW-accelerated) | Firmware sends **cleartext PIN** (`PASSWORD:%s`); no crypto on device | **Contradicted** |
| 2 | 160-bit subgroup (RFC5114) → 7.4 ms | `g=2`, malformed 1039-bit `q`, full ~1024-bit exponents; no subgroup opt | **Contradicted** |
| 3 | DB leak needs discrete-log break | `x=int(pin)`; PIN recovered from `Y` in 0.8 ms | **Contradicted** |
| 4 | Zero-knowledge, PIN never on network | True only in the Python sim; device sends PIN in clear | **True in sim, false in system** |
| 5 | 7.4 ms measured on ESP32; "ZKP Computation" PSRAM state | No ZKP on ESP32 to measure; likely a PC/Python timing | **Unsupported / mis-attributed** |
| 6 | Verification transcript (Fig. 3) | Log previews use a 2051-bit composite modulus | **Invalid evidence** |
| — | Protocol equation, completeness/soundness | Correct textbook Schnorr | **Correct** |
| — | Face 75.6% / PIN+Face 77.8% on 9 subjects | Real code, but N far too small; CIs ~±15% | **Underpowered** |

---

## D. Summary

There are three severity tiers:

- **Tier 1 — the system is not what the paper describes.** The paper's headline contribution ("interactive Schnorr executing directly on the ESP32, 7.4 ms via a 160-bit-subgroup + hardware-BigNum optimization") is not in the code. The device transmits the PIN in cleartext; the Schnorr code is a self-described Python *simulation* with the wrong generator, a malformed subgroup order, and full-width exponents; and it is not even connected to the live authentication path. The reported on-device timing has no on-device implementation behind it.
- **Tier 2 — the security contributions do not hold.** "Honeypot elimination" is empirically false (PIN recovered from `Y` in <1 ms because `x = int(pin)`), and the verification-log evidence is computed against a bogus composite modulus.
- **Tier 3 — the parts that survive are modest and underpowered.** The protocol equation is correct and the in-transit-privacy idea is sound *in principle*; the biometric evaluation is real code but statistically too small (9 subjects) to support its stated accuracy claims.

This is why Reviewer 2's terse "methodology and results insufficient to support the conclusions" is, on inspection, correct — and stronger than it sounds: the gap is not presentation, it is that the described system was not the system that was built and measured.

**Consequence for resubmission:** the claims cannot be reused as-is. Fixing the writing alone would mean re-reporting results the implementation did not produce. Any honest path is **code-first** — make the implementation actually do what the paper says, then let the real measurements define the claims.

---

## E. Possible decisions

### Option 1 — Make it true, then narrow the paper (recommended)
Rebuild the crypto to actually implement the claim, then re-measure and re-scope.
- **Do:** real RFC5114 generator + 160-bit `q`; reduce `z mod q`; derive `x = H(pin‖salt) mod q` (kills the 0.8 ms attack); **actually implement Schnorr on the ESP32** (or honestly reframe as an edge-prover on a companion MCU) and time it on-device; re-measure with hundreds of trials + mean/std/CI; regenerate logs/figures from the correct verifier; add completeness/special-soundness/HVZK proofs; demote biometrics to a "feasibility" note; fix references + single-column figure.
- **Claim afterward:** an honest, defensible applied result — interactive Schnorr identification practical on a $10-class MCU, characterized for latency/memory, with in-transit ZK privacy and a stated PAKE path for at-rest.
- **Effort:** ~2–4 weeks (crypto fix is ~1 day; the real work is on-device implementation + re-measurement). **No new subjects needed.**
- **Venue:** IoT/embedded or applied-crypto **workshop / mid-tier venue** — not a broad security conference.
- **Risk:** low technical risk; modest-but-real contribution.

### Option 2 — Full multimodal MFA paper (higher ceiling, much more work)
Do Option 1 **plus** collect a real dataset (30–50+ demographically diverse subjects) and add genuine biometric fusion methodology.
- **Effort:** months. **Venue:** a stronger venue becomes plausible.
- **Risk:** biometrics on cheap sensors may not reach competitive accuracy; larger scope, larger surface for reviewers.

### Option 3 — Pivot the framing to "measurement/experience," keep it small
If on-device Schnorr implementation is not feasible soon, write an **honest engineering/measurement paper**: "we implemented interactive Schnorr as an edge-prover and characterized cost on constrained hardware," explicitly stating the prover runs on the companion controller / PC, with the corrected parameters. Drop every claim the hardware doesn't support.
- **Effort:** ~1–2 weeks. **Venue:** workshop / short-paper track.
- **Risk:** contribution is small; must be scrupulously honest about what runs where.

### Option 4 — Do not resubmit this work
If neither on-device implementation nor more data is realistic, the honest conclusion is that there is not yet a publishable contribution. Shelve it rather than resubmit claims the code contradicts.

### The non-negotiables (any option that resubmits)
1. Remove the cleartext-PIN path or stop claiming on-device ZKP.
2. Replace `x = int(pin)` with a salted-hash secret (and state the low-entropy/PAKE limitation).
3. Either implement the 160-bit subgroup for real or drop the subgroup speed claim.
4. Regenerate all logs/figures from the correct verifier prime.
5. Report timings only from the platform they were actually measured on.
