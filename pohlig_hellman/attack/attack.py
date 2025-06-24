import sys
sys.path.append("/server")  # đường dẫn trong container
from ecc import Curve, Point
import requests
from ecc import Curve, Point
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import json

# ECC params
p = 9739
a = 497
b = 1768
curve = Curve(p, a, b)

# Step 1: Get Q = dG
res = requests.get("http://server:5000/pubkey")
Qx, Qy = res.json()["x"], res.json()["y"]
Q = Point(curve, Qx, Qy)

# Step 2: Brute d by solving dG = Q
G = Point(curve, 1804, 5368, validate=True)
d = 1
while d < p:
    if d * G == Q:
        print(f"[+] Found private key d = {d}")
        break
    d += 1

# Step 3: Send a random point C to encrypt
C = 123 * G
res = requests.post("http://server:5000/encrypt", json={"x": C.x, "y": C.y})
data = res.json()

# Step 4: Decrypt ciphertext
res = requests.get("http://server:5000/cipher")
cipher_hex = res.text
print("[*] Ciphertext as seen from server's file (cipher.enc):")
print(cipher_hex)

S = d * C
key = sha256(str(S.x).encode()).digest()[:16]
cipher = AES.new(key, AES.MODE_CBC, iv=b"\x00" * 16)
plaintext = unpad(cipher.decrypt(bytes.fromhex(data["cipher"])), AES.block_size)
print("[+] Decrypted message:", plaintext.decode())
