class Config:
    def __init__(self):
        self.imu = ImuConfig()
        self.init_screws = []
        self.map_physics_width = 2
        self.map_physics_height = 2

class ImuConfig:
    def __init__(self):
        self.vertical_h = 1.0
        self.center_point = [0, 0]

config = Config()