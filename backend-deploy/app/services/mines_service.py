"""
Расчёт множителя в минах.

Логика: чем больше клеток открыл подряд без мины — тем выше множитель.
Формула — обратная вероятность выжить (не попасть на мину) при данном
количестве открытых клеток, умноженная на house edge.

Пример на пальцах: поле 25 клеток, из них 5 мин (20 безопасных).
Открыл первую клетку не на мине — шанс был 20/25. Открыл вторую —
шанс (без учёта первой) 19/24. И так далее. Множитель — это "1 делить
на перемноженные шансы", то есть чем меньше был шанс выжить, тем больше
награда за то, что всё-таки выжил.
"""

TOTAL_CELLS = 25
HOUSE_EDGE = 0.97


def calc_multiplier(opened_count: int, mines_count: int) -> float:
    """Множитель после того, как открыто opened_count безопасных клеток подряд."""
    if opened_count == 0:
        return 1.0

    mult = 1.0
    for i in range(opened_count):
        remaining_cells = TOTAL_CELLS - i
        remaining_safe = remaining_cells - mines_count
        if remaining_safe <= 0:
            return mult  # больше открывать нечего — все безопасные уже найдены
        mult *= remaining_cells / remaining_safe

    return round(mult * HOUSE_EDGE, 4)


def max_safe_opens(mines_count: int) -> int:
    """Сколько всего безопасных клеток на поле при данном количестве мин."""
    return TOTAL_CELLS - mines_count
