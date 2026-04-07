from abc import ABC, abstractmethod


class BaseAgent(ABC):
    def __init__(self, id:int, type:str, pos_x:int = 0, pos_y:int = 0):
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
        if direction == 'down':
            self.pos_y += 1
        if direction == 'left':
            self.pos_x -= 1
        if direction == 'right':
            self.pos_x += 1

    def move_towards(self, target_x:int, target_y:int):
        if self.pos_y > target_y:
            self.move('up')
        if self.pos_y < target_y:
            self.move('down')
        if self.pos_x > target_x:
            self.move('left')
        if self.pos_x < target_x:
            self.move('right')

    def send_message(self, agent, message:str):
        agent.receive_message(message)


    @abstractmethod
    def receive_message(self):
        pass  # Implementar lógica de recepção de mensagens

    @abstractmethod
    def perceive_environment(self):
        pass  # Implementar lógica de percepção do ambiente