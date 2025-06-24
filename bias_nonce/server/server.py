# server.py
from flask import Flask, request, jsonify
from hashlib import sha256
from ecdsa import SigningKey, SECP256k1
from ecdsa.ecdsa import generator_secp256k1

app = Flask(__name__)

def inverse_mod(a, n):
    return pow(a, -1, n)

# Tạo khóa riêng và khóa công khai
sk = SigningKey.generate(curve=SECP256k1)
vk = sk.verifying_key
d = sk.privkey.secret_multiplier  # private key

with open("pri_key.txt", "w") as f:
    f.write(hex(d))

print("[INFO] Private key d đã được lưu vào pri_key.txt")

# Dùng 1 nonce k cố định (để minh họa lỗ hổng reuse k)
k_fixed = 1234567890123456789012345678901234567890

@app.route('/pubkey', methods=['GET'])
def get_pubkey():
    return jsonify({
        'curve': 'secp256k1',
        'public_key': vk.to_string().hex()
    })

@app.route('/sign', methods=['POST'])
def sign_message():
    msg = request.json['message']
    h = int.from_bytes(sha256(msg.encode()).digest(), 'big')

    G = generator_secp256k1
    n = G.order()

    r = (k_fixed * G).x() % n
    s = (inverse_mod(k_fixed, n) * (h + r * d)) % n

    return jsonify({
        'r': int(r),
        's': int(s),
        'hash': int(h)
    })

if __name__ == '__main__':
    print("[INFO] ECDSA Signing Server started on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000)
