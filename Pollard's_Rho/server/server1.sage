from sage.all import *
from Crypto.Util.number import *
import random
import secrets
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hashlib import sha3_512

def check(prime):
    if not is_prime(prime):
        print("Not prime")
        return False
    if prime <= (1<<35):
        print("Your prime is too weak!")
        return False
    return True

def encrypt(key, mess):
    key = sha3_512(str(key).encode()).digest()[:16]
    iv = secrets.token_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(mess, AES.block_size))
    return iv + ct

def genPara(p):
    while True:
        a, b = random.randrange(0, p-1), random.randrange(0, p-1)
        E = EllipticCurve(GF(p), [a, b])
        if (4 * a**3 + 27 * b**2) % p != 0 and is_prime(int(E.order())):
            return a, b
        
while True:
    p = int(input("Enter prime: "))
    if(check(p)):
        break

secret = random.randint(0, p-1)

F = GF(p)
a,b = genPara(p)
E = EllipticCurve(F, [a, b])
P = E.gens()[0]
Q = P * secret

print(f'{a = }')
print(f'{b = }')
print(f'{p = }')
print('P =', P.xy())
print('Q =', Q.xy())
print(f'{secret = }')

with open("/output/params.txt", "w") as f:
    f.write(f"{a}\n")
    f.write(f"{b}\n")
    f.write(f"{p}\n")
    f.write(f"{P.xy()[0]} {P.xy()[1]}\n")
    f.write(f"{Q.xy()[0]} {Q.xy()[1]}\n")

with open("file_test.jpg", 'rb') as file:
    pt = file.read()

ciphertext = encrypt(secret, pt)
with open("/output/encrypt_2.enc", "wb") as file:
    file.write(ciphertext)
    print("Encrypt succesfully!")