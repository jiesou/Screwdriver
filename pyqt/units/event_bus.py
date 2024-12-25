from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
from typing import Dict, Any

from processor import ProcessorAPI
from .stored_config import stored_config

class DataThread(QThread):
    # 定义信号
    data_updated = pyqtSignal(dict)
    
    def __init__(self, processor_api):
        super().__init__()
        self.processor_api = processor_api
        
    def run(self):
        for data in self.processor_api.handle_start_moving():
            self.data_updated.emit(data)

class EventBus(QObject):
    state_updated = pyqtSignal(dict)
    
    processor_api = ProcessorAPI()

    def __init__(self):
        super().__init__()
        self.processor_api.set_screws([
            { "tag": "1", "position": { "x": 1.05, "y": 1.2, "allowOffset": 0.08 } },
            { "tag": "2", "position": { "x": 1.05, "y": 0.8, "allowOffset": 0.08 } },
            { "tag": "3", "position": { "x": 1.5, "y": 1.2, "allowOffset": 0.1 } },
            { "tag": "4", "position": { "x": 1.5, "y": 0.8, "allowOffset": 0.1 } }
        ])
        self.processor_api.imu_api.processor.h = stored_config['imu_vertical_h']
        self.processor_api.imu_api.processor.center_point = (stored_config['imu_center_point_x'], stored_config['imu_center_point_y'])

        self._state = {
            'position': [0, 0],
            'screws': [],
            'is_screw_tightening': False,
            'screw_count': 0
        }
        
        # 创建并启动数据线程
        self.data_thread = DataThread(self.processor_api)
        self.data_thread.data_updated.connect(self.update_state)
        self.data_thread.start()

    @property 
    def state(self) -> Dict[str, Any]:
        return self._state

    @state.setter
    def state(self, new_state: Dict[str, Any]):
        self._state.update(new_state)
        self.state_updated.emit(new_state)

    @pyqtSlot(dict)
    def update_state(self, data):
        self.state = data

    def import_screws(self, screws):
        self.processor_api.set_screws(screws)
        stored_config['init_screws'] = screws
        self.state = {'screws': screws}

    def export_screws(self):
        return self.state.get('screws', [])

# 全局单例
event_bus = EventBus()