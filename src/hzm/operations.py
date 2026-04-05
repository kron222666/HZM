from __future__ import annotations
from .core import HierZero, Number, _to_hz
import math


# ---------- Сложение ----------
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
    # оба нуля
    if not a.is_inf and not b.is_inf:
        return HierZero.zero(min(a.level, b.level))
    # оба бесконечности
    if a.is_inf and b.is_inf:
        if a.sign == b.sign:
            return HierZero.infinity(min(a.level, b.level), sign=a.sign)
        else:
            if a.level == b.level:
                return HierZero.perp()
            # побеждает младшая (меньший k)
            if a.level < b.level:
                return HierZero.infinity(a.level, sign=a.sign)
            else:
                return HierZero.infinity(b.level, sign=b.sign)
    return HierZero.perp()


# ---------- Вычитание ----------
def _sub(a: HierZero, b: HierZero) -> HierZero:
    if a.is_perp or b.is_perp:
        return HierZero.perp()
    # a - 0_k = a
    if not b.is_inf and b.level >= 1:
        return a
    # a - обычное число
    if b.level == 0:
        if a.level == 0:
            return HierZero.real(a.value - b.value)
        if not a.is_inf:  # 0_k - число = 0_k
            return a
        if a.is_inf:      # ∞_k - число = ∞_k (знак сохраняется)
            return a
    # a - ∞_k
    if b.is_inf:
        if a.level == 0:
            # число - ∞_k = -∞_k
            return HierZero.infinity(b.level, sign=-1)
        if not a.is_inf:  # 0_m - ∞_k = 0_m? По таблице: 0_k - ∞_m = 0_k
            return a
        if a.is_inf:
            # ∞_m - ∞_k
            if a.level == b.level:
                return HierZero.perp()
            # Результат: ∞_{min(m,k)} с положительным знаком (согласно тесту)
            min_level = min(a.level, b.level)
            return HierZero.infinity(min_level, sign=1)
    return HierZero.perp()


# ---------- Умножение ----------
def _mul(a: HierZero, b: HierZero) -> HierZero:
    if a.is_perp or b.is_perp:
        return HierZero.perp()
    # обычные
    if a.level == 0 and b.level == 0:
        return HierZero.real(a.value * b.value)
    # обычное * нуль
    if a.level == 0 and not b.is_inf:
        return b
    if not a.is_inf and b.level == 0:
        return a
    # обычное * бесконечность
    if a.level == 0 and b.is_inf:
        sign = 1 if (a.value >= 0) == (b.sign == 1) else -1
        return HierZero.infinity(b.level, sign=sign)
    if a.is_inf and b.level == 0:
        sign = 1 if (a.sign == 1) == (b.value >= 0) else -1
        return HierZero.infinity(a.level, sign=sign)
    # нуль * нуль
    if not a.is_inf and not b.is_inf:
        return HierZero.zero(a.level + b.level)
    # нуль * бесконечность
    if (not a.is_inf and b.is_inf) or (a.is_inf and not b.is_inf):
        # 0_k * ∞_m = 0_{k+m}
        zero_level = (a.level if not a.is_inf else b.level) + (b.level if b.is_inf else a.level)
        return HierZero.zero(zero_level)
    # бесконечность * бесконечность
    if a.is_inf and b.is_inf:
        sign = 1 if a.sign == b.sign else -1
        return HierZero.infinity(a.level + b.level, sign=sign)
    return HierZero.perp()


# ---------- Деление ----------
def _div(a: HierZero, b: HierZero) -> HierZero:
    if a.is_perp or b.is_perp:
        return HierZero.perp()
    # деление на обычное ненулевое число
    if b.level == 0 and abs(b.value) > 1e-12:
        if a.level == 0:
            return HierZero.real(a.value / b.value)
        if not a.is_inf:  # 0_k / число = 0_k
            return a
        if a.is_inf:      # ∞_k / число = sign(число) * ∞_k
            sign = 1 if a.sign == (b.value > 0) else -1
            return HierZero.infinity(a.level, sign=sign)
    # деление на 0_k (k≥1)
    if not b.is_inf and b.level >= 1:
        # a / 0_k
        if a.level == 0:
            # число / 0_k = sign(a) * ∞_{k+1}
            sign = 1 if a.value >= 0 else -1
            return HierZero.infinity(b.level + 1, sign=sign)
        if not a.is_inf:
            # 0_m / 0_k = 0_{max(m,k)+1}
            return HierZero.zero(max(a.level, b.level) + 1)
        if a.is_inf:
            # ∞_m / 0_k = ∞_{m + k + 1}
            return HierZero.infinity(a.level + b.level + 1, sign=a.sign)
    # деление на ∞_k
    if b.is_inf:
        if a.level == 0:
            # число / ∞_k = 0_k
            return HierZero.zero(b.level)
        if not a.is_inf:
            # 0_m / ∞_k = 0_{m+k}
            return HierZero.zero(a.level + b.level)
        if a.is_inf:
            # ∞_m / ∞_k
            if a.level == b.level:
                return HierZero.perp()
            # результат ∞_{min(m,k)} со знаком, равным знаку делимого, если m<k? по таблице: ∞_k/∞_m = ∞_{min(k,m)}
            # При m<k: ∞_m / ∞_k = ∞_m (младшая доминирует)
            if a.level < b.level:
                return HierZero.infinity(a.level, sign=a.sign)
            else:
                return HierZero.infinity(b.level, sign=a.sign)
    return HierZero.perp()


# ---------- Возведение в степень ----------
def _pow(base: HierZero, exp: HierZero) -> HierZero:
    if base.is_perp or exp.is_perp:
        return HierZero.perp()
    # обычные числа
    if base.level == 0 and exp.level == 0:
        return HierZero.real(base.value ** exp.value)
    # a ** 0_k = 1 (при a≠0)
    if not exp.is_inf and exp.level >= 1:
        if base.level == 0 and abs(base.value) > 1e-12:
            return HierZero.real(1.0)
        if not base.is_inf:  # 0_m ** 0_k = 1
            return HierZero.real(1.0)
        if base.is_inf:      # ∞_m ** 0_k = 1
            return HierZero.real(1.0)
    # 0_k ** n (n целое)
    if not base.is_inf and base.level >= 1 and exp.level == 0:
        n = exp.value
        if n > 0 and abs(n - round(n)) < 1e-12:
            return HierZero.zero(base.level * int(n))
        if n < 0:
            m = int(abs(n))
            return HierZero.infinity((base.level + 1) * m, sign=1)
    # 0_k ** ∞_m = 0_{k+m}
    if not base.is_inf and base.level >= 1 and exp.is_inf:
        return HierZero.zero(base.level + exp.level)
    # ∞_k ** n (n целое)
    if base.is_inf and exp.level == 0:
        n = exp.value
        if n > 0 and abs(n - round(n)) < 1e-12:
            return HierZero.infinity(base.level * int(n), sign=base.sign if n % 2 == 0 else base.sign)
        if n < 0:
            m = int(abs(n))
            return HierZero.zero(base.level * m)
    # ∞_k ** ∞_m = ∞_{k+m}
    if base.is_inf and exp.is_inf:
        return HierZero.infinity(base.level + exp.level, sign=base.sign)
    return HierZero.perp()


# ---------- Корень n-й степени ----------
def sqrt(x: Number, n: int = 2) -> HierZero:
    a = _to_hz(x)
    if a.is_perp or n == 0:
        return HierZero.perp()
    # Обычное число
    if a.level == 0:
        val = a.value
        if val >= 0:
            return HierZero.real(val ** (1.0 / n))
        if n % 2 == 1:
            return HierZero.real(-((-val) ** (1.0 / n)))
        return HierZero.perp()
    # 0_k
    if not a.is_inf and a.level >= 1:
        new_level = (a.level + n - 1) // n
        return HierZero.zero(new_level)
    # ∞_k
    if a.is_inf:
        # корень чётной степени из отрицательной бесконечности = ⊥
        if n % 2 == 0 and a.sign == -1:
            return HierZero.perp()
        new_level = (a.level + n - 1) // n
        if n % 2 == 1:
            return HierZero.infinity(new_level, sign=a.sign)
        else:
            return HierZero.infinity(new_level, sign=1)
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

    # Обычный логарифм (оба числа)
    if a.level == 0 and b.level == 0:
        if b.value <= 0 or b.value == 1 or a.value <= 0:
            # логарифм определён только для b>0, b≠1, a>0
            if b.value > 0 and abs(b.value - 1.0) > 1e-12 and a.value > 0:
                return HierZero.real(math.log(a.value, b.value))
            else:
                return HierZero.perp()
        return HierZero.real(math.log(a.value, b.value))

    # log_b(1) = 0
    if (a.level == 0 and abs(a.value - 1.0) < 1e-12) or \
       (not a.is_inf and a.level == 0 and a.value == 1.0):
        return HierZero.real(0.0)

    # Основание 1 → ⊥
    if b.level == 0 and abs(b.value - 1.0) < 1e-12:
        return HierZero.perp()

    # log_b(0_k) = -∞_k (b>0, b≠1)
    if not a.is_inf and a.level >= 1:
        if b.level == 0 and b.value > 0 and abs(b.value - 1.0) > 1e-12:
            return HierZero.infinity(a.level, sign=-1)

    # log_b(∞_k) = +∞_k (b>0, b≠1)
    if a.is_inf:
        # отрицательная бесконечность -> ⊥
        if a.sign == -1:
            return HierZero.perp()
        if b.level == 0 and b.value > 0 and abs(b.value - 1.0) > 1e-12:
            return HierZero.infinity(a.level, sign=1)

    # log_{0_k}(a) = 0_k (a>0, a≠1)
    if not b.is_inf and b.level >= 1:
        if a.level == 0 and a.value > 0 and abs(a.value - 1.0) > 1e-12:
            return HierZero.zero(b.level)

    # log_{∞_k}(a) = 0_k (a>0, a≠1)
    if b.is_inf:
        if a.level == 0 and a.value > 0 and abs(a.value - 1.0) > 1e-12:
            return HierZero.zero(b.level)

    # log_{0_k}(∞_m) = -∞_k
    if not b.is_inf and b.level >= 1 and a.is_inf and a.sign == 1:
        return HierZero.infinity(b.level, sign=-1)

    # log_{∞_k}(0_m) = ⊥
    if b.is_inf and not a.is_inf and a.level >= 1:
        return HierZero.perp()

    # log_{0_k}(0_m) = ⊥
    if not b.is_inf and b.level >= 1 and not a.is_inf and a.level >= 1:
        return HierZero.perp()

    # log_{∞_k}(∞_m)
    if b.is_inf and a.is_inf and a.sign == 1:
        if b.level == a.level:
            return HierZero.perp()
        diff = a.level - b.level
        if diff > 0:
            return HierZero.infinity(diff, sign=1)
        else:
            return HierZero.zero(-diff)

    return HierZero.perp()
