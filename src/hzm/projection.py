from .core import HierZero
import math

def project_to_float(x: HierZero, eps: float = 1e-7, max_val: float = 1e7) -> float:
    """
    Проецирует элемент HZM на вещественное число по правилам:
    - 0ₖ → 0.0 (underflow не моделируется, возвращается 0)
    - ∞ₖ → inf
    - ⊥ → nan
    - Обычное число → как есть
    """
    if x.is_perp:
        return float('nan')
    if x.is_inf:
        return math.inf if x.sign == 1 else -math.inf
    if x.level == 0:
        return x.value
    return 0.0  # глубокий нуль

def from_float(x: float, eps: float = 1e-7, max_val: float = 1e7) -> HierZero:
    """
    Преобразует float в HierZero с автоматическим определением уровня k
    на основе порогов underflow/overflow.
    """
    if math.isnan(x):
        return HierZero.perp()
    if math.isinf(x):
        # бесконечность получает уровень 1 (можно уточнить)
        return HierZero.infinity(level=1, sign=1 if x>0 else -1)
    absx = abs(x)
    if absx < eps:
        # underflow -> 0₁
        return HierZero.zero(1)
    if absx > max_val:
        # overflow -> ∞₁
        return HierZero.infinity(level=1, sign=1 if x>0 else -1)
    return HierZero.real(x)
