from hashlib import sha3_512

with open("./encrypted_test.enc", "rb") as f:
    data = f.read()

hash_value = sha3_512(data).hexdigest()
print("SHA3-512 hash (first 16 chars):", hash_value[:16])
