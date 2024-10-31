import copy
import numpy as np
from imu import ImuAPI
from current import CurrentAPI

class ScrewMap:
    def __init__(self, screws):
        self.screws = screws.copy()

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
            if distance < current_min_distance:
                current_min_distance = distance
                current_closest_screw = screw
        return current_closest_screw

    def remove_screw(self, screw):
        print("removed", screw)
        self.screws.remove(screw)


class ProcessorAPI:
    def __init__(self, screws):
        self.screw_map: ScrewMap = ScrewMap(screws)
        self.imu_api = ImuAPI()
        self.current_api = CurrentAPI()
        self.current_screw_map = copy.deepcopy(self.screw_map)

    def requirement_analyze(self, imu_data, current_data):
            located_screw = self.current_screw_map.locate_closest_screw(
                imu_data["position"],
                self.current_screw_map.filter_screws_in_range(imu_data["position"])
            )

            if self.current_api.is_working:
                located_screw["status"] = "已完成"

            # 返回分析结果
            return {
                "positon": imu_data["position"],
                "located_screw": located_screw,
                "is_screw_tightening": self.current_api.is_working,
                "screw_count": len(self.current_screw_map.screws)
            }
    
    def handle_start_moving(self):
        imu_flow = self.imu_api.handle_start()
        current_flow = self.current_api.handle_start()
        
        while True:
            imu_data = next(imu_flow)
            current_data = next(current_flow)
            yield  self.requirement_analyze(imu_data, current_data)

    def handle_reset_desktop_coordinate_system(self):
        self.imu_api.imu_processor.positions = [[0, 0, 0]]


