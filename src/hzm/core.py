from __future__ import annotations
from typing import Union
import math

Number = Union[int, float, "HierZero"]


class HierZero:
    """
    Элемент иерархической алгебры нулей (HZM).
    Атрибуты:
        level (int): уровень k (≥0). Для обычных чисел level=0.
        value (float): вещественное значение (используется только при level=0).
        is_inf (bool): True для иерархической бесконечности.
        sign (int): 1 для положительных, -1 для отрицательных.
        is_perp (bool): True для поглощающего элемента ⊥.
    """

    def __init__(self, level: int = 0, value: float = 0.0, is_inf: bool = False,
                 sign: int = 1, is_perp: bool = False):
        self.level = level
        self.value = value
        self.is_inf = is_inf
        self.sign = sign
        self.is_perp = is_perp

        # Нормализация
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
            return str(self.value)
        return f"0_{self.level}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HierZero):
            return False
        if self.is_perp or other.is_perp:
            return self.is_perp == other.is_perp
        return (self.level == other.level and
                self.is_inf == other.is_inf and
                self.sign == other.sign and
                abs(self.value - other.value) < 1e-12)

    # ---------- Арифметические операторы (вызывают функции из operations) ----------
    # Чтобы избежать циклических импортов, импортируем функции локально внутри методов
    def __add__(self, other: Number) -> HierZero:
        from .operations import _add
        return _add(self, _to_hz(other))

    def __radd__(self, other: Number) -> HierZero:
        from .operations import _add
        return _add(_to_hz(other), self)

    def __sub__(self, other: Number) -> HierZero:
        from .operations import _sub
        return _sub(self, _to_hz(other))

    def __rsub__(self, other: Number) -> HierZero:
        from .operations import _sub
        return _sub(_to_hz(other), self)

    def __mul__(self, other: Number) -> HierZero:
        from .operations import _mul
        return _mul(self, _to_hz(other))

    def __rmul__(self, other: Number) -> HierZero:
        from .operations import _mul
        return _mul(_to_hz(other), self)

    def __truediv__(self, other: Number) -> HierZero:
        from .operations import _div
        return _div(self, _to_hz(other))

    def __rtruediv__(self, other: Number) -> HierZero:
        from .operations import _div
        return _div(_to_hz(other), self)

    def __pow__(self, exponent: Number) -> HierZero:
        from .operations import _pow
        return _pow(self, _to_hz(exponent))

    def __rpow__(self, base: Number) -> HierZero:
        from .operations import _pow
        return _pow(_to_hz(base), self)

    def __neg__(self) -> HierZero:
        if self.is_perp:
            return self
        if self.is_inf:
            return HierZero.infinity(level=self.level, sign=-self.sign)
        if self.level == 0:
            return HierZero.real(-self.value)
        return HierZero.zero(level=self.level)

    def __abs__(self) -> HierZero:
        if self.is_perp:
            return self
        if self.is_inf:
            return HierZero.infinity(level=self.level, sign=1)
        if self.level == 0:
            return HierZero.real(abs(self.value))
        return self


# ---------- Вспомогательная функция приведения ----------
def _to_hz(x: Number) -> HierZero:
    if isinstance(x, HierZero):
        return x
    return HierZero.real(float(x))
