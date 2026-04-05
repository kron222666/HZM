#!/usr/bin/env python3
"""
Полный тест всех операций HZM
Запуск: python tests/test_all.py
"""

from hzm import HierZero

def test_operation(name, actual, expected):
    ok = (str(actual) == str(expected))
    print(f"{'✓' if ok else '✗'} {name}: {actual} (ожидалось {expected})")
    return ok

def main():
    print("=== ПОЛНЫЙ ТЕСТ ОПЕРАЦИЙ HZM ===\n")

    a = HierZero(10)
    b = HierZero(0, level=2)
    c = HierZero(0, level=3)
    d = HierZero(0, level=1)
    inf1 = HierZero(0, level=1, is_inf=True, sign=1)
    inf2 = HierZero(0, level=2, is_inf=True, sign=1)
    inf3 = HierZero(0, level=3, is_inf=True, sign=1)
    neg_inf1 = HierZero(0, level=1, is_inf=True, sign=-1)
    perp = HierZero.perp()

    tests_passed = 0
    tests_total = 0

    # 1. Сложение
    print("1. СЛОЖЕНИЕ (+):")
    tests_total += 1; tests_passed += test_operation("10 + 0_2", a + b, HierZero(0, level=2))
    tests_total += 1; tests_passed += test_operation("0_2 + 0_3", b + c, HierZero(0, level=2))
    tests_total += 1; tests_passed += test_operation("∞_1 + ∞_1", inf1 + inf1, HierZero(0, level=1, is_inf=True))
    tests_total += 1; tests_passed += test_operation("∞_1 + (-∞_1)", inf1 + neg_inf1, perp)
    tests_total += 1; tests_passed += test_operation("∞_2 + ∞_1", inf2 + inf1, HierZero(0, level=1, is_inf=True))
    tests_total += 1; tests_passed += test_operation("∞_1 + ∞_2", inf1 + inf2, HierZero(0, level=1, is_inf=True))
    tests_total += 1; tests_passed += test_operation("∞_1 + (-∞_2)", inf1 + HierZero(0, level=2, is_inf=True, sign=-1), HierZero(0, level=1, is_inf=True))
    tests_total += 1; tests_passed += test_operation("0_2 + 10", b + a, HierZero(0, level=2))
    tests_total += 1; tests_passed += test_operation("10 + ∞_1", a + inf1, inf1)
    tests_total += 1; tests_passed += test_operation("⊥ + 10", perp + a, perp)
    print()

    # 2. Вычитание
    print("2. ВЫЧИТАНИЕ (-):")
    tests_total += 1; tests_passed += test_operation("10 - 0_2", a - b, a)
    tests_total += 1; tests_passed += test_operation("0_2 - 10", b - a, b)
    tests_total += 1; tests_passed += test_operation("0_2 - 0_3", b - c, HierZero(0, level=2))
    tests_total += 1; tests_passed += test_operation("∞_1 - ∞_1", inf1 - inf1, perp)
    tests_total += 1; tests_passed += test_operation("∞_2 - ∞_1", inf2 - inf1, HierZero(0, level=1, is_inf=True))
    tests_total += 1; tests_passed += test_operation("∞_1 - ∞_2", inf1 - inf2, HierZero(0, level=1, is_inf=True))
    tests_total += 1; tests_passed += test_operation("10 - ∞_1", a - inf1, neg_inf1)
    tests_total += 1; tests_passed += test_operation("0_2 - ∞_1", b - inf1, b)
    tests_total += 1; tests_passed += test_operation("⊥ - 10", perp - a, perp)
    print()

    # 3. Умножение
    print("3. УМНОЖЕНИЕ (*):")
    tests_total += 1; tests_passed += test_operation("10 * 0_2", a * b, b)
    tests_total += 1; tests_passed += test_operation("0_2 * 0_3", b * c, HierZero(0, level=5))
    tests_total += 1; tests_passed += test_operation("∞_1 * 0_2", inf1 * b, HierZero(0, level=3))
    tests_total += 1; tests_passed += test_operation("∞_1 * ∞_1", inf1 * inf1, HierZero(0, level=2, is_inf=True))
    tests_total += 1; tests_passed += test_operation("∞_1 * (-∞_2)", inf1 * HierZero(0, level=2, is_inf=True, sign=-1), HierZero(0, level=3, is_inf=True, sign=-1))
    tests_total += 1; tests_passed += test_operation("∞_1 * 10", inf1 * a, inf1)
    tests_total += 1; tests_passed += test_operation("⊥ * 10", perp * a, perp)
    print()

    # 4. Деление
    print("4. ДЕЛЕНИЕ (/):")
    tests_total += 1; tests_passed += test_operation("10 / 0_2", a / b, HierZero(0, level=3, is_inf=True))
    tests_total += 1; tests_passed += test_operation("10 / 0_3", a / c, HierZero(0, level=4, is_inf=True))
    tests_total += 1; tests_passed += test_operation("0_2 / 0_1", b / d, HierZero(0, level=3))
    tests_total += 1; tests_passed += test_operation("∞_1 / 0_2", inf1 / b, HierZero(0, level=4, is_inf=True))
    tests_total += 1; tests_passed += test_operation("∞_1 / ∞_1", inf1 / inf1, perp)
    tests_total += 1; tests_passed += test_operation("∞_2 / ∞_1", inf2 / inf1, HierZero(0, level=1, is_inf=True))
    tests_total += 1; tests_passed += test_operation("10 / ∞_1", a / inf1, HierZero(0, level=1))
    tests_total += 1; tests_passed += test_operation("0_2 / ∞_1", b / inf1, HierZero(0, level=3))
    tests_total += 1; tests_passed += test_operation("⊥ / 10", perp / a, perp)
    print()

    # 5. Степень
    print("5. СТЕПЕНЬ (**):")
    tests_total += 1; tests_passed += test_operation("0_2 ** 3", b ** 3, HierZero(0, level=6))
    tests_total += 1; tests_passed += test_operation("0_2 ** (-2)", b ** (-2), HierZero(0, level=6, is_inf=True))
    tests_total += 1; tests_passed += test_operation("∞_1 ** 2", inf1 ** 2, HierZero(0, level=2, is_inf=True))
    tests_total += 1; tests_passed += test_operation("∞_1 ** (-2)", inf1 ** (-2), HierZero(0, level=2))
    tests_total += 1; tests_passed += test_operation("10 ** 0_2", a ** b, HierZero(1.0))
    tests_total += 1; tests_passed += test_operation("0_2 ** 0_3", b ** c, HierZero(1.0))
    tests_total += 1; tests_passed += test_operation("0_2 ** ∞_1", b ** inf1, HierZero(0, level=3))
    tests_total += 1; tests_passed += test_operation("∞_1 ** ∞_2", inf1 ** inf2, HierZero(0, level=3, is_inf=True))
    tests_total += 1; tests_passed += test_operation("⊥ ** 2", perp ** 2, perp)
    print()

    # 6. Корень
    print("6. КОРЕНЬ (√):")
    tests_total += 1; tests_passed += test_operation("√[2](0_2)", b ** HierZero(0.5), HierZero(0, level=1))
    tests_total += 1; tests_passed += test_operation("√[3](0_5)", HierZero(0, level=5) ** HierZero(1/3), HierZero(0, level=2))
    tests_total += 1; tests_passed += test_operation("√[2](∞_7)", HierZero(0, level=7, is_inf=True) ** HierZero(0.5), HierZero(0, level=4, is_inf=True))
    tests_total += 1; tests_passed += test_operation("√[2](-∞_7)", HierZero(0, level=7, is_inf=True, sign=-1) ** HierZero(0.5), perp)
    print()

    # 7. Логарифм (только если реализован в operations)
    print("7. ЛОГАРИФМ (log):")
    try:
        from hzm.operations import log
        tests_total += 1; tests_passed += test_operation("log₂(0_3)", log(2, HierZero(0, level=3)), HierZero(0, level=3, is_inf=True, sign=-1))
        tests_total += 1; tests_passed += test_operation("log_{0_2}(10)", log(HierZero(0, level=2), 10), HierZero(0, level=2))
        tests_total += 1; tests_passed += test_operation("log_{∞_1}(∞_2)", log(inf1, inf2), HierZero(0, level=1))  # min(1,2)=1 -> 0_1?
        tests_total += 1; tests_passed += test_operation("log_{∞_1}(∞_1)", log(inf1, inf1), perp)
    except ImportError:
        print("! Функция логарифма не реализована в этой версии, пропускаем.")
    print()

    # 8. Унарный минус
    print("8. УНАРНЫЙ МИНУС (-):")
    tests_total += 1; tests_passed += test_operation("-0_2", -b, b)
    tests_total += 1; tests_passed += test_operation("-∞_1", -inf1, neg_inf1)
    tests_total += 1; tests_passed += test_operation("--∞_1", -neg_inf1, inf1)
    print()

    # 9. Поглощающий элемент
    print("9. ПОГЛОЩАЮЩИЙ ЭЛЕМЕНТ ⊥:")
    tests_total += 1; tests_passed += test_operation("⊥ + ∞_1", perp + inf1, perp)
    tests_total += 1; tests_passed += test_operation("∞_1 * ⊥", inf1 * perp, perp)
    tests_total += 1; tests_passed += test_operation("⊥ / ⊥", perp / perp, perp)
    print()

    print(f"\nИТОГО: {tests_passed} из {tests_total} тестов пройдено.")
    if tests_passed == tests_total:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("❌ ЕСТЬ ОШИБКИ, НЕОБХОДИМО ИСПРАВЛЕНИЕ.")

if __name__ == "__main__":
    main()
