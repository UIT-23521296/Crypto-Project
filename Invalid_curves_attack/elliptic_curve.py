#Class biểu diễn curve trên trường hữu hạn F_p
class Curve:
    def __init__(self, p, a, b):
        #Trường hữu hạn: modulo p (snt)
        self.p = p
        #Hệ số a và b trong phương trình curve
        self.a = a
        self.b = b

    def __eq__(self, other):
        #So sánh 2 curve
        if isinstance(other, Curve):
            return self.p == other.p and self.a == other.a and self.b == other.b
        return None
    
    def __str__(self):
        #Chuỗi biểu diễn curve
        return f"y^2 = x^3 + {self.a}x + {self.b} over F_{self.p}"
    
    def is_valid_point(self, x, y):
        #Kiểm tra điểm thuộc curve
        return (y*y) % self.p == (x**3 + self.a*x + self.b) % self.p
    
#Class biểu diễn điểm trên curve
class Point:
    def __init__(self, curve, x, y, validate=True):
        #Điểm vô cực
        if curve is None:
            self.curve = self.x = self.y = None
            return
        self.curve = curve
        #Đảm bảo x, y thuộc trường F_p
        self.x = int(x) % curve.p
        self.y = int(y) % curve.p
        #Kiểm tra điểm hợp lệ
        if validate and not curve.is_valid_point(x, y):
            raise ValueError(f"Point ({x}, {y}) is not on curve {curve}")
    
    def __str__(self):
        #Hiển thị điểm
        if self == INFINITY:
            return "INF" #Điểm vô cực
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other):
        #So sánh 2 điểm
        if isinstance(other, Point):
            return self.curve == other.curve and self.x == other.x and self.y == other.y
        return None
    
    def __add__(self, other):
        #Định nghĩa phép cộng
        if not isinstance(other, Point):
            return None
        
        #Cộng với điểm vô cực
        if other == INFINITY:
            return self
        if self == INFINITY:
            return other
        
        p = self.curve.p

        #x1 == x2
        if self.x == other.x:
            #y1 = -y2
            if (self.y + other.y) % p == 0:
                return INFINITY
            else:
                return self.double()
            
        #Tính hệ số trong công thức s = (y2 - y1)/(x2 - x1) mod p
        s = ((other.y - self.y)*pow(other.x - self.x, -1, p)) % p

        #Tính tọa độ điểm
        x3 = (s*s - self.x - other.x) % p
        y3 = (s*(self.x - x3) - self.y) % p

        return Point(self.curve, x3, y3, validate=False)
    
    def __neg__(self):
        # Phản điểm: (x, -y mod p)
        return Point(self.curve, self.x, self.curve.p - self.y, validate=False)
    
    def __mul__(self, e):
        #Nhân điểm
        if e == 0 or self == INFINITY:
            return INFINITY
        if e < 0:
            return (-self) * (-e)
        
        # Thuật toán lũy thừa nhị phân để tăng hiệu suất
        ret = self * (e // 2)
        ret = ret.double()
        if e % 2 == 1:
            ret = ret + self
        return ret
    
    def __rmul__(self, other):
        # Hỗ trợ phép nhân: e * P
        return self * other
    
    def double(self):
        # Phép nhân đôi điểm: P + P
        if self == INFINITY:
            return INFINITY

        p = self.curve.p
        a = self.curve.a

        # Tính hệ số λ = (3x^2 + a)/(2y) mod p
        l = ((3 * self.x * self.x + a) * pow(2 * self.y, -1, p)) % p

        # Tính tọa độ điểm mới
        x3 = (l * l - 2 * self.x) % p
        y3 = (l * (self.x - x3) - self.y) % p

        return Point(self.curve, x3, y3, validate=False)

# Khai báo điểm vô cực - đơn vị cộng trên đường cong elliptic
INFINITY = Point(None, None, None)
            
        
    

        