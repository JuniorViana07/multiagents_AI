# cell.py — Enum/dataclass para estado de cada célula da grade

from enum import Enum


class CellState(Enum):
    NORMAL = 0
    FIRE = 1
    VICTIM = 2
    FIRE_AND_VICTIM = 3
    HOSPITAL = 4
    