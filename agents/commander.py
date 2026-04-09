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
        self.drones = {}
        self.extinguished_fires = []
        self.rescued_victims = []
        self.active_rescuer = "optimizer"
    

    # registros dos agentes bombeiros e socorristas
    def register_firefighter(self, quadrant_id: int, firefighter):
        self.firefighters[quadrant_id] = firefighter

    def register_rescuers(self, rescuer_sequential, rescuer_optimizer):
        self.rescuers = [rescuer_sequential, rescuer_optimizer]

    def register_drones(self, drone):
        self.drones[drone.id] = drone

    def set_active_rescuer(self, rescuer_mode: str):
        mode = str(rescuer_mode).strip().lower()
        if mode in ("sequential", "optimizer"):
            self.active_rescuer = mode


    def receive_message(self, message: list):
        # Processa mensagens recebidas dos drones e atualiza crenças, desejos e intenções
        for item in message:
            self.beliefs[(item[0],item[1])] = item[2]

    
    def update_beliefs(self, new_beliefs:dict):        # Atualiza as crenças do comandante com base nas informações recebidas
        self.beliefs.update(new_beliefs)

    def register_extinguished_fire(self, fire: tuple):
        if fire not in self.extinguished_fires:
            self.extinguished_fires.append(fire)
        self.beliefs[fire] = CellState.NORMAL

    def register_rescued_victim(self, victim: tuple):
        if victim not in self.rescued_victims:
            self.rescued_victims.append(victim)
        self.beliefs[victim] = CellState.NORMAL
    
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
            # verificação se o fogo já não é target de um bombeiro, para evitar enviar dois bombeiros.
            if any(firefighter.target == fire for firefighter in self.firefighters.values()):
                continue
            q = self._get_quadrant(fire[0], fire[1])
            fires_by_quadrants[q].append(fire)

        reserved_firefighters = set()
        for quadrant, fires in fires_by_quadrants.items():
            if not fires:
                continue

            pending_fires = list(fires)
            firefighter = self.firefighters.get(quadrant)
            if firefighter and firefighter.target is None:
                target = pending_fires.pop(0)
                self.intentions.append(
                    {
                        "type": "EXTINGUISH_FIRE",
                        "firefighter": quadrant,
                        "targets": target
                    }
                )
                reserved_firefighters.add(quadrant)

            while pending_fires:
                idle_quadrant = self._find_idle_firefighter(
                    exclude=quadrant,
                    reserved=reserved_firefighters
                )
                if idle_quadrant is None:
                    break

                target = pending_fires.pop(0)
                self.intentions.append(
                    {
                        "type": "EXTINGUISH_FIRE",
                        "firefighter": idle_quadrant,
                        "targets": target
                    }
                )
                reserved_firefighters.add(idle_quadrant)
                print(f"o bombeiro {idle_quadrant} tá relaxando")
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
        victims = [
            victim
            for victim in self.desires["victims_to_save"]
            if not self._is_victim_assigned(victim)
        ]
        if not victims:
            return

        if self.active_rescuer == "sequential":
            self.intentions.append({
                "type": "RESCUE_VICTIMS",
                "rescuer": "sequential",
                "targets": victims
            })
        else:
            self.intentions.append({
                "type": "RESCUE_VICTIMS",
                "rescuer": "optimizer",
                "targets": victims
            })

    def _is_victim_assigned(self, victim: tuple):
        if not self.rescuers:
            return False

        for rescuer in self.rescuers:
            if rescuer.current_target == victim:
                return True

            if hasattr(rescuer, "queued_victims"):
                if victim in rescuer.queued_victims:
                    return True
            elif victim in rescuer.rescue_queue:
                return True

        return False

    def _find_idle_firefighter(self, exclude: int, reserved=None):
        """Retorna o quadrante de um bombeiro ocioso, excluindo o quadrante informado."""
        if reserved is None:
            reserved = set()

        for quadrant, firefighter in self.firefighters.items():
            if (
                quadrant != exclude
                and quadrant not in reserved
                and firefighter.state == "idle"
                and firefighter.target is None
            ):
                return quadrant
        return None


    def execute_plan(self):
        """Envia comandos aos agentes com base nas intenções geradas."""
        #print(f"Commander {self.id} executing plan with intentions: {self.intentions}")
        for intention in self.intentions:

            if intention["type"] == "EXTINGUISH_FIRE":
                quadrant = intention["firefighter"]
                firefighter = self.firefighters.get(quadrant)
                if firefighter:
                    #print("fire of babylon")
                    firefighter.receive_message({
                        "type": "GO_EXTINGUISH",
                        "target": intention["targets"]
                    })

            elif intention["type"] == "RESCUE_VICTIMS":
                #print("ajuda o maluco que tá doente")
                if intention["rescuer"] == "sequential" and len(self.rescuers) > 0:
                    self.rescuers[0].receive_message(intention["targets"])
                elif intention["rescuer"] == "optimizer" and len(self.rescuers) > 1:
                    self.rescuers[1].receive_message(intention["targets"])


    def update(self,service):
        """Ciclo BDI completo — chamar uma vez por tick."""
        #print(f"Commander {self.id} updating beliefs, desires, intentions...")
        #print(f"Current beliefs: {self.beliefs}")
        #print(f"Current desires: {self.desires}")
        #print(f"Current intentions: {self.intentions}")
        #verifica se os incêndios que ele tinha como desejo apagar já foram apagados, para atualizar as crenças e desejos.
        for drone in self.drones.values():
            drone.patrol(service.grid)
            visible_cells = drone.perceive_environment(service.grid)
            self.receive_message(visible_cells)
        for fire_fighter in self.firefighters.values():
            result = fire_fighter.update(service)
            if result is not None:
                self.register_extinguished_fire(result)

        if self.rescuers:
            for rescuer in self.rescuers:
                result = rescuer.update(service)
                if result is not None:
                    self.register_rescued_victim(result)

        self.generate_desires()
        self._generate_intentions()
        self.execute_plan()


    def plan_actions(self):            # Planeja ações específicas para alcançar as intenções (ex: escolher qual agente enviar)
        pass
    
    def perceive_environment(self, grid):
        # O comandante pode ter uma visão limitada do ambiente, dependendo das informações recebidas dos drones
        pass
