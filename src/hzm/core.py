import math

class HierZero:
    VANISHING_THRESHOLD = 1e-3
    EXPLODING_THRESHOLD = 1e3

    def __init__(self, value=0.0, level=0, is_inf=False, sign=1, is_perp=False):
        self.value = float(value)
        self.level = max(0, int(level))
        self.is_inf = bool(is_inf)
        self.sign = 1 if sign >= 0 else -1
        self.is_perp = bool(is_perp)

        if not self.is_perp and self.level == 0 and not self.is_inf and abs(self.value) > 0:
            abs_val = abs(self.value)
            if abs_val < self.VANISHING_THRESHOLD:
                self.level = max(1, int(-math.log10(abs_val)) // 2)
                self.value = 0.0
            elif abs_val > self.EXPLODING_THRESHOLD:
                self.level = max(1, int(math.log10(abs_val)) // 2)
                self.is_inf = True
                self.value = 0.0

    def copy(self):
        return HierZero(self.value, self.level, self.is_inf, self.sign, self.is_perp)

    @staticmethod
    def perp():
        return HierZero(is_perp=True)

    def __repr__(self):
        if self.is_perp:
            return "⊥"
        if self.is_inf:
            return f"{'-' if self.sign < 0 else ''}∞_{self.level}"
        if self.level > 0:
            return f"0_{self.level}"
        return f"{self.value:.6f}"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if not isinstance(other, HierZero):
            return False
        return (self.is_perp == other.is_perp and
                self.is_inf == other.is_inf and
                self.level == other.level and
                self.sign == other.sign and
                (self.value == other.value or (self.level == 0 and not self.is_inf)))

    # ========== Сложение ==========
    def __add__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)
        if self.is_perp or other.is_perp:
            return HierZero.perp()
        # 0_k + 0_m = 0_{min(k,m)}
        if self.level > 0 and other.level > 0:
            return HierZero(0, min(self.level, other.level))
        # глубокий нуль + что-то = нуль
        if self.level > 0:
            return self.copy()
        if other.level > 0:
            return other.copy()
        # ∞ + ∞
        if self.is_inf and other.is_inf:
            if self.sign == other.sign:
                return HierZero(0, min(self.level, other.level), is_inf=True, sign=self.sign)
            else:
                # разные знаки: если уровни равны -> ⊥, иначе молодая бесконечность
                if self.level == other.level:
                    return HierZero.perp()
                elif self.level < other.level:
                    return HierZero(0, self.level, is_inf=True, sign=self.sign)
                else:
                    return HierZero(0, other.level, is_inf=True, sign=other.sign)
        # ∞ + число = ∞
        if self.is_inf:
            return self.copy()
        if other.is_inf:
            return other.copy()
        # обычные числа
        return HierZero(self.value + other.value)

    def __radd__(self, other):
        return self.__add__(other)

    # ========== Вычитание ==========
    def __sub__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)
        if self.is_perp or other.is_perp:
            return HierZero.perp()
        # 0_k - 0_m = 0_{min(k,m)}
        if self.level > 0 and other.level > 0:
            return HierZero(0, min(self.level, other.level))
        # a - 0_k = a
        if other.level > 0:
            return self.copy()
        # для остальных: a - b = a + (-b)
        neg_other = HierZero(other.value, other.level, other.is_inf, -other.sign, other.is_perp)
        return self.__add__(neg_other)

    def __rsub__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)
        return other.__sub__(self)

    # ========== Умножение ==========
    def __mul__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)
        if self.is_perp or other.is_perp:
            return HierZero.perp()
        # 0_k * 0_m = 0_{k+m}
        if self.level > 0 and other.level > 0:
            return HierZero(0, self.level + other.level)
        # 0_k * ∞_m = 0_{k+m}
        if self.level > 0 and other.is_inf:
            return HierZero(0, self.level + other.level)
        if self.is_inf and other.level > 0:
            return HierZero(0, self.level + other.level)
        # ∞ * ∞ = ∞_{k+m}
        if self.is_inf and other.is_inf:
            return HierZero(0, self.level + other.level, is_inf=True, sign=self.sign * other.sign)
        # ∞ * число = ∞
        if self.is_inf:
            return HierZero(0, self.level, is_inf=True, sign=self.sign * (1 if other.sign >= 0 else -1))
        if other.is_inf:
            return HierZero(0, other.level, is_inf=True, sign=self.sign * other.sign)
        # обычное умножение
        return HierZero(self.value * other.value)

    def __rmul__(self, other):
        return self.__mul__(other)

    # ========== Деление ==========
    def __truediv__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)
        if self.is_perp or other.is_perp:
            return HierZero.perp()
        # 0_k / 0_m = 0_{max(k,m)+1}
        if self.level > 0 and other.level > 0:
            return HierZero(0, max(self.level, other.level) + 1)
        # деление на глубокий нуль
        if other.level > 0:
            if self.is_inf:
                # ∞_k / 0_m = ∞_{k+m+1}
                return HierZero(0, self.level + other.level + 1, is_inf=True, sign=self.sign)
            else:
                # a / 0_k = ∞_{k+1}
                return HierZero(0, other.level + 1, is_inf=True, sign=self.sign)
        # деление на бесконечность
        if other.is_inf:
            if self.level > 0:
                # 0_k / ∞_m = 0_{k+m}
                return HierZero(0, self.level + other.level)
            # число / ∞_k = 0_k
            return HierZero(0, other.level)
        # ∞ / число = ∞
        if self.is_inf:
            return HierZero(0, self.level, is_inf=True, sign=self.sign)
        # деление на вещественный ноль
        if other.value == 0 or abs(other.value) < 1e-10:
            return HierZero(0, 1, is_inf=True, sign=self.sign)
        return HierZero(self.value / other.value)

    def __rtruediv__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)
        return other.__truediv__(self)

    # ========== Степень ==========
    def __pow__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)
        if self.is_perp or other.is_perp:
            return HierZero.perp()
        # a^0 = 1
        if not other.is_inf and other.level == 0 and other.value == 0:
            return HierZero(1.0)
        # 0_k ^ n (n целое)
        if self.level > 0 and not other.is_inf and other.level == 0:
            n = other.value
            if n > 0:
                return HierZero(0, int(self.level * n))
            else:
                m = int(abs(n))
                return HierZero(0, (self.level + 1) * m, is_inf=True, sign=self.sign)
        # ∞_k ^ n (n целое)
        if self.is_inf and not other.is_inf and other.level == 0:
            n = other.value
            if n > 0:
                return HierZero(0, int(self.level * n), is_inf=True, sign=self.sign)
            else:
                m = int(abs(n))
                return HierZero(0, self.level * m)
        # 0_k ^ ∞_m = 0_{k+m}
        if self.level > 0 and other.is_inf:
            return HierZero(0, self.level + other.level)
        # ∞_k ^ ∞_m = ∞_{k+m}
        if self.is_inf and other.is_inf:
            return HierZero(0, self.level + other.level, is_inf=True, sign=self.sign)
        # обычная степень
        return HierZero(self.value ** other.value)

    def __neg__(self):
        return HierZero(self.value, self.level, self.is_inf, -self.sign, self.is_perp)
