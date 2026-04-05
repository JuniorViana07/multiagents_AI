# base_agent.py — Classe base abstrata para todos os agentes

class BaseAgent():
    def __init__(self, id:int, type:str, pos_x:int, pos_y:int):
        self.id = id
        self.type = type
        self.pos_x = pos_x
        self.pos_y = pos_y

    def get_position(self):
        return (self.pos_x, self.pos_y)

    def set_position(self, x:int, y:int):
        self.pos_x = x
        self.pos_y = y

    def move(self, direction:str):
        if direction == 'up':
            self.pos_y -= 1
        elif direction == 'down':
            self.pos_y += 1
        elif direction == 'left':
            self.pos_x -= 1
        elif direction == 'right':
            self.pos_x += 1
    
    def move_towards(self, target_x, target_y):
        if self.pos_x < target_x:
            self.move('right')
        elif self.pos_x > target_x:
            self.move('left')
        elif self.pos_y < target_y:
            self.move('down')
        elif self.pos_y > target_y:
            self.move('up')

    def send_message(self, agent:BaseAgent, message:str):
        agent.receive_message(message)

    def receive_message(self):
        pass  # Implementar lógica de recepção de mensagens
    
    def perceive_environment(self):
        pass  # Implementar lógica de percepção do ambiente