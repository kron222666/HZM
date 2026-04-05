from .core import HierZero

def add(a, b):
    if not isinstance(a, HierZero):
        a = HierZero(a)
    if not isinstance(b, HierZero):
        b = HierZero(b)
    return a + b

def sub(a, b):
    if not isinstance(a, HierZero):
        a = HierZero(a)
    if not isinstance(b, HierZero):
        b = HierZero(b)
    return a - b

def mul(a, b):
    if not isinstance(a, HierZero):
        a = HierZero(a)
    if not isinstance(b, HierZero):
        b = HierZero(b)
    return a * b

def div(a, b):
    if not isinstance(a, HierZero):
        a = HierZero(a)
    if not isinstance(b, HierZero):
        b = HierZero(b)
    return a / b

def power(a, b):
    if not isinstance(a, HierZero):
        a = HierZero(a)
    if not isinstance(b, HierZero):
        b = HierZero(b)
    return a ** b

def root(a, n):
    # корень n-й степени: a ** (1/n) с округлением уровня
    if not isinstance(a, HierZero):
        a = HierZero(a)
    if not isinstance(n, (int, float, HierZero)):
        n = HierZero(n)
    if isinstance(n, HierZero):
        n_val = n.value if n.level == 0 and not n.is_inf else 1
    else:
        n_val = float(n)
    if n_val <= 0:
        return HierZero(0).perp()
    # Для нулей и бесконечностей используем a ** (1/n)
    return a ** HierZero(1.0 / n_val)

def neg(x):
    if not isinstance(x, HierZero):
        x = HierZero(x)
    return -x
