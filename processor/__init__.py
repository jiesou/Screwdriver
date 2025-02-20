import copy, os
import threading
import time
import traceback
import numpy as np
from dotenv import load_dotenv
load_dotenv()
from .imu.top import API as ImuTopAPI
from .imu.end import API as ImuEndAPI
from .current import CurrentAPI


class ScrewMap:
    def __init__(self, screws):
        self.screws = screws.copy()

    def filter_screws_in_range(self, position):
        filtered_map = []
        unfinished_screws = [screw for screw in self.screws if screw["status"] != "已完成"]
        for screw in unfinished_screws:
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
    finished_products = 0

    def __init__(self):
        self.imu_top_api = ImuTopAPI()
        self.imu_end_api = ImuEndAPI()
        self.current_api = CurrentAPI()
        self.imu_top_data = {
            "connected_fine": False,
            "position": [0, 0, 0]
        }
        self.imu_end_data = {
            "connected_fine": False,
            "position": [0, 0, 0]
        }
        self.current_data = None

        def get_imu_top_data(self):
            try:
                for data in self.imu_top_api.handle_start():
                    self.imu_top_data = data
            except Exception as e:
                print("[IMU TOP] 线程故障", e)
                traceback.print_exc()

        def get_imu_end_data(self):
            try:
                for data in self.imu_end_api.handle_start():
                    self.imu_end_data = data
            except Exception as e:
                print("[IMU END] 线程故障", e)
                traceback.print_exc()

        def get_current_data(self):
            try:
                for data in self.current_api.handle_start():
                    self.current_data = data
            except Exception as e:
                print("[Current] 线程故障", e)
                traceback.print_exc()

        tasks = [
            (get_imu_top_data, (self,)),
            (get_imu_end_data, (self,)),
            (get_current_data, (self,))
        ]

        threads = []
        for target, args in tasks:
            thread = threading.Thread(target=target, args=args)
            thread.start()
            threads.append(thread)
        print("======Processor Threads started======")

    def set_screws(self, screws):
        self.screw_map: ScrewMap = ScrewMap(screws)
        self.current_screw_map = copy.deepcopy(self.screw_map)

    def compute_effector_position(self, l1: float = 1, l2: float = 0.1) -> dict:
        """
        使用前向运动学计算终端位置。
        IMU 数据中提供 "angel"（单位°）和 "position"（单位m）。
        processor.h 表示起始点与终端之间固定的垂直位置。
        """

        # 在一个 IMU 断开情况下的 backup 方法
        if "angle" not in self.imu_top_data:
            return self.imu_end_data["position"]
        if "angle" not in self.imu_end_data:
            return self.imu_top_data["position"]
        
        # 获取两个 IMU 的位置数据
        imu_top_position = self.imu_top_data["position"]
        imu_end_position = self.imu_end_data["position"]

        # 得到 imu end 的斜角，从而确认下面三角的 h
        end_angle = self.imu_end_data["angle"]
        # 将角度转换为弧度
        # 屏幕的 x y 和 imu 返回的 x y 相反
        x_rad = -np.radians(end_angle['y'])
        y_rad = np.radians(end_angle['x'])
        z_rad = np.radians(end_angle['z'])
 
        # 0.185 是 IMU 到螺丝刀头的固定距离
        end_h = np.cos(y_rad) *0.185

        # 基于确定的 h 计算偏移位置
        x = end_h * np.tan(x_rad)
        y = end_h * np.tan(y_rad)

        # 应用 z 轴旋转，对 x 和 y 进行旋转变换
        x_rotated = x * np.cos(z_rad) - y * np.sin(z_rad)
        y_rotated = x * np.sin(z_rad) + y * np.cos(z_rad)


        return [imu_top_position[0] + x, imu_top_position[1] + y]


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
        
        position = self.compute_effector_position()

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
        return {
            "position": position,
            "located_screw": located_screw,
            "is_screw_tightening": self.current_data["is_working"] if self.current_data is not None else False,
            "screw_count": len(self.current_screw_map.screws) - completed_count,
            "screws": self.current_screw_map.screws,
            "products_finished": self.finished_products,
            "sensor_connection": {
                "imu_top": self.imu_top_data["connected_fine"] if self.imu_top_data is not None else False,
                "imu_end": self.imu_end_data["connected_fine"] if self.imu_end_data is not None else False,
                "current": self.current_data["connected_fine"] if self.current_data is not None else False
            }
        }

    def handle_start_moving(self):
        print("======Processor Stream started======")
        while True:
            data_snippet = self.requirement_analyze()
            time.sleep(1/int(os.getenv("PROCESSOR_UPDATE_FREQ", 60)))
            yield data_snippet
