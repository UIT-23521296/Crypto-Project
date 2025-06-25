from random import randint
from sage.all import *

# Config
target_bits = 16
min_prime_factors = 3
max_attempts = 100000

def is_smooth_order(order):
    factors = factor(order)
    return len(factors) >= min_prime_factors and order.nbits() == target_bits

print("[*] Searching for a curve with ~16-bit smooth order...")

attempt = 0
while attempt < max_attempts:
    p = random_prime(2^17, lbound=2^16)
    F = GF(p)
    a = randint(0, p-1)
    b = randint(0, p-1)

    try:
        E = EllipticCurve(F, [a, b])
    except:
        attempt += 1
        continue

    for _ in range(20):
        try:
            G = E.random_point()
            n = G.order()
            if n > 1 and is_smooth_order(n):
                print("[+] Curve found!")
                print(f"    p = {p}")
                print(f"    a = {a}")
                print(f"    b = {b}")
                print(f"    Gx = {G.xy()[0]}")
                print(f"    Gy = {G.xy()[1]}")
                print(f"    order = {n}")
                print(f"    factor = {factor(n)}")
                quit(0)
        except:
            continue

    attempt += 1

print("[-] No suitable curve found.")
