import serial
import time, os
import numpy as np
from array import array

# 设置正确的串口参数------------------------
ser_port = "/dev/ttyUSB0"     #这是缺省串口号，应当被下方 read_data 传入的参数覆盖，windows系统写成COMx，若是linux则要根据所用系统进行调整如写成/dev/ttyUSBx或/dev/ttySx
ser_baudrate = 115200 # 串口波特率
ser_timeout = 2 # 串口操作超时时间


def Cmd_RxUnpack(buf, DLen):
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

CmdPacket_Begin = 0x49   # 起始码
CmdPacket_End = 0x4D     # 结束码
CmdPacketMaxDatSizeRx = 73  # 模块发来的数据包的数据体最大长度

CS = 0  # 校验和
i = 0
RxIndex = 0

buf = bytearray(5 + CmdPacketMaxDatSizeRx) # 接收包缓存
cmdLen = 0 # 长度

def Cmd_GetPkt(byte):
    global CS, i, RxIndex, buf, cmdLen
    CS += byte # 边收数据边计算校验码，校验码为地址码开始(包含地址码)到校验码之前的数据的和
    if RxIndex == 0: # 起始码
        if byte == CmdPacket_Begin:
            i = 0
            buf[i] = CmdPacket_Begin
            i += 1
            CS = 0 # 下个字节开始计算校验码
            RxIndex = 1
    elif RxIndex == 1: # 数据体的地址码
        buf[i] = byte
        i += 1
        if byte == 255: # 255是广播地址，模块作为从机，它的地址不可会出现255
            RxIndex = 0
        else:
            RxIndex += 1
    elif RxIndex == 2: # 数据体的长��
        buf[i] = byte
        i += 1
        if byte > CmdPacketMaxDatSizeRx or byte == 0:  # 长度无效
            RxIndex = 0
        else:
            RxIndex += 1
            cmdLen = byte
    elif RxIndex == 3: # 获取数据体的数据
        buf[i] = byte
        i += 1
        if i >= cmdLen + 3: # 已收完数据体
            RxIndex += 1
    elif RxIndex == 4: # 对比 效验码
        CS -= byte
        if (CS&0xFF) == byte: # 校验正确
            buf[i] = byte
            i += 1
            RxIndex += 1
        else: # 校验失败
            RxIndex = 0
    elif RxIndex == 5: # 结束码
        RxIndex = 0
        if byte == CmdPacket_End: # 捕获到完整包
            buf[i] = byte
            i += 1
            hex_string = " ".join(f"{b:02X}" for b in buf[0:i])
            # print(f"U-Rx[Len={i}]:{hex_string}")
            return Cmd_RxUnpack(buf[3:i-2], i-5) # 处理数据包的数据体
    else:
        RxIndex = 0
    return None

def Cmd_PackAndTx(ser, pDat, DLen):
    if DLen == 0 or DLen > 19:
        return -1  # 非法参数

    # 构建发送包缓存，包括50字节的前导码
    buf = bytearray([0x00]*46) + bytearray([0x00, 0xff, 0x00, 0xff,  0x49, 0xFF, DLen]) + bytearray(pDat[:DLen])

    # 计算校验和，从地址码开始到数据体结束
    CS = sum(buf[51:51+DLen+2]) & 0xFF  # 取低8位
    buf.append(CS)
    buf.append(0x4D)  # 添加结束码

    try:
        # 发送数据
        ser.write(buf)
        return 0
    except serial.SerialException as e:
        print(f"串口写入错误: {e}")
        raise

def read_data(serial_port):
    global ser_port
    ser_port = serial_port
    while True:  # 外层循环用于重连
        try:
            with serial.Serial(ser_port, ser_baudrate, timeout=ser_timeout) as ser:
                print("[IMU {ser_port}] 串口已连接")

                # 1.发送配置参数
                params = [0] * 11  # 数组
                isCompassOn = 0  # 1=开启磁场融合姿态 0=关闭磁场融合姿态
                barometerFilter = 2 # 气压计的滤波等级[取值0-3]
                Cmd_ReportTag = 0x0FFF  # 功能订阅标识
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
                Cmd_PackAndTx(ser, params, len(params))
                time.sleep(0.2)

                # 2.唤醒传感器
                Cmd_PackAndTx(ser, [0x03], 1)
                time.sleep(0.2)

                # 3.开启主动上报
                Cmd_PackAndTx(ser, [0x19], 1)

                # 循环接收数据并处理
                while True:
                    try:
                        data = ser.read(1)
                        if len(data) > 0:
                            result = Cmd_GetPkt(data[0])
                            if result is not None:
                                yield result
                    except serial.SerialException as e:
                        print(f"[IMU {ser_port}] 数据读取错误: {e}")
                        break
                    
        except serial.SerialException as e:
            print(f"[IMU {ser_port}] 串口连接断开，尝试重新连接... {e}")
            time.sleep(1)
        except Exception as e:
            print(f"[IMU {ser_port}] 未知错误: {e}")
            time.sleep(1)

def z_axes_to_zero():
    try:
        with serial.Serial(ser_port, ser_baudrate, timeout=ser_timeout) as ser:
            buf = bytearray([0x05])
            print("\nz-axes to zero--\n")
            Cmd_PackAndTx(ser, buf, 1)
    except serial.SerialException as e:
        print(f"[IMU {ser_port}] 串口操作失败: {e}")
