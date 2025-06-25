from flask import Flask, jsonify
from hashlib import sha1
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import secrets
import os
import random
from sage.all import *

# --- ECC toy parameters ---
p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
a = 115792089210356248762697446949407573530086143415290314195533631308867097853948
b = 1235004111951061474045987936620314048836031279781573542995567934901240450608
E = EllipticCurve(GF(p), [a, b])
G = E(58739589111611962715835544993606157139975695246024583862682820878769866632269,
    86857039837890738158800656283739100419083698574723918755107056633620633897772)

order = G.order()
factors = factor(order)

# --- Secret generation ---
d = randint(2, order - 1)
Q = d * G

# --- Encrypt the ms ---
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

cipher = aes_encrypt(Q.xy()[0], plaintext)

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
    print(f"[+] Order of G: {order}")
    print(f"[+] Order factors: {factors}")
    print(f"[+] Order bits: {order.bit_length()}")
    print(f"[+] Private key d: {d}")
    app.run(host="0.0.0.0", port=5000)
