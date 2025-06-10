from sage.all import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import sha3_512
import math

# Đọc tham số
with open("/data/params.txt") as f:
    p = int(f.readline())
    a = int(f.readline())
    b = int(f.readline())
    Px = int(f.readline())
    Py = int(f.readline())
    Qx = int(f.readline())
    Qy = int(f.readline())

curve = EllipticCurve(GF(p), [a, b])
P = curve(Px, Py)
Q = curve(Qx, Qy)

def baby_step_giant_step(P, Q, order_bound):
    m = math.isqrt(order_bound) + 1
    table = {}
    # Baby steps
    for j in range(m):
        point = j * P
        table[(point[0], point[1])] = j

    # Giant steps
    inv = -m * P
    Y = Q
    for i in range(m):
        key = (Y[0], Y[1])
        if key in table:
            return i * m + table[key]
        Y = Y + inv
    return None

order_guess = P.order()
print(f"[Attacker] Đoán order của P: {order_guess}")

d = baby_step_giant_step(P, Q, order_guess)
print(f"[Attacker] Tìm được d: {d}")

# Giải mã
with open("/data/cipher.enc", "rb") as f:
    cipher_data = f.read()
iv = cipher_data[:16]
ct = cipher_data[16:]
key = sha3_512(str(d).encode()).digest()[:16]
cipher = AES.new(key, AES.MODE_CBC, iv)
plain = unpad(cipher.decrypt(ct), AES.block_size)
with open("recovered.pdf", "wb") as f:
    f.write(plain)

print("✅ Đã giải mã và ghi recovered.pdf")
