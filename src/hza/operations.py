from .core import HierZero

# =============================================
# Основные арифметические операции для HZM
# =============================================

def add(a, b):
    """Сложение"""
    if not isinstance(a, HierZero):
        a = HierZero(a)
    if not isinstance(b, HierZero):
        b = HierZero(b)

    # Случай с ⊥
    if a.is_perp or b.is_perp:
        return HierZero(0, 0, False, 1).perp()

    # Обычные числа
    if a.level == 0 and b.level == 0 and not a.is_inf and not b.is_inf:
        return HierZero(a.value + b.value)

    # Нуль + что угодно
    if a.level > 0:
        return a
    if b.level > 0:
        return b

    # Бесконечность + бесконечность
    if a.is_inf and b.is_inf:
        if a.sign == b.sign:
            return HierZero(0, min(a.level, b.level), True, a.sign)
        else:
            return HierZero(0, 0, False, 1).perp()  # ∞ - ∞ = ⊥

    # Бесконечность + число
    if a.is_inf:
        return a
    if b.is_inf:
        return b

    # Нули разных уровней
    if a.level > 0 and b.level > 0:
        return HierZero(0, min(a.level, b.level))

    return HierZero(a.value + b.value)

def sub(a, b):
    """Вычитание: a - b = a + (-b)"""
    if not isinstance(b, HierZero):
        b = HierZero(b)
    neg_b = HierZero(b.value, b.level, b.is_inf, -b.sign)
    return add(a, neg_b)

def mul(a, b):
    """Умножение"""
    if not isinstance(a, HierZero):
        a = HierZero(a)
    if not isinstance(b, HierZero):
        b = HierZero(b)

    if a.is_perp or b.is_perp:
        return HierZero(0, 0, False, 1).perp()

    # Нуль × что угодно = нуль
    if a.level > 0:
        return HierZero(0, a.level + b.level if b.level > 0 else a.level)
    if b.level > 0:
        return HierZero(0, b.level + a.level if a.level > 0 else b.level)

    # ∞ × ∞ = ∞
    if a.is_inf and b.is_inf:
        return HierZero(0, a.level + b.level, True, a.sign * b.sign)

    # ∞ × число
    if a.is_inf:
        return HierZero(0, a.level, True, a.sign * b.sign)
    if b.is_inf:
        return HierZero(0, b.level, True, a.sign * b.sign)

    # Обычное умножение
    return HierZero(a.value * b.value)

def div(a, b):
    """Деление a / b"""
    if not isinstance(a, HierZero):
        a = HierZero(a)
    if not isinstance(b, HierZero):
        b = HierZero(b)

    if b.is_perp or a.is_perp:
        return HierZero(0, 0, False, 1).perp()

    # Деление на нуль
    if b.level > 0:
        return HierZero(0, b.level + 1, True, a.sign)

    # Число / ∞ = 0
    if b.is_inf:
        return HierZero(0, b.level)

    # ∞ / число
    if a.is_inf:
        return HierZero(0, a.level, True, a.sign)

    # Обычное деление
    if b.value == 0:
        return HierZero(0, 1, True, a.sign)  # деление на обычный 0
    return HierZero(a.value / b.value)

def power(a, b):
    """Возведение в степень a^b"""
    if not isinstance(a, HierZero):
        a = HierZero(a)
    if not isinstance(b, HierZero):
        b = HierZero(b)

    if a.is_perp or b.is_perp:
        return HierZero(0, 0, False, 1).perp()

    # a^0 = 1
    if b.level == 0 and not b.is_inf and b.value == 0:
        return HierZero(1.0)

    # 0_k ^ n (n > 0)
    if a.level > 0 and not b.is_inf and b.level == 0:
        if b.value > 0:
            return HierZero(0, int(a.level * b.value))
        else:
            return HierZero(0, int(a.level * abs(b.value)), True, a.sign)

    # ∞_k ^ n
    if a.is_inf and not b.is_inf and b.level == 0:
        if b.value > 0:
            return HierZero(0, int(a.level * b.value), True, a.sign)
        else:
            return HierZero(0, int(a.level * abs(b.value)))

    # 0_k ^ ∞_m
    if a.level > 0 and b.is_inf:
        return HierZero(0, a.level + b.level)

    # ∞_k ^ ∞_m
    if a.is_inf and b.is_inf:
        return HierZero(0, a.level + b.level, True, a.sign)

    # Обычное возведение в степень
    return HierZero(a.value ** b.value)

def root(a, n):
    """Извлечение корня n-ой степени из a"""
    if not isinstance(a, HierZero):
        a = HierZero(a)
    if not isinstance(n, HierZero):
        n = HierZero(n)

    if n.level == 0 and n.value <= 0:
        return HierZero(0, 0, False, 1).perp()  # корень из отрицательного или нулевого порядка

    if a.level > 0:
        return HierZero(0, int((a.level + n.level - 1) // n.level))  # округление вверх

    if a.is_inf:
        return HierZero(0, int((a.level + n.level - 1) // n.level), True, a.sign)

    # Обычный корень
    return HierZero(a.value ** (1.0 / n.value))

# Удобные алиасы
def neg(x):
    """Унарный минус"""
    if not isinstance(x, HierZero):
        x = HierZero(x)
    return HierZero(x.value, x.level, x.is_inf, -x.sign)
