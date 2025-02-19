import os
IMU_CONNECTION_MODE = os.getenv('IMU_CONNECTION_MODE', 'serial').lower()

# 根据连接模式选择相应的模块
if IMU_CONNECTION_MODE == 'bluetooth':
    from .bluetooth import  BluetoothCommunicator as bt_comm
    ImuComm = bt_comm
else:
    from .serial import SerialCommunicator as serial_comm
    ImuComm = serial_comm

# 负责管理 IMU 通信初始化传入参数
class Communicator:
    def __init__(self, port):
        if IMU_CONNECTION_MODE == 'serial':
            # 串口模式需要输入串口号
            self.comm =  ImuComm(port=port)
        else:
            # TODO: 蓝牙模式的多设备连接暂未实现
            self.comm = ImuComm()

    def read_data(self):
        yield from self.comm.read_data()

    def z_axes_to_zero(self):
        self.comm.z_axes_to_zero()
