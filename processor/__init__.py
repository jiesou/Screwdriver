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
        self.current_screw_map = copy.deepcopy(self.screw_map)
        self.imu_api = ImuAPI()
        self.current_api = CurrentAPI()
        self.imu_queue = queue.Queue()
        self.current_queue = queue.Queue()

        self.stop_event = threading.Event()
        imu_thread = threading.Thread(target=self.get_imu_data)
        current_thread = threading.Thread(target=self.get_current_data)

        imu_thread.start()
        # current_thread.start()

    def requirement_analyze(self, imu_data, current_data):
            located_screw = self.current_screw_map.locate_closest_screw(
                imu_data["position"],
                self.current_screw_map.filter_screws_in_range(imu_data["position"])
            )

            if current_data["is_working"] and located_screw is not None:
                located_screw["status"] = "已完成"

            # 返回分析结果
            return {
                "position": imu_data["position"],
                "located_screw": located_screw,
                "is_screw_tightening": current_data["is_working"],
                "screw_count": len(self.current_screw_map.screws)
            }
    
    def get_imu_data(self):
        while not self.stop_event.is_set():
            for imu_data in self.imu_api.handle_start():
                self.imu_queue.put(imu_data)

    def get_current_data(self):
        while not self.stop_event.is_set():
            for current_data in self.current_api.handle_start():
                self.current_queue.put(current_data)

    def handle_start_moving(self):
        while True:
            imu_data = self.imu_queue.get()
            current_data = self.current_queue.get()
            if not imu_data:
                continue
            
            data_snippet = self.requirement_analyze(imu_data, current_data)
            yield data_snippet

    def handle_reset_desktop_coordinate_system(self):
        self.imu_api.imu_processor.positions = [[0, 0, 0]]


