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
    """
    Адаптивный Adam с коррекцией на основе уровня HZM.
    Для каждого параметра, если его градиент превращается в 0_k (vanishing),
    мы увеличиваем learning rate для этого параметра.
    Если градиент становится ∞_k (exploding) – уменьшаем learning rate.
    """
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8,
                 weight_decay=0, amsgrad=False, *,
                 hzm_eps_min=1e-3, hzm_eps_max=1e3, hzm_c=2.0):
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
            lr = group['lr']
            for p in group['params']:
                if p.grad is None:
                    continue
                grad = p.grad
                # Анализируем градиент с помощью HZM
                # Берём среднее абсолютное значение градиента как репрезентативную норму
                grad_norm = grad.abs().mean().item()
                hz_grad = grad_to_hz(grad_norm, self.hzm_eps_min, self.hzm_eps_max, self.hzm_c)

                # Корректируем learning rate для этого параметра на основе уровня
                if hz_grad.is_perp:
                    # Полная неопределённость – пропускаем шаг
                    continue
                elif not hz_grad.is_inf and hz_grad.level > 0:
                    # vanishing: уровень k => увеличиваем LR
                    k = hz_grad.level
                    adaptive_lr = lr * (1.0 + 0.5 * k)   # например, +50% за каждый уровень
                elif hz_grad.is_inf:
                    # exploding: уровень k => уменьшаем LR
                    k = hz_grad.level
                    adaptive_lr = lr / (1.0 + 0.5 * k)
                else:
                    adaptive_lr = lr

                # Применяем стандартный шаг Adam с адаптивным LR
                # (временно меняем lr для этого параметра)
                orig_lr = group['lr']
                group['lr'] = adaptive_lr
                super().step()
                group['lr'] = orig_lr
                break   # после обработки одного параметра выходим, чтобы не делать двойной шаг
        return loss
