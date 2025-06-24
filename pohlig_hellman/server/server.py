from flask import Flask, jsonify, request
from ecc import Curve, Point
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import random
import os
import pickle

app = Flask(__name__)

# ECC params
p = 9739
a = 497
b = 1768
curve = Curve(p, a, b)
G = Point(curve, 1804, 5368, validate=True)
n = 9739

# Server private key
d = random.randint(1, n-1)
Q = d * G
print(f"[+] Private key: {d}")

# Encrypt message using shared secret
with open("ms.txt", "rb") as f:
    plaintext = f.read()

@app.route("/pubkey", methods=["GET"])
def get_pubkey():
    return jsonify({"x": Q.x, "y": Q.y})

@app.route("/encrypt", methods=["POST"])
def encrypt():
    data = request.json
    Cx, Cy = int(data['x']), int(data['y'])
    C = Point(curve, Cx, Cy)
    S = d * C
    key = sha256(str(S.x).encode()).digest()[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv=b"\x00" * 16)
    ct = cipher.encrypt(pad(plaintext, AES.block_size))

    # Ghi ciphertext vào file
    with open("cipher.enc", "wb") as f:
        f.write(ct)

    return jsonify({"cipher": ct.hex(), "Gx": G.x, "Gy": G.y})

@app.route("/cipher", methods=["GET"])
def get_cipher():
    with open("cipher.enc", "rb") as f:
        return f.read().hex()
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)