import numpy as np
from .communication import read_data

class IMUProcessor:
    def __init__(self):

        self.positions = [[0, 0, 0]]
        self.standing = [0, 0, 0]

        self.screw_tightening = False
        self.h = 1  # 固定高度为1米
        self.center_point = [1, 0.5]  # 添加模拟中心点坐标

    def at_initial_position(self, data):
        is_standing = data['offset']['x'] == 0 and data['offset']['y'] == 0 and data['offset']['z'] == 0
        is_state_valid = is_standing and abs(data['angle']['y'] + 50) < 7 and abs(
            data['angle']['x']) < 20 and abs(data['angle']['z']) < 20
        return is_state_valid

    def compute_position(self, angle):
        # 将角度转换为弧度
        x_rad = np.radians(angle['x'])
        y_rad = np.radians(angle['y'])
        
        # 基于中心点计算偏移位置
        x = self.center_point[0] + self.h * np.tan(x_rad)
        y = self.center_point[1] + self.h * np.tan(y_rad)
        
        return [x, y]

    def parse_data(self):
        for data in read_data():
            if data is None or 'angle' not in data:
                yield {
                    "position": [-1, -1, -1]
                }
                continue

            position = self.compute_position(data['angle'])
            self.positions.append(position)
            if len(self.positions) > 20:
                self.positions.pop(0)
            
            if self.at_initial_position(data):
                self.positions[-1] = [self.center_point[0], self.center_point[1], 0]

            yield {
                "position": self.positions[-1],
                **data
            }


class ImuAPI:
    def __init__(self):
        self.imu_processor = IMUProcessor()

    def handle_start(self):
        yield from self.imu_processor.parse_data()
