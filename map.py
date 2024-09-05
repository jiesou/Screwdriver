import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from imu import read_data


def process_data():
    # 初始化轨迹数据
    positions = [[0, 0, 0]]
    standing = [0, 0, 0]
    fig = plt.figure()

    ax = fig.add_subplot(111, projection='3d')

    for data in read_data():
        if data is None: continue
        offset = data['offset']

        new_position = standing.copy()

        if offset['x'] == 0:
            standing[0] = positions[-1][0]

        if offset['y'] == 0:
            standing[1] = positions[-1][1]

        if offset['z'] == 0:
            standing[2] = positions[-1][2]
        
        new_position[0] = standing[0] + offset['x']
        new_position[1] = standing[1] + offset['y']
        
        print("new_position: %.3f, %.3f, %.3f; offset: %.3f, %.3f, %.3f" % (new_position[0], new_position[1], new_position[2], offset['x'], offset['y'], offset['z']))
        positions.append(new_position)

        ax.clear()
        ax.plot([p[0] for p in positions], [p[1] for p in positions], [p[2] for p in positions])
        plt.pause(0.01)

    plt.ylim(0, 10)
    plt.show()

# 调用处理函数
process_data()
