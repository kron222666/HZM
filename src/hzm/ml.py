# src/hzm/ml.py
"""
Интеграция HZM с машинным обучением (PyTorch).
Содержит адаптивные оптимизаторы и утилиты для обработки градиентов.
"""

from .core import HierZero
import torch
import torch.nn as nn
import math

def grad_to_hz(grad: float, eps_min=1e-3, eps_max=1e3, c=2.0):
    # ... реализация ...

class HZMAdam(torch.optim.Adam):
    # ... реализация ...
