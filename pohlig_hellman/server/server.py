from flask import Flask, jsonify
from hashlib import sha1
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import secrets
import os
from sage.all import *

# --- ECC curve parameters ---
p = 79801
a = 15986
b = 44683
E = EllipticCurve(GF(p), [a, b])
G = E(16893, 4089)

order = G.order()
factors = factor(order)

# --- Secret generation ---
d = randint(2, order - 1)
Q = d * G

# --- Encrypt plaintext file using AES-CBC ---
ms_file = "ms.txt"
try:
    with open(ms_file, "rb") as f:
        plaintext = f.read()
except FileNotFoundError:
    print(f"[!] {ms_file} not found. Please create the file.")
    exit(1)

def aes_encrypt(key_int, plaintext_bytes):
    key = sha1(str(key_int).encode()).digest()[:16]
    iv = secrets.token_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(pad(plaintext_bytes, AES.block_size))

cipher = aes_encrypt(d, plaintext)

# --- Flask API setup ---
app = Flask(__name__)

@app.route("/exchange", methods=["POST"])
def exchange():
    return jsonify({
        "p": str(p),
        "a": str(a),
        "b": str(b),
        "Px": str(G.xy()[0]),
        "Py": str(G.xy()[1]),
        "Qx": str(Q.xy()[0]),
        "Qy": str(Q.xy()[1]),
        "n": str(order),
        "cipher": cipher.hex()
    })

if __name__ == "__main__":
    print("[SERVER] Running on port 5000...")
    print(f"[+] Curve: y² = x³ + {a}x + {b} mod {p}")
    print(f"[+] Base point G: {G.xy()}")
    print(f"[+] Public key Q: {Q.xy()}")
    print(f"[+] Order of G: {order}")
    print(f"[+] Order factors: {factors}")
    print(f"[+] Order bits: {order.bit_length()}")
    print(f"[+] Private key d: {d}")
    app.run(host="0.0.0.0", port=5000)
