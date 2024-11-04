from ast import Try
from time import sleep
import numpy as np
from numpy import array
import gatt
import time
import threading

from argparse import ArgumentParser
from array import array
import socket
import sys

mac_address = "67:F8:1E:C8:D6:77"


class AnyDevice(gatt.Device):

    sock_pc = None
    parse_imu_flage = False
    lzchar1 = None
    lzchar2 = None
    callback = None

    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] 蓝牙已连接" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] 蓝牙连接失败：%s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] 蓝牙连接已断开" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]\tService [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]\t\tCharacteristic [%s]" %
                      (self.mac_address, characteristic.uuid))

        # 保持连接
        self.lzchar1 = next(
            c for c in service.characteristics
            if c.uuid == '0000ae01-0000-1000-8000-00805f9b34fb'.lower())
        self.lzchar1.write_value(')'.encode())  # 发送十六进制的0x29，让设备保持连接

        # 尝试采用蓝牙高速通信特性 0x46
        self.lzchar1.write_value(bytes([0x46]))

        # GPIO 上拉
        # self.lzchar1.write_value(bytes([0x27,0x10]))

        # 参数设置
        isCompassOn = 0  # 1=使用磁场融合姿态，0=不使用
        barometerFilter = 2
        Cmd_ReportTag = 0x0FFF  # 功能订阅标识
        params = bytearray([0x00 for i in range(0, 11)])
        params[0] = 0x12
        params[1] = 5  # 静止状态加速度阀值
        params[2] = 255  # 静止归零速度(单位cm/s) 0:不归零 255:立即归零
        params[3] = 0  # 动态归零速度(单位cm/s) 0:不归零
        params[4] = ((barometerFilter & 3) << 1) | (isCompassOn & 1)
        params[5] = 60  # 数据主动上报的传输帧率[取值0-250HZ], 0表示0.5HZ
        params[6] = 1  # 陀螺仪滤波系数[取值0-2],数值越大越平稳但实时性越差
        params[7] = 3  # 加速计滤波系数[取值0-4],数值越大越平稳但实时性越差
        params[8] = 5  # 磁力计滤波系数[取值0-9],数值越大越平稳但实时性越差
        params[9] = Cmd_ReportTag & 0xff
        params[10] = (Cmd_ReportTag >> 8) & 0xff
        self.lzchar1.write_value(params)

        # 主动上报 0x19
        self.lzchar1.write_value(bytes([0x19]))

        self.lzchar2 = next(
            c for c in service.characteristics
            if c.uuid == '0000ae02-0000-1000-8000-00805f9b34fb'.lower())
        self.lzchar2.enable_notifications()

    def descriptor_read_value_failed(self, descriptor, error):
        print('descriptor_value_failed')

    def characteristic_write_value_succeeded(self, characteristic):
        super().characteristic_write_value_succeeded(characteristic)
        print("[%s] wr ok" % (self.mac_address))

    def characteristic_write_value_failed(self, characteristic, error):
        super().characteristic_write_value_failed(characteristic, error)
        print("[%s] wr err %s" % (self.mac_address, error))

    def characteristic_enable_notifications_succeeded(self, characteristic):
        super().characteristic_enable_notifications_succeeded(characteristic)
        print("[%s] notify ok" % (self.mac_address))

    def characteristic_enable_notifications_failed(self, characteristic, error):
        super().characteristic_enable_notifications_failed(characteristic, error)
        print("[%s] notify err. %s" % (self.mac_address, error))

    def characteristic_value_updated(self, characteristic, value):
        # self.parse_imu(value)

        if characteristic.uuid == '0000ae02-0000-1000-8000-00805f9b34fb'.lower():
            if self.parse_imu_flage:
                result = self.parse_imu(value)
                if self.callback is not None:
                    self.callback(result)

            if self.sock_pc is not None:
                print("send blue source data")
                self.sock_pc.sendall(value)

    # 这个是在本地解析
    def parse_imu(self, buf):
        scaleAccel = 0.00478515625
        scaleQuat = 0.000030517578125
        scaleAngle = 0.0054931640625
        scaleAngleSpeed = 0.06103515625
        scaleMag = 0.15106201171875
        scaleTemperature = 0.01
        scaleAirPressure = 0.0002384185791
        scaleHeight = 0.0010728836

        result = {}

        if buf[0] == 0x11:
            ctl = (buf[2] << 8) | buf[1]
            result['subscribe_tag'] = ctl
            result['ms'] = ((buf[6] << 24) | (buf[5] << 16)
                            | (buf[4] << 8) | buf[3])

            L = 7  # 从第7字节开始根据订阅标识tag来解析剩下的数据

            if (ctl & 0x0001) != 0:
                result['accel'] = {
                    'x': np.short((np.short(buf[L+1]) << 8) | buf[L]) * scaleAccel,
                    'y': np.short((np.short(buf[L+3]) << 8) | buf[L+2]) * scaleAccel,
                    'z': np.short((np.short(buf[L+5]) << 8) | buf[L+4]) * scaleAccel
                }
                L += 6

            if (ctl & 0x0002) != 0:
                result['gravity_accel'] = {
                    'x': np.short((np.short(buf[L+1]) << 8) | buf[L]) * scaleAccel,
                    'y': np.short((np.short(buf[L+3]) << 8) | buf[L+2]) * scaleAccel,
                    'z': np.short((np.short(buf[L+5]) << 8) | buf[L+4]) * scaleAccel
                }
                L += 6

            if (ctl & 0x0004) != 0:
                result['angle_accel'] = {
                    'x': np.short((np.short(buf[L+1]) << 8) | buf[L]) * scaleAngleSpeed,
                    'y': np.short((np.short(buf[L+3]) << 8) | buf[L+2]) * scaleAngleSpeed,
                    'z': np.short((np.short(buf[L+5]) << 8) | buf[L+4]) * scaleAngleSpeed
                }
                L += 6

            if (ctl & 0x0008) != 0:
                result['mag'] = {
                    'x': np.short((np.short(buf[L+1]) << 8) | buf[L]) * scaleMag,
                    'y': np.short((np.short(buf[L+3]) << 8) | buf[L+2]) * scaleMag,
                    'z': np.short((np.short(buf[L+5]) << 8) | buf[L+4]) * scaleMag
                }
                L += 6

            if (ctl & 0x0010) != 0:
                result['temperature'] = np.short(
                    (np.short(buf[L+1]) << 8) | buf[L]) * scaleTemperature
                L += 2

                air_pressure_raw = (buf[L+2] << 16) | (buf[L+1] << 8) | buf[L]
                result['air_pressure'] = np.int32(
                    air_pressure_raw) * scaleAirPressure
                L += 3

                height_raw = (buf[L+2] << 16) | (buf[L+1] << 8) | buf[L]
                result['height'] = np.int32(height_raw) * scaleHeight
                L += 3

            if (ctl & 0x0020) != 0:
                result['quaternion'] = {
                    'w': np.short((np.short(buf[L+1]) << 8) | buf[L]) * scaleQuat,
                    'x': np.short((np.short(buf[L+3]) << 8) | buf[L+2]) * scaleQuat,
                    'y': np.short((np.short(buf[L+5]) << 8) | buf[L+4]) * scaleQuat,
                    'z': np.short((np.short(buf[L+7]) << 8) | buf[L+6]) * scaleQuat
                }
                L += 8

            if (ctl & 0x0040) != 0:
                result['angle'] = {
                    'x': np.short((np.short(buf[L+1]) << 8) | buf[L]) * scaleAngle,
                    'y': np.short((np.short(buf[L+3]) << 8) | buf[L+2]) * scaleAngle,
                    'z': np.short((np.short(buf[L+5]) << 8) | buf[L+4]) * scaleAngle
                }
                L += 6

            if (ctl & 0x0080) != 0:
                result['offset'] = {
                    'x': np.short((np.short(buf[L+1]) << 8) | buf[L]) / 1000.0,
                    'y': np.short((np.short(buf[L+3]) << 8) | buf[L+2]) / 1000.0,
                    'z': np.short((np.short(buf[L+5]) << 8) | buf[L+4]) / 1000.0
                }
                L += 6

            if (ctl & 0x0100) != 0:
                result['steps'] = (buf[L+3] << 24) | (buf[L+2] <<
                                                      16) | (buf[L+1] << 8) | buf[L]
                L += 4

                result['motion_status'] = {
                    'walking': bool(buf[L] & 0x01),
                    'running': bool(buf[L] & 0x02),
                    'biking': bool(buf[L] & 0x04),
                    'driving': bool(buf[L] & 0x08)
                }
                L += 1

            if (ctl & 0x0200) != 0:
                result['accel_stability'] = {
                    'x': np.short((np.short(buf[L+1]) << 8) | buf[L]) * scaleAccel,
                    'y': np.short((np.short(buf[L+3]) << 8) | buf[L+2]) * scaleAccel,
                    'z': np.short((np.short(buf[L+5]) << 8) | buf[L+4]) * scaleAccel
                }
                L += 6

            if (ctl & 0x0400) != 0:
                result['adc'] = (buf[L+1] << 8) | buf[L]
                L += 2

            if (ctl & 0x0800) != 0:
                result['GPIO1'] = {
                    'M': (buf[L] >> 4) & 0x0f,
                    'N': buf[L] & 0x0f
                }
                L += 1

            return result
        return None
    

device = None
manager = None
def init_bluetooth():
    global device, manager
    host = None
    port = 6666
    sock = None
    print("host ip: ", host)
    if host is not None:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
        except:
            print("Could not make a connection to the server")
            input("Press enter to quit")
            sys.exit(0)
    print("Connecting bluetooth ...")

    manager = gatt.DeviceManager(adapter_name='hci0')
    device = AnyDevice(manager=manager, mac_address=mac_address)
    device.sock_pc = sock
    if host is None:
        device.parse_imu_flage = True
    
    def runner():
        device.connect()
        manager.run()
    threading.Thread(target=runner, daemon=True).start()

def read_data():
    results = []

    def data_callback(result):
        # yield 数据到外部
        nonlocal results
        results.append(result)

    device.callback = data_callback

    while True:
        if results:
            yield results.pop(0)
        if not device.is_connected():
            print("蓝牙断开，尝试重新连接...")
            reconnect_bluetooth()
            time.sleep(1)  # 等待一段时间后重试

def z_axes_to_zero():
    device.lzchar1.write_value(bytearray([0x05]))

def reconnect_bluetooth():
    while True:
        try:
            init_bluetooth()
            print("蓝牙重新连接……")
            break
        except Exception as e:
            print(f"重新连接失败: {e}")
            time.sleep(5)  # 等待一段时间后重试

init_bluetooth()