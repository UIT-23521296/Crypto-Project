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
# Pohlig-Hellman with Early CRT
# --------------------------------------
def solve_and_decrypt_early(P, Q, min_bits=40, max_trials=10):
    n = P.order()
    print(f"[*] Order of G: {n}")

    # Kiểm tra Q có nằm trong nhóm sinh bởi P không
    try:
        _ = discrete_log(Q, P, operation='+')
    except ValueError:
        print("[-] Q không thuộc nhóm sinh bởi G => không tấn công được.")
        return None

    prime_factors = sorted(factor(n), key=lambda x: x[0]**x[1])
    print(f"[*] Sorted Factorization: {prime_factors}")

    congruences = []
    moduli = []
    total_bits = 0

    print("[*] Solving discrete logs modulo prime powers...")
    for idx, (prime, exp) in enumerate(tqdm(prime_factors)):
        m = prime ** exp
        k = n // m
        P1 = k * P
        Q1 = k * Q

        print(f"\n    [>] Đang xử lý prime={prime}, exp={exp}, modulus={m}")
        print(f"        => k = n // m = {k}")
        print(f"        => P1 = ({'∞' if P1.is_zero() else P1.xy()})")
        print(f"        => Q1 = ({'∞' if Q1.is_zero() else Q1.xy()})")

        if P1.is_zero() or Q1.is_zero():
            print("    [x] P1 hoặc Q1 là điểm vô cực, bỏ qua bước này.")
            continue

        try:
            x = discrete_log(Q1, P1, operation='+')
        except Exception as e:
            print(f"    [x] discrete_log thất bại: {e}")
            continue

        congruences.append(ZZ(x))
        moduli.append(ZZ(m))

        mod_bits = m.nbits()
        total_bits += mod_bits
        print(f"    [+] Found x ≡ {x} mod {m}  ({mod_bits} bits)")
        print(f"    [=] Total bits gathered so far: {total_bits}")

    # Sau khi đã thu thập tất cả modulus khả dụng, thử CRT và brute-force
    if len(moduli) > 0:
        print(f"\n[*] Thử CRT với {len(moduli)} modulus...")
        try:
            base = crt(congruences, moduli)
            modulus_product = prod(moduli)
            print(f"    [=] Base CRT d mod {modulus_product} = {base}")

            # Brute-force phần còn thiếu
            print(f"[*] Brute-force phần còn thiếu (xét mọi d ≡ base mod {modulus_product})")
            for i in range(n // modulus_product + 1):
                d_candidate = (base + i * modulus_product) % n
                print(f"    [*] Thử d_candidate = {d_candidate}")
                if d_candidate * P == Q:
                    print(f"\n[+] Found correct d by brute-force: {d_candidate}")
                    print(f"[+] d mod n = {d_candidate % n}")
                    key = sha1(str(d_candidate).encode()).digest()[:16]
                    cipher_aes = AES.new(key, AES.MODE_CBC, iv)
                    flag = unpad(cipher_aes.decrypt(ct), AES.block_size)
                    print(f"[+] Flag giải mã được: {flag.decode()}")
                    return d_candidate

            print("    [x] Không tìm thấy khóa đúng sau brute-force.")
        except Exception as e:
            print(f"    [x] CRT hoặc brute-force thất bại: {e}")
    else:
        print("[-] Không thu thập được modulus nào để giải CRT.")
    return None


print("\n[2] Đang phục hồi private key bằng Pohlig-Hellman...")
d = solve_and_decrypt_early(G, Q)
