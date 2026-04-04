class HierZero:
    """
    Основной класс Иерархической алгебры нулей (HZM)
    
    Представляет числа с иерархическими уровнями:
    - Обычные вещественные числа (level = 0)
    - Глубокие нули 0_k
    - Иерархические бесконечности ±∞_k
    - Поглощающий элемент ⊥
    """
    
    def __init__(self, value=0.0, level=0, is_inf=False, sign=1):
        self.value = float(value)
        self.level = max(0, int(level))      # уровень не может быть отрицательным
        self.is_inf = bool(is_inf)
        self.sign = 1 if sign >= 0 else -1
        self.is_perp = False

    def __repr__(self):
        if self.is_perp:
            return "⊥"
        if self.is_inf:
            sign_str = "-" if self.sign < 0 else ""
            return f"{sign_str}∞_{self.level}"
        if self.level > 0:
            return f"0_{self.level}"
        return f"{self.value:.6f}"

    def __str__(self):
        return self.__repr__()

    @property
    def is_zero(self):
        return self.level > 0 and not self.is_inf

    @property
    def is_finite(self):
        return not self.is_inf and not self.is_perp and self.level == 0
