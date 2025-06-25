def inverse(x, p): return pow(x, -1, p)

def is_on_curve(x, y, a, b, p):
    return (y * y - x**3 - a * x - b) % p == 0

def point_add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and y1 != y2: return None
    try:
        if P == Q:
            denom = (2 * y1) % p
            if denom == 0: return None
            m = (3 * x1**2 + a) * inverse(denom, p) % p
        else:
            denom = (x2 - x1) % p
            if denom == 0: return None
            m = (y2 - y1) * inverse(denom, p) % p
    except Exception:
        return None
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)

def point_mul(P, k, a, p):
    R = None
    while k:
        if k & 1: R = point_add(R, P, a, p)
        P = point_add(P, P, a, p)
        k >>= 1
    return R

def point_order(P, a, p, max_trials=10000):
    try:
        for k in range(2, max_trials):
            R = point_mul(P, k, a, p)
            if R is None:
                return k
        raise ValueError("point_order() failed: no order found under max_trials")
    except Exception as e:
        raise ValueError("point_order() exception: " + str(e))

def factor(n):
    if n is None:
        raise ValueError("point_order() returned None")
    f = []
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            count = 0
            while n % i == 0:
                n //= i
                count += 1
            f.append((i, count))
    if n > 1: f.append((n, 1))
    return f

def crt(congs):
    x, m = 0, 1
    for a, n in congs:
        m1_inv = pow(m, -1, n)
        x = (x * n * pow(n, -1, m) + a * m * m1_inv) % (m * n)
        m *= n
    return x