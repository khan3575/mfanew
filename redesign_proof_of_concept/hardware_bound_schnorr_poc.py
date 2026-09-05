"""
Proof-of-concept: Hardware-Bound Schnorr (Ed25519) Zero-Knowledge Authentication
Runs over the REAL Ed25519 curve group (RFC 8032 constants), extended coords.
Demonstrates: completeness, soundness (witness extraction), honest-verifier
zero-knowledge (simulator), replay and tamper rejection, and the honeypot /
server-breach property.

Scope: this proves the MATH and the SECURITY LOGIC on a PC. It says nothing
about on-device performance -- no timing here may be quoted for an ESP32.
"""
import hashlib, secrets, time

# ---- Ed25519 curve constants (RFC 8032) ----
p = 2**255 - 19
d = (-121665 * pow(121666, p-2, p)) % p
L = 2**252 + 27742317777372353535851937790883648493   # prime order of base-point subgroup
d2 = (2*d) % p

def inv(z): return pow(z, p-2, p)

# Extended twisted Edwards coords: (X,Y,Z,T), x=X/Z, y=Y/Z, xy=T/Z. a=-1. Complete add.
IDENT = (0, 1, 1, 0)
def add(P, Q):
    X1,Y1,Z1,T1 = P; X2,Y2,Z2,T2 = Q
    A = (Y1 - X1) * (Y2 - X2) % p
    B = (Y1 + X1) * (Y2 + X2) % p
    C = T1 * d2 * T2 % p
    D = 2 * Z1 * Z2 % p
    E = (B - A) % p; F = (D - C) % p; G = (D + C) % p; H = (B + A) % p
    return (E*F % p, G*H % p, F*G % p, E*H % p)   # (X3, Y3, Z3, T3)
def mul(k, P):
    R = IDENT; k %= L
    while k:
        if k & 1: R = add(R, P)
        P = add(P, P); k >>= 1
    return R
def eq(P, Q):  # projective equality without inversion
    return (P[0]*Q[2] - Q[0]*P[2]) % p == 0 and (P[1]*Q[2] - Q[1]*P[2]) % p == 0

# Base point B (RFC 8032)
By = 4 * inv(5) % p
xx = (By*By - 1) * inv(d*By*By + 1) % p
Bx = pow(xx, (p+3)//8, p)
if (Bx*Bx - xx) % p != 0: Bx = Bx * pow(2, (p-1)//4, p) % p
if Bx % 2 != 0: Bx = (p - Bx) % p
B = (Bx, By, 1, Bx*By % p)

assert eq(mul(L, B), IDENT), "B must have order L"
assert eq(add(B, IDENT), B), "identity law"
print("[self-check] Ed25519 extended-coord arithmetic correct: L*B = identity")
print(f"[params] field p = 2^255-19, group order L is a {L.bit_length()}-bit prime\n")

def kdf(pin, device_key):
    """x = H(device_key || pin) mod L  -- the hardware-bound secret scalar."""
    return int.from_bytes(hashlib.sha512(device_key + pin.encode()).digest(), "little") % L

# =====================================================================
print("="*70); print("1. REGISTRATION"); print("="*70)
device_key = secrets.token_bytes(32)          # 256-bit, lives in ESP32 secure storage
PIN = "1234"
x = kdf(PIN, device_key)                       # secret scalar, never leaves device
Y = mul(x, B)                                  # public key -> stored on server
print(f"device_key (on-chip secret): {device_key.hex()[:24]}...  (256-bit)")
print(f"PIN (in user's head):        {PIN}")
print(f"secret x = H(device_key || PIN) mod L   (stays on device)")
print(f"public Y = x*B                          (stored on server)\n")

# =====================================================================
print("="*70); print("2. AUTHENTICATION   T -> c -> s -> verify"); print("="*70)
def commit():
    r = secrets.randbelow(L-1)+1; return r, mul(r, B)
def respond(r, c): return (r + c*x) % L
def verify(Y, T, c, s): return eq(mul(s, B), add(T, mul(c, Y)))

r, T = commit()                                 # 1 commitment
c = secrets.randbelow(L-1)+1                     # 2 challenge
s = respond(r, c)                               # 3 response  (uses x, hides it)
print(f"commitment T = r*B          (r secret random)")
print(f"challenge   c = {hex(c)[:22]}...")
print(f"response    s = (r + c*x) mod L")
print(f"verify  s*B == T + c*Y  ->  {verify(Y,T,c,s)}   <== COMPLETENESS\n")

# wrong PIN: a real failed login draws its own fresh r and receives a fresh c
r_bad, T_bad = commit()
c_bad = secrets.randbelow(L-1)+1
x_bad = kdf("9999", device_key)
s_bad = (r_bad + c_bad*x_bad) % L
print(f"wrong PIN 9999 (fresh r,c) ->  verify = {verify(Y, T_bad, c_bad, s_bad)}   <== correctly REJECTED\n")

# =====================================================================
print("="*70); print("3. SOUNDNESS  (extract secret from two answers on one commitment)"); print("="*70)
r2, T2 = commit()
c1 = secrets.randbelow(L-1)+1; s1 = (r2 + c1*x) % L
c2 = secrets.randbelow(L-1)+1; s2 = (r2 + c2*x) % L
x_ext = (s1 - s2) * pow((c1 - c2) % L, L-2, L) % L
print(f"same commitment T, two challenges c1,c2, two responses s1,s2")
print(f"extract x = (s1-s2)/(c1-c2) mod L")
print(f"extracted x == real x ?  {x_ext == x}")
print("=> being able to answer TWO challenges forces knowledge of x (proof-of-knowledge)\n")

# =====================================================================
print("="*70); print("4. ZERO-KNOWLEDGE  (forge a valid transcript WITHOUT x)"); print("="*70)
c_s = secrets.randbelow(L-1)+1
s_s = secrets.randbelow(L-1)+1                   # choose response first
T_s = add(mul(s_s, B), mul((-c_s) % L, Y))       # T = s*B - c*Y
print(f"simulator picks s,c at random, sets T = s*B - c*Y   (never touches x)")
print(f"forged transcript verifies ?  {verify(Y, T_s, c_s, s_s)}")
print("=> valid transcripts exist without the secret => a real one leaks nothing\n")

# =====================================================================
print("="*70); print("5. REPLAY AND TAMPERING  (attacker has a recorded transcript)"); print("="*70)
# The attacker records a full, valid transcript (T, c, s) from a real login.
# (a) Replay: reuse the recorded T and s against the NEXT session's challenge.
c_new = secrets.randbelow(L-1)+1                 # server issues a fresh challenge
while c_new == c: c_new = secrets.randbelow(L-1)+1
print(f"recorded a valid transcript (T, c, s); server now issues a fresh c'")
print(f"replay recorded s against c' ->  verify = {verify(Y, T, c_new, s)}   <== REPLAY REJECTED")
# (b) Tampering: flip the response on the original challenge.
s_tampered = (s + 1) % L
print(f"tampered response s+1 on original c ->  verify = {verify(Y, T, c, s_tampered)}   <== TAMPER REJECTED")
# (c) Tampering with the commitment instead.
print(f"tampered commitment T+B on original c ->  verify = {verify(Y, add(T, B), c, s)}   <== TAMPER REJECTED")
print("=> a captured transcript is worthless: s is bound to that one (T, c) pair\n")

# =====================================================================
print("="*70); print("6. HONEYPOT / SERVER-BREACH  (attacker has stolen Y)"); print("="*70)
# The attacker holds Y and knows the PIN is 4 digits, but does NOT have device_key.
# Fix one wrong key and sweep the ENTIRE PIN space -- the actual attack, run to completion.
wrong_key = secrets.token_bytes(32)              # attacker's guess at device_key
assert wrong_key != device_key
t0 = time.time(); hits = 0
for g in range(10000):                           # all 10^4 PINs, no early exit on failure
    if eq(mul(kdf(f"{g:04d}", wrong_key), B), Y): hits += 1
dt = time.time() - t0
print(f"attacker fixes one wrong device_key and tries ALL 10,000 PINs")
print(f"matches found = {hits}  ({dt:.1f}s)   <== ZERO")
print(f"=> the PIN space alone is exhausted with no result. To succeed the attacker")
print(f"   must also find the 256-bit device_key, or solve the Ed25519 discrete log")
print(f"   directly (~2^126 work, i.e. ~128-bit security).\n")
print("ALL PROPERTIES DEMONSTRATED ON THE REAL Ed25519 CURVE.")
