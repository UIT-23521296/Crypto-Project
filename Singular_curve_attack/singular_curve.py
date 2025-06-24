from elliptic_curve import EllipticCurve, Point
from sage.all import random_prime, GF
import random

class Server:
    def __init__(self, mode):
        if mode == "node":
            self.p = 4368590184733545720227961182704359358435747188309319510520316493183539079703
            a2, a4, a6 = 1, 0, 0
            self.curve = EllipticCurve( a2 , a4 , a6 , self.p, 0)
            F = GF(self.p)
            # base point
            gx = 8742397231329873984594235438374590234800923467289367269837473862487362482
            gy = 225987949353410341392975247044711665782695329311463646299187580326445253608
            self.G = Point(gx, gy, self.curve) 
            # public point
            px = 2582928974243465355371953056699793745022552378548418288211138499777818633265
            py = 2421683573446497972507172385881793260176370025964652384676141384239699096612

            self.public_key = Point(px, py, self.curve)
            self.private_key = 3963903911833444099026001790250531678485652182452420312170405092086735621359

        elif mode == "cusp":
            self.p = random_prime(2**256, lbound=2**255)
            a2, a4, a6 = 0, 0, 0
            self.curve = EllipticCurve(a2, a4, a6, self.p, 0)
            self.G = Point(1, 1, self.curve)

            self.private_key = random.randint(1, self.p - 1)
            self.public_key = self.curve.scalar_multiplication(self.private_key, self.G)
        else:
            raise ValueError("Chọn 'cusp' hoặc 'node'.")

        print(f"\nServer Private Key: {self.private_key}")
        print(f"Server Public Key: {self.public_key.x}, {self.public_key.y}")

    def send_public_key_to_client(self):
        return {
            "curve_params": {
                "a2": self.curve.a2.lift(),
                "a4": self.curve.a4.lift(),
                "a6": self.curve.a6.lift(),
                "p": self.curve.p
            },
            "base_point": {"x": self.G.x.lift(), "y": self.G.y.lift()},
            "server_public_key": {"x": self.public_key.x.lift(), "y": self.public_key.y.lift()}
        }

    def receive_client_public_key(self, client_public_key_data):
        client_Q = Point(client_public_key_data["x"], client_public_key_data["y"], self.curve)
        shared_secret_server = self.curve.scalar_multiplication(self.private_key, client_Q)
        return shared_secret_server

class Attacker:
    def __init__(self):
        self.curve = None
        self.G = None
        self.server_public_key_point = None
        self.private_key = None
        self.public_key = None

    def receive_server_info(self, server_data):
        params = server_data["curve_params"]
        self.curve = EllipticCurve(params["a2"], params["a4"], params["a6"], params["p"], 1)
        self.G = Point(server_data["base_point"]["x"], server_data["base_point"]["y"], self.curve)
        self.server_public_key_point = Point(
            server_data["server_public_key"]["x"],
            server_data["server_public_key"]["y"],
            self.curve
        )

    def launch_attack(self, server_true_private_key):
        recovered_private_key = self.curve.attack_singular_curve(
            self.server_public_key_point,
            self.G
        )

        if recovered_private_key is not None:
            if recovered_private_key == server_true_private_key:
                print(f"Server Private Key: {recovered_private_key}")
            else:
                print("Wrong key")
        else:
            print("Attack fail.")

# --------- MAIN ---------
if __name__ == "__main__":
    mode = input("Chọn loại đường cong (node/cusp): ").strip().lower()
    if mode not in ["node", "cusp"]:
        print("❌ Lựa chọn không hợp lệ. Chọn 'node' hoặc 'cusp'.")
        exit(1)

    server = Server(mode)
    attacker = Attacker()

    server_info = server.send_public_key_to_client()
    attacker.receive_server_info(server_info)

    print("\n⚔️  Thực hiện tấn công dựa trên điểm kỳ dị:")
    attacker.launch_attack(server.private_key)