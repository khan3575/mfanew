# Research Study — Zero-Knowledge Proofs for Multi-Factor / Device Authentication

**Compiled:** 2026-09-06
**Purpose:** Establish what the recent literature actually does, actually measures, and actually claims — so that our own paper (see `PROJECT_DRAFT_HardwareBound_ZKP.md`) is positioned against real work rather than against assumptions.
**Scope:** 9 papers retrieved and recorded, 2024–2026, biased toward (a) ZKP on constrained hardware and (b) hardware/device binding of credentials.

---

## 0. How this document was compiled — read this before using any number

The previous version of this project failed peer review because numbers in the paper did not come from the system the paper described. This document is written under rules designed to make that failure impossible to repeat here:

1. **Nothing is recorded that was not retrieved.** Every paper below was fetched. No citation was written from memory or from a search-engine summary.
2. **Provenance is attached to every number.** Each measurement records *the platform it was measured on*. A number without a platform is not usable.
3. **Retrieval depth is declared.** Some papers were read in full text; some only via publisher-verified metadata and abstract. §1 states which is which. **Do not cite an abstract-only entry for a methodological detail.**
4. **"NOT STATED" is preserved.** Where a paper does not report something, this document says so rather than filling the gap.
5. **Rejected claims are logged** (§8), not silently dropped.

### 0.1 Claims encountered during search and REJECTED

| Claim seen | Where it came from | Why rejected |
|---|---|---|
| FIDEM shows "sub-50 ms verification times and 288-byte proof sizes" on ESP32 | Search-engine result summary | **Not in the paper — confirmed against the full PDF.** FIDEM reports 9.06 ms median end-to-end (ESP32-S3) and states no proof size anywhere. Search summary fabricated or conflated both figures. |
| Z-PMA is a 2026 paper | Search-engine result summary | **Wrong year.** Publisher metadata gives IEEE Access **2024**, DOI 10.1109/ACCESS.2024.3450313. |

Both were plausible-sounding and both were wrong. This is the failure mode to guard against.

---

## 1. Verification ledger

| # | Short name | Retrieval depth | Source used |
|---|---|---|---|
| P1 | FIDEM (Lotto et al. 2026) | **Full text — PDF, 15 pp., incl. §7 evaluation and Appendix E** | arXiv PDF (verified against HTML) |
| P2 | Segkoulis & Limniotis 2025 | **Full text** (27 pp.; construction, implementation, evaluation, security analysis, conclusions) | Publisher PDF, obtained manually |
| P3 | Lee et al. 2025 (PUF+ZKP) | **Full text** (protocol figures + §4 + §5 read directly) | Publisher PDF, pages read |
| P4 | Friedrichs et al. 2026 (device binding) | **Full text** (60 pp.; abstract, intro, model, design principles read — formal proofs skimmed) | IACR ePrint PDF |
| P5 | Pathak et al. 2024 (Z-PMA) | **Full text** (19 pp.; testbed, Tables 4–6 read from page images, ProVerif analysis) | Publisher PDF, obtained manually |
| P6 | Seifelnasr et al. 2024 (MAPFS) | **Metadata + abstract only — PAYWALLED, no access available** | Semantic Scholar API |
| P7 | Tawfik et al. 2025 (quantum-resistant) | **Full text** (29 pp.; setup, results, limitations) | Publisher PDF |
| P8 | Mo et al. 2025 (two-factor IP) | **Full text** (methods + results) | PubMed Central PMC11836181 |
| P9 | Bodur 2026 (QR-assisted) | **Full text** (local PDF) | arXiv |

**Local PDFs:** `papers/` — 8 of 9 archived; see `papers/README.md`.

**Reading depth summary: 8 of 9 read in full.** The sole exception is **P6 (Seifelnasr et al., MAPFS)**, which is behind an IEEE paywall with no institutional access available. It is recorded here at abstract depth only, and **nothing in this document relies on P6 for any methodological or numerical claim** — its entry is limited to what its publisher-verified abstract states. If a reviewer challenges anything attributed to P6, the honest answer is that we have not read it.

> ⚠️ **Downloaded ≠ read** — a distinction worth keeping. P4's formal proofs were skimmed, not verified; its design principles and threat model were read closely. Do not cite P4 for a proof detail.

**Identified but NOT retrieved** (listed so they are not mistaken for read sources): "A Survey on Zero-Knowledge Authentication for Internet of Things", Electronics 12(5):1145; "Navigating Zero-Knowledge Authentication in the IoT Landscape: A Comprehensive Survey", IEEE (retrieval returned HTTP 429/404 on repeated attempts); Misra et al., *Multimedia Tools and Applications* 2025 (abstract elided by publisher).

---

## 2. The papers

### P1 — FIDEM: A Standard-Compliant Framework for Secure Binding of MUD Profiles to IoT Devices
**Lotto, Sciancalepore, Brighente, Conti.** arXiv:2605.29654, submitted 28 May 2026. Venue: NOT STATED.
**Retrieval: full text, from the PDF (15 pages, including appendices). Numbers below verified against §7.2 and Appendix E directly.**
**Artifact:** PoC source at https://github.com/aleLtt/FIDEM

> **This is the single most important paper for our project.** It is the closest thing in the retrieved literature to "Schnorr ZKP measured on a real ESP32."

- **Protocol:** Schnorr-based ZKP, **interactive** (challenge carried in DHCP option 161). Curve **secp256r1**, via **OpenSSL**. Security rests on the **Elliptic Curve Discrete Logarithm (ECDL) assumption**.
- **Flow:** device sends commitment `R = r·G`; receives challenge `C`; responds `Z = r + H·Kc` where `H = Hash(R ‖ Xc ‖ C ‖ URL)`. *(Structurally the same sigma protocol as our design, over a NIST curve instead of Ed25519.)*
- **Parameters (Appendix E):** nonce `r` 256 bits, challenge `C` 256 bits, secret key `K` 256 bits.
- **Hardware:** ESP32-S3 (dual-core Xtensa LX7, 512 KB internal SRAM, 2.4 GHz 802.11 b/g/n) and ESP32-C6 (32-bit RISC-V, 320 KB ROM, **has a TEE**) — real devices, not simulated.
- **Controller / test rig:** DELL Latitude 7400 laptop, Ubuntu 22.04.5 LTS, AlfaNetwork AR9271 USB antenna as AP (hostapd + systemd-networkd), Kea DHCPv4 server with `pkt4_receive` / `pkt4_send` hooks. Timing via POSIX `clock_gettime()`.
- **Energy instrument:** **Nordic Power Profiler Kit II (PPK2)**, connected directly to the IoT device.

> ### ⚠️ CRITICAL — what the 9.06 ms actually measures
> §7.2 defines it precisely: it is **the elapsed time of the overall MUD-Binding verification procedure measured at the MUD Controller side**, from reception of the DHCP Discovery message up to reception and verification of the ZKP response. It **includes the WiFi round trips and the device-side operations**.
>
> **It is NOT on-device proof-generation time.** FIDEM never isolates the cost of the Schnorr computation on the ESP32.
>
> Worse for comparison purposes: Appendix E states the device computes `H` and `Z` in an **asynchronous worker thread** *while the main process builds the DHCP Request*, a design explicitly chosen to "minimise latency introduced by cryptographic computations." The crypto cost is therefore partly overlapped with other work and partly hidden inside the network latency.
>
> **Consequence: we cannot compare our on-device proof-generation time to 9.06 ms.** Doing so would be exactly the platform-mismatch error our own audit condemned. See §3.2.

**Measured results (all medians over 100 protocol runs, reported as boxplots; no std/CI given):**

| Metric | Std. DHCP | FIDEM | X.509+HTTP | X.509+TLS |
|---|---|---|---|---|
| Time, ESP32-S3 (controller-side, end-to-end) | 6.99 ms | **9.06 ms** (≈+30%) | ≈1.05 s | ≈1.79 s |
| Energy, ESP32-S3 (device only) | 354 mJ | **385 mJ** (≈+8%) | 370 mJ | 574 mJ |

- **ESP32-C6:** FIDEM time overhead vs DHCP ≈ **7% (≈5 ms)**; **×20 faster** and **≈35% less energy** than X.509+TLS; FIDEM **with TEE ≈334 mJ**. Enabling the TEE costs ≈**3.5 ms** and ≈**6 mJ** (world-switching overhead). The C6's DHCP *baseline* time is higher than the S3's (different architecture/WiFi card), but it consumes less energy overall — a lower average power profile favouring idle states.
- **Energy scope:** measured on the IoT device only, from system setup (including cryptographic context initialisation) to reception of the DHCP Ack. Controller energy deliberately not measured.
- **Formal verification:** modelled in **ProVerif**. Q1/Q2 prove secrecy of the nonce `r` and class key `Kc`; Q3/Q4/Q5 prove **injective correspondence** on bindings, commitments `R`, challenges `C` and responses `Z` — i.e. replay resistance and freshness. ProVerif source in their repo.
- **Proof / message sizes:** NOT STATED. (`R` and `DevID` are carried in custom DHCP options 224 and 225 due to option-length limits.)
- **Stated limitations:** out-of-band channels (cellular, BLE, ZigBee) excluded and could bypass the router; compromise of the class-level key `Kc` affects **all** devices in that MUD class; LLDP cannot be supported because it is non-interactive while their Schnorr ZKP is interactive (a non-interactive variant would expose them to pre-computation and replay); **they explicitly assume secret material is protected in secure hardware**, acknowledging that some IoT devices lack such protection. They also observed **network failures during the TLS tests** affecting those timings.

✅ **Flag from the previous draft of this study — now RESOLVED.** The abstract's "≈5 ms and ≈20 mJ" overhead refers to the **ESP32-C6**, confirmed by §7.2 ("reduce FIDEM time overhead compared to standard DHCP to ∼7% (∼5ms)"). The ESP32-S3 deltas are ≈2.1 ms and ≈31 mJ. The two figures are consistent, not contradictory — they are different devices. *(Note: the ≈20 mJ figure is not restated numerically in §7.2; it is readable only from Fig. 7d. Cite it as approximate.)*

⚠️ **Minor terminology note (theirs):** §7.2 attributes the hardware acceleration to "the Cryptographic Acceleration and Assurance Modules (CAAM) module of the ESP-32 device." CAAM is NXP nomenclature; Espressif's ESP32 accelerators are not normally called CAAM. Their result stands, but do not repeat this name in our paper without checking Espressif's own documentation.

**Why it matters to us:** (i) it proves an interactive Schnorr ZKP on an ESP32 is a publishable, real result in 2026; (ii) **it leaves the exact gap we can fill — nobody has isolated and reported on-device sigma-protocol proof-generation cost**; (iii) its "secure hardware" assumption is *stated as an assumption* and its `Kc`-compromise weakness is a class-wide break, whereas our per-device eFuse binding is the actual contribution; (iv) 100 runs + boxplots + PPK2 energy + ProVerif is the evaluation standard we must meet; (v) their PoC is open source, so our comparison can be grounded rather than asserted.

---

### P2 — Enhancing Multi-Factor Authentication for Mobile Devices Through Cryptographic Zero-Knowledge Protocols
**Thomas Segkoulis** (Open University of Cyprus) and **Konstantinos Limniotis** (Open University of Cyprus / Hellenic Data Protection Authority). *Electronics* 14(9):1846, 2025, 27 pp. DOI 10.3390/electronics14091846. Received 27 Mar 2025, accepted 29 Apr, published 30 Apr 2025. Open access (CC BY). Citations: 3.
**Retrieval: full text (PDF obtained manually).**

> **Verdict after reading in full: this does NOT pre-empt our work. It is the nearest neighbour by idea, and it strengthens rather than threatens our position.** Details below.

- **Protocol: Feige–Fiat–Shamir (FFS)**, not Schnorr. Security rests on the difficulty of computing modular square roots / factoring `N = p·q`, with `p ≡ q ≡ 3 mod 4`.
  - Public key `υ_d = s_d² mod N`; witness `x = r² mod N`; challenge **`e ∈ {0,1}` — a single bit**; response `y = r·s_d^e mod N`; verifier checks `y² ≡ x·υ_d^e mod N`. Repeated `k` times.
  - `s_d` and `r` are **2048-bit**.
- **The secret is an OS-level software identifier, not a hardware key.** `s_d` is derived from the **iOS `identifierForVendor` (UUID)** or the **Android ID (SSAID)**, concatenated with the user identifier.
- **Implementation:** prover = iOS library (Swift); verifier = **Django 5.0.1 / Python 3.12.1**, one HTTP POST for registration plus two WebSocket connections. Code released across three repositories (their refs [31], [32], [33]).
- **Evaluation:** iPhone app as prover, **local** Django server as verifier. Three network conditions emulated with **Apple's Network Link Conditioner** (broadband, 3G, degraded). **Only ten tests per configuration point; averages only.**
- **Measured:** under broadband, "well below one second even at 10 rounds"; on 3G and degraded networks, "always within 3–4.5 s." The authors state plainly that **"fixed network latency is the dominant factor in overall verification time, rather than computational complexity."**
- **Recommended parameter:** `k = 8–10` rounds, giving an attacker bypass probability of `2⁻¹⁰ ≈ 0.98 × 10⁻³`.

**Three substantive weaknesses found by reading it — all of which we can improve on:**

1. ⚠️ **The security analysis argues about a construction the implementation does not use.** §5.2 states `s_d` is built by *"concatenating the unique device's identifier with the user identifier and adding required padding at the end in order to ensure a 2048-bit size."* But §6.1.1 justifies its security by *"using a strong hash function—i.e., one-way and collision-resistant—for deriving the user's secret key `s_d`."* **Concatenation-plus-padding is not a hash.** It is invertible and structurally predictable, and the true entropy of `s_d` is only that of the device identifier (a 128-bit UUID on iOS, 64-bit SSAID on Android) — not 2048 bits. *This is the same paper-versus-code gap our own audit documented, in a peer-reviewed 2025 journal article.*
2. ⚠️ **Soundness error of ~10⁻³ is weak for an authentication factor.** A single-bit challenge repeated 10 times gives a 1-in-1024 chance of blind bypass. Schnorr with a 256-bit challenge gives ~2⁻²⁵⁶ in **one** round. Their own §5.3 shows the cost of this: `k` round trips is why degraded-network authentication takes 3–4.5 s.
3. ⚠️ **The possession factor is software-readable and resettable.** They acknowledge the iOS identifier *"could be reset after re-installation"* — so the factor breaks on app reinstall. It lives in OS-managed storage, not in tamper-resistant hardware.

⚠️ **Internal inconsistency (theirs):** §5.3 reports broadband timings "well below one second even at 10 rounds"; §8 describes the same experiments as "less than 2 s in ideal communication conditions." Also §8 calls them "our simulations" though §5.3 describes real iPhone-plus-server measurements.

**Why it matters to us — and why it helps:** their **own stated future work asks for exactly what we build**: *"other ways to further strengthen the unpredictability of the device's private key could also be considered."* A 256-bit random key burned into eFuse is precisely that answer. So P2 establishes the idea's legitimacy and publishability, identifies the weakness of a software identifier, and leaves the hardware-rooted version open. Our differentiators are now concrete and defensible: **(a)** a hardware-protected secret instead of a software-readable OS identifier, **(b)** Schnorr's single round with negligible soundness error instead of FFS's 10 round trips at 10⁻³, **(c)** a genuine hash-based KDF matching what the security argument assumes, and **(d)** a $5 MCU instead of a smartphone.

---

### P3 — PUF-Based Device Authentication with Zero-Knowledge Proof in IoT
**Tung-Tsun Lee, Shyi-Tsong Wu, Yao-Jen Liang** (National Ilan University, Taiwan). *Journal of Internet Technology*, Vol. 26, No. 5, September 2025, article begins p. 675.
**Retrieval: full text.**

- **Idea:** device authentication rooted in an **SRAM-PUF** rather than a stored key, with the server holding no full CRP database.
- **Hardware:** Raspberry Pi 3 Model B; SRAM PUF is a **23LC1024** chip, 1 Mbit capacity. Power-off duration fixed at **300 ms** to obtain stable cells.
- **PUF quality:** 1 Mbit split into K=10 blocks of 256-bit; measured **Inter-Hamming-distance 49.53%** (ideal 50%).
- **Remanence data:** at 300 ms power-off, **81.93%** 1-skewed cells / **18.07%** 0-skewed; degrading to ~73–74% / ~26% at 330–930 ms.
- **Key space:** stated **2¹²⁸**, argued sufficient against brute force.
- **Claimed resistance:** brute force, replay (timestamps `T_D1, T_D2, T_S1, T_S2`), MITM, machine-learning attacks on the PUF.

> ⚠️ **Critical observation — terminology inflation.** Despite "Zero-Knowledge Proof" in the title, the protocol in their Figures 11–12 is a **hash-and-XOR challenge–response**: `R₀ = H(puf₀ ⊕ C₀)`, `K' = H(C₀ ⊕ R₀)`, `H₂ = H(R₀, data)`, with `H()` = SHA-256 and symmetric encryption `E_K`. There is **no commitment–challenge–response over a hard problem, no witness, and no simulator**. It is not a sigma protocol and not a zero-knowledge proof in the cryptographic sense. The "zero-knowledge" claim appears to mean only "the server does not store all CRPs."

> ⚠️ **Reported experimental results contain no timings at all.** §5 "Experimental Results" consists of PUF remanence tables and two **screenshots of authentication log output** (Figures 13–14) — hex dumps of `C0`, `H1`, `H2`, keys. No latency, no memory, no energy, no repetitions.

> ⚠️ **Internal inconsistency in the paper itself:** §4 states the Raspberry Pi 3B "has 1GB LPDDR2 RAM"; §5 states the experimental environment is "Raspberry Pi 3 Model B with 2GB of RAM."

**Why it matters to us:** three things. (1) It is the closest published analogue to our hardware-binding idea — a chip-intrinsic secret replacing a stored one — and can be cited as such. (2) It demonstrates that **"log screenshots as evidence" is a real pattern in this literature** — the exact pattern our audit condemned in our own Fig. 3. We should not imitate it; we should beat it. (3) It shows reviewers in this area *do* let loose ZKP terminology through, which is an opportunity: a paper with a genuine sigma protocol and real proofs stands out.

---

### P4 — Device-Bound Anonymous Credentials With(out) Trusted Hardware
**Karla Friedrichs¹, Franklin Harding², Anja Lehmann¹, Anna Lysyanskaya²** (¹ Hasso Plattner Institute, University of Potsdam; ² Brown University). IACR ePrint 2025/1995, posted 24 October 2025, 60 pp. **Accepted to EUROCRYPT 2026.**
**Retrieval: full text (local PDF; theory sections read, proofs skimmed).**

- **Problem:** anonymous credentials lack **device binding** — tying a credential to a secure-element-protected key to prevent cloning/transfer between corrupt users. Motivated by the **EU Digital Identity (EUDI) wallet** and the eIDAS regulation, which mandate unlinkability, untraceability and selective disclosure.
- **Primitives:** BBS credentials with BLS or Schnorr signatures at the SE; three constructions; unforgeability proved in **AGM + ROM**, **privacy proved unconditionally**.
- **Two design principles for secure elements, stated explicitly as requirements:**
  1. **Round-optimal** — exactly one call to the SE per presentation. They criticise prior work (e.g. DAA) for needing two TPM calls.
  2. **Stateless** — the SE must not keep credential-specific state, which "violat[es] the design principles of resource-limited SEs."
  The SE "remains extremely lightweight, computing only a single BLS or Schnorr signature."
- **The SE threat model is notably strong.** They define two unlinkability levels: **Unlink-1** (SE fully trusted but imperfectly shielded) and **Unlink-2** (SE algorithms **subverted** — replaced with arbitrary stateless code). Their schemes preserve user privacy *even when the SE is subverted or fully corrupted*, on the grounds that SEs are black-box components whose honesty is "hard to vet."
- **Blind DBACs:** a variant where the SE learns nothing about the presentations it helps compute — targeting **remote/cloud-hosted SEs**, a deployment model under consideration for the EUDI wallet.
- **Performance: none. Confirmed by reading — this is a pure theory paper with no implementation, no prototype and no benchmarks.** (Its Tables 1 and 2 are a scheme-comparison matrix and a security-game bookkeeping table, not measurements.) Do not cite it for any number.

**Why it matters to us — including one uncomfortable point.** It gives us (a) a top-tier, formally-grounded justification for hardware binding as the right primitive for non-transferability, and (b) two design principles we should adopt and state explicitly: **one SE call, no SE state.** Our design satisfies both — the ESP32 derives `x` and computes the response in a single invocation and stores nothing per session.

⚠️ **But it also exposes a limitation in our own threat model that we must state honestly.** P4 designs for a *subverted* secure element. Our design **trusts the ESP32 eFuse completely** — if that key is extracted or the key-store is subverted, our scheme collapses to a 4-digit PIN. Our draft §10 does scope out physical extraction, but P4 shows the state of the art no longer treats SE honesty as an assumption. We should cite P4, state plainly that we assume an honest key store, and note that removing that assumption is future work. Claiming otherwise against a EUROCRYPT paper would be indefensible.

---

### P5 — Blockchain-Enhanced Zero Knowledge Proof-Based Privacy-Preserving Mutual Authentication for IoT Networks (Z-PMA)
**Aditya Pathak¹, Irfan Al-Anbagi¹˒², Howard J. Hamilton³** (¹ University of Regina; ² University of Saskatchewan; ³ University of Regina, Computer Science). *IEEE Access* 12, 2024, 19 pp. DOI 10.1109/ACCESS.2024.3450313. Received 2 Aug 2024, accepted 17 Aug, published 26 Aug 2024. Open access (CC BY-NC-ND). **26 citations** — the most-cited item in this set.
**Retrieval: full text (PDF obtained manually; tables read from the page images).**

> **This is the most rigorously evaluated paper in the set, and it forces a correction to this study's earlier claim about isolated crypto timings. See the box below.**

- **Crypto family: quadratic residues mod `N`** (`p ≡ q ≡ 3 mod 4`), security resting on the **Modular Square Root (MSR)** problem — the same family as P2's FFS, **not** elliptic-curve Schnorr.
- Z-PMA = ZKP + a game-theoretic **incentive mechanism** + a **permissioned blockchain** (Hyperledger Fabric), with a main chain on edge devices and a sidechain on authentication agents.
- **Design principle worth stealing:** they deliberately place cheap operations on the IoT device and expensive ones (`T_QRD`, decryption via CRT) on the base-station and edge devices. Their IoT-side cost is `5·T_HF + 3·T_QRE + 1·T_RN + 1·T_MM + 1·T_EXP`. *(Verified: 5(1.012) + 3(3.051) + 0.120 + 2.988 + 0.228 = 17.549 ms — the paper's arithmetic checks out.)*
- **Formal verification in ProVerif:** 15 queries — 12 secrecy plus 3 injective-correspondence — all reported as passing.

**Testbed (Table 4) — real hardware:**

| Role | Device | Spec | OS |
|---|---|---|---|
| IoT device | **Raspberry Pi 2 Model B (2015)** | 1 GB RAM, **900 MHz quad-core ARM Cortex-A7** | Ubuntu 32-bit |
| Base station | MacBook Pro 2012 | 4 GB RAM, 2.5 GHz dual-core i5 | Ubuntu |
| Edge device | Dell desktop | 16 GB RAM, 1.8 GHz Intel Core i7-8565U | Ubuntu |

**Table 5 — per-primitive execution time (ms), measured with the MIRACL and Chebyshev libraries.** *This is the granularity our own evaluation should aim for.*

| Primitive | IoT device (Pi 2) | BS device | Edge device |
|---|---|---|---|
| Random number `T_RN` | 0.120 | 0.070 | 0.010 |
| Exponentiation `T_EXP` | 0.228 | 0.093 | 0.039 |
| **Modular exponentiation `T_ME`** | **210.691** | 10.614 | 6.851 |
| **ECC scalar multiplication `T_ESM`** | **143.590** | 5.610 | 2.010 |
| Chebyshev polynomial `T_CP` | 250.780 | 7.610 | 3.926 |
| Hash `T_HF` | 1.012 | 0.120 | 0.014 |
| Modular multiplication `T_MM` | 2.988 | 0.674 | 0.061 |
| QR encryption `T_QRE` | 3.051 | 1.806 | 0.913 |
| QR decryption `T_QRD` | 10.724 | 5.400 | 2.325 |
| AES encrypt / decrypt | 7.820 / 5.616 | 3.470 / 2.891 | 1.903 / 1.110 |

**Table 6 — total authentication time (ms):** Z-PMA **28.616** (IoT 17.549 + BS 8.686 + Edge 2.381), versus Yang et al. 450.721 / 1714.867; Sharma et al. 907.146; Wang et al. 1036.520 / 1464.720. Z-PMA wins because it keeps `T_ME`, `T_ESM` and `T_CP` **off** the IoT device.

- **Separate network-scale simulation:** docker + Hyperledger Composer on an Ubuntu desktop (i9-10900KF, 3.5 GHz, 10 cores, 64 GB RAM), Kafka consensus, 25 peer nodes, 8 orderer nodes, smart contracts in Golang. Figure 10 varies 100–600 IoT devices; authentication time there is in **seconds**, with error bars. *Do not confuse these seconds-scale network numbers with Table 6's millisecond per-device costs.*
- A further smart-grid case study (§VII) uses a Raspberry Pi 3 B+ (1.4 GHz) as a smart meter — a **different** setup from Table 4, not an inconsistency.

> ### ⚠️ CORRECTION to §3.2 — and a genuine conflict in the literature
> **This study previously asserted that no retrieved paper isolates cryptographic cost. That was wrong, and P5 is the counterexample:** Table 5 isolates fifteen primitives on real hardware, per device role. The claim has been narrowed in §3.2 accordingly.
>
> **But P5's numbers sit in real tension with P1's.** P5 measures an **ECC scalar multiplication at 143.590 ms on a 900 MHz quad-core Cortex-A7**. P1 measures FIDEM's *entire* authenticated handshake — which contains an EC operation on secp256r1 — as adding only **≈2 ms** over plain DHCP on a 240 MHz-class ESP32-S3. Those cannot both be typical. For reference, an optimised Curve25519 scalar multiplication on a Cortex-A7 is normally in the low single-digit milliseconds, so **143.59 ms looks anomalously slow** — plausibly an unoptimised MIRACL build, a large curve, or 32-bit Ubuntu overhead.
>
> **Consequence for us: do not use P5's `T_ESM` to predict our ESP32 performance, and do not use it as a baseline to beat.** Flagging the conflict is the honest move; resolving it requires our own measurement. This is precisely why Phase 4 has to produce our own numbers.

**Why it matters to us:** (1) it is the standard, most-cited citation for ZKP mutual authentication in IoT, and its three-way framing (security/privacy vs scalability vs authentication time) is a well-cited way to motivate a latency-focused evaluation; (2) **its Table 5 is the model for how to report our own results** — per-primitive, per-device, with the library named; (3) its asymmetric design (cheap ops on the constrained device) is a legitimate technique we should acknowledge; (4) note the field's gravitational pull toward blockchain — **our paper deliberately does not use one and should say why**: no ledger is needed to verify a sigma protocol, and adding one adds latency, not security.

---

### P6 — Privacy-Preserving Mutual Authentication Protocol With Forward Secrecy for IoT–Edge–Cloud (MAPFS)
**Seifelnasr, Altawy, Youssef, Ghadafi.** *IEEE Internet of Things Journal*, 2024 (published 2024-03-01). DOI 10.1109/JIOT.2023.3318180. 14 citations. Closed access.
**Retrieval: metadata + abstract only.**

- Three-tier IoT–Edge–Cloud; removes the need for an online trusted cloud admin during authentication.
- Achieves anonymity using **zero-knowledge proofs** plus randomization of the authentication request.
- Security rests on **discrete logarithm and decisional Diffie–Hellman in elliptic curve groups** — the same assumption family as our design.
- **Formal proofs** of mutual authentication and semantic security of session keys.
- Evaluated on a **Raspberry Pi 4**, compared against certificate-less protocols; metrics: communication overhead, storage, computation complexity. Numbers: NOT RETRIEVED.

**Why it matters to us:** the model to imitate for rigor — EC-DLog/DDH assumptions, *formal* proofs, and a real constrained-device evaluation with communication/storage/computation broken out. Our draft's §6 proofs are hand-written algebra; this is the standard they should be raised toward.

---

### P7 — Quantum-Resistant Privacy-Preserving IoT Authentication via Zero-Knowledge Proofs and Blockchain Integration
**Mohammed Tawfik¹, Amr H. Abdelhaliem², Islam S. Fathi¹** (¹ Ajloun National University, Jordan; ² Irbid National University, Jordan). *Statistics, Optimization & Information Computing*, **Vol. 14, September 2025, pp. 1374–1402**, 29 pp. DOI 10.19139/soic-2310-5070-2399. Open access. 6 citations.
**Retrieval: full text (local PDF).**

- Combines blockchain, lattice-based (Module-SIS) post-quantum ZKPs, Paillier homomorphic encryption and chameleon hashes.
- **Platform, in full:** Asus TUF laptop, **Intel Core i7 8th-generation, 16 GB RAM, Windows 11**. Python 3.10.3 with a **Tkinter desktop GUI**; libraries `web3`, `paho-mqtt`, `paillier`, `psutil`; Truffle + Node.js with **Ganache local blockchain**. No physical IoT device anywhere in the setup.
- **Reported:** 350 ms registration/authentication (GUI-to-blockchain); 180 ms per homomorphic encryption operation; 300 ms ZKP generation / 120 ms verification; 145,000 gas per device registration and 85,000 gas per ZKP verification, confirmed in 2–3 s; 150 ms network sync; 100 concurrent simulated devices at 30 tx/s with 1.2 GB peak memory.
- Several headline "performance" figures are **desktop-GUI metrics**: 45 ms average GUI response, 30 fps rendering, 25 ms event-handling latency, "98% GUI responsiveness."

> ### ✅ Correction to this study's earlier characterisation
> Reading the full text shows this paper is **considerably more honest than its abstract implies**, and my earlier "cautionary reference" framing understated it. §4.6 states outright:
> - *"We acknowledge this represents a significant limitation as real IoT deployments require validation on resource-constrained hardware."*
> - *"The current implementation faces specific deployment challenges on typical IoT hardware such as Raspberry Pi Zero or **ESP32** platforms. The 180MB Security Module memory footprint significantly exceeds the 8–64MB RAM typically available in such devices."*
> - They project a **minimum of 256 MB RAM, 50 MB storage and a ~400 MHz ARM processor** would be needed for sub-second authentication.
>
> So the authors explicitly say their framework **does not fit on an ESP32.** That is a stronger and more useful statement than "they measured on a PC."

⚠️ **Minor internal inconsistency (theirs):** §4.2.2 attributes the 350 ms to device *registration*; §4.3 and the abstract call the same figure *authentication* time.

**Why it matters to us — this is now a supporting citation, not just a cautionary one.** It is published, peer-reviewed evidence that a **blockchain + post-quantum ZKP + homomorphic encryption stack cannot run on our target hardware** — by the authors' own analysis, needing ~30× more RAM than an ESP32 has. Combined with P8 (PLONK ≈0.42 s on a laptop) and P1 (a sigma protocol disappearing into network latency on a real ESP32), the argument for choosing lightweight Schnorr over heavyweight ZKP machinery for constrained devices is no longer our opinion — it is documented in the literature, including by authors advocating the heavyweight approach.

---

### P8 — Two-Factor Authentication for Intellectual Property Transactions Based on Improved Zero-Knowledge Proof
**Mo, Feng, Huang, Feng, Wang, Li.** *Scientific Reports*, 2025, published 2025-02-18. DOI 10.1038/s41598-025-89597-7. PMC11836181. 5 citations.
**Retrieval: full text.**

- **Two factors:** (1) ID/password authentication; (2) **fingerprint biometrics combined with intellectual-property features**.
- **Proof system:** an **improved PLONK**, circuits in **Circom**, proving with **snarkjs**; a **Poseidon-hash-based constraint-compression strategy** to cut proving workload. Deployed to smart contracts via Remix.
- **Platform:** ASUS ROG Strix Scar 7 laptop, **Intel Core i5-9300H @ 2.40 GHz**. RAM and OS: NOT STATED.
- **Measured:** proof generation **0.42346 s**; verification **0.19119 s**; combined **0.61465 s**. Over **100 experiments each** for generation and verification. **Averages only — no standard deviation or CI reported.**
- Proof size: reduced vs standard PLONK, but exact bytes NOT STATED. Constraint counts, gas, throughput: NOT STATED.

**Why it matters to us:** the clearest available cost comparison between proof families. A SNARK (PLONK) two-factor scheme costs **~0.42 s to prove on a laptop**; a sigma protocol costs **~9 ms on an ESP32** (P1). For a 4-digit-PIN identification problem, general-purpose SNARK machinery buys nothing and costs ~50× more on hardware ~100× more powerful. **This is the quantitative justification for choosing Schnorr over zk-SNARKs in our design, and it should appear in our paper.** Also note: 100 trials with averages only is apparently acceptable at *Scientific Reports* — but FIDEM's boxplots are better practice and we should follow FIDEM.

---

### P9 — A Lightweight QR-assisted Zero-knowledge Identification Protocol For Secure Authentication
**Hüseyin Bodur** (Assistant Professor, Düzce University, Dept. of Computer Engineering, Turkey; ORCID 0000-0002-2815-3397). arXiv:2605.16912, submitted 16 May 2026.
**Venue (from the PDF title page, not visible in the arXiv abstract): Tokyo 11th International Innovative Studies & Contemporary Scientific Research Congress, 6–7 April 2026, Tokyo, Japan.** This is a broad multidisciplinary congress, not a security venue — weight its findings accordingly.
**Retrieval: full text (local PDF).**

- **Schnorr** authentication protocol, with **nonce + timestamp** added against replay; proof data embedded in a **QR code** and transmitted to the verifier.
- **Group:** not named explicitly, but the text attributes first-run cost to "prime number generation and parameter initialisation," which indicates **classical Schnorr in a multiplicative group mod p**, not elliptic curve. Security parameter: **256-bit**.
- **Platform: a "Python-based simulation environment."** Host CPU/RAM: NOT STATED.
- **Measured (Python simulation, ~50 runs):** proof generation **0.00014–0.00018 s** (0.14–0.18 ms); verification **0.00030–0.00078 s** (0.30–0.78 ms), "below one millisecond." Proof size constant at **≈0.5 KB**. The paper attributes fluctuation to "system load variations, randomness in parameter generation, and **Python interpreter overhead**."
- **Stated future work — and it is the honest part:** "performing experimental tests on **real hardware**." The author states plainly that no hardware testing was done.

**Why it matters to us:** three lessons. (1) Adding nonce+timestamp to Schnorr for replay resistance is an accepted, publishable increment — our draft §6.5 makes the same argument and currently has **no experiment behind it**, which we must fix. (2) This paper reports sub-millisecond timings from a **Python simulation on an unstated host**, then concludes the model suits "devices with low computational capacity" — the same inference our prior paper made and was rejected for. Note the difference in framing though: Bodur explicitly defers hardware testing to future work rather than presenting the numbers as embedded results. That is the minimum honest standard, and our old paper fell below it. (3) A Python-simulated 0.14 ms is not evidence about an MCU. **Our differentiator remains measuring on the actual chip.**

---

## 3. Synthesis — what the field actually does

### 3.1 Two distinct ZKP families, with very different costs

| Family | Used by | Cost, with platform | Rounds | Soundness error | Suits |
|---|---|---|---|---|---|
| **Sigma protocols, EC** (Schnorr / EC-DLog) | P1, P6, P9, **our design** | protocol cost vanishes into network latency on a real ESP32 (P1) | **1** | ~2⁻²⁵⁶ | proving knowledge of one secret — identification |
| **Quadratic-residue ZKPs** (FFS / modular square root) | P2, **P5** | P2: <1 s broadband / 3–4.5 s degraded (iPhone + local server, `k`=10). P5: 28.616 ms total, 17.549 ms IoT-side (Raspberry Pi 2) | P2: **k (8–10)**; P5: 1 | P2: 2⁻ᵏ ≈ **10⁻³** | same job, pre-EC; cheap primitives but large moduli |
| **General-purpose SNARKs** (PLONK/Circom) | P8 | ~0.42 s prove on a Core i5 laptop (P8) | 1 (non-interactive) | negligible | proving *arbitrary statements* — biometric matching, policy compliance |
| **Lattice / post-quantum ZKP + blockchain** | P7 | 300 ms prove / 120 ms verify on a Core i7; **180 MB footprint — does not fit an ESP32 (authors' own analysis)** | — | — | post-quantum settings with server-class hardware |

**Conclusion for our project — now supported by three independent data points.** Authenticating a PIN-derived key is a single-secret identification problem, so it needs a sigma protocol.

- Against **SNARKs** (P8): ~50× more expensive, on hardware ~100× more capable, to prove a statement far simpler than what SNARKs are for.
- Against **post-quantum + blockchain** (P7): the authors themselves state it will not fit on an ESP32.
- Against **FFS** (P2): the nearest prior work in our own niche needs 8–10 network round trips to reach a soundness error of only ~10⁻³. Schnorr reaches ~2⁻²⁵⁶ in one round trip. On a constrained device over a lossy link, round trips are the dominant cost — P2's own §5.3 says so explicitly.

**That last comparison is the strongest single argument in this study for our design, because it is against the most similar prior work rather than against a strawman.**

### 3.2 Measured performance reference — every number with its platform

*Never quote a row from this table without its platform column.*

| Source | Operation — **exactly what was timed** | Value | **Platform** | Trials / statistic |
|---|---|---|---|---|
| P1 FIDEM | **end-to-end** protocol, controller-side, incl. WiFi RTT | **9.06 ms** | **ESP32-S3** (real device) | 100 runs, median |
| P1 FIDEM | end-to-end DHCP baseline (no security) | 6.99 ms | ESP32-S3 | 100 runs, median |
| P1 FIDEM | end-to-end X.509+TLS baseline | ≈1.79 s | ESP32-S3 | 100 runs, median |
| P1 FIDEM | energy, device only, setup → DHCP Ack | 385 mJ | ESP32-S3, Nordic PPK2 | 100 runs, median |
| P1 FIDEM | energy, DHCP baseline | 354 mJ | ESP32-S3, Nordic PPK2 | 100 runs, median |
| P1 FIDEM | TEE world-switch overhead | ≈3.5 ms / ≈6 mJ | ESP32-C6 | 100 runs, median |
| P1 FIDEM | **on-device Schnorr proof generation** | **NOT ISOLATED — never reported** | — | — |
| P5 Z-PMA | **ECC scalar multiplication (isolated)** | **143.590 ms** ⚠️ see conflict note in P5 entry | **Raspberry Pi 2 B, 900 MHz Cortex-A7, MIRACL** | mean, n not stated |
| P5 Z-PMA | modular exponentiation (isolated) | 210.691 ms | Raspberry Pi 2 B, MIRACL | mean, n not stated |
| P5 Z-PMA | hash (isolated) | 1.012 ms | Raspberry Pi 2 B, MIRACL | mean, n not stated |
| P5 Z-PMA | full mutual authentication | **28.616 ms** (IoT 17.549 + BS 8.686 + Edge 2.381) | Pi 2 + MacBook Pro + Dell desktop | mean, n not stated |
| P5 Z-PMA | network-scale auth, 100–600 devices | **seconds**, not ms | i9-10900KF desktop, docker + Hyperledger | with error bars |
| P2 Segkoulis | FFS protocol, `k`=10, end-to-end | <1 s | **iPhone + local Django server, broadband (emulated)** | 10 tests, mean |
| P2 Segkoulis | FFS protocol, `k`=10, end-to-end | 3–4.5 s | **iPhone + local Django server, 3G/degraded (emulated)** | 10 tests, mean |
| P2 Segkoulis | **isolated crypto cost** | **NOT ISOLATED — authors state network latency dominates** | — | — |
| P7 Tawfik | ZKP generation | 300 ms | **Asus TUF, Core i7 8th gen, 16 GB, Windows 11** | not stated |
| P7 Tawfik | ZKP verification | 120 ms | **Asus TUF, Core i7 8th gen, 16 GB, Windows 11** | not stated |
| P7 Tawfik | registration / authentication (GUI→blockchain) | 350 ms | **same laptop, simulated devices, Ganache local chain** | not stated |
| P7 Tawfik | Security Module memory footprint | **180 MB — exceeds ESP32 RAM by ~30×** | authors' own analysis | — |
| P8 Mo | PLONK proof generation | 0.42346 s | **Intel Core i5-9300H laptop** | 100 runs, mean only |
| P8 Mo | PLONK verification | 0.19119 s | **Intel Core i5-9300H laptop** | 100 runs, mean only |
| P9 Bodur | Schnorr proof generation | 0.14–0.18 ms | **Python simulation, host NOT STATED** | ~50 runs, range |
| P9 Bodur | Schnorr verification | 0.30–0.78 ms | **Python simulation, host NOT STATED** | ~50 runs, range |
| P3 Lee | — | **no timings reported at all** | Raspberry Pi 3B | — |

> **Read the second column before using any row.** The single most important fact in this table is the row that says NOT ISOLATED.

**What we can and cannot conclude:**

- ❌ **We cannot say** "our proof generation is faster/slower than FIDEM's 9.06 ms." Different quantities: theirs is end-to-end including WiFi and with the crypto deliberately overlapped onto an async worker thread; ours would be an isolated on-device computation. Comparing them is the same platform-mismatch error our audit condemned.
- ✅ **We can say** that a full ZKP-authenticated handshake on an ESP32-class device costs ≈2 ms and ≈31 mJ *more than an unauthenticated one* (P1, ESP32-S3) — a comparison that is like-for-like because both were measured the same way on the same rig.
- ✅ **We can say** that EC sigma protocols are cheap enough on an ESP32 that the protocol cost disappears into network latency, whereas SNARK proving costs ~0.42 s on a laptop CPU (P8).
- ⚠️ **CORRECTED CLAIM.** An earlier version of this study said no retrieved paper isolates cryptographic cost. **That was wrong — P5 does**, per primitive and per device role (its Table 5), on a Raspberry Pi 2. The claim as it now stands, and as it survives checking:

> **No retrieved paper reports isolated sigma-protocol proof-generation cost on a microcontroller.**
> - P5 isolates primitives, but on a **Linux SBC** (900 MHz quad-core Cortex-A7, 1 GB RAM) — roughly two orders of magnitude more capable than an ESP32, and running a full OS — and for a **quadratic-residue** scheme, not Schnorr.
> - P1 runs Schnorr on a real ESP32 but **never isolates it**, overlapping the computation onto an async worker inside a network handshake.
> - P2 reports end-to-end only and states outright that "fixed network latency is the dominant factor in overall verification time, rather than computational complexity."
>
> The gap is narrower than first claimed, but it is real: **Schnorr proof generation, isolated, on an MCU.** If we measure it cleanly — network excluded, computation not overlapped, distribution rather than a point estimate — it is a small contribution nobody in this set has made. And P5's Table 5 shows us exactly the format in which to report it.

**Our expectation (a hypothesis to test, not a result):** since FIDEM's whole authenticated handshake adds ≈2 ms over plain DHCP on an ESP32-S3, the isolated Ed25519 commitment + response should plausibly be in the **low single-digit milliseconds or below**. *Nothing resembling this sentence goes in our paper until it is measured on our own hardware with our own instrument.*

### 3.3 How the field handles hardware binding

Ordered by how strong the hardware root is:

| Paper | What the device secret actually is | Strength of the root | SE threat model |
|---|---|---|---|
| **P4** (EUROCRYPT 2026) | key in a secure element; SE computes one BLS/Schnorr signature | strong, formally modelled | **Subverted SE tolerated** — privacy holds even if the SE is corrupt |
| **P3** (JIT 2025) | SRAM-PUF response (23LC1024, Inter-HD 49.53%, 2¹²⁸ key space) | strong — nothing stored at all | PUF assumed honest; ML attacks on CRPs discussed |
| **our design** | 256-bit random key in ESP32 eFuse, mixed with the PIN | strong *if* eFuse holds | **eFuse assumed honest and unextractable** |
| **P1** (arXiv 2026) | per-*class* key `Kc` in secure storage | weakened by sharing: one compromise breaks the whole class | assumed secure, explicitly out of scope |
| **P2** (Electronics 2025) | **iOS `identifierForVendor` / Android SSAID** — a software-readable OS value | **weakest**: not tamper-resistant, and resets on app reinstall | assumed unretrievable by attackers |

**Where our design sits: between P3 and P4 in strength, and clearly above P1 and P2.** We use a per-device eFuse key (unlike P1's per-class key) that is hardware-protected (unlike P2's OS identifier) and explicitly purposed to raise the entropy of a low-entropy PIN — a use no retrieved paper makes.

**Novelty, now that the nearest neighbour has been read in full:** P2 is the only paper in the set that uses a device identifier as an MFA possession factor proven in zero knowledge, and it does so with a *software* identifier, over FFS, on a phone — and its own future-work section asks for stronger unpredictability of the device key. **Our combination is not pre-empted by anything in this set.** That remains 9 papers, not a systematic search (§6), but the specific pre-emption risk flagged earlier is now resolved.

⚠️ **The honest counterweight:** P4 shows top-tier work no longer assumes the secure element is honest. We do assume that. State it as an assumption and cite P4 when doing so.

### 3.4 Evaluation practice — the bar our results must clear

| Practice | Who does it | Verdict |
|---|---|---|
| Real constrained hardware | P1 (ESP32-S3/C6), P3 (RPi 3B), **P5 (RPi 2 B)**, P6 (RPi 4) | **required for us** |
| **Per-primitive isolated timings, per device role, library named** | **P5 only** (Table 5) | **the format our results should take** |
| Quantitative comparison against named prior schemes | **P5** (Table 6, 4 schemes), P1 (3 baselines), P8 | required |
| ≥100 runs | P1, P8 | **required for us** — note P2 used only **10** tests per point, P9 ~50, and P5 does not state `n` |
| Adverse conditions modelled, not just best case | P2 (3 emulated network profiles) | worth copying — cheap and it impressed reviewers |
| Distribution, not a point estimate (boxplots) | P1 only | **the bar to clear** — P8 gives means only |
| Energy measurement with a named instrument | P1 only (**Nordic PPK2**) | strong differentiator; cheap to add |
| Baselines compared against | P1 (3 baselines), P6, P8 | required |
| **Machine-checked** formal verification | P1 (**ProVerif**: secrecy + injective correspondence) | the real bar — see below |
| Hand-written / model-based security proofs | P4 (AGM+ROM), P6 | our §6 is currently below both |
| Open-source artifact released | P1 (github.com/aleLtt/FIDEM) | expected in 2026; we should release ours |
| States exactly what was timed | P1 (explicitly defines the measured interval) | **required — this is where our old paper died** |
| Evidence = log screenshots | P3 | **do not imitate** |
| Numbers from a PC labelled "IoT" | P7, P9 | **do not imitate** |

**Two papers set the bar, and they set it in different places.** P1 (FIDEM) is strongest on *measurement method* — real hardware, 100 runs, distributions, instrumented energy, three baselines, ProVerif, open artifact. P5 (Z-PMA) is strongest on *reporting granularity* — fifteen isolated primitives across three device roles with the library named, plus a four-way quantitative comparison against named prior schemes, plus ProVerif.

**Our target is the union of the two: P1's method with P5's granularity.** Neither paper does both, so matching both is achievable and would make our evaluation the most thorough in this set. Note that P5 does **not** state its number of repetitions — so we can beat it simply by reporting `n` and a distribution.

**On ProVerif specifically:** FIDEM's Q3/Q4/Q5 prove injective correspondence on commitments, challenges and responses — which is precisely the replay-resistance property our draft asserts in §6.5 with *no evidence at all*. ProVerif is free, and modelling a single-round sigma protocol is a small job. This is the cheapest available upgrade to our paper's rigour, and it closes our weakest claim.

---

## 4. Gap analysis — where our project actually stands

**Genuinely supported by this literature:**
1. Interactive Schnorr on an ESP32 is real, publishable, and fast (P1) — our Phase 1 is achievable, not speculative.
2. Hardware binding for non-transferability is a first-tier research idea in 2026 (P4).
3. Sigma protocols beat SNARKs decisively for single-secret identification (P1 vs P8).
4. A chip-intrinsic secret as an authentication root is established practice (P3).

**Not yet supported, and honestly stated:**
1. **Our specific combination** — eFuse-bound key + low-entropy PIN + Ed25519 Schnorr on an MCU — was not found in the retrieved set. That is a *provisional* novelty claim. It cannot be asserted until P2's full text is read and a proper systematic search is done (§6).
2. **Ed25519 on ESP32 has no retrieved measurement.** P1 measured secp256r1. Our expected performance is an extrapolation.
3. **We have no numbers of our own.** Everything in `PROJECT_DRAFT_HardwareBound_ZKP.md` §7 is PC-side Python.

3. **On-device sigma-protocol proof-generation cost is unmeasured in this literature.** P1 comes closest and explicitly does not isolate it (it times an end-to-end handshake, with the crypto overlapped onto an async worker). A clean measurement is a small, real, unclaimed result.

**Contribution framing that survives contact with this literature:**
> P1 shows Schnorr ZKP is practical on an ESP32 but *assumes* secure hardware, binds a key per device *class* (so one compromise breaks the class), and never isolates the on-device proof cost. P4 shows device binding is the right primitive but targets phones with secure elements and anonymous credentials. P3 roots a secret in silicon but its protocol is not actually a ZKP. **Our contribution is the intersection none of them occupy: using the MCU's own per-device key store to make a 4-digit PIN's public verifier non-brute-forceable, with a real sigma protocol, and the on-device proof cost measured and reported in isolation.**

That is a narrow, honest, defensible claim — appropriate for a workshop or mid-tier embedded/applied-crypto venue, which is what the audit's Option 1 recommended.

---

## 5. Direct consequences for our draft

| Finding | Action on `PROJECT_DRAFT_HardwareBound_ZKP.md` |
|---|---|
| P1 reports 100 runs + boxplots + PPK2 energy | Rewrite Phase 4 to specify ≥100 trials, distributions not means, and instrumented energy per authentication |
| **P1 never isolates on-device proof-generation time** | **This is our opening.** Phase 4 must measure and report it cleanly — network excluded, computation not overlapped onto a worker thread, distribution reported |
| P1 defines its measured interval explicitly in prose | Phase 4 must state, in one sentence, exactly what interval each number covers |
| P1 uses secp256r1 + OpenSSL; we assume Ed25519 | Check mbedTLS/Arduino Ed25519 availability before committing; be ready to justify the curve choice or match theirs. Their 256-bit nonce/challenge/key sizing is a sane default to mirror |
| P1 verified in ProVerif | Model our protocol in ProVerif — closes draft §6.5, which currently has no evidence |
| P1 releases its PoC on GitHub | Release ours; it is expected practice in this venue class in 2026 |
| P1's `Kc` is shared per device *class* — one compromise breaks the class | **Position against this.** Our per-device eFuse key has no class-wide failure mode. Say so explicitly |
| P8: PLONK ≈0.42 s on a laptop | Add a sentence justifying sigma-over-SNARK with this number and its platform |
| P4: keep the secure-element operation minimal | State this design principle explicitly in §4 |
| P3 uses log screenshots as evidence | Our §7 must report distributions, not transcripts |
| P9 and our old paper both report simulated ms | Keep the draft's §7 honesty note; make it more prominent |
| ~~P2 may pre-empt our device-identifier factor~~ — **resolved, it does not** | Position against P2 explicitly: hardware key vs OS identifier; 1 round vs 8–10; real KDF vs concatenation. Answer their stated future work |
| P2 derives its secret by concatenation but argues security as if hashed | **Make our KDF real and say so.** A salted hash is what our §6.4 proof assumes — make the code match, unlike P2 |
| P2 emulated 3 network conditions with Apple's Network Link Conditioner | Cheap to copy; shows robustness rather than a best-case number |
| P4 assumes the SE may be **subverted**; we assume ours is honest | Add an explicit assumption to draft §10, cite P4, and list removing it as future work |
| P4: one SE call, no SE state | State that our design satisfies both, citing P4's principles |
| P7's authors state their stack needs ~256 MB RAM and will not fit an ESP32 | Cite as third-party evidence for choosing a sigma protocol over heavyweight ZKP machinery |
| **P5's Table 5 is the reporting format to copy** | Report per-primitive, per-role timings with the library and version named — but **also state `n` and a distribution, which P5 omits** |
| P5 and P1 disagree on EC scalar-multiplication cost by ~70× | Do not cite either as our expected performance. Measure ours, and note the discrepancy in our results discussion — it is a legitimate observation about the literature |
| P5 verified in ProVerif with 15 queries; P1 also uses ProVerif | Two of the strongest papers here use it. Reinforces the ProVerif action above |
| P5 offloads expensive ops to edge/base-station devices | Acknowledge as an alternative strategy, and state ours differs: we keep the proof on-device because the device secret must never leave the chip |
| Draft §6.5 (replay) has no experiment; P9 treats nonce+timestamp as the contribution | Add a replay/tampered-`s` test to the PoC — already flagged in the previous discrepancy review |

---

## 6. What this study does NOT establish

Stated plainly so it is not over-read:

1. **This is not a systematic literature review.** It is 9 papers from targeted keyword searches. There was no protocol, no database-by-database coverage (no IEEE Xplore / ACM DL / Scopus enumeration), no inclusion/exclusion criteria applied at scale, no PRISMA. **Do not describe it as a survey in the paper.**
2. **One of the nine (P6, Seifelnasr et al.) was read at abstract depth only**, because it is paywalled and no institutional access is available. Its methodological details are unknown to us and it is not relied on for any claim here. P4's formal proofs were skimmed rather than checked, and P5's tables were read from page images rather than extracted text (transcription was manual — worth spot-checking before any figure is quoted in the paper).
3. **Novelty is not confirmed, only un-refuted.** The specific pre-emption risk (P2) has been checked and cleared by reading it in full, but absence from 9 papers remains weak evidence of absence from the field.
4. **Two publisher sites (IEEE Xplore, and Nature/PMC for the HTML route) blocked automated retrieval**, and the two surveys could not be fetched at all. There is a known hole in the coverage — surveys are exactly where a pre-empting citation would most likely surface.
5. **No claim here has been checked against the papers' own cited sources.** Where a paper reports a number, this document records that the paper reports it — not that it is correct.

6. **An unresolved numerical conflict sits in the middle of this study.** P5 measures an isolated ECC scalar multiplication at 143.590 ms on a 900 MHz Cortex-A7; P1's entire EC-based handshake adds ≈2 ms on a slower ESP32-S3. These are not reconcilable from the papers alone, and this study does not resolve them. Our own measurement is the only way to settle which is representative.

**To close these gaps:** obtain P6 (needs an author request — email the corresponding author, this usually works); retrieve both surveys and mine their reference lists; run explicit searches for `Ed25519 + ESP32 + benchmark`, `eFuse + key derivation + authentication`, and `PIN + hardware binding + PAKE`; then re-run this study with stated inclusion criteria.

---

## 7. References (as verified)

1. **Lotto, A., Sciancalepore, S., Brighente, A., Conti, M.** "FIDEM: A Standard-Compliant Framework for Secure Binding of MUD Profiles to IoT Devices." arXiv:2605.29654, 28 May 2026. https://arxiv.org/abs/2605.29654 — code: https://github.com/aleLtt/FIDEM
2. **Segkoulis, T., Limniotis, K.** "Enhancing Multi-Factor Authentication for Mobile Devices Through Cryptographic Zero-Knowledge Protocols." *Electronics* 14(9):1846, 2025, 27 pp. DOI: 10.3390/electronics14091846 (Open University of Cyprus; Hellenic Data Protection Authority). Uses **Feige–Fiat–Shamir**, not Schnorr.
3. **Lee, T.-T., Wu, S.-T., Liang, Y.-J.** "PUF-Based Device Authentication with Zero-Knowledge Proof in IoT." *Journal of Internet Technology* 26(5), September 2025, p. 675 ff.
4. **Friedrichs, K., Harding, F., Lehmann, A., Lysyanskaya, A.** "Device-Bound Anonymous Credentials With(out) Trusted Hardware." IACR ePrint 2025/1995, 24 Oct 2025. EUROCRYPT 2026. https://eprint.iacr.org/2025/1995
5. **Pathak, A., Al-Anbagi, I. S., Hamilton, H. J.** "Blockchain-Enhanced Zero Knowledge Proof-Based Privacy-Preserving Mutual Authentication for IoT Networks." *IEEE Access* **12**, pp. 118621–118639 approx., 2024, 19 pp. DOI: 10.1109/ACCESS.2024.3450313 (University of Regina / University of Saskatchewan). *Quadratic-residue ZKP, not Schnorr. Page range inferred from running headers 118629–118632 — **verify before citing**.*
6. **Seifelnasr, M., Altawy, R., Youssef, A. M., Ghadafi, E.** "Privacy-Preserving Mutual Authentication Protocol With Forward Secrecy for IoT–Edge–Cloud." *IEEE Internet of Things Journal*, 2024. DOI: 10.1109/JIOT.2023.3318180
7. **Tawfik, M., Abdelhaliem, A. H., Fathi, I. S.** "Quantum-Resistant Privacy-Preserving IoT Authentication via Zero-Knowledge Proofs and Blockchain Integration." *Statistics, Optimization & Information Computing*, **Vol. 14, September 2025, pp. 1374–1402**. DOI: 10.19139/soic-2310-5070-2399 *(Semantic Scholar records the publication date as 2025-07-15; the PDF masthead reads September 2025 — the usual online-first vs issue-date gap. Cite the issue.)*
8. **Mo, S., Feng, W., Huang, M., Feng, S., Wang, Z., Li, Y.** "Two-factor authentication for intellectual property transactions based on improved zero-knowledge proof." *Scientific Reports*, 18 Feb 2025. DOI: 10.1038/s41598-025-89597-7 (PMC11836181)
9. **Bodur, H.** (Düzce University) "A Lightweight QR-assisted Zero-knowledge Identification Protocol For Secure Authentication." **Tokyo 11th International Innovative Studies & Contemporary Scientific Research Congress, 6–7 April 2026, Tokyo, Japan.** Also arXiv:2605.16912, 16 May 2026. https://arxiv.org/abs/2605.16912 *(Venue appears only on the PDF title page, not in the arXiv metadata.)*

*Identified, not retrieved:* "A Survey on Zero-Knowledge Authentication for Internet of Things," *Electronics* 12(5):1145; "Navigating Zero-Knowledge Authentication in the IoT Landscape: A Comprehensive Survey," IEEE; Misra, G., Hazela, B., Chaurasia, B. K., "A user-adaptive privacy-preserving authentication of IoMT using zero knowledge proofs with ECC," *Multimedia Tools and Applications*, 2025, DOI 10.1007/s11042-025-20759-5.
