from sage.all import *
from elliptic_curve import Curve, Point, INFINITY
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hashlib import sha3_512
from Crypto.Cipher import ARC4
from random import choice
import socket
import pickle
import sys

# Thêm print để debug
print("[DEBUG] Starting server...")
print("[DEBUG] Python version:", sys.version)
print("[DEBUG] Sage version:", sage.version.version)

# NIST P-256 parameters
p = 2**256 - 2**224 + 2**192 + 2**96 - 1
a = -3
b = 41058363725152142129326129780047268409114441015993725554835256314039467401291
curve = Curve(p, a, b)
Gx = 48439561293906451759052585252797914202762949526041747995844080717082404635286
Gy = 36134250956749795798585127919587881956611106672985015071877198253568414405109
G = Point(curve, Gx, Gy, validate=True)

# Server key
k_B = 11079208921356230762697446949407573529996920224135760342421115906106851204435

# Data
with open("test.jpg", "rb") as file:
    message = file.read()
file.close()

system_para = [
    "To the well-organized mind, death is but the next great adventure.",
    "It takes a great deal of bravery to stand up to our enemies, but just as much to stand up to our friends.",
    "The truth. It is a beautiful and terrible thing, and should therefore be treated with great caution." ,
    "Happiness can be found, even in the darkest of times, if one only remembers to turn on the light.",
    "If you want to know what a man's like, take a good look at how he treats his inferiors, not his equals.",
    "Death Eater",
    "Draught of Living Death",
]

def encryptPoint(P, key_str):
    # Chuyển key string thành bytes và hash
    key_bytes = key_str.encode()
    key = sha3_512(key_bytes).digest()[:16]
    
    # Chuyển điểm P thành bytes
    point_bytes = pickle.dumps(P)
    
    # Tạo IV
    iv = b'\x00' * 16
    
    # Tạo cipher
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Pad và mã hóa
    padded_message = pad(point_bytes, AES.block_size)
    encrypted = cipher.encrypt(padded_message)
    
    return iv + encrypted

def encrypt(key, message):
    print(f"[DEBUG] Encrypting message with key: {key}")
    # Convert key to bytes and hash
    key_bytes = str(key.x % p).encode()
    key = sha3_512(key_bytes).digest()[:16]
    
    # Create IV and cipher
    iv = b'\x00' * 16
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Pad and encrypt
    padded_message = pad(message, AES.block_size)
    encrypted = cipher.encrypt(padded_message)
    
    return iv + encrypted

# Server socket
print("[INFO] Starting server...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind(('0.0.0.0', 2025))
    print("[INFO] Binding to 0.0.0.0:2025 successful")
except Exception as e:
    print(f"[ERROR] Bind failed: {e}")
    exit(1)
server.listen(3)
print("[INFO] Server running on 0.0.0.0:2025")

try:
    while True:
        try:
            print("[INFO] Waiting for connection...")
            client, addr = server.accept()
            print(f"[INFO] Connected by {addr}")
            
            # Receive Q_A
            buffer = b''
            while True:
                data = client.recv(4096)
                if not data:
                    break
                buffer += data
                try:
                    Q_A = pickle.loads(buffer)
                    break
                except EOFError:
                    continue
            print(Q_A)
            
            # Compute Q_B = k_B * G
            Q_B = k_B * G
            
            # Encrypt data using shared_key
            shared_key = k_B * Q_A
            random_key = choice(system_para)
            encrypted_shared_key = encryptPoint(shared_key, random_key)
            ciphertext = encrypt(shared_key, message)
            print(f"Cipher text: {sha3_512(ciphertext).hexdigest()[:16]}")
            try:
                with open("/home/sage/encrypted/encrypted_test.enc", "wb") as f:
                    f.write(ciphertext)
            except Exception as e:
                print(f"[ERROR] Failed to save encrypted file: {e}")
                print(f"[DEBUG] Current working directory: {os.getcwd()}")
                print(f"[DEBUG] Files in current directory: {os.listdir()}")
            
            # Send ciphertext and Q_B
            response = pickle.dumps((ciphertext, Q_B, encrypted_shared_key))
            client.send(response)
            
        except Exception as e:
            print(f"[ERROR] Error handling connection: {e}")
            import traceback
            traceback.print_exc()
        finally:
            client.close()
            print("[INFO] Connection closed")
except KeyboardInterrupt:
    print("[INFO] Server shutting down...")
finally:
    server.close()
    print("[INFO] Server closed")