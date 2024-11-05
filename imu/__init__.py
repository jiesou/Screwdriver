import numpy as np
from .communication import read_data

class IMUProcessor:
    def __init__(self):

        self.positions = [[0, 0, 0]]
        self.standing = [0, 0, 0]

        self.screw_tightening = False

    def at_initial_position(self, data):
        is_standing = data['offset']['x'] == 0 and data['offset']['y'] == 0 and data['offset']['z'] == 0
        is_state_valid = is_standing and abs(data['angle']['y'] + 50) < 7 and abs(
            data['angle']['x']) < 20 and abs(data['angle']['z']) < 20
        return is_state_valid

    def accumulate_offset_to_position(self, offset):
        if offset['x'] == 0:
            self.standing[0] = self.positions[-1][0]
        if offset['y'] == 0:
            self.standing[1] = self.positions[-1][1]
        new_position = self.standing.copy()
        new_position[0] = self.standing[0] + offset['x']
        new_position[1] = self.standing[1] + offset['y']
        return new_position

    def parse_data(self):
        for data in read_data():
            if data is None:
                yield {
                    "position": [-1, -1, -1]
                }
                continue
            self.positions.append(self.accumulate_offset_to_position(data['offset']))
            if len(self.positions) > 20:
                self.positions.pop(0)
            
            if self.at_initial_position(data):
                self.positions[-1] = [0, 0, 0]

            yield {
                "position": self.positions[-1],
                **data
            }


class ImuAPI:
    def __init__(self):
        self.imu_processor = IMUProcessor()

    def handle_start(self):
        yield from self.imu_processor.parse_data()
