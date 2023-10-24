class Move:
    def __init__(self, moveto: str):
        self.distance_x_m, self.distance_y_m, self.distance_z_m, self.velocity = map(float, moveto.split(","))
