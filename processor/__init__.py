import copy, os
import threading
import time
import traceback
from collections.abc import Generator
from turtle import pos
import numpy as np
from dotenv import load_dotenv
load_dotenv()
from .imu import API as ImuAPI
from .current import API as CurrentAPI
from .encoder import API as EncoderAPI
from pyqt.units.types import Position, State, Screw, SensorConnection


class ScrewMap:
    def __init__(self, screws: list[Screw]) -> None:
        self.screws: list[Screw] = copy.deepcopy(screws)
        for screw in self.screws:
            screw.pop("status", None)

    def filter_screws_in_range(self, position: list[float]) -> list[Screw]:
        filtered_map: list[Screw] = []
        unfinished_screws = [screw for screw in self.screws if screw.get("status", "等待中") != "已完成"]
        for screw in unfinished_screws:
            space_distance = np.sqrt(
                (position[0] - screw['position']['x'])**2 +
                (position[1] - screw['position']['y'])**2
            )
            if space_distance < screw['position']['allowOffset']:
                filtered_map.append(screw)
        return filtered_map

    def locate_closest_screw(self, position: list[float], ranged_screws: list[Screw]) -> Screw | None:
        current_min_distance = float('inf')
        current_closest_screw: Screw | None = None
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

    def remove_screw(self, screw: Screw) -> None:
        print("removed", screw)
        self.screws.remove(screw)


class ProcessorAPI:
    finished_products = 0

    def __init__(self):
        self.imu_api = ImuAPI()
        self.current_api = CurrentAPI()
        self.encoder_api = EncoderAPI()
        self.imu_data = {
            "connected_fine": False,
            "position": [0, 0, 0]
        }
        self.current_data = {
            "connected_fine": False,
            "is_working": False
        }
        self.encoder_data = {
            "connected_fine": False,
            "line_length": 1,
        }

        def get_imu_data(self):
            try:
                for data in self.imu_api.handle_start():
                    if data is None:
                        self.imu_data = {
                            "connected_fine": False,
                            "position": [0, 0, 0]
                        }
                        continue
                    self.imu_data = data
            except Exception as e:
                print("[IMU] 线程故障", e)
                traceback.print_exc()
        def get_current_data(self):
            try:
                for data in self.current_api.handle_start():
                    if data is None:
                        self.current_data = {
                            "connected_fine": False,
                            "is_working": False
                        }
                        continue
                    self.current_data = data
            except Exception as e:
                print("[Current] 线程故障", e)
                traceback.print_exc()
        def get_encoder_data(self):
            try:
                for data in self.encoder_api.handle_start():
                    if data is None:
                        self.encoder_data = {
                            "connected_fine": False,
                            "line_length": 1,
                        }
                        continue
                    self.encoder_data = data
            except Exception as e:
                print("[Encoder] 线程故障", e)
                traceback.print_exc()

        imu_thread = threading.Thread(target=get_imu_data, args=(self,), daemon=True)
        current_thread = threading.Thread(target=get_current_data, args=(self,), daemon=True)
        encoder_thread = threading.Thread(target=get_encoder_data, args=(self,), daemon=True)

        imu_thread.start()
        current_thread.start()
        encoder_thread.start()
        print("======Processor Threads started======")

    def set_screws(self, screws: list[Screw]) -> None:
        self.screw_map: ScrewMap = ScrewMap(screws)
        self.current_screw_map = copy.deepcopy(self.screw_map)
    
    def compute_position(self) -> list[float]:
        # 使用 encoder 的线长数据和 imu 的角度数据进行融合计算
        line_length = self.encoder_data.get("line_length", 1)
        imu_angle = self.imu_data.get("angle", {'x':0,'y':0,'z':0})

        print("Line Length:", line_length)
        print("IMU Angle Z:", imu_angle['z'])

        # 极坐标计算：x = r * cos(θ), y = r * sin(θ)
        # IMU angle Z 是欧拉角（度数），转换为弧度
        r = line_length
        theta_deg = imu_angle['z']
        theta = np.radians(theta_deg)
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        return [x, y]

    def requirement_analyze(self) -> State:
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

        position = self.compute_position()
        located_screw = self.current_screw_map.locate_closest_screw(
            position,
            self.current_screw_map.filter_screws_in_range(position)
        )

        completed_count = 0
        for screw in self.current_screw_map.screws:
            if "status" not in screw: screw["status"] = "等待中"
            if screw["status"] == "已完成":
                completed_count += 1
                if completed_count >= len(self.current_screw_map.screws):
                    # 一个产品完成了
                    # 防止“拧紧螺丝状态”继承到下一个产品，而直接将同位螺丝拧下
                    self.current_api.processor.is_working = False
                    self.current_api.processor.appliance_on = True
                    self.current_data["is_working"] = False
                    self.current_screw_map = copy.deepcopy(self.screw_map)
                    self.finished_products += 1
                    break
                continue
            screw["status"] = "等待中"

        if located_screw is not None and located_screw["status"] != "已完成":
            located_screw["status"] = "已定位"
            if self.current_data["is_working"]:
                located_screw["status"] = "已完成"
                # “拧紧螺丝状态”继承到下一个孔位
                self.current_api.processor.is_working = False
                self.current_api.processor.appliance_on = True
                self.current_data["is_working"] = False

        # 返回分析结果
        return State(
            position=Position(x=position[0], y=position[1]),
            located_screw=located_screw,
            is_screw_tightening=self.current_data["is_working"] if self.current_data is not None else False,
            screw_count=len(self.current_screw_map.screws) - completed_count,
            screws=self.current_screw_map.screws,
            products_finished=self.finished_products,
            sensor_connection=SensorConnection(
                imu=self.imu_data["connected_fine"] if self.imu_data is not None else False,
                current=self.current_data["connected_fine"] if self.current_data is not None else False
            )
        )

    def handle_start_moving(self) -> Generator[State]:
        print("======Processor Stream started======")
        while True:
            data_snippet = self.requirement_analyze()
            time.sleep(1/int(os.getenv("PROCESSOR_UPDATE_FREQ", 60)))
            yield data_snippet
