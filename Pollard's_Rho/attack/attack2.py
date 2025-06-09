import os
import time

def wait_for_file_update(filepath, last_mtime):
    while True:
        if os.path.exists(filepath):
            mtime = os.path.getmtime(filepath)
            if mtime > last_mtime:
                return mtime
        time.sleep(1)

last_params_mtime = 0
last_enc_mtime = 0

from sage.all import *
from Crypto.Util.number import *
from fractions import Fraction
from pwn import *
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES 
from hashlib import sha3_512

while True:
    last_params_mtime = wait_for_file_update("/output/params.txt", last_params_mtime)
    last_enc_mtime = wait_for_file_update("/output/encrypt_2.enc", last_enc_mtime)

    with open("/output/params.txt", "r") as f:
        lines = f.read().splitlines()

    a = int(lines[0])
    b = int(lines[1])
    p = int(lines[2])

    Px, Py = map(int, lines[3].split())
    Qx, Qy = map(int, lines[4].split())

    P = (Px, Py)
    Q = (Qx, Qy)

    E = EllipticCurve(GF(p), [a, b])
    n = E.order()
    P = E(*P)
    Q = E(*Q)

    try:
        x = discrete_log_rho(Q, P, operation="+")
        assert int(x)*P == Q
        print("Found secret, ",x)   
    except:
        print ("Solve unsuccessfully!")
        continue

    ciphertext = open("/output/encrypt_2.enc", 'rb').read()

    key = sha3_512(str(x).encode()).digest()[:16]
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)

    with open("/output/recover_file_2.jpg", "wb") as write:
        write.write(unpad(cipher.decrypt(ciphertext), AES.block_size))

    print("Recovered successfully!")
    break