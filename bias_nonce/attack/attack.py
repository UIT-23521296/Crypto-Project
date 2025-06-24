# attack.py
import requests
from hashlib import sha256

def inverse_mod(a, n):
    return pow(a, -1, n)

def get_signature(msg):
    """Gửi message đến server và nhận lại chữ ký."""
    res = requests.post('http://server:5000/sign', json={'message': msg})
    print(f"[DEBUG] Status code: {res.status_code}")
    print(f"[DEBUG] Raw response: {res.text}")
    
    if res.status_code != 200:
        raise Exception("Lỗi khi gọi server ký!")
    
    return res.json()

def main():
    print("[INFO] Đang gửi 2 thông điệp khác nhau...")
    sig1 = get_signature("message 1")
    sig2 = get_signature("message 2")

    r1, r2 = sig1['r'], sig2['r']
    if r1 != r2:
        print("[ERROR] r khác nhau, server không reuse nonce!")
        return

    r = r1
    s1, s2 = sig1['s'], sig2['s']
    z1, z2 = sig1['hash'], sig2['hash']

    # Order của SECP256k1
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    print("[INFO] Khôi phục nonce k từ 2 chữ ký...")
    try:
        k = ((z1 - z2) * inverse_mod(s1 - s2, n)) % n
        print("[+] Nonce k:", hex(k))
    except ValueError:
        print("[ERROR] Không thể tính nghịch đảo s1 - s2")
        return

    print("[INFO] Khôi phục private key d...")
    try:
        d = ((s1 * k - z1) * inverse_mod(r, n)) % n
        print("[+] Private key d khôi phục được:")
        print("    " + hex(d))
    except ValueError:
        print("[ERROR] Không thể tính nghịch đảo r")

if __name__ == "__main__":
    main()
