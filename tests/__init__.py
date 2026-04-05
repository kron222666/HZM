import math
from hzm import HierZero, sqrt, log


def test_arithmetic():
    """Проверка всех арифметических операций HZM по таблицам из документа."""

    def check(name, actual, expected):
        if actual == expected:
            print(f"✓ {name}")
        else:
            print(f"✗ {name}: {actual} != {expected}")

    print("\n" + "=" * 60)
    print("ТЕСТ АРИФМЕТИЧЕСКИХ ОПЕРАЦИЙ HZM")
    print("=" * 60)

    # ------------------------------------------------------------
    # 1. СЛОЖЕНИЕ (таблица из документа)
    # ------------------------------------------------------------
    print("\n--- Сложение ---")
    # a + b обычные
    check("5 + 7 = 12", HierZero.real(5) + HierZero.real(7), HierZero.real(12))
    # a + 0_k
    check("10 + 0_3 = 0_3", HierZero.real(10) + HierZero.zero(3), HierZero.zero(3))
    # a + ∞_k
    check("5 + ∞_2 = ∞_2", HierZero.real(5) + HierZero.infinity(2), HierZero.infinity(2))
    check("5 + (-∞_4) = -∞_4", HierZero.real(5) + HierZero.infinity(4, sign=-1), HierZero.infinity(4, sign=-1))
    # 0_k + 0_m = 0_min(k,m)
    check("0_5 + 0_2 = 0_2", HierZero.zero(5) + HierZero.zero(2), HierZero.zero(2))
    # 0_k + ∞_m = 0_k
    check("0_3 + ∞_7 = 0_3", HierZero.zero(3) + HierZero.infinity(7), HierZero.zero(3))
    check("0_4 + (-∞_9) = 0_4", HierZero.zero(4) + HierZero.infinity(9, sign=-1), HierZero.zero(4))
    # ∞_k + ∞_m = ∞_min(k,m)
    check("∞_3 + ∞_8 = ∞_3", HierZero.infinity(3) + HierZero.infinity(8), HierZero.infinity(3))
    # ∞_k + (-∞_m)
    check("∞_5 + (-∞_5) = ⊥", HierZero.infinity(5) + HierZero.infinity(5, sign=-1), HierZero.perp())
    check("∞_3 + (-∞_5) = ∞_3", HierZero.infinity(3) + HierZero.infinity(5, sign=-1), HierZero.infinity(3))
    # -∞_k + (-∞_m) = -∞_min(k,m)
    check("-∞_2 + (-∞_6) = -∞_2", HierZero.infinity(2, sign=-1) + HierZero.infinity(6, sign=-1),
          HierZero.infinity(2, sign=-1))
    # ⊥ + x = ⊥
    check("⊥ + 100 = ⊥", HierZero.perp() + HierZero.real(100), HierZero.perp())

    # ------------------------------------------------------------
    # 2. ВЫЧИТАНИЕ (таблица)
    # ------------------------------------------------------------
    print("\n--- Вычитание ---")
    # a - b обычные
    check("10 - 4 = 6", HierZero.real(10) - HierZero.real(4), HierZero.real(6))
    # a - 0_k = a
    check("20 - 0_3 = 20", HierZero.real(20) - HierZero.zero(3), HierZero.real(20))
    # a - ∞_k = -∞_k
    check("5 - ∞_2 = -∞_2", HierZero.real(5) - HierZero.infinity(2), HierZero.infinity(2, sign=-1))
    # a - (-∞_k) = +∞_k
    check("5 - (-∞_3) = +∞_3", HierZero.real(5) - HierZero.infinity(3, sign=-1), HierZero.infinity(3))
    # 0_k - a = 0_k
    check("0_4 - 100 = 0_4", HierZero.zero(4) - HierZero.real(100), HierZero.zero(4))
    # 0_k - 0_m = 0_min(k,m)
    check("0_5 - 0_3 = 0_3", HierZero.zero(5) - HierZero.zero(3), HierZero.zero(3))
    # 0_k - ∞_m = 0_k
    check("0_3 - ∞_8 = 0_3", HierZero.zero(3) - HierZero.infinity(8), HierZero.zero(3))
    check("0_2 - (-∞_4) = 0_2", HierZero.zero(2) - HierZero.infinity(4, sign=-1), HierZero.zero(2))
    # ∞_k - a = ∞_k
    check("∞_3 - 10 = ∞_3", HierZero.infinity(3) - HierZero.real(10), HierZero.infinity(3))
    # ∞_k - 0_m = ∞_k
    check("∞_4 - 0_2 = ∞_4", HierZero.infinity(4) - HierZero.zero(2), HierZero.infinity(4))
    # ∞_k - ∞_m
    check("∞_6 - ∞_6 = ⊥", HierZero.infinity(6) - HierZero.infinity(6), HierZero.perp())
    check("∞_4 - ∞_2 = ∞_2", HierZero.infinity(4) - HierZero.infinity(2), HierZero.infinity(2))
    # ⊥ - x = ⊥
    check("⊥ - 100 = ⊥", HierZero.perp() - HierZero.real(100), HierZero.perp())

    # ------------------------------------------------------------
    # 3. УМНОЖЕНИЕ (таблица)
    # ------------------------------------------------------------
    print("\n--- Умножение ---")
    # обычные
    check("6 * 7 = 42", HierZero.real(6) * HierZero.real(7), HierZero.real(42))
    # a * 0_k = 0_k
    check("15 * 0_4 = 0_4", HierZero.real(15) * HierZero.zero(4), HierZero.zero(4))
    # 0_k * 0_m = 0_{k+m}
    check("0_2 * 0_3 = 0_5", HierZero.zero(2) * HierZero.zero(3), HierZero.zero(5))
    # 0_k * ∞_m = 0_{k+m}
    check("0_1 * ∞_4 = 0_5", HierZero.zero(1) * HierZero.infinity(4), HierZero.zero(5))
    check("∞_2 * 0_3 = 0_5", HierZero.infinity(2) * HierZero.zero(3), HierZero.zero(5))
    # ∞_k * ∞_m = ∞_{k+m}
    check("∞_2 * ∞_3 = ∞_5", HierZero.infinity(2) * HierZero.infinity(3), HierZero.infinity(5))
    # ∞_k * a (a≠0) = sign(a)*∞_k
    check("∞_3 * (-5) = -∞_3", HierZero.infinity(3) * HierZero.real(-5), HierZero.infinity(3, sign=-1))
    check("-∞_2 * 4 = -∞_2", HierZero.infinity(2, sign=-1) * HierZero.real(4), HierZero.infinity(2, sign=-1))
    # ⊥ * x = ⊥
    check("⊥ * 10 = ⊥", HierZero.perp() * HierZero.real(10), HierZero.perp())

    # ------------------------------------------------------------
    # 4. ДЕЛЕНИЕ (таблица)
    # ------------------------------------------------------------
    print("\n--- Деление ---")
    # обычные
    check("20 / 4 = 5", HierZero.real(20) / HierZero.real(4), HierZero.real(5))
    # a / 0_k = sign(a) * ∞_{k+1}
    check("7 / 0_2 = ∞_3", HierZero.real(7) / HierZero.zero(2), HierZero.infinity(3))
    check("-8 / 0_1 = -∞_2", HierZero.real(-8) / HierZero.zero(1), HierZero.infinity(2, sign=-1))
    # 0_k / 0_m = 0_{max(k,m)+1}
    check("0_3 / 0_1 = 0_4", HierZero.zero(3) / HierZero.zero(1), HierZero.zero(4))
    # 0_k / ∞_m = 0_{k+m}
    check("0_2 / ∞_5 = 0_7", HierZero.zero(2) / HierZero.infinity(5), HierZero.zero(7))
    # ∞_k / 0_m = ∞_{k+m+1}
    check("∞_1 / 0_3 = ∞_5", HierZero.infinity(1) / HierZero.zero(3), HierZero.infinity(5))
    # a / ∞_k = 0_k
    check("100 / ∞_4 = 0_4", HierZero.real(100) / HierZero.infinity(4), HierZero.zero(4))
    # ∞_k / ∞_m
    check("∞_5 / ∞_5 = ⊥", HierZero.infinity(5) / HierZero.infinity(5), HierZero.perp())
    check("∞_2 / ∞_6 = ∞_2", HierZero.infinity(2) / HierZero.infinity(6), HierZero.infinity(2))
    check("-∞_3 / ∞_3 = ⊥", HierZero.infinity(3, sign=-1) / HierZero.infinity(3), HierZero.perp())
    check("-∞_3 / ∞_5 = -∞_3", HierZero.infinity(3, sign=-1) / HierZero.infinity(5), HierZero.infinity(3, sign=-1))
    # ⊥ / x = ⊥, x / ⊥ = ⊥
    check("⊥ / 5 = ⊥", HierZero.perp() / HierZero.real(5), HierZero.perp())
    check("10 / ⊥ = ⊥", HierZero.real(10) / HierZero.perp(), HierZero.perp())

    # ------------------------------------------------------------
    # 5. ВОЗВЕДЕНИЕ В СТЕПЕНЬ (таблица)
    # ------------------------------------------------------------
    print("\n--- Возведение в степень ---")
    # обычные
    check("2^3 = 8", HierZero.real(2) ** HierZero.real(3), HierZero.real(8))
    # a ** 0_k = 1 (a≠0, ±1) – a=5
    check("5^0_3 = 1", HierZero.real(5) ** HierZero.zero(3), HierZero.real(1))
    # 0_k ** n (n>0 целое) = 0_{n*k}
    check("0_2^4 = 0_8", HierZero.zero(2) ** HierZero.real(4), HierZero.zero(8))
    # 0_k ** n (n<0 целое) = ∞_{(k+1)*|n|}
    check("0_3^{-2} = ∞_8", HierZero.zero(3) ** HierZero.real(-2), HierZero.infinity(8))
    # 0_k ** 0_m = 1 (k,m≥1)
    check("0_5^0_7 = 1", HierZero.zero(5) ** HierZero.zero(7), HierZero.real(1))
    # 0_k ** ∞_m = 0_{k+m}
    check("0_4^∞_2 = 0_6", HierZero.zero(4) ** HierZero.infinity(2), HierZero.zero(6))
    # ∞_k ** n (n>0) = ∞_{n*k}
    check("∞_1^5 = ∞_5", HierZero.infinity(1) ** HierZero.real(5), HierZero.infinity(5))
    # ∞_k ** n (n<0) = 0_{k*|n|}
    check("∞_4^{-3} = 0_{12}", HierZero.infinity(4) ** HierZero.real(-3), HierZero.zero(12))
    # ∞_k ** 0_m = 1
    check("∞_6^0_2 = 1", HierZero.infinity(6) ** HierZero.zero(2), HierZero.real(1))
    # ∞_k ** ∞_m = ∞_{k+m}
    check("∞_3^∞_7 = ∞_{10}", HierZero.infinity(3) ** HierZero.infinity(7), HierZero.infinity(10))
    # ⊥ ** b = ⊥
    check("⊥^2 = ⊥", HierZero.perp() ** HierZero.real(2), HierZero.perp())

    # ------------------------------------------------------------
    # 6. КОРЕНЬ (функция sqrt)
    # ------------------------------------------------------------
    print("\n--- Извлечение корня ---")
    # обычные
    check("√[4]{16} = 2", sqrt(HierZero.real(16), 4), HierZero.real(2))
    check("∛(-8) = -2", sqrt(HierZero.real(-8), 3), HierZero.real(-2))
    check("√[4]{-16} = ⊥", sqrt(HierZero.real(-16), 4), HierZero.perp())
    # корень из 0_k
    check("√(0_2) = 0_1", sqrt(HierZero.zero(2), 2), HierZero.zero(1))
    check("∛(0_5) = 0_2", sqrt(HierZero.zero(5), 3), HierZero.zero(2))
    # корень из ∞_k
    check("√(∞_7) = ∞_4", sqrt(HierZero.infinity(7), 2), HierZero.infinity(4))
    check("∛(-∞_6) = -∞_2", sqrt(HierZero.infinity(6, sign=-1), 3), HierZero.infinity(2, sign=-1))
    check("√[4]{-∞_6} = ⊥", sqrt(HierZero.infinity(6, sign=-1), 4), HierZero.perp())

    # ------------------------------------------------------------
    # 7. ЛОГАРИФМ (функция log)
    # ------------------------------------------------------------
    print("\n--- Логарифм ---")
    # обычные
    check("log₂8 = 3", log(HierZero.real(8), HierZero.real(2)), HierZero.real(3))
    # log_b(0_k) = -∞_k
    check("log₂0_3 = -∞_3", log(HierZero.zero(3), HierZero.real(2)), HierZero.infinity(3, sign=-1))
    # log_b(∞_k) = +∞_k
    check("log₁₀∞_4 = +∞_4", log(HierZero.infinity(4), HierZero.real(10)), HierZero.infinity(4))
    # log_b(-∞_k) = ⊥
    check("log₂(-∞_5) = ⊥", log(HierZero.infinity(5, sign=-1), HierZero.real(2)), HierZero.perp())
    # log_{0_k}(a) = 0_k
    check("log_{0₂}10 = 0₂", log(HierZero.real(10), HierZero.zero(2)), HierZero.zero(2))
    # log_{0_k}(0_m) = ⊥
    check("log_{0₃}0₁ = ⊥", log(HierZero.zero(1), HierZero.zero(3)), HierZero.perp())
    # log_{0_k}(∞_m) = -∞_k
    check("log_{0₂}∞_5 = -∞₂", log(HierZero.infinity(5), HierZero.zero(2)), HierZero.infinity(2, sign=-1))
    # log_{∞_k}(a) = 0_k
    check("log_{∞₃}100 = 0₃", log(HierZero.real(100), HierZero.infinity(3)), HierZero.zero(3))
    # log_{∞_k}(∞_m)
    check("log_{∞₅}∞₅ = ⊥", log(HierZero.infinity(5), HierZero.infinity(5)), HierZero.perp())
    check("log_{∞₂}∞₅ = ∞₃", log(HierZero.infinity(5), HierZero.infinity(2)), HierZero.infinity(3))
    # log_1(a) = ⊥
    check("log₁10 = ⊥", log(HierZero.real(10), HierZero.real(1)), HierZero.perp())
    # log_⊥(a) = ⊥
    check("log_⊥10 = ⊥", log(HierZero.real(10), HierZero.perp()), HierZero.perp())

    print("\n" + "=" * 60)
    print("ТЕСТ ЗАВЕРШЁН")
    print("=" * 60)


if __name__ == "__main__":
    test_arithmetic()
