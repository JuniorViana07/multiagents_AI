# city_grid.py — Classe CityGrid (grade n×n, spawn de eventos)
import random
from .cell import CellState
from .city_grid import CityGrid


class CityGridService():
    def __init__(self, grid:CityGrid, event_probability:float=0.05, fire_probability:float=0.4, victim_probability:float=0.4, fire_victim_probability:float=0.2):
        self.grid = grid
        self.event_prob = max(0.0, min(1.0, float(event_probability)))

        self.fire_prob = max(0.0, float(fire_probability))
        self.victim_prob = max(0.0, float(victim_probability))
        self.fire_victim_prob = max(0.0, float(fire_victim_probability))
        self._normalize_event_weights()

    def _normalize_event_weights(self):
        total = self.fire_prob + self.victim_prob + self.fire_victim_prob
        if total <= 0:
            self.fire_prob = 1.0 / 3.0
            self.victim_prob = 1.0 / 3.0
            self.fire_victim_prob = 1.0 / 3.0
            return

        self.fire_prob /= total
        self.victim_prob /= total
        self.fire_victim_prob /= total


    def spawn_fire(self, x:int, y:int):
        if self.grid.get_cell_state(x, y) == CellState.VICTIM:
            self.grid.set_cell_state(x, y, CellState.FIRE_AND_VICTIM)
        else:
            self.grid.set_cell_state(x, y, CellState.FIRE)

    def spawn_victim(self, x:int, y:int):
        if self.grid.get_cell_state(x, y) == CellState.FIRE:
            self.grid.set_cell_state(x, y, CellState.FIRE_AND_VICTIM)
        else:
            self.grid.set_cell_state(x, y, CellState.VICTIM)

    def spawn_hospital(self, x:int, y:int):
        self.grid.set_cell_state(x, y, CellState.HOSPITAL)

    def extinguish_fire(self, x:int, y:int):
        if self.grid.get_cell_state(x, y) == CellState.FIRE_AND_VICTIM:
            self.grid.set_cell_state(x, y, CellState.VICTIM)
        if self.grid.get_cell_state(x, y) == CellState.FIRE:
            self.grid.set_cell_state(x, y, CellState.NORMAL)
    
    def rescue_victim(self, x:int, y:int):
        if self.grid.get_cell_state(x, y) == CellState.FIRE_AND_VICTIM:
            self.grid.set_cell_state(x, y, CellState.FIRE)
        if self.grid.get_cell_state(x, y) == CellState.VICTIM:
            self.grid.set_cell_state(x, y, CellState.NORMAL)

    def clear_cell(self, x:int, y:int):
        self.grid.set_cell_state(x, y, CellState.NORMAL)

    def update(self):
        if random.random() < self.event_prob:
            x = random.randint(0, self.grid.get_size() - 1)
            y = random.randint(0, self.grid.get_size() - 1)
            event_type = random.choices(
                ['fire', 'victim', 'fire_and_victim'],
                weights=[self.fire_prob, self.victim_prob, self.fire_victim_prob]
            )[0]
            if event_type == 'fire':
                self.spawn_fire(x, y)
            elif event_type == 'victim':
                self.spawn_victim(x, y)
            elif event_type == 'fire_and_victim':
                self.spawn_fire(x, y)
                self.spawn_victim(x, y)
