"""
HZM - Иерархическая алгебра нулей
"""

from .core import HierZero
from .operations import add, sub, mul, div, power, root, neg
from .projection import projection, HZMProjection

__version__ = "0.1.0"
__author__ = "Марат Джанбулатов"

# Основной экспорт
__all__ = [
    "HierZero",
    "add", "sub", "mul", "div", "power", "root", "neg",
    "projection", "HZMProjection"
]

# Для удобства использования
HierZero = HierZero
