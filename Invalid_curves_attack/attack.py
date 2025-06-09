from sage.all import *
from sage.groups.generic import discrete_log
from elliptic_curve import Curve, Point
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import sha3_512
import socket
import pickle
import time
import matplotlib.pyplot as plt

# NIST P-256 parameters
p = 2**256 - 2**224 + 2**192 + 2**96 - 1
a = -3
b = 41058363725152142129326129780047268409114441015993725554835256314039467401291
E = EllipticCurve(GF(p), [a, b])
Gx = 48439561293906451759052585252797914202762949526041747995844080717082404635286
Gy = 36134250956749795798585127919587881956611106672985015071877198253568414405109
G = E(Gx, Gy)

system_para = [
    "To the well-organized mind, death is but the next great adventure.",
    "It takes a great deal of bravery to stand up to our enemies, but just as much to stand up to our friends.",
    "The truth. It is a beautiful and terrible thing, and should therefore be treated with great caution." ,
    "Happiness can be found, even in the darkest of times, if one only remembers to turn on the light.",
    "If you want to know what a man's like, take a good look at how he treats his inferiors, not his equals.",
    "Death Eater",
    "Draught of Living Death",
]

# param from find_invalid_curve output
# param = [(55374142742056320173571819787638777809472808911336014480884317286813436773845, 29445413), 
#          (18683340606237798162839665554819902562078278271152292185206948669269254230573, 162263531), 
#          (24624047588339450439272204081149894170198019866724433619179522253068021779886, 3476383747), 
#          (55902766844192818853349178750639525185968852147752636007309716099481040626885, 10487969), 
#          (52747115907965531604384938330824351387999587888780246057838615834696934575358, 2123141), 
#          (108232452892497826311561131892338314696129649158423199517090362383919394433991, 2203997), 
#          (90481521012725922649701551112858596167711449568080783403246099132591745270507, 539750069), 
#          (28011845194834396615899024385750801804824562202897145426874917021984099984567, 10629007), 
#          (113987535422036877277675647077877815533200060438538889639190756175419110124578, 3881443), 
#          (109509272759190264405760199419896053318904150440188275352947737728386878053685, 507508801), 
#          (83236566530711825898226925099842178605458817240088953369114820344421196003979, 8201753543)]

param = [(38890960983694756269929133086511469058631323800811368734669566297683073445492, 1120529), 
         (38890960983694756269929133086511469058631323800811368734669566297683073445492, 3678657497), 
         (38890960983694756269929133086511469058631323800811368734669566297683073445492, 19703246659), 
         (38890960983694756269929133086511469058631323800811368734669566297683073445492, 94708355267), 
         (38890960983694756269929133086511469058631323800811368734669566297683073445492, 577569976573), 
         (81888671554415061129585237542382856292560128776348758353718055621891570491654, 1914853), 
         (68689208311510086269319353678828519906576583340442773367994228418676314164351, 56252461), 
         (68689208311510086269319353678828519906576583340442773367994228418676314164351, 141991729571), 
         (68689208311510086269319353678828519906576583340442773367994228418676314164351, 207831768671)]

def recvall(sock):
    data = b""
    while True:
        part = sock.recv(4096)
        if not part:
            break
        data += part
    return data

def decryptPoint(encrypted_data, key_str):
    try:
        # Chuyển key string thành bytes và hash
        key_bytes = key_str.encode()
        key = sha3_512(key_bytes).digest()[:16]
        
        # Tách IV và ciphertext
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Tạo cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Giải mã và unpad
        decrypted = cipher.decrypt(ciphertext)
        unpadded = unpad(decrypted, AES.block_size)
        
        # Chuyển bytes thành điểm
        point = pickle.loads(unpadded)
        print(f"[DEBUG] Successfully decrypted with key: {key_str}")
        return point
    except Exception as e:
        print(f"[DEBUG] Decryption failed with key '{key_str}': {str(e)}")
        return None

results = []
order = []
for b_, prime in param:
    order.append(prime)
    # Create invalid curve
    E_prime = EllipticCurve(GF(p), [a, b_])
    point = E_prime.gen(0) * (E_prime.order() // prime)
    invalid_point = Point(Curve(p, a, b_), point.xy()[0], point.xy()[1], validate=False)
    print(f"[DEBUG]: Invalid point from attacker: {invalid_point}")
    
    # Connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('server', 2025))
    
    # Send invalid point as Q_A
    data = pickle.dumps(invalid_point)
    print(f"[DEBUG] Size of data being sent: {len(data)} bytes")
    client.send(data)
    
    # Receive ciphertext and shared_key
    response = recvall(client)
    try:
        ciphertext, Q_B, encrypted_shared_key = pickle.loads(response)
        for key in system_para:
            try:
                uncheck_point = decryptPoint(encrypted_shared_key, key)
                sharedkey = E_prime(uncheck_point.x, uncheck_point.y)
            except Exception as e:
                continue
        print(f"[DEBUG] Valid point: {sharedkey}")
        results.append(sharedkey.log(point))
    except EOFError:
        print(f"Error receiving data for prime {prime}: Server closed connection.")
    client.close()

# Combine with CRT
k_B = crt(results, order)
print(f"Full k_B: {k_B}")

# Get Q_A and ciphertext from a real client
Q_A = (22937851354780616147313360886532884264565432893318490032385207694166407524532, 
       107786184760770155735260324838992585922762586602543854051633377041487364561131)


# Compute shared secret K = k_B * G (dummy Q_A)
k_B_sage = Integer(k_B)
Q_A_point = E(Q_A[0], Q_A[1])  # Chuyển tuple thành điểm trên đường cong
print(f"Q_A from client: {Q_A_point}")
K = k_B_sage * Q_A_point
x, y = K.xy()
shared_key = Point(Curve(p, a, b), x, y, validate=False)
# Thêm log để debug
print(f"[DEBUG] K.x: {K.x}")
print(f"[DEBUG] K[0]: {K[0]}")
print(f"[DEBUG] K.x == K[0]: {K.x == K[0]}")

key_bytes = str(K[0] % p).encode()
key = sha3_512(key_bytes).digest()[:16]

with open("/home/sage/encrypted/encrypted_test_server.enc", "rb") as file:
    message = file.read()
file.close()

print(f"Cipher text: {sha3_512(message).hexdigest()[:16]}")

iv = message[:16]
ct = message[16:]
cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = cipher.decrypt(ct)
with open("/home/sage/decrypted/attack.jpg", "wb") as fi:
    fi.write(decrypted)
print(f"Hehe, decrypted data is now ready, check attack.jpg")