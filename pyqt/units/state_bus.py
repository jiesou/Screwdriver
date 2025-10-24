from .types import State, ConfigData
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from processor import ProcessorAPI
from .stored_config import stored_config

class ProcessorStateThread(QThread):
    # 定义信号，传递 State
    updated: pyqtSignal = pyqtSignal(State)

    def __init__(self, processor_api: ProcessorAPI) -> None:
        super().__init__()
        self.processor_api: ProcessorAPI = processor_api

    def run(self) -> None:
        for data_snippet in self.processor_api.handle_start_moving():
            self.updated.emit(data_snippet)

class StateBus(QObject):
    updated: pyqtSignal = pyqtSignal(State)

    _state: State = State()

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

    def update_config(self, config_data: ConfigData) -> None:
        """处理配置更新，接收完整的 ConfigData"""
        # 更新螺丝配置
        self.processor_api.set_screws(config_data.init_screws)
        
        # 更新 IMU 垂直高度
        self.processor_api.imu_api.processor.h = config_data.imu_vertical_h
        
        # 更新 IMU 中心点
        self.processor_api.imu_api.processor.center_point = (
            config_data.imu_center_point_x,
            config_data.imu_center_point_y
        )

    @property
    def state(self) -> State:
        return self._state

    @state.setter
    def state(self, new_state: State) -> None:
        """接受 State 更新状态，同时发送更新信号。"""
        # 先更新内部状态
        self._state = new_state
        # 发出完整的分析结果
        self.updated.emit(self._state)

# 全局单例
state_bus: StateBus = StateBus()