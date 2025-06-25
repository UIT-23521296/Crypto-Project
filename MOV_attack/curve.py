import random as pyrandom
from sage.all import *

def gen_keypair(G, p):
    n = pyrandom.randint(1, p - 1)
    P = n * G
    return n, P

def gen_shared_secret(P, n):
    S = P * n
    return S.xy()[0]

def worker(worker_id=0):
    a = 2709
    b = 2802
    LOWER = 2**59
    UPPER = 2**60
    MAX_K = 10
    trials = 0

    while True:
        trials += 1
        p = next_prime(pyrandom.randint(LOWER, UPPER))
        try:
            E = EllipticCurve(GF(p), [a, b])

            # Kiểm tra singular curve
            if E.discriminant() == 0:
                continue

            G = E.gens()[0]
            order = G.order()

            if not is_prime(order):
                continue  # tránh Pohlig-Hellman

            # Kiểm tra embedding degree nhỏ
            k = 1
            while pow(p, k, order) != 1:
                k += 1
                if k > MAX_K:
                    raise ValueError("k too large")

            # Thành công
            print(f"\n✅ Worker {worker_id} OK sau {trials} thử:")
            print(f"p = {p}")
            print(f"Curve: y² = x³ + {a}x + {b} mod {p}")
            print(f"Order(G) = {order}")
            print(f"k = {k} (embedding degree nhỏ)")

            # Sinh khóa
            n_a, P1 = gen_keypair(G, p)
            n_b, P2 = gen_keypair(G, p)
            S1 = gen_shared_secret(P1, n_b)
            S2 = gen_shared_secret(P2, n_a)
            assert S1 == S2
            print(f"🔐 Shared secret: {S1}")
            break  # Thoát vòng lặp sau khi tìm được curve hợp lệ

        except Exception as e:
            continue

if __name__ == "__main__":
    worker()
