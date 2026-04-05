from __future__ import annotations
from .core import HierZero, Number, _to_hz
import math


# ---------- Сложение (таблица из документа) ----------
def _add(a: HierZero, b: HierZero) -> HierZero:
    if a.is_perp or b.is_perp:
        return HierZero.perp()
    # Оба обычные
    if a.level == 0 and b.level == 0:
        return HierZero.real(a.value + b.value)
    # a - обычное, b - нуль
    if a.level == 0 and not b.is_inf:
        return b
    # a - обычное, b - бесконечность
    if a.level == 0 and b.is_inf:
        return b
    # a - нуль, b - обычное
    if not a.is_inf and b.level == 0:
        return a
    # a - нуль, b - бесконечность
    if not a.is_inf and b.is_inf:
        return a
    # a - бесконечность, b - обычное
    if a.is_inf and b.level == 0:
        return a
    # a - бесконечность, b - нуль
    if a.is_inf and not b.is_inf:
        return b
    # оба нуля: 0ₖ + 0ₘ = 0_min(k,m)
    if not a.is_inf and not b.is_inf:
        return HierZero.zero(min(a.level, b.level))
    # оба бесконечности одного знака
    if a.is_inf and b.is_inf:
        if a.sign == b.sign:
            return HierZero.infinity(min(a.level, b.level), sign=a.sign)
        else:
            if a.level == b.level:
                return HierZero.perp()
            winner = a if a.level < b.level else b
            return HierZero.infinity(winner.level, sign=winner.sign)
    return HierZero.perp()


def _sub(a: HierZero, b: HierZero) -> HierZero:
    return _add(a, -b)


# ---------- Умножение ----------
def _mul(a: HierZero, b: HierZero) -> HierZero:
    if a.is_perp or b.is_perp:
        return HierZero.perp()
    # Обычные числа
    if a.level == 0 and b.level == 0:
        return HierZero.real(a.value * b.value)
    # Обычное * нуль
    if a.level == 0 and not b.is_inf:
        return b
    if not a.is_inf and b.level == 0:
        return a
    # Обычное * бесконечность
    if a.level == 0 and b.is_inf:
        sign = 1 if (a.value >= 0) == (b.sign == 1) else -1
        return HierZero.infinity(b.level, sign=sign)
    if a.is_inf and b.level == 0:
        sign = 1 if (a.sign == 1) == (b.value >= 0) else -1
        return HierZero.infinity(a.level, sign=sign)
    # Нуль * нуль
    if not a.is_inf and not b.is_inf:
        return HierZero.zero(a.level + b.level)
    # Нуль * бесконечность
    if not a.is_inf and b.is_inf:
        return HierZero.zero(a.level + b.level)
    if a.is_inf and not b.is_inf:
        return HierZero.zero(a.level + b.level)
    # Бесконечность * бесконечность
    if a.is_inf and b.is_inf:
        sign = 1 if a.sign == b.sign else -1
        return HierZero.infinity(a.level + b.level, sign=sign)
    return HierZero.perp()


# ---------- Деление ----------
def _div(a: HierZero, b: HierZero) -> HierZero:
    if a.is_perp or b.is_perp:
        return HierZero.perp()
    # a / обычное (≠0)
    if b.level == 0 and abs(b.value) > 1e-12:
        if a.level == 0:
            return HierZero.real(a.value / b.value)
        if not a.is_inf:  # 0ₖ / число = 0ₖ
            return a
        if a.is_inf:
            sign = 1 if a.sign == (b.value > 0) else -1
            return HierZero.infinity(a.level, sign=sign)
    # a / 0ₖ (k≥1)
    if not b.is_inf and b.level >= 1:
        if a.level == 0:
            sign = 1 if a.value >= 0 else -1
            return HierZero.infinity(b.level + 1, sign=sign)
        if not a.is_inf:  # 0ₘ / 0ₖ = 0_{max(m,k)+1}
            return HierZero.zero(max(a.level, b.level) + 1)
        if a.is_inf:  # ∞ₘ / 0ₖ = ∞_{m+k+1}
            return HierZero.infinity(a.level + b.level + 1, sign=a.sign)
    # a / ∞ₖ
    if b.is_inf:
        if a.level == 0:
            return HierZero.zero(b.level)
        if not a.is_inf:  # 0ₘ / ∞ₖ = 0_{m+k}
            return HierZero.zero(a.level + b.level)
        if a.is_inf:  # ∞ₘ / ∞ₖ
            if a.level == b.level:
                return HierZero.perp()
            min_level = min(a.level, b.level)
            sign = 1 if a.sign == b.sign else -1
            return HierZero.infinity(min_level, sign=sign)
    return HierZero.perp()


# ---------- Возведение в степень ----------
def _pow(base: HierZero, exp: HierZero) -> HierZero:
    if base.is_perp or exp.is_perp:
        return HierZero.perp()
    # Обычные числа
    if base.level == 0 and exp.level == 0:
        return HierZero.real(base.value ** exp.value)
    # a ** 0ₖ = 1 (при a≠0)
    if not exp.is_inf and exp.level >= 1:
        if base.level == 0 and abs(base.value) > 1e-12:
            return HierZero.real(1.0)
        if not base.is_inf:  # 0ₘ ** 0ₖ = 1
            return HierZero.real(1.0)
        if base.is_inf:  # ∞ₘ ** 0ₖ = 1
            return HierZero.real(1.0)
    # 0ₖ ** n (n целое положительное)
    if not base.is_inf and base.level >= 1 and exp.level == 0:
        n = exp.value
        if n > 0 and abs(n - round(n)) < 1e-12:
            return HierZero.zero(base.level * int(n))
        if n < 0:
            m = int(abs(n))
            return HierZero.infinity((base.level + 1) * m, sign=1)
    # 0ₖ ** ∞ₘ = 0_{k+m}
    if not base.is_inf and base.level >= 1 and exp.is_inf:
        return HierZero.zero(base.level + exp.level)
    # ∞ₖ ** n (n целое)
    if base.is_inf and exp.level == 0:
        n = exp.value
        if n > 0:
            return HierZero.infinity(base.level * int(n), sign=base.sign if n % 2 == 0 else base.sign)
        if n < 0:
            m = int(abs(n))
            return HierZero.zero(base.level * m)
    # ∞ₖ ** ∞ₘ = ∞_{k+m}
    if base.is_inf and exp.is_inf:
        return HierZero.infinity(base.level + exp.level, sign=base.sign)
    return HierZero.perp()


# ---------- Корень n-й степени (функция, не перегрузка) ----------
def sqrt(x: Number, n: int = 2) -> HierZero:
    a = _to_hz(x)
    if a.is_perp:
        return HierZero.perp()
    if n == 0:
        return HierZero.perp()
    # Обычное положительное
    if a.level == 0 and a.value >= 0:
        return HierZero.real(a.value ** (1.0 / n))
    # Обычное отрицательное при нечётном n
    if a.level == 0 and a.value < 0 and n % 2 == 1:
        return HierZero.real(-((-a.value) ** (1.0 / n)))
    if a.level == 0 and a.value < 0 and n % 2 == 0:
        return HierZero.perp()
    # Корень из 0ₖ
    if not a.is_inf and a.level >= 1:
        new_level = (a.level + n - 1) // n  # ceil(k/n)
        return HierZero.zero(new_level)
    # Корень из ∞ₖ
    if a.is_inf:
        new_level = (a.level + n - 1) // n
        return HierZero.infinity(new_level, sign=a.sign if n % 2 == 1 else 1)
    return HierZero.perp()


# ---------- Логарифм ----------
def log(arg: Number, base: Number = None) -> HierZero:
    a = _to_hz(arg)
    if base is None:
        b = HierZero.real(math.e)
    else:
        b = _to_hz(base)

    if a.is_perp or b.is_perp:
        return HierZero.perp()
    # log(1) = 0
    if (a.level == 0 and abs(a.value - 1.0) < 1e-12) or \
            (not a.is_inf and a.level == 0 and a.value == 1.0):
        return HierZero.real(0.0)
    # Основание 1 → ⊥
    if b.level == 0 and abs(b.value - 1.0) < 1e-12:
        return HierZero.perp()
    # Основание 0ₖ, аргумент >0 обычный
    if not b.is_inf and b.level >= 1 and a.level == 0 and a.value > 0 and abs(a.value - 1) > 1e-12:
        return HierZero.zero(b.level)
    # Основание ∞ₖ, аргумент >0 обычный
    if b.is_inf and a.level == 0 and a.value > 0 and abs(a.value - 1) > 1e-12:
        return HierZero.zero(b.level)
    # log_b(0ₖ) = -∞ₖ
    if not a.is_inf and a.level >= 1 and b.level == 0 and b.value > 0 and b.value != 1:
        return HierZero.infinity(a.level, sign=-1)
    # log_b(∞ₖ) = +∞ₖ
    if a.is_inf and b.level == 0 and b.value > 0 and b.value != 1:
        return HierZero.infinity(a.level, sign=1)
    # log_∞ₖ(∞ₘ)
    if b.is_inf and a.is_inf:
        if b.level == a.level:
            return HierZero.perp()
        else:
            diff = a.level - b.level
            if diff > 0:
                return HierZero.infinity(diff, sign=1)
            else:
                return HierZero.zero(-diff)
    # log_0ₖ(0ₘ) → ⊥
    if not b.is_inf and b.level >= 1 and not a.is_inf and a.level >= 1:
        return HierZero.perp()
    return HierZero.perp()
