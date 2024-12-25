import serial
import json
import time

def read_data(timeout=1):
    buffer = ""
    while True:  # 外层无限循环用于重连
        try:
            with serial.Serial("/dev/ttyUSB1", 9600, timeout=timeout) as ser:
                print("电流检测原件串口已连接")
                while True:
                    if ser.in_waiting > 0:
                        buffer += ser.read(ser.in_waiting).decode('utf-8')
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            if line:
                                try:
                                    data = json.loads(line)
                                    yield data
                                except json.JSONDecodeError as e:
                                    print(f"Current JSON decode error: {e} {line}")
                                    yield None
        except Exception as e:
            print(f"电流检测原件串口连接断开，尝试重新连接... {e}")
            yield None
            time.sleep(1)
