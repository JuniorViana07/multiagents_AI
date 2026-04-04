# city_grid.py — Classe CityGrid (grade n×n, spawn de eventos)
from .cell import CellState


class CityGrid():
    def __init__(size:int):
        self.size = size
        self.grid = [[CellState.NORMAL for _ in range(size)] for _ in range(size)]
    
    def get_cell_state(self, x:int, y:int) -> CellState:
        return self.grid[y][x]

    def set_cell_state(self, x:int, y:int, state:CellState):
        self.grid[y][x] = state

    def get_size(self) -> int:
        return self.size