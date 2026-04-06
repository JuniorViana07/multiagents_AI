# drone.py — Agente Reativo Simples (Drone de Vigilância)
from agents.base_agent import BaseAgent


class Drone(BaseAgent):
    def __init__(self, id:int, pos_x:int, pos_y:int, view_range:int):
        super().__init__(id, "drone", pos_x, pos_y)
        self.view_range = view_range
        self.heading = 'right'  # direção horizontal atual
        self.vert_dir = 1       # +1 desce, -1 sobe
        self.vert_steps_left = 0

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
                    state = grid.get_cell_state(x, y)
                    visible_cells.append((x, y, state))


        return visible_cells

    def patrol(self, grid):
        cx, cy = self.get_position()
        size = grid.get_size()
        step = self.view_range * 2  # total de células a descer/subir na virada

        # --- Modo vertical: ainda tem passos verticais para dar ---
        if self.vert_steps_left > 0:
            next_y = cy + (self.view_range + 1) * self.vert_dir

            # Chegou na borda vertical → inverte direção vertical para o retorno
            if next_y < 0 or next_y >= size:
                self.vert_dir *= -1
                self.vert_steps_left = 0
                return

            self.set_position(cx, cy + self.vert_dir)
            self.vert_steps_left -= 1
            return  # não anda horizontalmente enquanto está virando

        # --- Modo horizontal: anda 1 célula na direção atual ---
        if self.heading == 'right':
            next_x = cx + self.view_range + 1
            if next_x < size:
                self.set_position(cx + 1, cy)
            else:
                # Bateu na borda → inicia a descida/subida
                self.heading = 'left'
                self.vert_steps_left = step

        elif self.heading == 'left':
            next_x = cx - self.view_range - 1
            if next_x >= 0:
                self.set_position(cx -1, cy)
            else:
                # Bateu na borda → inicia a descida/subida
                self.heading = 'right'
                self.vert_steps_left = step

