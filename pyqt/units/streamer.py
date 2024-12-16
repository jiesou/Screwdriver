import json
import asyncio
from PyQt5.QtCore import QObject, pyqtSignal
import aiohttp
from .state import ReactiveState

class Streamer(QObject):
    data_received = pyqtSignal(dict)
    connection_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.timeout_ms = 300
        self.event_state = ReactiveState()
        self.event_state.is_doing = False
        self.event_state.loading = False
        
        self.state = ReactiveState()
        self.state.position = None
        self.state.screws = []
        self.state.is_screw_tightening = False
        
        self._session = None
        self._running = False

    async def start_stream(self, config):
        """启动数据流"""
        try:
            if self._session is None:
                self._session = aiohttp.ClientSession()
            
            async with self._session.post('http://localhost:5000/api/start_moving', json={
                'screws': config.init_screws,
                'h': config.imu.vertical_h, 
                'center_point': config.imu.center_point
            }) as response:
                self.event_state.loading = False
                self.event_state.is_doing = True
                self.connection_changed.emit(True)
                
                self._running = True
                while self._running:
                    try:
                        data = await response.content.readline()
                        if not data:
                            break
                        
                        json_data = json.loads(data)
                        # 更新状态
                        for key, value in json_data.items():
                            setattr(self.state, key, value)
                        self.data_received.emit(json_data)
                            
                    except asyncio.TimeoutError:
                        print("Stream timeout")
                        break
                        
        except Exception as e:
            print(f"Stream error: {e}")
            self.connection_changed.emit(False)
            raise
        finally:
            self._running = False

    def stop(self):
        """停止数据流"""
        self._running = False
        self.event_state.is_doing = False
        self.connection_changed.emit(False)
        return "已停止"