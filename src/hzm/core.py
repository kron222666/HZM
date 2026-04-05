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

        # Автоматическое определение уровня (только для обычных чисел)
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

        # 0_k + 0_m = 0_{min(k,m)}
        if self.level > 0 and other.level > 0:
            return HierZero(0, min(self.level, other.level))

        # Глубокий нуль + что угодно = нуль
        if self.level > 0:
            return self
        if other.level > 0:
            return other

        # ∞ + ∞
        if self.is_inf and other.is_inf:
            if self.sign == other.sign:
                # одинаковые знаки → ∞_{min(level)}
                return HierZero(0, min(self.level, other.level), True, self.sign)
            else:
                # разные знаки: если уровни равны → ⊥, иначе → молодая бесконечность
                if self.level == other.level:
                    return self.perp()
                elif self.level < other.level:
                    return HierZero(0, self.level, True, self.sign)
                else:
                    return HierZero(0, other.level, True, other.sign)

        # ∞ + число (или число + ∞)
        if self.is_inf:
            return self
        if other.is_inf:
            return other

        # обычное сложение
        return HierZero(self.value + other.value)

    def __radd__(self, other):
        return self.__add__(other)

    # ====================== ВЫЧИТАНИЕ ======================
    def __sub__(self, other):
        if not isinstance(other, HierZero):
            other = HierZero(other)

        if self.is_perp or other.is_perp:
            return self.perp()

        # 0_k - 0_m = 0_{min(k,m)}
        if self.level > 0 and other.level > 0:
            return HierZero(0, min(self.level, other.level))

        # a - 0_k = a (число или бесконечность)
        if other.level > 0:
            return self

        # Для бесконечностей и чисел: a - b = a + (-b)
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
            return HierZero(0, self.level + other.level, True, self.sign * other.sign)

        # ∞ * число = ∞ (с соответствующим знаком)
        if self.is_inf:
            return HierZero(0, self.level, True, self.sign * other.sign)
        if other.is_inf:
            return HierZero(0, other.level, True, self.sign * other.sign)

        # обычное умножение
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

        # a / 0_k = ∞_{k+1}   (a — число или бесконечность)
        if other.level > 0:
            # Если числитель бесконечность: ∞_k / 0_m = ∞_{k+m+1}
            if self.is_inf:
                return HierZero(0, self.level + other.level + 1, True, self.sign)
            else:
                # Обычное число / 0_k = ∞_{k+1}
                return HierZero(0, other.level + 1, True, self.sign)

        # a / ∞_k = 0_k
        if other.is_inf:
            # 0_k / ∞_m = 0_{k+m}
            if self.level > 0:
                return HierZero(0, self.level + other.level)
            return HierZero(0, other.level)

        # ∞_k / число = ∞_k
        if self.is_inf:
            return HierZero(0, self.level, True, self.sign)

        # деление на вещественный ноль (обычный 0.0)
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

        # a^0 = 1
        if not other.is_inf and other.level == 0 and other.value == 0:
            return HierZero(1.0)

        # 0_k ^ n (n целое)
        if self.level > 0 and not other.is_inf and other.level == 0:
            # n > 0: 0_k^n = 0_{n*k}
            if other.value > 0:
                return HierZero(0, int(self.level * other.value))
            # n < 0: 0_k^n = ∞_{(k+1)*|n|}
            else:
                n = int(abs(other.value))
                return HierZero(0, (self.level + 1) * n, True, self.sign)

        # ∞_k ^ n (n целое)
        if self.is_inf and not other.is_inf and other.level == 0:
            # n > 0: ∞_k^n = ∞_{n*k}
            if other.value > 0:
                return HierZero(0, int(self.level * other.value), True, self.sign)
            # n < 0: ∞_k^n = 0_{k*|n|}
            else:
                n = int(abs(other.value))
                return HierZero(0, self.level * n)

        # 0_k ^ ∞_m = 0_{k+m}
        if self.level > 0 and other.is_inf:
            return HierZero(0, self.level + other.level)

        # ∞_k ^ ∞_m = ∞_{k+m}
        if self.is_inf and other.is_inf:
            return HierZero(0, self.level + other.level, True, self.sign)

        # Дробные показатели для нулей и бесконечностей (через корень)
        # Это общий случай: a ** (p/q) = корень степени q из a^p
        # Для упрощения используем логарифмическое округление
        if (self.level > 0 or self.is_inf) and not other.is_inf and other.level == 0 and other.value != int(other.value):
            # Дробный показатель
            from fractions import Fraction
            frac = Fraction(other.value).limit_denominator()
            p = frac.numerator
            q = frac.denominator
            if self.level > 0:
                # 0_k^(p/q) = 0_{ceil(k*p/q)}
                new_level = (self.level * p + q - 1) // q
                return HierZero(0, new_level)
            if self.is_inf:
                # ∞_k^(p/q) = ∞_{ceil(k*p/q)}
                new_level = (self.level * p + q - 1) // q
                return HierZero(0, new_level, True, self.sign)
        # Обычная степень
        return HierZero(self.value ** other.value)

    def __neg__(self):
        return HierZero(self.value, self.level, self.is_inf, -self.sign)

    def perp(self):
        obj = HierZero(0)
        obj.is_perp = True
        return obj
