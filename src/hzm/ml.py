import math
import torch
import torch.nn as nn
from .core import HierZero

def grad_to_hz(grad: float, eps_min: float = 1e-4, eps_max: float = 1e1, c: float = 1.0):
    if math.isnan(grad) or math.isinf(grad):
        return HierZero.perp()
    abs_g = abs(grad)
    if abs_g < eps_min:
        if abs_g == 0:
            k = 5
        else:
            k = max(0, int(math.floor(-math.log10(abs_g) / c)))
        return HierZero.zero(max(1, k))
    elif abs_g > eps_max:
        k = max(0, int(math.floor(math.log10(abs_g) / c)))
        sign = 1 if grad > 0 else -1
        return HierZero.infinity(max(1, k), sign=sign)
    else:
        return HierZero.real(grad)

class HZMAdam(torch.optim.Adam):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8,
                 weight_decay=0, amsgrad=False, *,
                 hzm_eps_min=1e-4, hzm_eps_max=1e1, hzm_c=1.0,
                 vanishing_fix=True, exploding_clip=True):
        super().__init__(params, lr, betas, eps, weight_decay, amsgrad)
        self.hzm_eps_min = hzm_eps_min
        self.hzm_eps_max = hzm_eps_max
        self.hzm_c = hzm_c
        self.vanishing_fix = vanishing_fix
        self.exploding_clip = exploding_clip

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
                    p.grad = None
                    continue

                if not hz_grad.is_inf and hz_grad.level > 0:
                    k = hz_grad.level
                    if self.vanishing_fix and k >= 3:
                        # Агрессивное восстановление: заменяем градиент на константу 1e-3
                        p.grad = torch.full_like(grad, 1e-3) * grad.sign()
                    else:
                        scale = 1.0 + 0.5 * k
                        p.grad = grad * scale
                elif hz_grad.is_inf:
                    k = hz_grad.level
                    if self.exploding_clip and k >= 3:
                        # Клиппируем градиент по норме (максимум 1.0)
                        torch.nn.utils.clip_grad_norm_([p], max_norm=1.0)
                    else:
                        scale = 1.0 / (1.0 + 0.5 * k)
                        p.grad = grad * scale
                # иначе scale=1

        super().step(closure)
        return loss
