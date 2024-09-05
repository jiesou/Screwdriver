import serial
import time
import numpy as np
from array import array

# 设置正确的串口参数------------------------
ser_port = "/dev/ttyUSB0"     #此处需要替换为对应使用的串口号，windows系统写成COMx，若是linux则要根据所用系统进行调整如写成/dev/ttyUSBx或/dev/ttySx
ser_baudrate = 115200 # 串口波特率

ser_timeout = 2 # 串口操作超时时间
# Open the serial port
ser = serial.Serial(ser_port, ser_baudrate, timeout=ser_timeout)



def turningPreviousData(previous_data, data):
    if len(previous_data) > 9:
        previous_data.pop(0)
    previous_data.append(data)

def isSameSign(a, b):
    if a == 0 and b == 0: return True
    return a * b > 0


screw_plan = [
    { "spaceX": 1, "spaceY": 0 },
    { "spaceX": 1, "spaceY": 0 },
    { "spaceX": 0, "spaceY": 1 },
    { "spaceX": -1, "spaceY": 0 },
]

previous_data = {
    'AXs': [],
    'AYs': [],
    'AZs': [],
    'angelZs': [],
    'spaceXs': [],
    'spaceYs': [],
}
last_trigger_time = 0
suddenly_changed = False

def parseData(data):
    global previous_data, last_trigger_time, suddenly_changed

    if len(data) == 0:
        return

    turningPreviousData(previous_data['AXs'], data['AX'])
    turningPreviousData(previous_data['AYs'], data['AY'])
    turningPreviousData(previous_data['AZs'], data['AZ'])
    turningPreviousData(previous_data['angelZs'], data['angleZ'])
    
    # 保持 X、Y 轴稳定
    x_stable = len(previous_data['AXs']) > 9 and all([abs(ax - 0) < 1.5 for ax in previous_data['AXs']])
    y_stable = len(previous_data['AYs']) > 9 and all([abs(ay - 0) < 1.5 for ay in previous_data['AYs']])

    # 保持方向朝下
    aligned = abs(data['angleX']) < 25 and abs(data['angleY']) < 25

    located = locateScrew(data, screw_plan[0])
    print(f"located: {located}, x_stable: {x_stable}, y_stable: {y_stable}, aligned: {aligned}, screw_plan: {screw_plan[0]}, left: {len(screw_plan)}")
    if located and x_stable and y_stable and aligned:
        # 得到过去 3 个数据的最小值，用于判断是否有数据突变
        last_min_angelZ = min(previous_data['angelZs'][-8:-5])
        if suddenly_changed:
            current_time = time.time()
            if current_time - last_trigger_time >= 1:
                last_trigger_time = current_time
                screw_plan.pop(0)
                print(f"screwd, {len(screw_plan)} left")
                if len(screw_plan) < 1:
                    print("done")
                    exit()
        suddenly_changed = 5 < (data['angleZ'] - last_min_angelZ)


def locateScrew(data, plan):
    if not(data['spaceX'] == 0 and data['spaceY'] == 0):
        turningPreviousData(previous_data['spaceXs'], data['spaceX'])
        turningPreviousData(previous_data['spaceYs'], data['spaceY'])
        return False
    elif len(previous_data['spaceXs']) > 0 and len(previous_data['spaceYs']) > 0:
        # 已静止，仅在静止时判断位置
        last_spaceX = previous_data['spaceXs'][-1]
        last_spaceY = previous_data['spaceYs'][-1]
        last_spaceX = 0 if last_spaceX < 0.01 else last_spaceX
        last_spaceY = 0 if last_spaceY < 0.01 else last_spaceY
        print(f"last_spaceX: {last_spaceX}, last_spaceY: {last_spaceY}")
        if last_spaceX == 0 and last_spaceY == 0:
            # 忽略不计
            return False
        # 如果符号相同，说明在同一方向
        if isSameSign(last_spaceX, plan['spaceX']) and isSameSign(last_spaceY, plan['spaceY']):
            return True
        else:
            # 位置错了
            return False
        
    
        

def Cmd_RxUnpack(buf, DLen):
    scaleAccel       = 0.00478515625
    scaleQuat        = 0.000030517578125
    scaleAngle       = 0.0054931640625
    scaleAngleSpeed  = 0.06103515625
    scaleMag         = 0.15106201171875
    scaleTemperature = 0.01
    scaleAirPressure = 0.0002384185791
    scaleHeight      = 0.0010728836

    imu_data = {}

    if buf[0] == 0x11:
        ctl = (buf[2] << 8) | buf[1]

        L =7 # 从第7字节开始根据 订阅标识tag来解析剩下的数据
        if ((ctl & 0x0001) != 0):
            tmpX = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAccel; L += 2 
            tmpY = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAccel; L += 2 
            tmpZ = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAccel; L += 2

            imu_data['aX'] = tmpX
            imu_data['aY'] = tmpY
            imu_data['aZ'] = tmpZ
        if ((ctl & 0x0002) != 0):
            tmpX = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAccel; L += 2
            tmpY = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAccel; L += 2
            tmpZ = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAccel; L += 2
            imu_data['AX'] = tmpX
            imu_data['AY'] = tmpY
            imu_data['AZ'] = tmpZ

        if ((ctl & 0x0004) != 0):
            tmpX = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAngleSpeed; L += 2 
            tmpY = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAngleSpeed; L += 2 
            tmpZ = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAngleSpeed; L += 2
        
        if ((ctl & 0x0008) != 0):
            tmpX = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleMag; L += 2
            tmpY = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleMag; L += 2
            tmpZ = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleMag; L += 2
        
        if ((ctl & 0x0010) != 0):
            tmpX = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleTemperature; L += 2

            tmpU32 = np.uint32(((np.uint32(buf[L+2]) << 16) | (np.uint32(buf[L+1]) << 8) | np.uint32(buf[L])))
            if ((tmpU32 & 0x800000) == 0x800000): # 若24位数的最高位为1则该数值为负数，需转为32位负数，直接补上ff即可
                tmpU32 = (tmpU32 | 0xff000000)      
            tmpY = np.int32(tmpU32) * scaleAirPressure; L += 3

            tmpU32 = np.uint32((np.uint32(buf[L+2]) << 16) | (np.uint32(buf[L+1]) << 8) | np.uint32(buf[L]))
            if ((tmpU32 & 0x800000) == 0x800000): # 若24位数的最高位为1则该数值为负数，需转为32位负数，直接补上ff即可
                tmpU32 = (tmpU32 | 0xff000000)
            tmpZ = np.int32(tmpU32) * scaleHeight; L += 3 

        if ((ctl & 0x0020) != 0):
            tmpAbs = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleQuat; L += 2
            tmpX =   np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleQuat; L += 2
            tmpY =   np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleQuat; L += 2
            tmpZ =   np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleQuat; L += 2

        if ((ctl & 0x0040) != 0):
            tmpX = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAngle; L += 2
            tmpY = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAngle; L += 2
            tmpZ = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAngle; L += 2
            imu_data['angleX'] = tmpX
            imu_data['angleY'] = tmpY
            imu_data['angleZ'] = tmpZ

        if ((ctl & 0x0080) != 0):
            tmpX = np.short((np.short(buf[L+1])<<8) | buf[L]) / 1000.0; L += 2
            tmpY = np.short((np.short(buf[L+1])<<8) | buf[L]) / 1000.0; L += 2
            tmpZ = np.short((np.short(buf[L+1])<<8) | buf[L]) / 1000.0; L += 2
            imu_data['spaceX'] = tmpX
            imu_data['spaceY'] = tmpY
            imu_data['spaceZ'] = tmpZ

        if ((ctl & 0x0200) != 0):
            tmpX = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAccel; L += 2
            tmpY = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAccel; L += 2
            tmpZ = np.short((np.short(buf[L+1])<<8) | buf[L]) * scaleAccel; L += 2
                    
        if ((ctl & 0x0400) != 0):
            tmpU16 = ((buf[L+1]<<8) | (buf[L]<<0)); L += 2

        if ((ctl & 0x0800) != 0):
            tmpU8 = buf[L]; L += 1
    else:
        print("------data head not define")
    parseData(imu_data)

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
    elif RxIndex == 2: # 数据体的长度
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
            Cmd_RxUnpack(buf[3:i-2], i-5) # 处理数据包的数据体
            return 1
    else:
        RxIndex = 0
    return 0

def Cmd_PackAndTx(pDat, DLen):
    if DLen == 0 or DLen > 19:
        return -1  # 非法参数

    # 构建发送包缓存，包括50字节的前导码
    buf = bytearray([0x00]*46) + bytearray([0x00, 0xff, 0x00, 0xff,  0x49, 0xFF, DLen]) + bytearray(pDat[:DLen])

    # 计算校验和，从地址码开始到数据体结束
    CS = sum(buf[51:51+DLen+2]) & 0xFF  # 取低8位
    buf.append(CS)
    buf.append(0x4D)  # 添加结束码

    # 发送数据
    ser.write(buf)
    return 0


def read_data():

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
    params[5] = 30  # 数据主动上报的传输帧率[取值0-250HZ], 0表示0.5HZ
    params[6] = 1  # 陀螺仪滤波系数[取值0-2],数值越大越平稳但实时性越差
    params[7] = 3  # 加速计滤波系数[取值0-4],数值越大越平稳但实时性越差
    params[8] = 5  # 磁力计滤波系数[取值0-9],数值越大越平稳但实时性越差
    params[9] = Cmd_ReportTag & 0xff
    params[10] = (Cmd_ReportTag >> 8) & 0xff
    Cmd_PackAndTx(params, len(params)) # 发送指令给传感器
    time.sleep(0.2)

    # 2.唤醒传感器
    Cmd_PackAndTx([0x03], 1)
    time.sleep(0.2)

    # 3.开启主动上报
    Cmd_PackAndTx([0x19], 1)

    # 循环接收数据并处理
    while True:
        data = ser.read(1) # read 1 bytes
        if len(data) > 0: # if data is not empty
            Cmd_GetPkt(data[0])

# Start reading data
read_data()

