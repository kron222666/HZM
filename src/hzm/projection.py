import sys
import math
from .core import HierZero

class HZMProjection:
    """Проекция HZM на float IEEE 754 и обратно"""

    def __init__(self, epsilon=None, max_float=None):
        self.epsilon = epsilon if epsilon is not None else sys.float_info.epsilon * 100
        self.max_float = max_float if max_float is not None else sys.float_info.max

    def to_float(self, hzm: HierZero) -> float:
        """HZM -> float"""
        if hzm.is_perp:
            return float('nan')
        if hzm.is_inf:
            return float('inf') if hzm.sign > 0 else float('-inf')
        if hzm.level > 0:
            # Глубокий нуль -> очень маленькое число
            underflow = self.epsilon / (2 ** hzm.level)
            if underflow < sys.float_info.min:
                return 0.0
            return underflow * hzm.sign
        return hzm.value * hzm.sign

    def from_float(self, value: float) -> HierZero:
        """float -> HZM"""
        if math.isnan(value):
            return HierZero.perp()
        if math.isinf(value):
            return HierZero(0, level=1, is_inf=True, sign=1 if value > 0 else -1)
        if value == 0.0:
            return HierZero(0.0)
        abs_val = abs(value)
        if abs_val < self.epsilon:
            level = max(1, int(-math.log10(abs_val)) // 2)
            return HierZero(0.0, level=level)
        if abs_val > self.max_float * 0.9:
            level = max(1, int(math.log10(abs_val)) // 2)
            return HierZero(0.0, level=level, is_inf=True, sign=1 if value > 0 else -1)
        return HierZero(value)

# Глобальный экземпляр
projection = HZMProjection()
