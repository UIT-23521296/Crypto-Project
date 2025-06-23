from sage.all import *
from Crypto.Util.number import *
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES 
from hashlib import sha3_512

while True:

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
    cipher = AES.new(key, AES.MODE_GCM, iv)

    with open("/output/recover_file_2.jpg", "wb") as write:
        write.write(unpad(cipher.decrypt(ciphertext), AES.block_size))

    print("Recovered successfully!")
    break