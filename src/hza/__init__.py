"""
HZM - Иерархическая алгебра нулей
Hierarchical Zero Mathematics
"""

from .core import HierZero
from .operations import add, sub, mul, div, power, root, neg
from .projection import projection, HZMProjection

__version__ = "0.1.0"
__author__ = "Марат Джанбулатов"
__description__ = "Библиотека для работы с делением на ноль через иерархические уровни"

# Удобные импорты для пользователя
__all__ = [
    "HierZero",
    "add", "sub", "mul", "div", "power", "root", "neg",
    "projection", "HZMProjection"
]

# Для удобства: можно писать from hza import HierZero
