from PyQt5.QtCore import QObject, pyqtSignal
from .streamer import Streamer

class EventBus(QObject):
    server_connected_changed = pyqtSignal(bool)
    counter_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self._server_connected = False
        self._counter = -1
        self.moving_streamer = Streamer()
        
        # 连接信号
        self.moving_streamer.connection_changed.connect(self.set_server_connected)

    @property
    def server_connected(self):
        return self._server_connected

    @server_connected.setter
    def server_connected(self, value):
        self._server_connected = value
        self.server_connected_changed.emit(value)

    def set_server_connected(self, connected):
        self.server_connected = connected

# 全局事件总线实例
event_bus = EventBus()