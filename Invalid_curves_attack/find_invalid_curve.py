from sage.all import *
import random

#Tham số
p = 2**256 - 2**224 + 2**192 + 2**96 - 1
a = -3
F = GF(p)
n = 115792089210356248762697446949407573529996955224135760342422259061068512044369

def find_invalid_curve():
    invalid_curves = []
    order = 1
    while order < n:
        b1 = random.randint(0, p - 1)
        try:
            E1 = EllipticCurve(F, [a, b1])
            new_order = E1.order()
            for prime, ex in factor(new_order): #Phân tích order thành thừa số nto
                if (1 << 20) < prime < (1 << 40):
                    invalid_curves.append((b1, prime))
                    order *= prime
        except:
            continue
    return invalid_curves

param = find_invalid_curve()
with open("invalid_curves.txt", "w") as f:
    f.write(str(param))
print(f"Invalid curves saved to invalid_curves.txt: {param}")