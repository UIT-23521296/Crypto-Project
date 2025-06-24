from sage.all import GF, discrete_log

class Point:
    def __init__(self, x, y, curve):
        self.curve = curve
        F = curve.F
        self.x = F(x) if x is not None else None
        self.y = F(y) if y is not None else None
    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y and self.curve == other.curve

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if self.x is None and self.y is None:
            return "Point at Infinity (O)"
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()

class EllipticCurve:
    def __init__(self, a, b, c, p, info):
        self.p = p
        self.F = GF(p)
        self.a2 = self.F(a) if a is not None else self.F(0)
        self.a4 = self.F(b) if b is not None else self.F(0)
        self.a6 = self.F(c) if c is not None else self.F(0)
        self.O = Point(None, None, self)

        if info == 0:
            def fmt(coef, term):
                if coef == 0: return ""
                if coef == 1: return f"+ {term}"
                if coef == -1: return f"- {term}"
                return f"+ {coef}{term}" if coef > 0 else f"- {-coef}{term}"

            rhs = "x^3"
            rhs += " " + fmt(self.a2, "x^2")
            rhs += " " + fmt(self.a4, "x")
            rhs += " " + (f"+ {self.a6}" if self.a6 > 0 else f"- {-self.a6}" if self.a6 != 0 else "")

            rhs = rhs.replace("+ -", "- ").strip()
            print(f"\nPhương trình: y^2 = {rhs} (mod {self.p})")

        discriminant_simplified = 4 * self.a4**3 + 27 * self.a6**2

        if discriminant_simplified.is_zero():
            R = self.F['x']
            x = R.gen()
            f_poly = x**3 + self.a2 * x**2 + self.a4 * x + self.a6
            roots = f_poly.roots(multiplicities=True)

            f1 = f_poly.derivative(1)
            f2 = f_poly.derivative(2)
            
            for root, mult in roots:
                if f1(root) == 0:
                    if f2(root) == 0:
                        if info == 0: print(f"    - CUSP tại ({root}, 0)")
                    else:
                        if info == 0: print(f"    - NODE tại ({root}, 0)")
        else:
            if info == 0: print("  --> Đường cong KHÔNG KỲ DỊ (Non-singular Curve).")    
    def is_on_curve(self, x, y):
        if x is None and y is None: 
            return True
        x_gf = GF(self.p)(x)
        y_gf = GF(self.p)(y)
        return (y_gf**2) == (x_gf**3 + self.a2 * x_gf**2 + self.a4 * x_gf + self.a6)

    def point_addition(self, P1, P2):
        if P1 == self.O:
            return P2
        if P2 == self.O:
            return P1        
        if P1.x == P2.x:
            if P1.y != P2.y:
                return self.O
            else: 
                if P1.y == GF(self.p)(0): 
                    return self.O
                slope = (3 * P1.x**2 + 2 * self.a2 * P1.x + self.a4) / (2 * P1.y) 
        else: 
            slope = (P2.y - P1.y) / (P2.x - P1.x)

        x3 = slope**2 - P1.x - P2.x - self.a2
        y3 = slope * (P1.x - x3) - P1.y - self.a2 * x3 
        return Point(x3, y3, self)

    def scalar_multiplication(self, k, P):
        if k == 0:
            return self.O
        result = self.O
        addend = P
        while k > 0:
            if k % 2 == 1:
                result = self.point_addition(result, addend)
            addend = self.point_addition(addend, addend)
            k //= 2
        return result

    def attack_cusp_method(self, Gx, Gy, Px, Py):
        print("\n--- Start attack CUSP ---")
        R = GF(self.p)['x']
        x = R.gen()
        f = x**3 + self.a2 * x**2 + self.a4 * x + self.a6

        roots = f.roots()

        Gx_gf = GF(self.p)(Gx)
        Gy_gf = GF(self.p)(Gy)
        Px_gf = GF(self.p)(Px)
        Py_gf = GF(self.p)(Py)
        print(f"G: ({Gx_gf}, {Gy_gf})")
        print(f"Server Public Key: {Px_gf}, {Py_gf}")
        
        if len(roots) == 1 and roots[0][1] == 3:
            alpha = roots[0][0]
            u = (Gx_gf - alpha) / Gy_gf
            v = (Px_gf - alpha) / Py_gf
            
            recovered_private_key = int(v / u)
            return recovered_private_key
        else:
            print("Not Cusp. Attack fail.")
            return None

    def attack_node_method(self, Gx, Gy, Px, Py):
        R = GF(self.p)['x'] 
        x = R.gen()
        f = x**3 + self.a2 * x**2 + self.a4 * x + self.a6
        roots_with_multiplicities = f.roots()
        alpha = None
        beta = None
        if len(roots_with_multiplicities) == 2:
            if roots_with_multiplicities[0][1] == 2:
                alpha = roots_with_multiplicities[0][0]  # Double root
                beta = roots_with_multiplicities[1][0]   # Simple root
            elif roots_with_multiplicities[1][1] == 2:
                alpha = roots_with_multiplicities[1][0]  # Double root
                beta = roots_with_multiplicities[0][0]   # Simple root
            else:
                print("Curve is not a node with double root, cannot apply this attack.")
                return None    
            print(f"Double root: α = {alpha}")
            print(f"Simple root: β = {beta}")           
            try:
                # Tính tham số biến đổi
                t = (alpha - beta).sqrt()
                print(f"Parameter t = √(α - β) = {t}")
                
                # Kiểm tra các trường hợp đặc biệt
                if Gx == alpha or Px == alpha:
                    print("Points lie on vertical line x = α, cannot apply this method")
                    return None
                u = (Gy + t * (Gx - alpha)) / (Gy - t * (Gx - alpha))
                v = (Py + t * (Px - alpha)) / (Py - t * (Px - alpha))
                
                print(f"u = (G.y + t(G.x - α))/(G.y - t(G.x - α)) = {u}")
                print(f"v = (P.y + t(P.x - α))/(P.y - t(P.x - α)) = {v}")
                # Tính discrete log trong multiplicative group
                try:
                    #k = int(v.log(u)) 
                    k = int(discrete_log(v, u))
                    print(f"Private key found: k = {k}")
                    return k
                except ValueError as e:
                    print(f"Error in discrete log calculation: {e}")
                    return None
                
            except Exception as e:
                print(f"Error in node attack: {e}")
                return None
        else:
            print("Curve is not a node with double root, cannot apply this attack.")
            return None   
        
    def attack_singular_curve(self, server_public_key_point, G):
        R = GF(self.p)['x']
        x_poly = R.gen()
        f_poly = x_poly**3 + self.a2 * x_poly**2 + self.a4 * x_poly + self.a6
        roots_with_multiplicities = f_poly.roots()

        # Check for Cusp (triple root)
        if len(roots_with_multiplicities) == 1 and roots_with_multiplicities[0][1] == 3:
            print("--> Phát hiện CUSP. Use attack Cusp.")
            return self.attack_cusp_method(G.x, G.y, server_public_key_point.x, server_public_key_point.y)
        # Check for Node (double root)
        elif len(roots_with_multiplicities) > 0 and any(root[1] >= 2 for root in roots_with_multiplicities):
            print("--> Phát hiện NODE. Use attack Node.")
            return self.attack_node_method(G.x, G.y, server_public_key_point.x, server_public_key_point.y)
        else:
            print("--> Không xác định được loại điểm kỳ dị. Cannot apply a specific attack.")
            return None