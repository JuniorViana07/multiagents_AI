# rescuer_sequential.py — Agente Baseado em Objetivos (Socorrista Sequencial / FIFO)


# base_agent.py — Classe base abstrata para todos os agentes
from agents.base_agent import BaseAgent
from collections import deque

class RescuerSequential(BaseAgent):
    def __init__(self, id, pos_x, pos_y):
        super().__init__(id, "rescuer_sequential", pos_x, pos_y)
        
        # fila de vitimas FIFO
        self.rescue_queue = deque()

        # vitima atual sendo atendida
        self.current_target = None

        self.status = "idle"

        self.carrying_victim = False

        self.hospital_pos = (10,10)

        self.steps_taken = 0

        self.victims_rescued = 0


    def update(self, grid_service):
        if self.status == "idle":
            if self.rescue_queue:
                #escolhe primeira vitima da fila
                self.current_target = self.rescue_queue.popleft()
                self.status = "moving_to_victim"

            elif self.status == "moving_to_victim":
                tx, ty = self.current_target
                self.move_towards(tx, ty)
                self.steps_taken += 1


                if self.pos_x == tx and self.pos_y == ty:
                    self.status = "rescuing"

            elif self.status == "rescuing":
                grid_service.rescue_victim(self.current_target)
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


                