from sage.all import *
from Crypto.Util.number import *
from fractions import Fraction
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

def f(Ri, P, Q):
    y = Ri.xy()[1]
    if 0 < y <= p//3:
        return Q + Ri
    elif p//3 < y < 2*p//3:
        return 2*Ri
    else:
        return P+ Ri

def update_ab(Ri, ai, bi):
    y = Ri.xy()[1]
    if 0 < y <= p//3:
        return ai, (bi + 1) % n
    elif p//3 < y < 2*p//3:
        return 2*ai % n, 2*bi % n
    else:
        return (ai +1) % n, bi

def attack(P, Q, n):
    a = []
    b = []
    R = []
    R.append(P)
    a.append(1)
    b.append(0)
    i = 1
    while True:
        R.append(f(R[i-1], P,Q))
        ab = update_ab(R[i-1], a[i-1], b[i-1])
        a.append(ab[0])
        b.append(ab[1])
        if i % 2 == 0 and R[i] == R[i//2]:
            m = i//2
            break
        i += 1  
    fr = Fraction(int(a[2*m] - a[m]), int(b[m] - b[2*m]))
    a_num, b_den = int(fr.numerator), int(fr.denominator)
    try:
        inv_b = pow(b_den, -1, n)
    except ValueError:
        raise ValueError("No modular inverse for denominator")

    x = (a_num * inv_b) % n
    return x

while True:
    r = remote('server', 8888)
    a, b, p, P, Q = getPara()
    E = EllipticCurve(GF(p), [a, b])
    n = E.order()
    P = E(*P)
    Q = E(*Q)

    try:
        x = attack(P,Q,n)
        x = x % n
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