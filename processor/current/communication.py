import requests
import json
import time
import os

class CurrentCommunicator:
    response = None

    def __init__(self):
        if self.response is None:
            try:
                self.response = requests.get(
                    os.getenv("CURRENT_SENSOR_HTTP", "http://ESP-1720F6.lan/status"),
                    stream=True,
                    timeout=1
                )
                self.response.raise_for_status()
                print("[CurrentSensor] 网络已连接")
            except Exception as e:
                print(f"[CurrentSensor] 网络连接失败: {e}")
                time.sleep(1)
                self.response = None

    def read_data(self):
        while True:
            try:
                for line in self.response.iter_lines(decode_unicode=True):
                    if line and line.startswith('data: '):
                        try:
                            yield json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                print(f"[CurrentSensor] 网络连接断开: {e}")
                time.sleep(1)
                self.response = None
                yield None
                continue
