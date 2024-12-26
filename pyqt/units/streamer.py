import json
import asyncio
from PyQt6.QtCore import QObject
import aiohttp
from .state_bus import state_bus

class Streamer(QObject):
    def __init__(self):
        super().__init__()
        self._session = None

    async def start_stream(self, config = {
        "init_screws": [
            { "tag": "1", "position": { "x": 1.05, "y": 1.2, "allowOffset": 0.08 } },
            { "tag": "2", "position": { "x": 1.05, "y": 0.8, "allowOffset": 0.08 } },
            { "tag": "3", "position": { "x": 1.5, "y": 1.2, "allowOffset": 0.1 } },
            { "tag": "4", "position": { "x": 1.5, "y": 0.8, "allowOffset": 0.1 } }
        ],
        "imu": {
            "vertical_h": 1.0,
            "center_point": [0, 0]
        }
    }):
        """启动数据流"""
        try:
            if self._session is None:
                self._session = aiohttp.ClientSession()
                
            async with self._session.post('http://localhost:3000/api/start_moving', json={
                'screws': config.init_screws,
                'h': config.imu.vertical_h,
                'center_point': config.imu.center_point
            }) as response:
                state_bus.loading = False
                state_bus.connection = True
                
                while True:
                    data = await response.content.readline()
                    if not data:
                        break
                        
                    json_data = json.loads(data)
                    state_bus.state = json_data
                    
        except Exception as e:
            print(f"Stream error: {e}")
            state_bus.connection = False
            raise


    def start(self):
        state_bus.doing = True
        state_bus.loading = True
        asyncio.ensure_future(self.start_stream())
        return "正在连接..."

    def stop(self):
        if self._session:
            asyncio.ensure_future(self._session.close())
            self._session = None
        state_bus.doing = False
        state_bus.connection = False
        return "已停止"
    
streamer = Streamer()