from sage.all import *
from Crypto.Util.number import *
from pwn import *
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES 
from hashlib import sha3_512

def getPara():
    p = getPrime(36)
    r.sendlineafter(b'Enter prime: ', str(p).encode())
    a = int(r.recvlineS().split('=')[1].strip())
    b = int(r.recvlineS().split('=')[1].strip())
    p = int(r.recvlineS().split('=')[1].strip())
    P = eval(r.recvlineS().split('=')[1].strip())
    Q = eval(r.recvlineS().split('=')[1].strip())
    r.recvline()
    return a, b, p, P, Q

while True:
    r = remote('server', 8888)
    a, b, p, P, Q = getPara()
    E = EllipticCurve(GF(p), [a, b])
    n = E.order()
    P = E(*P)
    Q = E(*Q)

    try:
        x = discrete_log_rho(Q, P, operation="+")
        assert int(x)*P == Q
        print("Found secret, ",x)
        break
    except:
        print ("Solve unsuccessfully!")

ciphertext = open("/output/encrypt_1.enc", 'rb').read()

key = sha3_512(str(x).encode()).digest()[:16]
iv = ciphertext[:16]
ciphertext = ciphertext[16:]
cipher = AES.new(key, AES.MODE_GCM, iv)

with open("/output/recover_file_1.jpg", "wb") as write:
    write.write(unpad(cipher.decrypt(ciphertext), AES.block_size))
print("Recovered successfully!")