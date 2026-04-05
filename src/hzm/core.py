from __future__ import annotations
from typing import Union
import math

Number = Union[int, float, "HierZero"]


class HierZero:
    def __init__(self, level: int = 0, value: float = 0.0, is_inf: bool = False,
                 sign: int = 1, is_perp: bool = False):
        self.level = level
        self.value = value
        self.is_inf = is_inf
        self.sign = sign
        self.is_perp = is_perp

        if is_perp:
            self.level = -1
            self.value = float('nan')
        elif not is_inf and level == 0:
            self.value = float(value)
        elif not is_inf and level > 0:
            self.value = 0.0
        elif is_inf and level >= 1:
            self.value = math.inf if sign == 1 else -math.inf
        else:
            raise ValueError("Некорректная комбинация параметров HZM")

    @classmethod
    def real(cls, x: float) -> HierZero:
        return cls(level=0, value=x, is_inf=False, sign=1 if x >= 0 else -1)

    @classmethod
    def zero(cls, level: int = 1) -> HierZero:
        if level < 1:
            raise ValueError("Уровень нуля должен быть ≥ 1")
        return cls(level=level, value=0.0, is_inf=False)

    @classmethod
    def infinity(cls, level: int = 1, sign: int = 1) -> HierZero:
        if level < 1:
            raise ValueError("Уровень бесконечности должен быть ≥ 1")
        return cls(level=level, is_inf=True, sign=sign)

    @classmethod
    def perp(cls) -> HierZero:
        return cls(is_perp=True)

    def __repr__(self) -> str:
        if self.is_perp:
            return "⊥"
        if self.is_inf:
            sign_str = "" if self.sign == 1 else "-"
            return f"{sign_str}∞_{self.level}"
        if self.level == 0:
            # Для целых чисел не показываем .0
            if self.value == int(self.value):
                return str(int(self.value))
            return str(self.value)
        return f"0_{self.level}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HierZero):
            return False
        # ⊥ равен только ⊥
        if self.is_perp or other.is_perp:
            return self.is_perp == other.is_perp
        # Сравнение обычных чисел с допуском
        if self.level == 0 and other.level == 0:
            return abs(self.value - other.value) < 1e-12
        # Иерархические элементы должны совпадать по всем атрибутам
        return (self.level == other.level and
                self.is_inf == other.is_inf and
                self.sign == other.sign)

    # ---------- Арифметические операторы ----------
    def __add__(self, other: Number) -> HierZero:
        from .operations import _add
        return _add(self, _to_hz(other))

    def __radd__(self, other: Number) -> HierZero:
        return self + other

    def __sub__(self, other: Number) -> HierZero:
        from .operations import _sub
        return _sub(self, _to_hz(other))

    def __rsub__(self, other: Number) -> HierZero:
        return _sub(_to_hz(other), self)

    def __mul__(self, other: Number) -> HierZero:
        from .operations import _mul
        return _mul(self, _to_hz(other))

    def __rmul__(self, other: Number) -> HierZero:
        return self * other

    def __truediv__(self, other: Number) -> HierZero:
        from .operations import _div
        return _div(self, _to_hz(other))

    def __rtruediv__(self, other: Number) -> HierZero:
        return _div(_to_hz(other), self)

    def __pow__(self, exponent: Number) -> HierZero:
        from .operations import _pow
        return _pow(self, _to_hz(exponent))

    def __rpow__(self, base: Number) -> HierZero:
        return _pow(_to_hz(base), self)

    def __neg__(self) -> HierZero:
        if self.is_perp:
            return self
        if self.is_inf:
            return HierZero.infinity(self.level, sign=-self.sign)
        if self.level == 0:
            return HierZero.real(-self.value)
        return HierZero.zero(self.level)

    def __abs__(self) -> HierZero:
        if self.is_perp:
            return self
        if self.is_inf:
            return HierZero.infinity(self.level, sign=1)
        if self.level == 0:
            return HierZero.real(abs(self.value))
        return self


def _to_hz(x: Number) -> HierZero:
    if isinstance(x, HierZero):
        return x
    return HierZero.real(float(x))
