# drone.py — Agente Reativo Simples (Drone de Vigilância)

class Drone(BaseAgent):
    def __init__(self, id:int, pos_x:int, pos_y:int, view_range:int):
        super().__init__(id, "drone", pos_x, pos_y)
        self.view_range = view_range

    def receive_message(self, message:str):
        pass

    def perceive_environment(self, grid):
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
