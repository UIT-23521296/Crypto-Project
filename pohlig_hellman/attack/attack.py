import sys
sys.path.append("/server")
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import sha3_512
from ecc import *

def aes_decrypt(key_int, ciphertext_hex):
    key = sha3_512(str(key_int).encode()).digest()[:16]
    iv = bytes.fromhex(ciphertext_hex[:32])
    ct = bytes.fromhex(ciphertext_hex[32:])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size)

def discrete_log_pohlig(P, Q, a, p, n):
    congs = []
    for prime, exp in factor(n):
        m = prime**exp
        k = n // m
        P1 = point_mul(P, k, a, p)
        Q1 = point_mul(Q, k, a, p)
        for d in range(m):
            if point_mul(P1, d, a, p) == Q1:
                congs.append((d, m))
                break
    return crt(congs)

r = requests.post("http://pohlig_server:5000/exchange")
data = r.json()
p, a, b = data['p'], data['a'], data['b']
P = (data['Px'], data['Py'])
Q = (data['Qx'], data['Qy'])
ciphertext = data['cipher']

n = point_order(P, a, p)
d = discrete_log_pohlig(P, Q, a, p, n)
print(f"Recovered d = {d}")
print("Message:", aes_decrypt(Q[0], ciphertext).decode())