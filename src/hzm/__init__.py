# src/hzm/__init__.py
from .core import HierZero
from .projection import project_to_float, from_float
from .operations import sqrt, log

# Опционально: если PyTorch установлен, подключаем ML-функции
try:
    from .ml import HZMAdam, grad_to_hz
    __all__ = ["HierZero", "project_to_float", "from_float", "sqrt", "log", "HZMAdam", "grad_to_hz"]
except ImportError:
    __all__ = ["HierZero", "project_to_float", "from_float", "sqrt", "log"]
