# drone.py — Agente Reativo Simples (Drone de Vigilância)

class Drone(BaseAgent):
    def __init__(self, id:int, pos_x:int, pos_y:int, view_range:int):
        super().__init__(id, "drone", pos_x, pos_y)
        self.view_range = view_range

    def receive_message(self, message:str):
        pass

    def perceive_environment(self, grid):
        '''
        Recebe o grid e retorna uma lista de células visíveis dentro do alcance de visão do drone.
        A visão é circular, ou seja, o drone pode ver todas as células dentro de um círculo de raio view_range ao seu redor.
        Cada célula é representada como uma tupla (x, y, state).

        Ex.:
            [
                (4, 5, CellState.NORMAL),
                (5, 5, CellState.FIRE),
                (6, 5, CellState.VICTIM),
                (5, 6, CellState.NORMAL),
                (5, 4, CellState.FIRE_AND_VICTIM)
            ]

        '''
        visible_cells = []

        cx, cy = self.get_position()
        size = grid.get_size()
        r = self.view_range

        for x in range(cx - r, cx + r + 1):
            for y in range(cy - r, cy + r + 1):
                
                # Verifica limites da grid
                if 0 <= x < size and 0 <= y < size:
                    
                    # Verifica se está dentro do círculo
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                        state = grid.get_cell_state(x, y)
                        visible_cells.append((x, y, state))

        return visible_cells
