import math

class HierZero:
    
    VANISHING_THRESHOLD = 1e-3
    EXPLODING_THRESHOLD = 1e3

    def __init__(self, value=0.0, level=0, is_inf=False, sign=1):
        self.value = float(value)
        self.level = max(0, int(level))
        self.is_inf = bool(is_inf)
        self.sign = 1 if sign >= 0 else -1
        self.is_perp = False

        # Автоматическое определение уровня
        if self.level == 0 and not self.is_inf and abs(self.value) > 0:
            abs_val = abs(self.value)
            if abs_val < self.VANISHING_THRESHOLD:
                self.level = max(1, int(-math.log10(abs_val)) // 2)
                self.value = 0.0
            elif abs_val > self.EXPLODING_THRESHOLD:
                self.level = max(1, int(math.log10(abs_val)) // 2)
                self.is_inf = True
                self.value = 0.0

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

        # Оба глубокие нули → 0_{min(k,m)}
        if self.level > 0 and other.level > 0:
            return HierZero(0, min(self.level, other.level))

        # Глубокий нуль (один) поглощает всё
        if self.level > 0:
            return self
        if other.level > 0:
            return other

        # Оба бесконечности
        if self.is_inf and other.is_inf:
            if self.sign == other.sign:
                return HierZero(0, min(self.level, other.level), True, self.sign)
            else:
                # Разные знаки: молодая бесконечность доминирует
                if self.level < other.level:
                    return HierZero(0, self.level, True, self.sign)
                elif other.level < self.level:
                    return HierZero(0, other.level, True, other.sign)
                else:
                    return self.perp()  # равные уровни → ⊥

        # Одна бесконечность
        if self.is_inf:
            return self
        if other.is_inf:
            return other

        # Обычные числа
        return HierZero(self.value + other.value)

    def __radd__(self, other):
        return self.__add__(other)

    # ====================== ВЫЧИТАНИЕ ======================
    def __sub__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)

        if self.is_perp or other.is_perp:
            return self.perp()

        # a - 0_k = a  (для обычного числа или бесконечности)
        if other.level > 0:
            if self.level == 0 and not self.is_inf:
                return self
            if self.is_inf:
                return self
            # 0_k - 0_m = 0_{min(k,m)}
            if self.level > 0:
                return HierZero(0, min(self.level, other.level))

        # Для всех остальных случаев: a - b = a + (-b)
        neg_other = HierZero(other.value, other.level, other.is_inf, -other.sign)
        return self.__add__(neg_other)

    def __rsub__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)
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

        # 0_k / 0_m = 0_{max(k,m)+1}
        if self.level > 0 and other.level > 0:
            return HierZero(0, max(self.level, other.level) + 1)

        # Деление на глубокий нуль
        if other.level > 0:
            # ∞_k / 0_m = ∞_{k+m+1}
            if self.is_inf:
                return HierZero(0, self.level + other.level + 1, True, self.sign)
            # a / 0_k = ∞_{k+1}  (a — число, 0 или обычный ноль)
            else:
                return HierZero(0, other.level + 1, True, self.sign)

        # Деление на бесконечность: a / ∞_k = 0_k
        if other.is_inf:
            return HierZero(0, other.level)

        # Деление бесконечности на число: ∞_k / a = ∞_k
        if self.is_inf:
            return HierZero(0, self.level, True, self.sign)

        # Деление на вещественный ноль (обычный 0.0)
        if other.value == 0 or abs(other.value) < 1e-10:
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

        if self.level > 0 and not other.is_inf and other.level == 0:
            if other.value > 0:
                return HierZero(0, int(self.level * other.value))
            else:
                return HierZero(0, int((self.level + 1) * abs(other.value)), True, self.sign)

        if self.is_inf and not other.is_inf and other.level == 0:
            if other.value > 0:
                return HierZero(0, int(self.level * other.value), True, self.sign)
            else:
                return HierZero(0, int(self.level * abs(other.value)))

        if self.level > 0 and other.is_inf:
            return HierZero(0, self.level + other.level)

        if self.is_inf and other.is_inf:
            return HierZero(0, self.level + other.level, True, self.sign)

        return HierZero(self.value ** other.value)

    # ====================== УНАРНЫЙ МИНУС ======================
    def __neg__(self):
        return HierZero(self.value, self.level, self.is_inf, -self.sign)

    # ====================== ПОГЛОЩАЮЩИЙ ЭЛЕМЕНТ ======================
    def perp(self):
        obj = HierZero(0)
        obj.is_perp = True
        return obj
