import json
import asyncio
from PyQt5.QtCore import QObject
import aiohttp
from .event_bus import event_bus

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
                event_bus.loading = False
                event_bus.connection = True
                
                while True:
                    data = await response.content.readline()
                    if not data:
                        break
                        
                    json_data = json.loads(data)
                    event_bus.state = json_data
                    
        except Exception as e:
            print(f"Stream error: {e}")
            event_bus.connection = False
            raise


    def start(self):
        event_bus.doing = True
        event_bus.loading = True
        asyncio.ensure_future(self.start_stream())
        return "正在连接..."

    def stop(self):
        if self._session:
            asyncio.ensure_future(self._session.close())
            self._session = None
        event_bus.doing = False
        event_bus.connection = False
        return "已停止"
    
streamer = Streamer()