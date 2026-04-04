class HierZero:
    """
    Основной класс Иерархической алгебры нулей (HZM)
    Поддерживает все операции, которые мы вывели.
    """
    def __init__(self, value=0.0, level=0, is_inf=False, sign=1):
        self.value = float(value)
        self.level = max(0, int(level))          # уровень не может быть отрицательным
        self.is_inf = bool(is_inf)
        self.sign = 1 if sign >= 0 else -1
        self.is_perp = False

    def __repr__(self):
        if self.is_perp:
            return "⊥"
        if self.is_inf:
            sign_str = "-" if self.sign < 0 else ""
            return f"{sign_str}∞_{self.level}"
        if self.level > 0:
            return f"0_{self.level}"
        return f"{self.value:.6f}"

    def __str__(self):
        return self.__repr__()

    # ====================== СЛОЖЕНИЕ ======================
    def __add__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)

        if self.is_perp or other.is_perp:
            return self.perp()

        # Нуль побеждает всё
        if self.level > 0:
            return self
        if other.level > 0:
            return other

        # ∞ + ∞
        if self.is_inf and other.is_inf:
            if self.sign == other.sign:
                return HierZero(0, min(self.level, other.level), True, self.sign)
            else:
                return self.perp()

        # ∞ + число
        if self.is_inf:
            return self
        if other.is_inf:
            return other

        # Обычное сложение
        return HierZero(self.value + other.value)

    def __radd__(self, other):
        return self.__add__(other)

    # ====================== ВЫЧИТАНИЕ ======================
    def __sub__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)

        if other.level > 0:
            return self

        neg_other = HierZero(other.value, other.level, other.is_inf, -other.sign)
        return self.__add__(neg_other)

    def __rsub__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)
        # other - 0_k = other
        if self.level > 0:
            return other
        return other.__sub__(self)

    # ====================== УМНОЖЕНИЕ ======================
    def __mul__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)

        if self.is_perp or other.is_perp:
            return self.perp()

        if self.level > 0:
            return HierZero(0, self.level + (other.level if other.level > 0 else 0))
        if other.level > 0:
            return HierZero(0, other.level + (self.level if self.level > 0 else 0))

        if self.is_inf and other.is_inf:
            return HierZero(0, self.level + other.level, True, self.sign * other.sign)

        if self.is_inf:
            return HierZero(0, self.level, True, self.sign * other.sign)
        if other.is_inf:
            return HierZero(0, other.level, True, self.sign * other.sign)

        return HierZero(self.value * other.value)

    def __rmul__(self, other):
        return self.__mul__(other)

    # ====================== ДЕЛЕНИЕ ======================
    def __truediv__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)

        if other.is_perp or self.is_perp:
            return self.perp()

        # a / 0_k = sign(a) * ∞_{k+1}
        if other.level > 0:
            return HierZero(0, other.level + 1, True, self.sign)

        # a / ∞_k = 0_k
        if other.is_inf:
            return HierZero(0, other.level)

        # ∞_k / число
        if self.is_inf:
            return HierZero(0, self.level, True, self.sign)

        if other.value == 0:
            return HierZero(0, 1, True, self.sign)

        return HierZero(self.value / other.value)

    def __rtruediv__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)
        return other.__truediv__(self)

    # ====================== СТЕПЕНЬ ======================
    def __pow__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)

        if self.is_perp or other.is_perp:
            return self.perp()

        # 0_k ^ n (n > 0)
        if self.level > 0 and not other.is_inf and other.level == 0:
            if other.value > 0:
                return HierZero(0, int(self.level * other.value))
            else:  # отрицательная степень
                return HierZero(0, int(self.level * abs(other.value)), True, self.sign)

        # ∞_k ^ n
        if self.is_inf and not other.is_inf and other.level == 0:
            if other.value > 0:
                return HierZero(0, int(self.level * other.value), True, self.sign)
            else:
                return HierZero(0, int(self.level * abs(other.value)))

        # 0_k ^ ∞_m
        if self.level > 0 and other.is_inf:
            return HierZero(0, self.level + other.level)

        # ∞_k ^ ∞_m
        if self.is_inf and other.is_inf:
            return HierZero(0, self.level + other.level, True, self.sign)

        # Обычное возведение в степень
        return HierZero(self.value ** other.value)

    # ====================== УНАРНЫЙ МИНУС ======================
    def __neg__(self):
        return HierZero(self.value, self.level, self.is_inf, -self.sign)

    # ====================== Поглощающий элемент ======================
    def perp(self):
        """Создаёт ⊥"""
        obj = HierZero(0)
        obj.is_perp = True
        return obj
