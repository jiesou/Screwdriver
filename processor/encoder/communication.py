import serial
import struct
import time
import asyncio


def calculate_crc(data):
    """计算 Modbus CRC16 校验码"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def read_encoder_value(ser, slave_id=0x01):
    """
    读取编码器值 (功能码 0x03)
    寄存器地址: 0x0000
    寄存器数量: 0x0002 (读取2个寄存器，共4字节)
    """
    # 构建 Modbus RTU 请求: 从站地址 + 功能码 + 起始地址 + 寄存器数量
    request = bytes([slave_id, 0x03, 0x00, 0x00, 0x00, 0x02])

    # 计算并添加 CRC 校验码
    crc = calculate_crc(request)
    request += struct.pack('<H', crc)  # 小端序

    # 发送请求
    ser.write(request)

    # 读取响应 (从站地址 + 功能码 + 字节数 + 数据 + CRC)
    # 预期响应长度: 1 + 1 + 1 + 4 + 2 = 9 字节
    response = ser.read(9)

    if len(response) < 9:
        print(f"响应数据不完整: {response.hex()}")
        return None

    # 验证 CRC
    received_crc = struct.unpack('<H', response[-2:])[0]
    calculated_crc = calculate_crc(response[:-2])

    if received_crc != calculated_crc:
        print(
            f"[Encoder] CRC 校验失败: 接收={received_crc:04X}, 计算={calculated_crc:04X}")
        return None

    # 验证从站地址和功能码
    if response[0] != slave_id or response[1] != 0x03:
        print(f"[Encoder] 响应格式错误: {response.hex()}")
        return None

    # 解析编码器值 (4字节，大端序)
    byte_count = response[2]
    if byte_count != 4:
        print(f"[Encoder] 数据字节数错误: {byte_count}")
        return None

    encoder_value = struct.unpack('>I', response[3:7])[0]
    return encoder_value


class EncoderCommunicator:
    def __init__(self):
        pass

    async def read_data(self):
        """异步生成器：模拟异步 IO，周期性产出数据"""
        while True:
            # 模拟异步等待
            await asyncio.sleep(0.1)
            yield 1  # 占位符，后续实现具体逻辑

    def read_data(self, port="/dev/ttyUSB2", baudrate=9600, slave_id=0x01, timeout=1, interval=0.01):
        """
        持续读取拉线编码器的值
        
        参数:
            port: 串口设备路径
            baudrate: 波特率 (9600, 19200, 38400, 57600, 115200)
            slave_id: 从站地址 (默认 0x01)
            timeout: 串口超时时间
            interval: 读取间隔时间
        """
        while True:  # 外层无限循环用于重连
            try:
                with serial.Serial(port, baudrate, timeout=timeout) as ser:
                    print(
                        f"[Encoder] 拉线编码器串口已连接: {port}, 波特率: {baudrate}, 从站地址: {slave_id}")
                    time.sleep(0.1)  # 等待串口稳定

                    while True:
                        value = read_encoder_value(ser, slave_id)
                        if value is not None:
                            yield value
                        else:
                            yield None

                        time.sleep(interval)  # 读取间隔

            except Exception as e:
                print(f"[Encoder] 拉线编码器连接断开，尝试重新连接... {e}")
                yield None
                time.sleep(1)
