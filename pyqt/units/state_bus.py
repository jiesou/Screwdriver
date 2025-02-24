import threading
from typing import Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from processor import ProcessorAPI
from .stored_config import stored_config

class ProcessorStateThread(QThread):
    # 定义信号
    updated = pyqtSignal(dict)
    
    def __init__(self, processor_api):
        super().__init__()
        self.processor_api = processor_api
        
    def run(self):
        for data_snippet in self.processor_api.handle_start_moving():
            self.updated.emit(data_snippet)

class StateBus(QObject):
    updated = pyqtSignal(dict)
    
    _state = {
            'position': [0, 0],
            'screws': [],
            'is_screw_tightening': False,
            'screw_count': 0
        }

    processor_api = ProcessorAPI()

    def __init__(self):
        super().__init__()
        self.processor_api.set_screws(stored_config['init_screws'])
        self.processor_api.imu_top_api.processor.h = stored_config['imu_vertical_h']
        self.processor_api.imu_top_api.processor.center_point = (stored_config['imu_center_point_x'], stored_config['imu_center_point_y'])


        # 创建并启动状态拉取线程
        self.state_thread = ProcessorStateThread(self.processor_api)
        self.state_thread.updated.connect(lambda data: setattr(self, 'state', data))
        self.state_thread.start()

        stored_config.updated.connect(self.update_config)
    
    def update_config(self, updated_config):
        if 'init_screws' in updated_config:
            self.processor_api.set_screws(updated_config['init_screws'])
        
        if 'imu_vertical_h' in updated_config:
            self.processor_api.imu_top_api.processor.h = updated_config['imu_vertical_h']
        
        if 'imu_center_point_x' in updated_config or 'imu_center_point_y' in updated_config:
            x = updated_config.get('imu_center_point_x', stored_config['imu_center_point_x'])
            y = updated_config.get('imu_center_point_y', stored_config['imu_center_point_y'])
            self.processor_api.imu_top_api.processor.center_point = (x, y)

    @property 
    def state(self) -> Dict[str, Any]:
        return self._state

    @state.setter
    def state(self, new_state: Dict[str, Any]):
        self._state.update(new_state)
        self.updated.emit(new_state)

# 全局单例
state_bus = StateBus()