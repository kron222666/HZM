import math
from .core import HierZero

def add(a, b):
    return HierZero(a) + HierZero(b)

def sub(a, b):
    return HierZero(a) - HierZero(b)

def mul(a, b):
    return HierZero(a) * HierZero(b)

def div(a, b):
    return HierZero(a) / HierZero(b)

def power(a, b):
    return HierZero(a) ** HierZero(b)

def root(x, n):
    """Корень n-й степени из x (x ** (1/n))"""
    x = HierZero(x)
    n = HierZero(n)
    if n.level == 0 and n.value <= 0:
        return HierZero.perp()
    if x.is_inf and x.sign < 0 and n.level == 0 and (int(n.value) % 2 == 0):
        return HierZero.perp()
    return x ** (HierZero(1.0) / n)

def log(base, arg):
    """Логарифм по основанию base от arg (log_base(arg))"""
    base = HierZero(base)
    arg = HierZero(arg)

    if base.is_perp or arg.is_perp:
        return HierZero.perp()

    # log_1 a = ⊥
    if base.level == 0 and not base.is_inf and base.value == 1:
        return HierZero.perp()

    # Обычные числа
    if (base.level == 0 and not base.is_inf and base.value > 0 and base.value != 1 and
        arg.level == 0 and not arg.is_inf and arg.value > 0):
        return HierZero(math.log(arg.value, base.value))

    # log_{0_k} a = 0_k  (a > 0 обычное)
    if base.level > 0 and arg.level == 0 and not arg.is_inf and arg.value > 0 and arg.value != 1:
        return HierZero(0, base.level)

    # log_{0_k} 0_m = ⊥
    if base.level > 0 and arg.level > 0:
        return HierZero.perp()

    # log_{0_k} ∞_m = -∞_k
    if base.level > 0 and arg.is_inf:
        return HierZero(0, base.level, is_inf=True, sign=-1)

    # log_{∞_k} a = 0_k
    if base.is_inf and arg.level == 0 and not arg.is_inf and arg.value > 0 and arg.value != 1:
        return HierZero(0, base.level)

    # log_{∞_k} 0_m = ⊥
    if base.is_inf and arg.level > 0:
        return HierZero.perp()

    # log_{∞_k} ∞_m
    if base.is_inf and arg.is_inf:
        if base.level == arg.level:
            return HierZero.perp()
        else:
            # молодой уровень доминирует (∞_{min(k,m)})
            return HierZero(0, min(base.level, arg.level), is_inf=True, sign=1)

    return HierZero.perp()
