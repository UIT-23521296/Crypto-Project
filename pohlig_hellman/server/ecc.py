from math import gcd

class Curve:
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b

    def is_on_curve(self, x, y):
        return (y * y - (x ** 3 + self.a * x + self.b)) % self.p == 0

class Point:
    def __init__(self, curve, x, y, validate=False):
        self.curve = curve
        self.x = x
        self.y = y
        if validate and not curve.is_on_curve(x, y):
            raise ValueError("Point is not on the curve")

    def __add__(self, Q):
        if self.x == Q.x and self.y == Q.y:
            return self.double()

        lam = ((Q.y - self.y) * pow(Q.x - self.x, -1, self.curve.p)) % self.curve.p
        xr = (lam ** 2 - self.x - Q.x) % self.curve.p
        yr = (lam * (self.x - xr) - self.y) % self.curve.p
        return Point(self.curve, xr, yr)

    def double(self):
        lam = ((3 * self.x ** 2 + self.curve.a) * pow(2 * self.y, -1, self.curve.p)) % self.curve.p
        xr = (lam ** 2 - 2 * self.x) % self.curve.p
        yr = (lam * (self.x - xr) - self.y) % self.curve.p
        return Point(self.curve, xr, yr)

    def __rmul__(self, k):
        R = None
        Q = self
        while k:
            if k & 1:
                R = Q if R is None else R + Q
            Q = Q.double()
            k >>= 1
        return R

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"