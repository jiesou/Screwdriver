class Config:
    def __init__(self):
        self.imu = ImuConfig()
        self.init_screws = []

class ImuConfig:
    def __init__(self):
        self.vertical_h = 1.0
        self.center_point = [0, 0]