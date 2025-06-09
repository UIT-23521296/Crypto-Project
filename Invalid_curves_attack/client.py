from elliptic_curve import Curve, Point
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import sha3_512
import socket
import pickle
import random

# NIST P-256 parameters
p = 2**256 - 2**224 + 2**192 + 2**96 - 1
a = -3
b = 41058363725152142129326129780047268409114441015993725554835256314039467401291
curve = Curve(p, a, b)
Gx = 48439561293906451759052585252797914202762949526041747995844080717082404635286
Gy = 36134250956749795798585127919587881956611106672985015071877198253568414405109
G = Point(curve, Gx, Gy, validate=True)

# Client key
k_A = 115792089210356248762697446049107523539994955224133762342422259061068512044369
Q_A = k_A * G
print(Q_A)

def recvall(sock):
    data = b""
    while True:
        part = sock.recv(4096)
        if not part:
            break
        data += part
    return data

# Connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('server', 2025))

# Send Q_A
client.send(pickle.dumps(Q_A))

# Receive Q_B, ciphertext, and R
response = recvall(client)

ciphertext, Q_B, encrypted_shared_key = pickle.loads(response)
print(Q_B)

# Compute shared secret K = k_A * Q_B
K = k_A * Q_B
print(f"[DEBUG] Computed shared key: {K}")

# Decrypt data
key_bytes = str(K.x % p).encode()
key = sha3_512(key_bytes).digest()[:16]
print(f"[DEBUG] Generated key: {key.hex()}")

iv = ciphertext[:16]
ct = ciphertext[16:]

cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = cipher.decrypt(ct)
print(f"[DEBUG] Decrypted (before unpadding): {decrypted.hex()}")

try:
    plaintext = unpad(decrypted, AES.block_size)
    with open("decrypted_data.jpg", "wb") as fi:
        fi.write(plaintext)
    print(f"Decrypted data: {plaintext.decode()}")
except ValueError as e:
    print(f"[ERROR] Failed to unpad: {e}")
    print(f"[DEBUG] Last bytes of decrypted data: {decrypted[-16:].hex()}")
    # Try to decode anyway
    try:
        print(f"Raw decrypted data: {decrypted.decode()}")
    except:
        pass

client.close()