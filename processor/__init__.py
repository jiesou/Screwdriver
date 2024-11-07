import copy
import numpy as np
import asyncio
import threading
import queue
import time
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
            if space_distance < screw['position']['allowOffset']:
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
    def __init__(self):
        self.imu_api = ImuAPI()
        self.current_api = CurrentAPI()
        self.imu_data = None
        self.current_data = None

        def get_imu_data(self):
            try:
                for imu_data in self.imu_api.handle_start():
                    self.imu_data = imu_data
            except Exception as e:
                print("Error in imu data", e)

        def get_current_data(self):
            try:
                for current_data in self.current_api.handle_start():
                    self.current_data = current_data
            except Exception as e:
                print("Error in current data", e)

        imu_thread = threading.Thread(target=get_imu_data, args=(self,))
        current_thread = threading.Thread(target=get_current_data, args=(self,))

        imu_thread.start()
        current_thread.start()
        print("inited")

    def set_screws(self, screws):
        self.screw_map: ScrewMap = ScrewMap(screws)
        self.current_screw_map = copy.deepcopy(self.screw_map)

    def requirement_analyze(self):
        # 在 current_data["is_working"] 为 True 时，屏蔽掉 position 的更新（振动导致 imu 检测不准）
        # if self.current_data["is_working"]:
        #     for pos in self.imu_api.imu_processor.positions:
        #         formatted_pos = [f"{coord:.2f}" for coord in pos]
        #         print("working", formatted_pos)
        #     print("----- End of positions -----")
        #     if len(self.imu_api.imu_processor.positions) > 1:
        #         self.imu_api.imu_processor.positions = [
        #             self.imu_api.imu_processor.positions[1],
        #             self.imu_api.imu_processor.positions[1],
        #             self.imu_api.imu_processor.positions[1],
        #             self.imu_api.imu_processor.positions[1], 
        #             self.imu_api.imu_processor.positions[1],
        #             self.imu_api.imu_processor.positions[1],
        #             self.imu_api.imu_processor.positions[1],
        #             self.imu_api.imu_processor.positions[1],
        #             self.imu_api.imu_processor.positions[1],
        #             self.imu_api.imu_processor.positions[1]
        #         ]
        #         self.imu_api.imu_processor.standing = self.imu_api.imu_processor.positions[-1]
                
        position = self.imu_api.imu_processor.positions[-1]
        located_screw = self.current_screw_map.locate_closest_screw(
            position,
            self.current_screw_map.filter_screws_in_range(position)
        )
        for screw in self.current_screw_map.screws:
            if "status" not in screw: screw["status"] = "等待中"
            if screw["status"] == "已完成": continue
            screw["status"] = "等待中"
            if self.current_data["is_working"]:
                screw["status"] = "已完成"

        if located_screw is not None and located_screw["status"] != "已完成":
            located_screw["status"] = "已定位"
            if self.current_data["is_working"]:
                located_screw["status"] = "已完成"

        # 返回分析结果
        return {
            "position": position,
            "located_screw": located_screw,
            "is_screw_tightening": self.current_data["is_working"],
            "screw_count": len(self.current_screw_map.screws),
            "screws": self.current_screw_map.screws
        }

    def handle_start_moving(self):
        while True:
            data_snippet = self.requirement_analyze()
            print
            time.sleep(1/60)
            yield data_snippet

    def handle_reset_desktop_coordinate_system(self):
        self.imu_api.imu_processor.positions = [[0, 0, 0]]
