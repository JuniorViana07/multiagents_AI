# rescuer_optimizer.py — Agente Baseado em Utilidade (Socorrista Otimizador)


from agents.base_agent import BaseAgent
from collections import deque
from heapq import heappush, heappop
from environment.cell import CellState


class RescuerOptimizer(BaseAgent):
    def __init__(self, id, pos_x, pos_y, hospital_pos):
        super().__init__(id, "rescuer_optimizer", pos_x, pos_y)
        self.hospital_pos = hospital_pos

        # fila por prioridade   
        self.rescue_queue = []
        self.queued_victims = set()

        # vitima atual sendo atendida
        self.current_target = None

        self.status = "idle"

        self.carrying_victim = False

        self.steps_taken = 0

        self.victims_rescued = 0

    def _is_target_rescuable(self, grid_service, target):
        tx, ty = target
        state = grid_service.grid.get_cell_state(tx, ty)
        return state in (CellState.VICTIM, CellState.FIRE_AND_VICTIM)

    def update(self, grid_service):
        if self.status == "idle":
            while self.rescue_queue:
                # escolhe primeira vítima válida da fila
                candidate = heappop(self.rescue_queue)[1]
                self.queued_victims.discard(candidate)
                if self._is_target_rescuable(grid_service, candidate):
                    self.current_target = candidate
                    self.status = "moving_to_victim"
                    break
                    

        elif self.status == "moving_to_victim":
                if self.current_target is None:
                    self.status = "idle"
                    return None

                if not self._is_target_rescuable(grid_service, self.current_target):
                    # alvo ficou inválido durante o deslocamento: aborta e replana
                    self.current_target = None
                    self.status = "idle"
                    return None

                tx, ty = self.current_target
                print(f"Rescuer {self.id} moving towards victim at ({tx}, {ty})")
                self.move_towards(tx, ty)
                self.steps_taken += 1

                if self.pos_x == tx and self.pos_y == ty:
                    if self._is_target_rescuable(grid_service, self.current_target):
                        self.status = "rescuing"
                    else:
                        self.current_target = None
                        self.status = "idle"

        elif self.status == "rescuing":
                if self.current_target is None:
                    self.status = "idle"
                    return None

                if not self._is_target_rescuable(grid_service, self.current_target):
                    self.current_target = None
                    self.status = "idle"
                    return None

                grid_service.rescue_victim(self.current_target[0], self.current_target[1])
                result = self.current_target
                self.current_target = None
                self.carrying_victim = True
                self.status = "moving_to_hospital"
                return result
        elif self.status == "moving_to_hospital":
                hx, hy = self.hospital_pos
                # funcao do agente socorrista(porenquanto)
                self.move_towards(hx, hy)
                self.steps_taken += 1

                if self.pos_x == hx and self.pos_y == hy:
                    self.carrying_victim = False
                    self.victims_rescued += 1
                    self.status = "idle"         
        return None
    def receive_message(self, message):
        # vai receber o commander.desires.get("victim_to_rescue") -> um set() de coordenadas.
        for victim in message:
            if victim == self.current_target:
                continue
            if victim in self.queued_victims:
                continue
            distance = abs(self.pos_x - victim[0]) + abs(self.pos_y - victim[1])
            heappush(self.rescue_queue, (distance, victim))  # Prioriza por distância
            self.queued_victims.add(victim)

    def perceive_environment(self):
        x, y = self.get_position()
        state = grid.get_cell_state(x, y)
        return (x, y, state)
        pass  # Implementar lógica de percepção do ambiente
