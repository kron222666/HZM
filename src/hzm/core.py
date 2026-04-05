from __future__ import annotations
from typing import Union, Optional
import math

Number = Union[int, float, "HierZero"]


class HierZero:
    """
    Представляет элемент иерархической алгебры нулей (HZM).
    
    Атрибуты:
        level (int): уровень k (≥0). Для обычных чисел level=0.
        value (float): вещественное значение (используется только при level=0).
        is_inf (bool): True для иерархической бесконечности (±∞ₖ).
        sign (int): 1 для положительных, -1 для отрицательных.
        is_perp (bool): True для поглощающего элемента ⊥.
    """
    
    def __init__(self, 
                 level: int = 0, 
                 value: float = 0.0, 
                 is_inf: bool = False, 
                 sign: int = 1, 
                 is_perp: bool = False):
        self.level = level
        self.value = value
        self.is_inf = is_inf
        self.sign = sign
        self.is_perp = is_perp
        
        # Нормализация: обычное число с level=0
        if not is_inf and not is_perp and level == 0:
            self.value = float(value)
        # Глубокий нуль: level>0, is_inf=False, value=0
        elif not is_inf and not is_perp and level > 0:
            self.value = 0.0
        # Бесконечность: is_inf=True, level≥1
        elif is_inf and level >= 1:
            self.value = math.inf if sign == 1 else -math.inf
        # ⊥
        elif is_perp:
            self.level = -1
            self.value = float('nan')
        else:
            raise ValueError("Некорректная комбинация параметров HZM")
    
    @classmethod
    def real(cls, x: float) -> HierZero:
        """Обычное вещественное число (уровень 0)."""
        return cls(level=0, value=x, is_inf=False, sign=1 if x >= 0 else -1)
    
    @classmethod
    def zero(cls, level: int = 1) -> HierZero:
        """Глубокий нуль уровня k (k≥1)."""
        if level < 1:
            raise ValueError("Уровень нуля должен быть ≥ 1")
        return cls(level=level, value=0.0, is_inf=False)
    
    @classmethod
    def infinity(cls, level: int = 1, sign: int = 1) -> HierZero:
        """Иерархическая бесконечность уровня k (k≥1)."""
        if level < 1:
            raise ValueError("Уровень бесконечности должен быть ≥ 1")
        return cls(level=level, is_inf=True, sign=sign)
    
    @classmethod
    def perp(cls) -> HierZero:
        """Поглощающий элемент ⊥."""
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
    
    # ------------------- Арифметические операции -------------------
    def __add__(self, other: Number) -> HierZero:
        return _add(self, _to_hz(other))
    
    def __radd__(self, other: Number) -> HierZero:
        return _add(_to_hz(other), self)
    
    def __sub__(self, other: Number) -> HierZero:
        return _sub(self, _to_hz(other))
    
    def __rsub__(self, other: Number) -> HierZero:
        return _sub(_to_hz(other), self)
    
    def __mul__(self, other: Number) -> HierZero:
        return _mul(self, _to_hz(other))
    
    def __rmul__(self, other: Number) -> HierZero:
        return _mul(_to_hz(other), self)
    
    def __truediv__(self, other: Number) -> HierZero:
        return _div(self, _to_hz(other))
    
    def __rtruediv__(self, other: Number) -> HierZero:
        return _div(_to_hz(other), self)
    
    def __pow__(self, exponent: Number) -> HierZero:
        return _pow(self, _to_hz(exponent))
    
    def __rpow__(self, base: Number) -> HierZero:
        return _pow(_to_hz(base), self)
    
    def __neg__(self) -> HierZero:
        if self.is_perp:
            return self
        if self.is_inf:
            return HierZero.infinity(level=self.level, sign=-self.sign)
        if self.level == 0:
            return HierZero.real(-self.value)
        # глубокий нуль остаётся нулём (знак не имеет значения)
        return HierZero.zero(level=self.level)
    
    def __abs__(self) -> HierZero:
        if self.is_perp:
            return self
        if self.is_inf:
            return HierZero.infinity(level=self.level, sign=1)
        if self.level == 0:
            return HierZero.real(abs(self.value))
        return self  # нуль неотрицателен
