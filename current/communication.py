import serial
import json

def read_data(timeout=1):
    buffer = ""
    try:
        with serial.Serial("/dev/ttyUSB0", 9600, timeout=timeout) as ser:
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
    except serial.SerialException as e:
        print(f"Current serial error: {e}")
