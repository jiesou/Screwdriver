import requests
import json
import time
import os

class CurrentCommunicator:
    response = None

    def open_connection(self):
        if self.response is None:
            try:
                self.response = requests.get(
                    os.getenv("CURRENT_SENSOR_HTTP", "http://192.168.4.1/status"),
                    stream=True,
                    timeout=2
                )
                # 后端的 http 故障也直接抛出异常
                self.response.raise_for_status()
                print("[CurrentSensor] 网络已连接")
            except Exception as e:
                print(f"[CurrentSensor] 网络连接失败: {e}")
                self.response = None

    def __init__(self):
        self.open_connection()

    def read_data(self):
        while True:
            try:
                for line in self.response.iter_lines(chunk_size=1, decode_unicode=True):
                    if line and line.startswith('data: '):
                        try:
                            yield json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                print(f"[CurrentSensor] 网络连接断开: {e}")
                time.sleep(1)
                self.response = None
                self.open_connection()
                yield None
                continue
