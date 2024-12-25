import os
IMU_CONNECTION_MODE = os.getenv('IMU_CONNECTION_MODE', 'serial').lower()

# 根据连接模式选择相应的模块
if IMU_CONNECTION_MODE == 'bluetooth':
    from . import communication_bluetooth as bt_comm
    comm = bt_comm
else:
    from . import communication_serial as serial_comm
    comm = serial_comm

def open_connection():
    if IMU_CONNECTION_MODE == 'bluetooth':
        comm.init_bluetooth()
    # 串口模式不需要特殊初始化

# 初始化连接
open_connection()

def read_data():
    yield from comm.read_data()

def z_axes_to_zero():
    comm.z_axes_to_zero()
