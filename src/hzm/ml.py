import math
import torch
import torch.nn as nn
from .core import HierZero

def grad_to_hz(grad: float, eps_min: float = 1e-3, eps_max: float = 1e3, c: float = 2.0):
    """
    Превращает обычный градиент (скаляр) в объект HierZero.
    Уровень k = floor( -log10(|g|) / c ) для vanishing,
    и floor( log10(|g|) / c ) для exploding.
    """
    if math.isnan(grad) or math.isinf(grad):
        return HierZero.perp()
    abs_g = abs(grad)
    if abs_g < eps_min:
        # vanishing gradient
        if abs_g == 0:
            k = 10   # максимальный уровень для нуля (можно настроить)
        else:
            k = max(0, int(math.floor(-math.log10(abs_g) / c)))
        return HierZero.zero(max(1, k))
    elif abs_g > eps_max:
        # exploding gradient
        k = max(0, int(math.floor(math.log10(abs_g) / c)))
        sign = 1 if grad > 0 else -1
        return HierZero.infinity(max(1, k), sign=sign)
    else:
        # нормальный градиент
        return HierZero.real(grad)


class HZMAdam(torch.optim.Adam):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8,
                 weight_decay=0, amsgrad=False, *,
                 hzm_eps_min=1e-4, hzm_eps_max=1e2, hzm_c=1.0):
        super().__init__(params, lr, betas, eps, weight_decay, amsgrad)
        self.hzm_eps_min = hzm_eps_min
        self.hzm_eps_max = hzm_eps_max
        self.hzm_c = hzm_c

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue
                grad = p.grad
                grad_norm = grad.abs().mean().item()
                hz_grad = grad_to_hz(grad_norm, self.hzm_eps_min, self.hzm_eps_max, self.hzm_c)

                if hz_grad.is_perp:
                    p.grad = None   # пропускаем параметр
                    continue
                elif not hz_grad.is_inf and hz_grad.level > 0:
                    k = hz_grad.level
                    scale = 1.0 + 0.5 * k      # увеличиваем эффективный LR
                elif hz_grad.is_inf:
                    k = hz_grad.level
                    scale = 1.0 / (1.0 + 0.5 * k)  # уменьшаем LR
                else:
                    scale = 1.0

                p.grad = grad * scale   # масштабируем градиент

        super().step(closure)
        return loss
