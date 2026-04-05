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
    """
    Корень n-й степени: x ** (1/n)
    n может быть числом или HierZero
    """
    x = HierZero(x)
    n = HierZero(n)
    if n.level == 0 and n.value <= 0:
        return HierZero.perp()
    # Для корня из отрицательной бесконечности с чётной степенью -> ⊥
    if x.is_inf and x.sign < 0 and n.level == 0 and n.value % 2 == 0:
        return HierZero.perp()
    # Для корня из нуля или бесконечности: используем степень
    return x ** (HierZero(1.0) / n)

def log(base, arg):
    """
    Логарифм по основанию base от arg.
    Реализует таблицу логарифмов HZM.
    """
    base = HierZero(base)
    arg = HierZero(arg)

    if base.is_perp or arg.is_perp:
        return HierZero.perp()

    # log_1 a = ⊥
    if base.level == 0 and not base.is_inf and base.value == 1:
        return HierZero.perp()

    # log_{0_k} a = 0_k (для обычного положительного a)
    if base.level > 0 and arg.level == 0 and not arg.is_inf and arg.value > 0 and arg.value != 1:
        return HierZero(0, base.level)

    # log_{0_k} 0_m = ⊥
    if base.level > 0 and arg.level > 0:
        return HierZero.perp()

    # log_{0_k} ∞_m = -∞_k
    if base.level > 0 and arg.is_inf:
        return HierZero(0, base.level, is_inf=True, sign=-1)

    # log_{∞_k} a = 0_k (для обычного положительного a)
    if base.is_inf and arg.level == 0 and not arg.is_inf and arg.value > 0 and arg.value != 1:
        return HierZero(0, base.level)

    # log_{∞_k} 0_m = ⊥ (по таблице)
    if base.is_inf and arg.level > 0:
        return HierZero.perp()

    # log_{∞_k} ∞_m
    if base.is_inf and arg.is_inf:
        if base.level == arg.level:
            return HierZero.perp()
        else:
            # По таблице: результат ∞_{m-k} (если m>k) или 0_{...}? Упростим: 0_{min(k,m)}? 
            # В вашей таблице указано ∞_{m-k} для k≠m. Реализуем так:
            if arg.level > base.level:
                return HierZero(0, arg.level - base.level, is_inf=True, sign=1)
            else:
                # если arg.level < base.level: результат 0_{base.level - arg.level}? Не определено. 
                # Пока вернём 0_{min(k,m)} как в ранних версиях.
                return HierZero(0, min(base.level, arg.level))

    # Обычный логарифм (base>0, base≠1, arg>0)
    if (base.level == 0 and not base.is_inf and base.value > 0 and base.value != 1 and
        arg.level == 0 and not arg.is_inf and arg.value > 0):
        import math
        return HierZero(math.log(arg.value, base.value))

    # Если ничего не подошло -> ⊥
    return HierZero.perp()
