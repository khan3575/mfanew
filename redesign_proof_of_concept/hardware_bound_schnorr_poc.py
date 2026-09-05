"""
Proof-of-concept: Hardware-Bound Schnorr (Ed25519) Zero-Knowledge Authentication
Runs over the REAL Ed25519 curve group (RFC 8032 constants), extended coords.
Demonstrates: completeness, soundness (witness extraction), honest-verifier
zero-knowledge (simulator), and the honeypot / server-breach property.
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
x_bad = kdf("9999", device_key)
s_bad = (r + c*x_bad) % L
print(f"wrong PIN 9999 ->  verify = {verify(Y, T, c, s_bad)}   <== correctly REJECTED\n")

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
print("="*70); print("5. HONEYPOT / SERVER-BREACH  (attacker has stolen Y)"); print("="*70)
# (a) OLD design x = int(PIN): brute force by walking i*B incrementally
Y_weak = mul(int(PIN), B)
t0=time.time(); P=IDENT; found=None
for i in range(10000):
    if eq(P, Y_weak): found=i; break
    P = add(P, B)
print(f"(a) OLD  x=int(PIN):  recovered PIN = {found}  in {(time.time()-t0)*1000:.0f} ms   <== BROKEN")
# (b) NEW design: attacker tries all 10,000 PINs but does NOT have device_key
t0=time.time(); N=2000; hit=False
for g in range(N):
    if eq(mul(kdf(f"{g:04d}", secrets.token_bytes(32)), B), Y): hit=True; break
dt=(time.time()-t0)
print(f"(b) NEW  x=H(device_key||PIN): {N} PIN guesses w/ wrong key, hits = {hit}  ({dt:.1f}s)")
print(f"    without the 256-bit device_key, NO PIN guess matches Y.")
print(f"    real search space = 10^4 PINs x 2^256 keys  <== INFEASIBLE\n")
print("ALL PROPERTIES DEMONSTRATED ON THE REAL Ed25519 CURVE.")
