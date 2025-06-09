from sage.all import *
from Crypto.Util.number import *
import random
import secrets
from Crypto.Cipher import AES 
from Crypto.Util.Padding import pad
from hashlib import sha3_512

def encrypt(key, mess):
    key = sha3_512(str(key).encode()).digest()[:16]
    iv = secrets.token_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(mess, AES.block_size))
    return iv + ct

def genPara(p):
    while True:
        a,b = random.randrange(0,p-1), random.randrange(0,p-1)
        if (4*a**3 + 27 * b**2) % p != 0:
            return a,b

p = getPrime(30)
F = GF(p)
a,b = genPara(p)
E = EllipticCurve(F, [a,b])
P = E.gens()[0]
secret = random.randint(1, P.order() - 1)
Q = P * secret

# Save params
with open("params.txt", "w") as f:
    f.write(f"{p}\n{a}\n{b}\n")
    f.write(f"{P[0]}\n{P[1]}\n")
    f.write(f"{Q[0]}\n{Q[1]}\n")

# Save private key
with open("private_key.txt", "w") as f:
    f.write(str(secret))
print("Private key saved to private_key.txt")


# Encrypt input.pdf
with open("input.pdf", "rb") as inp:
    input_data = inp.read()
ciphertext = encrypt(secret, input_data)
with open("cipher.enc", "wb") as out:
    out.write(ciphertext)
print("✅ Server đã ghi cipher.enc và params.txt.")
