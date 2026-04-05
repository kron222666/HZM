"""
HZM - Иерархическая алгебра нулей (Hierarchical Zero Mathematics)
"""

from .core import HierZero
from .operations import add, sub, mul, div, power, root, log
from .projection import projection, HZMProjection

__version__ = "0.1.0"
__author__ = "Марат Джанбулатов"

__all__ = [
    "HierZero",
    "add", "sub", "mul", "div", "power", "root", "log",
    "projection", "HZMProjection"
]
