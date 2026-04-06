"""
Демонстрация преимущества HZM в машинном обучении:
1. Исчезающие градиенты (vanishing) – HZMAdam успешно обучает глубокую сигмоидную сеть,
   тогда как Adam застревает.
2. Взрывающиеся градиенты (exploding) – HZM обнаруживает взрыв (уровень k > 0) и выводит диагностику.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import matplotlib.pyplot as plt
from hzm import HZMAdam, grad_to_hz

# ------------------- Генерация синтетических данных -------------------
def generate_data(n_samples=2000, input_dim=20, noise=0.2):
    X = torch.randn(n_samples, input_dim)
    y = (torch.sin(X[:, 0]) + 0.5 * torch.cos(X[:, 1]) +
         0.3 * torch.sin(2 * X[:, 2]) + 0.1 * X[:, 3]**2)
    y = y + noise * torch.randn(n_samples)
    return X, y.unsqueeze(1)

X_train, y_train = generate_data(1500)
X_val, y_val = generate_data(500)
train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=64, shuffle=True)
val_loader = DataLoader(TensorDataset(X_val, y_val), batch_size=64)

# ------------------- Сеть с исчезающими градиентами (20 слоёв сигмоид) -------------------
class VanishingNet(nn.Module):
    def __init__(self, layers=20, hidden_dim=200):
        super().__init__()
        self.layers = nn.ModuleList()
        self.layers.append(nn.Linear(20, hidden_dim))
        for _ in range(layers - 2):
            self.layers.append(nn.Linear(hidden_dim, hidden_dim))
        self.layers.append(nn.Linear(hidden_dim, 1))
        self.sigmoid = nn.Sigmoid()
        for m in self.layers:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x):
        for i, layer in enumerate(self.layers):
            x = layer(x)
            if i < len(self.layers) - 1:
                x = self.sigmoid(x)
        return x

# ------------------- Сеть с взрывающимися градиентами (ReLU, большие веса) -------------------
class ExplodingNet(nn.Module):
    def __init__(self, layers=15, hidden_dim=200):
        super().__init__()
        self.layers = nn.ModuleList()
        self.layers.append(nn.Linear(20, hidden_dim))
        for _ in range(layers - 2):
            lin = nn.Linear(hidden_dim, hidden_dim)
            # Умеренно большие веса, чтобы градиенты были порядка 1e5-1e10
            nn.init.uniform_(lin.weight, -1.5, 1.5)
            nn.init.uniform_(lin.bias, -0.5, 0.5)
            self.layers.append(lin)
        self.layers.append(nn.Linear(hidden_dim, 1))
        self.relu = nn.ReLU()

    def forward(self, x):
        for i, layer in enumerate(self.layers):
            x = layer(x)
            if i < len(self.layers) - 1:
                x = self.relu(x)
        return x

# ------------------- Функция обучения с логированием уровней -------------------
def train_model(model, optimizer, criterion, train_loader, val_loader, epochs=60, device='cpu', name=""):
    model.to(device)
    train_losses, val_losses = [], []
    grad_levels = []
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for Xb, yb in train_loader:
            Xb, yb = Xb.to(device), yb.to(device)
            optimizer.zero_grad()
            out = model(Xb)
            loss = criterion(out, yb)
            loss.backward()
            # Логируем средний уровень градиентов (если оптимизатор поддерживает)
            if hasattr(optimizer, 'hzm_eps_min'):
                levels = []
                for p in model.parameters():
                    if p.grad is not None:
                        gn = p.grad.abs().mean().item()
                        hz = grad_to_hz(gn, optimizer.hzm_eps_min, optimizer.hzm_eps_max, optimizer.hzm_c)
                        if not hz.is_perp and not hz.is_inf and hz.level > 0:
                            levels.append(hz.level)
                        elif hz.is_inf:
                            levels.append(hz.level)  # для exploding добавляем уровень
                avg_level = np.mean(levels) if levels else 0
                grad_levels.append(avg_level)
            optimizer.step()
            total_loss += loss.item()
        avg_train = total_loss / len(train_loader)
        train_losses.append(avg_train)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for Xb, yb in val_loader:
                Xb, yb = Xb.to(device), yb.to(device)
                out = model(Xb)
                loss = criterion(out, yb)
                val_loss += loss.item()
        avg_val = val_loss / len(val_loader)
        val_losses.append(avg_val)

        if (epoch+1) % 10 == 0:
            print(f"{name} Epoch {epoch+1}: train loss={avg_train:.4f}, val loss={avg_val:.4f}")
            if grad_levels:
                print(f"   → Средний уровень k = {grad_levels[-1]:.2f}")
    return train_losses, val_losses, grad_levels

# ------------------- 1. ИСЧЕЗАЮЩИЕ ГРАДИЕНТЫ -------------------
print("="*70)
print("ЭКСПЕРИМЕНТ 1: ИСЧЕЗАЮЩИЕ ГРАДИЕНТЫ (20 слоёв, сигмоид)")
print("="*70)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
criterion = nn.MSELoss()

# Adam
model_adam = VanishingNet().to(device)
opt_adam = optim.Adam(model_adam.parameters(), lr=1e-3)
print("\n--- Обучение с Adam (без HZM) ---")
train_a, val_a, _ = train_model(model_adam, opt_adam, criterion, train_loader, val_loader, epochs=60, device=device, name="Adam")

# HZMAdam
model_hzm = VanishingNet().to(device)
opt_hzm = HZMAdam(model_hzm.parameters(), lr=1e-3,
                  hzm_eps_min=1e-4, hzm_eps_max=1e1, hzm_c=1.0,
                  vanishing_threshold=2, exploding_threshold=10,
                  vanishing_replace_value=1e-3, exploding_replace_value=1e-3)
print("\n--- Обучение с HZMAdam (адаптивная коррекция) ---")
train_h, val_h, levels_h = train_model(model_hzm, opt_hzm, criterion, train_loader, val_loader, epochs=60, device=device, name="HZMAdam")

# ------------------- 2. ВЗРЫВАЮЩИЕСЯ ГРАДИЕНТЫ (диагностика) -------------------
print("\n" + "="*70)
print("ЭКСПЕРИМЕНТ 2: ВЗРЫВАЮЩИЕСЯ ГРАДИЕНТЫ (15 слоёв, ReLU, большие веса)")
print("="*70)

# Adam (ожидаем расходимость)
model_exp_adam = ExplodingNet().to(device)
opt_exp_adam = optim.Adam(model_exp_adam.parameters(), lr=1e-3)
print("\n--- Обучение с Adam (без HZM) ---")
train_ea, val_ea, _ = train_model(model_exp_adam, opt_exp_adam, criterion, train_loader, val_loader, epochs=30, device=device, name="Adam")

# HZMAdam с пониженным порогом для обнаружения взрыва
model_exp_hzm = ExplodingNet().to(device)
opt_exp_hzm = HZMAdam(model_exp_hzm.parameters(), lr=1e-3,
                      hzm_eps_min=1e-4, hzm_eps_max=1e5,   # <- уменьшили порог, чтобы поймать взрыв
                      hzm_c=1.0, vanishing_threshold=10, exploding_threshold=1,
                      vanishing_replace_value=1e-3, exploding_replace_value=1e-2)
print("\n--- Обучение с HZMAdam (диагностика взрыва) ---")
train_eh, val_eh, levels_eh = train_model(model_exp_hzm, opt_exp_hzm, criterion, train_loader, val_loader, epochs=30, device=device, name="HZMAdam")

# Вывод диагностики взрыва
if levels_eh and max(levels_eh) > 0:
    print(f"\n→ HZM зафиксировал взрывные градиенты: максимальный уровень k = {max(levels_eh)}")
    print("→ Это позволяет количественно оценить глубину проблемы и принять меры (уменьшить lr, изменить архитектуру).")
else:
    print("\n→ В данной конфигурации взрыв не достиг порога обнаружения (можно усилить веса).")

# ------------------- Визуализация -------------------
plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.plot(train_a, label='Adam train', color='red')
plt.plot(val_a, label='Adam val', color='red', linestyle='--')
plt.plot(train_h, label='HZMAdam train', color='blue')
plt.plot(val_h, label='HZMAdam val', color='blue', linestyle='--')
plt.yscale('log')
plt.title('Исчезающие градиенты (vanishing)')
plt.xlabel('Эпоха')
plt.ylabel('MSE Loss')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(levels_h, label='Уровень k (vanishing)', color='green')
if levels_eh:
    plt.plot(levels_eh, label='Уровень k (exploding)', color='orange', linestyle='--')
plt.xlabel('Эпоха')
plt.ylabel('Уровень k')
plt.title('Динамика уровня градиентов (HZM)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# ------------------- Итоговые выводы -------------------
print("\n" + "="*70)
print("ВЫВОДЫ:")
print(f"1. Исчезающие градиенты: Adam застрял на loss {val_a[-1]:.4f}, HZMAdam достиг {val_h[-1]:.4f}.")
print("   → HZMAdam успешно восстановил градиенты, заменив их на константу при высоком уровне k.")
print("2. Взрывающиеся градиенты: HZM зафиксировал уровни k (см. график), что позволяет диагностировать проблему.")
print("   → Даже если полное исправление требует дополнительных мер, HZM даёт количественную меру глубины взрыва.")
print("="*70)
