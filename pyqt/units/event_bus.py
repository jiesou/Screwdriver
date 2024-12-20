from PyQt5.QtCore import QObject, pyqtSignal
from typing import Dict, Any
import threading

from processor import ProcessorAPI
from .stored_config import stored_config

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
        
        def data_stream_handler():
            for data in self.processor_api.handle_start_moving():
                self.state = data
        self.data_thread = threading.Thread(target=data_stream_handler, daemon=True)
        self.data_thread.start()

    @property 
    def state(self) -> Dict[str, Any]:
        return self._state

    @state.setter
    def state(self, new_state: Dict[str, Any]):
        self._state.update(new_state)
        self.state_updated.emit(new_state)

    def import_screws(self, screws):
        self.processor_api.set_screws(screws)
        stored_config['init_screws'] = screws
        self.state = {'screws': screws}

    def export_screws(self):
        return self.state.get('screws', [])

# 全局单例
event_bus = EventBus()