import hashlib
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from sage.all import *

def gen_shared_secret(P, n):
    S = P * n
    return S.xy()[0]

# ==== Curve parameters ====
p = 1973
a = 2709
b = 2802
E = EllipticCurve(GF(p), [a, b])

# ==== Generator G ====
gx = 1525
gy = 27
G = E((gx, gy))

# ==== Alice's public key ====
Px = 1784
Py = 218
P = E((Px, Py))

# ==== Bob's public key (cho việc test decrypt sau này) ====
P2x = 445
P2y = 723
P2 = E((P2x, P2y))

print("===== Curve Info =====")
print(f"p = {p}")
print(f"Curve: y^2 = x^3 + {a}x + {b} mod {p}")
print()

print("===== Generator G =====")
print(f"G = ({gx}, {gy})")
print()

print("===== Public Keys =====")
print(f"Alice's Public Key: P = ({Px}, {Py})")
print(f"Bob's Public Key:   P2 = ({P2x}, {P2y})")
print()

# ==== Bước 1: Tìm embedding degree k ====
order = G.order()
k = 1
while (p**k - 1) % order != 0:
    k += 1
print(f"[+] Embedding degree k = {k}")

# ==== Bước 2: Mở rộng trường và ánh xạ các điểm ====
K = GF(p**k, names='a')
EK = E.base_extend(K)
PK = EK(P)
GK = EK(G)

# ==== Bước 3: Sinh điểm Q tuyến tính độc lập với G ====
R = EK.random_point()
m = R.order()
d = gcd(m, G.order())
Q = (m // d) * R 

# ==== Bước 4: Tính pairing ====
print("[+] Tính Tate Pairing...")
AA = PK.tate_pairing(Q, G.order(), k)
GG = GK.tate_pairing(Q, G.order(), k)

# ==== Bước 5: Giải discrete log ====
print("[+] Đang giải discrete log...")
dlA = AA.log(GG)
print(f"[+] Alice's secret key recovered: {dlA}")

# ==== Bước 6: Tính shared secret với Bob ====
S2 = gen_shared_secret(P2, dlA)

# ==== Bước 7: Encrypt file ====
def encrypt_data(shared_secret: int, data: bytes):
    sha1 = hashlib.sha3_512()
    sha1.update(str(shared_secret).encode('ascii'))
    key = sha1.digest()[:16]
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(data, AES.block_size))
    return iv.hex(), ct.hex()

# ==== Bước 8: Decrypt lại ====
def decrypt_data(shared_secret: int, iv: str, ct: str) -> bytes:
    sha1 = hashlib.sha3_512()
    sha1.update(str(shared_secret).encode('ascii'))
    key = sha1.digest()[:16]
    cipher = AES.new(key, AES.MODE_CBC, bytes.fromhex(iv))
    return unpad(cipher.decrypt(bytes.fromhex(ct)), AES.block_size)

# ==== DEMO: Encrypt flag rồi giải mã ====
with open("file_test.jpg", "rb") as f:
    img_data = f.read()

print(f"[+] Encrypting image ({len(img_data)} bytes)...")
iv, ct = encrypt_data(S2, img_data)
print(f"[+] Image encrypted:\niv = {iv}\nct length = {len(ct)}")

# ==== Giai mã và ghi ra file mới ====
print("[+] Decrypting image...")
recovered_data = decrypt_data(S2, iv, ct)

with open("recovered.png", "wb") as f:
    f.write(recovered_data)

print("[+] Image recovered and written to recovered.png")