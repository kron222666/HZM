import sys
from .core import HierZero

class HZMProjection:
    """
    Класс для проекции объектов HZM на машинные числа (IEEE 754)
    и обратно. Используется для интеграции с NumPy, PyTorch и т.д.
    """

    def __init__(self, epsilon=None, max_float=None):
        self.epsilon = epsilon or sys.float_info.epsilon * 1e2   # подстраховка
        self.max_float = max_float or sys.float_info.max

    def to_float(self, hzm: HierZero) -> float:
        """Проецирует объект HZM на обычный float"""
        if hzm.is_perp:
            return float('nan')                     # ⊥ → NaN

        if hzm.is_inf:
            if hzm.sign > 0:
                return float('inf')
            else:
                return float('-inf')

        if hzm.level > 0:
            # Глубокий нуль → очень маленькое число или 0.0
            underflow = self.epsilon / (2 ** hzm.level)
            if underflow < sys.float_info.min:
                return 0.0
            return underflow * hzm.sign

        # Обычное число
        return hzm.value * hzm.sign

    def from_float(self, value: float) -> HierZero:
        """Преобразует обычный float обратно в объект HZM"""
        if value == 0.0:
            return HierZero(0.0, level=0)

        if value == float('inf'):
            return HierZero(0, level=1, is_inf=True, sign=1)
        if value == float('-inf'):
            return HierZero(0, level=1, is_inf=True, sign=-1)

        if abs(value) < self.epsilon:
            # Определяем уровень vanishing
            level = max(1, int(-torch.log10(torch.tensor(abs(value))).item()) // 2)
            return HierZero(0.0, level=level)

        if abs(value) > self.max_float * 0.9:
            level = max(1, int(torch.log10(torch.tensor(abs(value))).item()) // 2)
            return HierZero(0, level=level, is_inf=True, sign=1 if value > 0 else -1)

        return HierZero(value)

# Глобальный экземпляр для удобства
projection = HZMProjection()

