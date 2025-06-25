import sys
sys.path.append("/server")
from flask import Flask, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from ecc import *
from hashlib import sha3_512
import secrets, random

app = Flask(__name__)

def aes_encrypt(key_int, plaintext_bytes):
    key = sha3_512(str(key_int).encode()).digest()[:16]
    iv = secrets.token_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext_bytes, AES.block_size))
    return iv + ciphertext

p = 49157
a = 2
b = 3

# Chọn điểm P sao cho order của nó có phân tích nhỏ (smooth)
def has_smooth_order(P, a, p):
    try:
        n = point_order(P, a, p, max_trials=50000)
        fs = [f for f, _ in factor(n)]
        return all(f in [2, 3, 5, 7, 11, 13, 17, 19, 23] for f in fs), n
    except:
        return False, None

P = None
order = None
while True:
    x = random.randint(0, p - 1)
    rhs = (x**3 + a*x + b) % p
    for y in range(p):
        if (y*y) % p == rhs:
            if is_on_curve(x, y, a, b, p):
                candidate = (x, y)
                ok, n = has_smooth_order(candidate, a, p)
                if ok:
                    P = candidate
                    order = n
                    break
    if P: break

d = random.randint(2, order - 1)
Q = point_mul(P, d, a, p)
cipher = aes_encrypt(Q[0], b"Demo ECC message")

@app.route("/exchange", methods=["POST"])
def exchange():
    return jsonify({
        "p": p,
        "a": a,
        "b": b,
        "Px": P[0],
        "Py": P[1],
        "Qx": Q[0],
        "Qy": Q[1],
        "n": order,
        "cipher": cipher.hex()
    })

if __name__ == "__main__":
    print("[SERVER] Running on port 5000...")
    print(f"[+] Curve: y² = x³ + {a}x + {b} mod {p}")
    print(f"[+] Base point P: {P}")
    print(f"[+] Order of P: {order}")
    print(f"[+] Private key d: {d}")
    app.run(host="0.0.0.0", port=5000)
