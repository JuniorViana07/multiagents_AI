class Hospital():
    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y

    def get_position(self):
        return (self.pos_x, self.pos_y)
    
    def set_position(self, x:int, y:int):
        self.pos_x = x
        self.pos_y = y