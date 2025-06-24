import random as pyrandom
from sage.all import *

def gen_keypair(G, p):
    n = pyrandom.randint(1, p-1)
    P = n*G
    return n, P

def gen_shared_secret(P, n):
    S = P*n
    return S.xy()[0]

# Define Curve params
p = 1973
a = 2709
b = 2802
E = EllipticCurve(GF(p), [a,b])
G = E.gens()[0]

# Generate keypair
n_a, P1 = gen_keypair(G, p)
n_b, P2 = gen_keypair(G, p)

# Calculate shared secret
S1 = gen_shared_secret(P1, n_b)
S2 = gen_shared_secret(P2, n_a)

# Check protocol works
assert S1 == S2

print(f"p: {p}")
print(f"Generator: {G}")
print(f"Alice Public key: {P1}")
print(f"Bob Public key: {P2}")

#Generator: (1525 : 27 : 1)
#Alice Public key: (1784 : 218 : 1)
#Bob Public key: (445 : 723 : 1)