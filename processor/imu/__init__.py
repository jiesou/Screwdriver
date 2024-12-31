import os
import numpy as np
from .communication import read_data

class IMUProcessor:
    h = 1
    center_point = (0.0, 0.0)

    def __init__(self):
        self.positions = [[0, 0]]
        self.standing = [0, 0]
        self.screw_tightening = False

    def at_initial_position(self, data):
        is_standing = data['offset']['x'] == 0 and data['offset']['y'] == 0 and data['offset']['z'] == 0
        is_state_valid = is_standing and abs(data['angle']['y'] + 50) < 7 and abs(
            data['angle']['x']) < 20 and abs(data['angle']['z']) < 20
        return is_state_valid

    def compute_position(self, angle):
        # 将角度转换为弧度
        # 屏幕的 x y 和 imu 返回的 x y 相反
        x_rad = -np.radians(angle['y'])
        y_rad = np.radians(angle['x'])
        z_rad = np.radians(angle['z'])

        # 基于中心点计算偏移位置
        x = self.h * np.tan(x_rad)
        y = self.h * np.tan(y_rad)

        # 只在启用 Z 轴矫正时进行旋转变换
        if os.environ.get('ENABLE_Z_AXIS_CORRECTION') == 'True':
            # 应用 z 轴旋转，对 x 和 y 进行旋转变换
            x_rotated = x * np.cos(z_rad) - y * np.sin(z_rad)
            y_rotated = x * np.sin(z_rad) + y * np.cos(z_rad)
        else:
            x_rotated = x
            y_rotated = y

        # 将旋转后的坐标平移回中心点
        x_final = self.center_point[0] + x_rotated
        y_final = self.center_point[1] + y_rotated

        return [x_final, y_final]

    def parse_data(self):
        for data in read_data():
            if data is None or 'angle' not in data:
                yield {
                    "connected_fine": False,
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
                "connected_fine": True,
                "position": self.positions[-1],
                **data
            }


class ImuAPI:
    def __init__(self):
        self.processor = IMUProcessor()

    def handle_start(self):
        yield from self.processor.parse_data()
