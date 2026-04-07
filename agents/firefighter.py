# firefighter.py — Agente Reativo Baseado em Modelo (Bombeiro)
# recebe as coordenadas do fogo 
#
#
from agents.base_agent import BaseAgent

class Firefighter(BaseAgent):
    def __init__(self, id:int, pos_x:int, pos_y:int, quadrant:int = 1):
        super().__init__(id, "firefighter", pos_x, pos_y)
        self.state = 'idle' # o bombeiro pode estar "idle" ou "moving_to_fire" ou "extinguishing", importante para a lógica de pedir auxilio para um bombeiro de outro quadrante
        self.quadrant = quadrant
        self.target = None # coordenada do fogo a ser extinto
        self.steps_taken = 0
        self.initial_position = (pos_x, pos_y)


    def receive_message(self, message):
        # vai receber o commander.desires.get("fire_to_extinguish") -> um set() de coordenadas.
        new_target = message.get("target")
        if new_target is None:
            return

        # Hardening: não troca de alvo enquanto já estiver executando outro.
        if self.target is not None and self.target != new_target:
            return

        self.target = new_target


    def perceive_environment(self, grid):
        # O bombeiro pode perceber apenas a célula em que está localizado
        x, y = self.get_position()
        state = grid.get_cell_state(x, y)
        return (x, y, state)

    def act(self, command:str):
        # O bombeiro pode executar ações como "move_up", "move_down", "move_left", "move_right", "extinguish_fire"
        # Na verdade não faz sentido o bombeiro receber as ações? sendo que ele recebe as coordenadas do fogo.
        if self.state == 'idle' and command.startswith("extinguish_fire"):
            self.state = 'extinguishing'
            # lógica para extinguir o fogo na coordenada do target
        pass

    # movimentação do bombeiro, o bombeiro deve se mover do ponto x,y atual para o ponto x,y do fogo:
    def update(self, grid_service):
        if self.target is None:
            self.state = "idle"
            if (self.pos_x, self.pos_y) != self.initial_position:
                self.move_towards(self.initial_position[0], self.initial_position[1]) # volta para a posição inicial
                self.steps_taken += 1
            return

        tx, ty = self.target

        # Extingue de forma robusta ao chegar no alvo, independente do estado anterior.
        if self.pos_x == tx and self.pos_y == ty:
            self.state = "extinguishing"
            extinguished_target = self.target
            grid_service.extinguish_fire(extinguished_target[0], extinguished_target[1])
            self.state = "idle"
            self.target = None
            return extinguished_target

        self.state = "moving_to_fire"
        self.move_towards(tx, ty)
        self.steps_taken += 1
        if self.pos_x == tx and self.pos_y == ty:
            self.state = "extinguishing"
        return None
