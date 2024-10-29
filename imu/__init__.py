import json
import numpy as np
from .communication import read_data
import time
import csv


class ScrewMap:
    def __init__(self, screws):
        self.screws = screws

    def filter_screws_in_range(self, position):
        filtered_map = []
        for screw in self.screws:
            space_distance = np.sqrt(
                (position[0] - screw['position']['x'])**2 +
                (position[1] - screw['position']['y'])**2
            )
            if space_distance < screw['position']['allow_offset']:
                filtered_map.append(screw)
        return filtered_map

    def locate_closest_screw(self, position, ranged_screws):
        current_min_distance = float('inf')
        current_closest_screw = None
        for screw in ranged_screws:
            space_distance = np.sqrt(
                (position[0] - screw['position']['x'])**2 +
                (position[1] - screw['position']['y'])**2
            )
            distance = space_distance
            print(f"SCREW: tag: %s, space_distance: %.3f, combined_distance: %.3f" % (
                screw['tag'], space_distance, distance))
            # 找距离最小的
            if distance < current_min_distance:
                current_min_distance = distance
                current_closest_screw = screw
        return current_closest_screw

    def remove_screw(self, screw):
        self.screws.remove(screw)


class IMUProcessor:
    def __init__(self, screw_map):
        self.screw_map = ScrewMap(screw_map)
        self.previous_data = []
        self.positions = [[0, 0, 0]]
        self.standing = [0, 0, 0]
        self.inited = False
        self.init_position_manually = False
        self.screw_tightening = False

    def turning_previous_data(self, data):
        if len(self.previous_data) > 9:
            self.previous_data.pop(0)
        self.previous_data.append(data)

    def at_initial_position(self, data):
        if self.init_position_manually:
            self.init_position_manually = False
            return True
        is_standing = data['offset']['x'] == 0 and data['offset']['y'] == 0 and data['offset']['z'] == 0
        is_state_valid = is_standing and abs(data['angle']['y'] + 50) < 7 and abs(
            data['angle']['x']) < 20 and abs(data['angle']['z']) < 20
        if not self.inited and is_state_valid:
            self.inited = True
        return is_state_valid

    def accumulate_offset_to_position(self, offset):
        new_position = self.standing.copy()
        if offset['x'] == 0:
            self.standing[0] = self.positions[-1][0]
        if offset['y'] == 0:
            self.standing[1] = self.positions[-1][1]
        new_position[0] = self.standing[0] + offset['x']
        new_position[1] = self.standing[1] + offset['y']
        return new_position

    def requirement_process(self, data):
        self.turning_previous_data(data)
        if len(self.previous_data) < 10:
            return False

        located_screw = self.screw_map.locate_closest_screw(self.positions[-1], self.screw_map.filter_screws_in_range(self.positions[-1]))

        if located_screw:
            located_screw['status'] = "已定位"

        if self.screw_tightening and self.inited:
            self.screw_map.remove_screw(located_screw)
            print(f"screwd, {len(self.screw_map.screws)} left")
            self.inited = False
            if len(self.screw_map.screws) < 1:
                print("done")

        return {
            "located_screw": located_screw,
            "is_screw_tightening": self.screw_tightening
        }

    def parse_data(self):
        filename = f"logs/imu_{time.strftime('%Y%m%d%H%M%S')}.csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['position_x', 'position_y', 'offset_x', 'offset_y', 'offset_z', 'angle_x', 'angle_y', 'angle_z', 'angle_accel_x', 'angle_accel_y', 'angle_accel_z',
                             'gravity_accel_x', 'gravity_accel_y', 'gravity_accel_z'])
            for data in read_data():
                if data is None:
                    continue
                new_position = self.accumulate_offset_to_position(
                    data['offset'])
                writer.writerow([new_position[0], new_position[1], data['offset']['x'], data['offset']['y'], data['offset']['z'], data['angle']['x'], data['angle']['y'], data['angle']['z'], data['angle_accel']['x'], data['angle_accel']['y'], data['angle_accel']['z'],
                                 data['gravity_accel']['x'], data['gravity_accel']['y'], data['gravity_accel']['z']])
                if self.at_initial_position(data):
                    new_position = [0, 0, 0]
                self.positions.append(new_position)

                state = self.requirement_process(data)

                yield {
                    "position": new_position,
                    "state": state if state else None,
                    "offset": data['offset'],
                    "angle": data['angle'],
                    "angle_accel": data['angle_accel'],
                    "gravity_accel": data['gravity_accel'],
                }


class API:
    def __init__(self, screw_map):
        self.imu_processor = IMUProcessor(screw_map)

    def handle_start_moving(self):
        for state in self.imu_processor.parse_data():
            yield json.dumps(state)

    def handle_simulate_screw_tightening(self):
        self.imu_processor.screw_tightening = not self.imu_processor.screw_tightening
        print(f"screw_tightening: {self.imu_processor.screw_tightening}")

    def handle_reset_desktop_coordinate_system(self):
        self.imu_processor.init_position_manually = True

    def handle_screw_data(self):
        return json.dumps(self.imu_processor.screw_map.screws)

    def input_current_data(self, data):
        # 电流采样所返回的频率
        self.imu_processor.screw_tightening = data['frequency'] > 18

