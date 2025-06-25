import requests
from hashlib import sha1
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from sage.all import *
from tqdm import tqdm

HOST = "http://server:5000"

print("[*] Đang kết nối đến server Flask...")
try:
    response = requests.post(f"{HOST}/exchange")
    challenge = response.json()
except Exception as e:
    print("[-] Không thể kết nối tới server:", e)
    exit(1)

print("[*] Đang khôi phục tham số elliptic curve...")

p = int(challenge['p'])
a = int(challenge['a'])
b = int(challenge['b'])
E = EllipticCurve(GF(p), [a, b])

Px = int(challenge['Px'])
Py = int(challenge['Py'])
Qx = int(challenge['Qx'])
Qy = int(challenge['Qy'])

G = E(Px, Py)
Q = E(Qx, Qy)

cipher = bytes.fromhex(challenge['cipher'])
iv = cipher[:16]
ct = cipher[16:]

print(f"    - Generator G: {G.xy()}")
print(f"    - Public key Q: {Q.xy()}")

# --------------------------------------
# 3. Pohlig-Hellman + CRT thử từng phần
# --------------------------------------
def solve_and_decrypt_early(P, Q, max_factors=6):
    n = P.order()
    print(f"[*] Order of G: {n}")
    prime_factors = sorted(factor(n), key=lambda x: x[0]**x[1])  # nhỏ trước
    print(f"[*] Sorted Factorization: {prime_factors}")

    congruences = []
    moduli = []

    print("[*] Solving discrete logs modulo prime powers...")
    for idx, (prime, exp) in enumerate(tqdm(prime_factors)):
        m = prime ** exp
        k = n // m
        P1 = k * P
        Q1 = k * Q
        x = discrete_log(Q1, P1, operation='+')
        congruences.append(x)
        moduli.append(m)
        print(f"    [+] Found x ≡ {x} mod {m}")

        # Giới hạn số lượng CRT ban đầu
        if len(moduli) >= max_factors:
            try:
                partial_d = crt(congruences, moduli)
                key = sha1(str(partial_d).encode()).digest()[:16]
                cipher_aes = AES.new(key, AES.MODE_CBC, iv)
                flag = unpad(cipher_aes.decrypt(ct), AES.block_size)
                print(f"[+] Flag giải mã được: {flag.decode()}")
                print(f"[+] Private key d = {partial_d}")
                return partial_d
            except Exception:
                pass

    print("[-] Không thể giải mã với số thừa số giới hạn.")
    return None

print("\n[2] Đang phục hồi private key bằng Pohlig-Hellman...")
d = solve_and_decrypt_early(G, Q)
