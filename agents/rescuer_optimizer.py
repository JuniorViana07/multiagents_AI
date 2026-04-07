# rescuer_optimizer.py — Agente Baseado em Utilidade (Socorrista Otimizador)


from agents.base_agent import BaseAgent
from collections import deque
from heapq import heappush, heappop


class RescuerOptimizer(BaseAgent):
    def __init__(self, id, pos_x, pos_y, hospital_pos):
        super().__init__(id, "rescuer_optimizer", pos_x, pos_y)
        self.hospital_pos = hospital_pos

        # fila por prioridade   
        self.rescue_queue = []

        # vitima atual sendo atendida
        self.current_target = None

        self.status = "idle"

        self.carrying_victim = False

        self.steps_taken = 0

        self.victims_rescued = 0

    def update(self, grid_service):
        if self.status == "idle":
            if self.rescue_queue:
                #escolhe primeira vitima da fila
                self.current_target = heappop(self.rescue_queue)[1]
                self.status = "moving_to_victim"
                    

        elif self.status == "moving_to_victim":
                tx, ty = self.current_target
                print(f"Rescuer {self.id} moving towards victim at ({tx}, {ty})")
                self.move_towards(tx, ty)
                self.steps_taken += 1


                if self.pos_x == tx and self.pos_y == ty:
                    self.status = "rescuing"

        elif self.status == "rescuing":
                grid_service.rescue_victim(self.current_target[0], self.current_target[1])
                self.current_target = None
                self.carrying_victim = True
                self.status = "moving_to_hospital"

        elif self.status == "moving_to_hospital":
                hx, hy = self.hospital_pos
                # funcao do agente socorrista(porenquanto)
                self.move_towards(hx, hy)
                self.steps_taken += 1

                if self.pos_x == hx and self.pos_y == hy:
                    self.carrying_victim = False
                    self.victims_rescued += 1
                    self.status = "idle"         

    def receive_message(self, message):
        # vai receber o commander.desires.get("victim_to_rescue") -> um set() de coordenadas.
        for victim in message:
            distance = abs(self.pos_x - victim[0]) + abs(self.pos_y - victim[1])
            heappush(self.rescue_queue, (distance, victim))  # Prioriza por distância

    def perceive_environment(self):
        x, y = self.get_position()
        state = grid.get_cell_state(x, y)
        return (x, y, state)
        pass  # Implementar lógica de percepção do ambiente
