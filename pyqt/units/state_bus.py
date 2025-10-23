import threading
from typing import Dict
from .types import StateDict, PartialState, Screw, Position, ConfigUpdate
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from processor import ProcessorAPI
from .stored_config import stored_config

class ProcessorStateThread(QThread):
    # 定义信号
    updated: pyqtSignal = pyqtSignal(dict)

    def __init__(self, processor_api: ProcessorAPI) -> None:
        super().__init__()
        self.processor_api: ProcessorAPI = processor_api

    def run(self) -> None:
        for data_snippet in self.processor_api.handle_start_moving():
            self.updated.emit(data_snippet)

class StateBus(QObject):
    updated: pyqtSignal = pyqtSignal(dict)

    # 使用 StateDict 作为静态类型，运行时仍然用普通 dict 保持兼容
    _state: StateDict = {
        'position': [0, 0],
        'screws': [],
        'is_screw_tightening': False,
        'screw_count': 0
    }

    processor_api: ProcessorAPI = ProcessorAPI()

    def __init__(self) -> None:
        super().__init__()
        self.processor_api.set_screws(stored_config['init_screws'])
        self.processor_api.imu_api.processor.h = stored_config['imu_vertical_h']
        self.processor_api.imu_api.processor.center_point = (
            stored_config['imu_center_point_x'],
            stored_config['imu_center_point_y'],
        )

        self.state_thread: ProcessorStateThread = ProcessorStateThread(self.processor_api)
        self.state_thread.updated.connect(lambda data: setattr(self, 'state', data))
        self.state_thread.start()

        stored_config.updated.connect(self.update_config)

    def update_config(self, updated_config: ConfigUpdate) -> None:
        if 'init_screws' in updated_config:
            self.processor_api.set_screws(updated_config['init_screws'])

        if 'imu_vertical_h' in updated_config:
            self.processor_api.imu_api.processor.h = updated_config['imu_vertical_h']

        if 'imu_center_point_x' in updated_config or 'imu_center_point_y' in updated_config:
            x = updated_config.get('imu_center_point_x', stored_config['imu_center_point_x'])
            y = updated_config.get('imu_center_point_y', stored_config['imu_center_point_y'])
            self.processor_api.imu_api.processor.center_point = (x, y)

    @property
    def state(self) -> StateDict:
        return self._state

    @state.setter
    def state(self, new_state: PartialState) -> None:
        """接受部分更新 PartialState 或普通 dict，向后兼容老的写法。"""
        # 保持运行时兼容：把 TypedDict 当作普通 dict 来更新
        self._state.update(new_state)  # type: ignore[arg-type]
        self.updated.emit(new_state)  # 发出实际更新的片段

# 全局单例
state_bus: StateBus = StateBus()