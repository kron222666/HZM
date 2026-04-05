# quick_test.py
from hzm import HierZero

a = HierZero(10)
b = HierZero(0, level=2)
print(a / b)  # должно быть ∞_3
print(a * b)  # 0_2
print(HierZero(0, level=1, is_inf=True) ** 2)  # ∞_2
