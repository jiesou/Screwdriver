import requests
import json
import time
import os

# 模块级别的全局变量
response = None
results = []

def open_connection():
    global response
    if response is None:
        try:
            response = requests.get(
                os.getenv("CURRENT_SENSOR_HTTP", "http://ESP-1720F6.lan/status"),
                stream=True,
                timeout=1
            )
            response.raise_for_status()
            print("[CurrentSensor] 网络已连接")
        except Exception as e:
            print(f"[CurrentSensor] 网络连接失败: {e}")
            time.sleep(0.1)
            response = None

# 模块导入时就尝试建立连接
open_connection()

def read_data():
    global response, results
    
    while True:
        if not results:
            if response is None:
                open_connection()
                yield None
                continue
                
            try:
                for line in response.iter_lines(decode_unicode=True):
                    if line and line.startswith('data: '):
                        try:
                            yield json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                print(f"[CurrentSensor] 网络连接断开: {e}")
                response = None
                yield None
                continue

        if results:
            yield results.pop(0)
