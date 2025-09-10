import serial
import time, os
import numpy as np

CmdPacket_Begin = 0x49   # 起始码
CmdPacket_End = 0x4D     # 结束码
CmdPacketMaxDatSizeRx = 73  # 模块发来的数据包的数据体最大长度

class SerialCommunicator:
    def __init__(self, port, baudrate=115200, timeout=2):
        self.ser_port = port
        self.ser_baudrate = baudrate
        self.ser_timeout = timeout
        # 使用实例变量保存状态
        self.reset_state()
    
    def reset_state(self):
        self.CS = 0  # 校验和
        self.i = 0
        self.RxIndex = 0
        self.cmdLen = 0
        self.buf = bytearray(5 + CmdPacketMaxDatSizeRx)
    
    def Cmd_RxUnpack(self, buf, DLen):
        scaleAccel       = 0.00478515625
        scaleQuat        = 0.000030517578125
        scaleAngle       = 0.0054931640625
        scaleAngleSpeed  = 0.06103515625
        scaleMag         = 0.15106201171875
        scaleTemperature = 0.01
        scaleAirPressure = 0.0002384185791
        scaleHeight      = 0.0010728836

        result = {}
        
        if buf[0] == 0x11:
            ctl = (buf[2] << 8) | buf[1]
            result['subscribe_tag'] = ctl
            result['ms'] = ((buf[6] << 24) | (buf[5] << 16) | (buf[4] << 8) | buf[3])

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
                result['temperature'] = np.short((np.short(buf[L+1]) << 8) | buf[L]) * scaleTemperature
                L += 2

                air_pressure_raw = (buf[L+2] << 16) | (buf[L+1] << 8) | buf[L]
                result['air_pressure'] = np.int32(air_pressure_raw) * scaleAirPressure
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
                result['steps'] = (buf[L+3] << 24) | (buf[L+2] << 16) | (buf[L+1] << 8) | buf[L]
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

    def Cmd_GetPkt(self, byte):
        # 每次接收前不清空状态，只有在一次包结束或错误时重置（避免多个包数据混叠）
        self.CS += byte  # 累计校验和
        if self.RxIndex == 0:  # 起始码
            if byte == CmdPacket_Begin:
                self.i = 0
                self.buf[self.i] = CmdPacket_Begin
                self.i += 1
                self.CS = 0  # 从下一个字节开始重新计算校验和
                self.RxIndex = 1
        elif self.RxIndex == 1:  # 地址码
            self.buf[self.i] = byte
            self.i += 1
            if byte == 255:
                # 地址非法，重置状态
                self.reset_state()
            else:
                self.RxIndex += 1
        elif self.RxIndex == 2:  # 数据体长度
            self.buf[self.i] = byte
            self.i += 1
            if byte > CmdPacketMaxDatSizeRx or byte == 0:
                self.reset_state()
            else:
                self.RxIndex += 1
                self.cmdLen = byte
        elif self.RxIndex == 3:  # 数据体内容
            self.buf[self.i] = byte
            self.i += 1
            if self.i >= self.cmdLen + 3:
                self.RxIndex += 1
        elif self.RxIndex == 4:  # 校验码
            self.CS -= byte
            if (self.CS & 0xFF) == byte:
                self.buf[self.i] = byte
                self.i += 1
                self.RxIndex += 1
            else:
                self.reset_state()
        elif self.RxIndex == 5:  # 结束码
            if byte == CmdPacket_End:
                self.buf[self.i] = byte
                self.i += 1
                # 完整包接收成功后，提取数据体部分进行解析
                result = self.Cmd_RxUnpack(self.buf[3:self.i-2], self.i-5)
                self.reset_state()
                return result
            else:
                self.reset_state()
        else:
            self.reset_state()
        return None

    def Cmd_PackAndTx(self, ser, pDat, DLen):
        if DLen == 0 or DLen > 19:
            return -1  # 非法参数

        # 构建发送包缓存，包括50字节的前导码
        buf = bytearray([0x00]*46) + bytearray([0x00, 0xff, 0x00, 0xff,  CmdPacket_Begin, 0xFF, DLen]) + bytearray(pDat[:DLen])
        # 计算校验和，从地址码开始到数据体结束
        CS = sum(buf[51:51+DLen+2]) & 0xFF  # 取低8位
        buf.append(CS)
        buf.append(CmdPacket_End)  # 添加结束码
        
        try:
            ser.write(buf)
            return 0
        except serial.SerialException as e:
            print(f"串口写入错误: {e}")
            raise

    def read_data(self):
        while True:  # 外层循环用于重连
            try:
                with serial.Serial(self.ser_port, self.ser_baudrate, timeout=self.ser_timeout) as ser:
                    print(f"[IMU {self.ser_port}] 串口已连接")

                    # 1.发送配置参数
                    params = [0] * 11
                    isCompassOn = 0
                    barometerFilter = 2
                    Cmd_ReportTag = 0x0FFF
                    params[0] = 0x12
                    params[1] = 5
                    params[2] = 255
                    params[3] = 0
                    params[4] = ((barometerFilter & 3) << 1) | (isCompassOn & 1)
                    params[5] = 60
                    params[6] = 1
                    params[7] = 3
                    params[8] = 5
                    params[9] = Cmd_ReportTag & 0xff
                    params[10] = (Cmd_ReportTag >> 8) & 0xff
                    self.Cmd_PackAndTx(ser, params, len(params))
                    time.sleep(0.2)

                    # 2.唤醒传感器
                    self.Cmd_PackAndTx(ser, [0x03], 1)
                    time.sleep(0.2)

                    # 3.开启主动上报
                    self.Cmd_PackAndTx(ser, [0x19], 1)

                    # 循环接收数据并处理
                    while True:
                        try:
                            data = ser.read(1)
                            if data:
                                result = self.Cmd_GetPkt(data[0])
                                if result is not None:
                                    yield result
                        except serial.SerialException as e:
                            print(f"[IMU {self.ser_port}] 数据读取错误: {e}")
                            yield None
                            break
                    
            except serial.SerialException as e:
                print(f"[IMU {self.ser_port}] 串口连接断开，尝试重新连接... {e}")
                yield None
                time.sleep(1)
            except Exception as e:
                print(f"[IMU {self.ser_port}] 未知错误: {e}")
                yield None
                time.sleep(1)

    def z_axes_to_zero(self):
        try:
            with serial.Serial(self.ser_port, self.ser_baudrate, timeout=self.ser_timeout) as ser:
                buf = bytearray([0x05])
                print("\nz-axes to zero--\n")
                self.Cmd_PackAndTx(ser, buf, 1)
        except serial.SerialException as e:
            print(f"[IMU {self.ser_port}] 串口操作失败: {e}")