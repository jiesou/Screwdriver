import copy, os
import threading
import time, math
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
        根据 top 和 end IMU 的 angle 数据计算终端位置。
        注意：忽略传感器返回的不可信 "position" 字段，仅使用 "angle" 数据计算方向。
        """
        # 若 END 传感器无 "angle" 数据，则直接返回 TOP 端的 position（备份方案）
        if "angle" not in self.imu_end_data:
            return self.imu_top_data["position"]
        
        tx_rad = np.radians(self.imu_top_data['angle']['x'])
        ty_rad = np.radians(-self.imu_top_data['angle']['y'])
        top_start = np.array([0, 0, 0])
        top_dir = np.array([
            math.tan(ty_rad),   
            math.tan(tx_rad),   
            -1.0               
        ])
        # 归一化：只保留方向信息。并固定射线长度为 -1.0
        top_dir = top_dir / np.linalg.norm(top_dir)
        
        # END射线计算
        ex_rad = np.radians(self.imu_end_data['angle']['x'])
        ey_rad = np.radians(-self.imu_end_data['angle']['y'])
        end_start = np.array([0.5, 0.07, -1.0])
        end_dir = np.array([
            math.tan(ey_rad),   
            math.tan(ex_rad),   
            1.0                
        ])
        # 归一化：只保留方向信息。并固定射线长度为 -1.0
        end_dir = end_dir / np.linalg.norm(end_dir)
        

        # ****计算两条射线上的最近点****
        # 向量：如一个向量 V = [vx, vy, vz]，vx 就是 V 在 x 轴的分量，表示水平方向有多长。

        # 计算从 end_start 指向 top_start 的向量 w0
        w0 = top_start - end_start

        # 分别计算点积值
        a = np.dot(top_dir, top_dir)       # top_dir 自己的长度平方（归一化后为1）
        b = np.dot(top_dir, end_dir)        # 两个方向在相同坐标轴上的"重合"程度
        c = np.dot(end_dir, end_dir)         # end_dir 自己的长度平方（归一化后为1）
        d = np.dot(top_dir, w0)              # w0 在 top_dir 方向上的分量（投影长度）
        e = np.dot(end_dir, w0)              # w0 在 end_dir 方向上的分量

        # 计算参数 sc 和 tc，表示从各射线起点沿方向走多少长度可以到达最近点
        # 计算时只考虑方向，不考虑长度（点积后）
        sc = (b * e - c * d) / (a * c - b * b)
        tc = (a * e - b * d) / (a * c - b * b)

        # 利用参数计算两条射线上的最近点坐标
        closest_point_top = top_start + sc * top_dir
        closest_point_end = end_start + tc * end_dir

        # 求中点
        mid_point = (closest_point_top + closest_point_end) / 2
        return mid_point


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
            },
            "imu_top_data": self.imu_top_data,
            "imu_end_data": self.imu_end_data,
        }

    def handle_start_moving(self):
        print("======Processor Stream started======")
        while True:
            data_snippet = self.requirement_analyze()
            time.sleep(1/int(os.getenv("PROCESSOR_UPDATE_FREQ", 60)))
            yield data_snippet
