import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from imu import read_data

matplotlib.use('TkAgg')
plt.switch_backend('TkAgg')

def process_data():
    # 初始化轨迹数据
    positions = [[0, 0, 0]]
    standing = {
        'isStanding': True,
        'position': [0, 0, 0]
    }
    fig = plt.figure()

    ax = fig.add_subplot(111, projection='3d')

    # 处理每个传感器数据
    for data in read_data():
        if data is None: continue
        offset = data['offset']
        print(offset, standing)


        if offset['x'] == 0 and offset['y'] == 0 and offset['z'] == 0:
            # 静止
            standing['isStanding'] = True
            standing['position'] = positions[-1]
            continue

        if standing['isStanding']:
            standing['isStanding'] = False
        positions.append([
            standing['position'][0] + offset['x'],
            standing['position'][1] + offset['y'],
            0,
        ])

        ax.clear()
        ax.plot([p[0] for p in positions], [p[1] for p in positions], [p[2] for p in positions])
        plt.pause(0.03333)

    plt.ylim(0, 10)
    plt.show()

# 调用处理函数
process_data()
