# firefighter.py — Agente Reativo Baseado em Modelo (Bombeiro)

from agents.base_agent import BaseAgent

class Firefighter(BaseAgent):
    def __init__(self, id:int, pos_x:int, pos_y:int):
        super().__init__(id, "firefighter", pos_x, pos_y)

    def receive_message(self, message:str):
        pass

    def perceive_environment(self, grid):
        # O bombeiro pode perceber apenas a célula em que está localizado
        x, y = self.get_position()
        state = grid.get_cell_state(x, y)
        return (x, y, state)

    def act(self, command:str):
        # O bombeiro pode executar ações como "move_up", "move_down", "move_left", "move_right", "extinguish_fire"
        pass