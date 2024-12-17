# pyqt/units/event_bus.py
from PyQt5.QtCore import QObject, pyqtSignal
from typing import Dict, Any
from processor import ProcessorAPI
import threading

processor_api = ProcessorAPI()
processor_api.set_screws([])
processor_api.imu_api.processor.h = 1
processor_api.imu_api.processor.center_point = (1, 1)

class EventBus(QObject):
    state_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._state = {
            'position': [0, 0],
            'screws': [],
            'is_screw_tightening': False,
            'screw_count': 0
        }
        
        # Create a thread to handle data stream
        def data_stream_handler():
            for data in processor_api.handle_start_moving():
                self.state = data
            
        self.data_thread = threading.Thread(target=data_stream_handler)
        self.data_thread.daemon = True  # Make thread daemon so it exits when main program exits
        self.data_thread.start()

    @property 
    def state(self) -> Dict[str, Any]:
        return self._state

    @state.setter
    def state(self, new_state: Dict[str, Any]):
        self._state.update(new_state)
        self.state_updated.emit(new_state)

# 全局单例
event_bus = EventBus()