# commander.py — Agente BDI (Belief, Desire, Intention) — Comandante Central
from agents.base_agent import BaseAgent
from environment.cell import CellState
from agents.firefighter import Firefighter
from agents.rescuer_sequential import RescuerSequential
from agents.rescuer_optimizer import RescuerOptimizer

class Commander(BaseAgent):
    def __init__(self, id:int, grid_size:int = 20):
        super().__init__(id, "commander")
        self.grid_size = grid_size
        self.beliefs = {}  # Crenças sobre o ambiente (ex: (x1,y1): incêndio, (x2,y2): vítimas, (x3,y3): normal...)
        self.desires = {"fire_to_extinguish": [], "victims_to_save": []}  # Desejos ou objetivos (ex: apagar incêndios, resgatar vítimas)
        self.intentions = {} # Intenções ou planos de ação (ex: enviar bombeiro para apagar fogo, enviar socorrista para resgatar vítima)

        self.firefighters = {} # registro dos bombeiros por quadrante
        self.rescuers = None
    

    # registros dos agentes bombeiros e socorristas
    def register_firefighter(self, quadrant_id: int, firefighter):
        self.firefighters[quadrant_id] = firefighter

    def register_rescuers(self, rescuer_sequential, rescuer_optimizer):
        self.rescuers = [rescuer_sequential, rescuer_optimizer]


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
                if key not in self.desires["fire_to_extinguish"]:
                    self.desires["fire_to_extinguish"].append(key)
            if self.beliefs[key] in (CellState.VICTIM,CellState.FIRE_AND_VICTIM):
                if key not in self.desires["victims_to_save"]:
                    self.desires["victims_to_save"].append(key)
            if self.beliefs[key] == CellState.NORMAL:
                if key in self.desires["victims_to_save"]:
                    self.desires["victims_to_save"].remove(key)
                if key in self.desires["fire_to_extinguish"]:
                    self.desires["fire_to_extinguish"].remove(key)


    def _generate_intentions(self):
        self.intentions = []  # limpa intenções antigas

        self._generate_fire_intentions()
        self._generate_rescue_intentions()
    
    def _generate_fire_intentions(self):      # Gera intenções com base nos desejos (ex: se o desejo é apagar um incêndio, a intenção pode ser enviar um bombeiro para isso)
        fires_by_quadrants = {1: [], 2: [], 3: [], 4: []}
        for fire in self.desires["fire_to_extinguish"]:
            q = self._get_quadrant(fire[0], fire[1])
            fires_by_quadrants[q].append(fire)

        for quadrant, fires in fires_by_quadrants.items():
            if not fires:
                continue

            self.intentions.append(
                {
                    "type": "extinguish_fire", 
                    "firefighter": quadrant, 
                    "targets": fires[0]
                }
            ) 

            if len(fires) > 1:

                idle_quadrant = self._find_idle_firefighter(exclude=quadrant)
                if idle_quadrant is not None:
                    self.intentions.append(
                        {
                            "type": "extinguish_fire", 
                            "firefighter": quadrant, 
                            "targets": fires[1:]
                        }
                )
                
    def _get_quadrant(self, x: int, y: int) -> int:
        half = self.grid_size // 2
        if x < half and y < half:
            return 1
        elif x >= half and y < half:
            return 2
        elif x < half and y >= half:
            return 3
        else:
            return 4


    def _generate_rescue_intentions(self):
        victims = self.desires["victims_to_save"]
        if not victims:
            return

        # Divide alternadamente entre os dois socorristas
        list_sequential = victims[0::2]  # índices pares
        list_optimizer  = victims[1::2]  # índices ímpares

        if list_sequential:
            self.intentions.append({
                "type": "RESCUE_VICTIMS",
                "rescuer": "sequential",
                "targets": list_sequential
            })
        if list_optimizer:
            self.intentions.append({
                "type": "RESCUE_VICTIMS",
                "rescuer": "optimizer",
                "targets": list_optimizer
            })

    def _find_idle_firefighter(self, exclude: int):
        """Retorna o quadrante de um bombeiro ocioso, excluindo o quadrante informado."""
        for quadrant, firefighter in self.firefighters.items():
            if quadrant != exclude and firefighter.state == "idle":
                return quadrant
        return None


    def execute_plan(self):
        """Envia comandos aos agentes com base nas intenções geradas."""
        for intention in self.intentions:

            if intention["type"] == "EXTINGUISH_FIRE":
                quadrant = intention["firefighter_quadrant"]
                firefighter = self.firefighters.get(quadrant)
                if firefighter:
                    firefighter.receive_message({
                        "type": "GO_EXTINGUISH",
                        "target": intention["target"]
                    })

            elif intention["type"] == "RESCUE_VICTIMS":
                if intention["rescuer"] == "sequential" and len(self.rescuers) > 0:
                    self.rescuers[0].receive_message(intention["targets"])
                elif intention["rescuer"] == "optimizer" and len(self.rescuers) > 1:
                    self.rescuers[1].receive_message(intention["targets"])


    def update(self):
        """Ciclo BDI completo — chamar uma vez por tick."""
        self.generate_desires()
        self._generate_intentions()
        self.execute_plan()


    def plan_actions(self):            # Planeja ações específicas para alcançar as intenções (ex: escolher qual agente enviar)
        pass
    
    def perceive_environment(self, grid):
        # O comandante pode ter uma visão limitada do ambiente, dependendo das informações recebidas dos drones
        pass