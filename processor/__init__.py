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

    def compute_effector_position(self) -> dict:
        """
        根据 top 和 end IMU 的 angle 数据计算终端位置（二维）。
        
        假设：
        - 起始点 S 为 (0,0,0)
        - S 到中间点 M 的距离（弹簧长度） L_spring = 0.3
        - 中间点 M 到连杆传感器所在点的距离 L_connector = 0.1
        - 中间点 M 到终端位置的距离 L_effector = 0.18 (因此终端距离传感器 0.08)
        
        注意：忽略传感器返回的不可信 "position" 字段，仅使用 "angle" 数据计算方向。
        """
        import math
        # 若任一传感器无 "angle" 数据，则直接返回另一端的 "position"（备份方案）
        if "angle" not in self.imu_top_data:
            return self.imu_end_data["position"]
        if "angle" not in self.imu_end_data:
            return self.imu_top_data["position"]

        def compute_normalized_direction(angle: dict) -> tuple:
            # 根据 top.py 中的计算方法，只计算水平方向（二维）
            x_rad = -math.radians(angle.get('y', 0))
            y_rad = math.radians(angle.get('x', 0))
            z_rad = math.radians(angle.get('z', 0))
            x_off = math.tan(x_rad)
            y_off = math.tan(y_rad)
            # 如果启用 Z 轴校正，则应用旋转变换
            if os.environ.get('ENABLE_Z_AXIS_CORRECTION') == 'True':
                x_rot = x_off * math.cos(z_rad) - y_off * math.sin(z_rad)
                y_rot = x_off * math.sin(z_rad) + y_off * math.cos(z_rad)
            else:
                x_rot = x_off
                y_rot = y_off
            norm = math.sqrt(x_rot * x_rot + y_rot * y_rot)
            if norm == 0:
                return (0, 0)
            return (x_rot / norm, y_rot / norm)

        d_top = compute_normalized_direction(self.imu_top_data["angle"])  # top 传感器方向
        d_end = compute_normalized_direction(self.imu_end_data["angle"])  # end 传感器方向

        # 固定参数（单位：米）
        L_spring = 0.3      # 起始点 S 到中间点 M
        L_connector = 0.1   # 中间点 M 到传感器所在点（第二个点）
        L_effector = 0.18   # 中间点 M 到终端位置

        # 假设起始点 S 固定为原点 (0, 0, 0)
        S = (0.0, 0.0, 0.0)
        # 计算中间点 M（沿 top 传感器方向延伸 L_spring）
        M = (S[0] + L_spring * d_top[0],
            S[1] + L_spring * d_top[1],
            0.0)
        # 如果需要，可以计算传感器所在点 p2（沿 end 传感器方向，从 M 延伸 L_connector）
        p2 = (M[0] + L_connector * d_end[0],
            M[1] + L_connector * d_end[1],
            0.0)
        # 终端位置 T：从中间点 M 沿 end 传感器方向延伸 L_effector
        T = (M[0] + L_effector * d_end[0],
            M[1] + L_effector * d_end[1],
            0.0)

        return [T[0], T[1]]


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
