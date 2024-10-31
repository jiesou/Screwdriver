import serial
import json

def read_data(timeout=1):
    try:
        with serial.Serial("/dev/ttyUSB0", 9600, timeout=timeout) as ser:
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    print(line)
                    try:
                        data = json.loads(line)
                        yield data
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
    except serial.SerialException as e:
        print(f"Error: {e}")
