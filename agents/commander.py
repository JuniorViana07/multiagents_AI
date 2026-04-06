# commander.py — Agente BDI (Belief, Desire, Intention) — Comandante Central
from agents.base_agent import BaseAgent
from environment.cell import CellState

class Commander(BaseAgent):
    def __init__(self, id:int):
        super().__init__(id, "commander")
        self.beliefs = {}  # Crenças sobre o ambiente (ex: (x1,y1): incêndio, (x2,y2): vítimas, (x3,y3): normal...)
        self.desires = {"fire_to_extinguish": set(), "victims_to_save": set()}  # Desejos ou objetivos (ex: apagar incêndios, resgatar vítimas)
        self.intentions = [] # Intenções ou planos de ação (ex: enviar bombeiro para apagar fogo, enviar socorrista para resgatar vítima)
    
    def receive_message(self, message: list):
        # Processa mensagens recebidas dos drones e atualiza crenças, desejos e intenções
        for item in message:
            self.beliefs[(item[0],item[1])] = item[2]

    
    def update_beliefs(self, new_beliefs:dict):        # Atualiza as crenças do comandante com base nas informações recebidas
        self.beliefs.update(new_beliefs)
    
    def generate_desires(self):
        # Gera desejos com base nas crenças atuais (ex: se há um incêndio, o desejo é apagá-lo)
        for key in self.beliefs.keys():
            if self.beliefs[key] in (CellState.FIRE,CellState.FIRE_AND_VICTIM):
                self.desires["fire_to_extinguish"].add(key)
            if self.beliefs[key] in (CellState.VICTIM,CellState.FIRE_AND_VICTIM):
                self.desires["victims_to_save"].add(key)
            if self.beliefs[key] == CellState.NORMAL:
                self.desires["victims_to_save"].discard(key)
                self.desires["fire_to_extinguish"].discard(key)

    
    def generate_intentions(self):      # Gera intenções com base nos desejos (ex: se o desejo é apagar um incêndio, a intenção pode ser enviar um bombeiro para isso)
        pass
    
    def plan_actions(self):            # Planeja ações específicas para alcançar as intenções (ex: escolher qual agente enviar)
        pass
    
    def execute_plan(self):            # Executa o plano de ações, enviando comandos para os agentes
        pass
    
    def perceive_environment(self, grid):
        # O comandante pode ter uma visão limitada do ambiente, dependendo das informações recebidas dos drones
        pass