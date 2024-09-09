import numpy as np
from .communication import read_data
import time, threading, csv

"""
The data structure for the `map` variable is a list of dictionaries. Each dictionary represents a screw and contains the following keys:
Example:
[
    {
        "position": {"x": 0.1, "y": 0},
        "quaternion": {"x": 0, "y": 0}
    },
    {
        "position": {"x": 0.2, "y": 0},
        "quaternion": {"x": 0, "y": 0}
    },
    ...
"""
screw_map = []

def turningPreviousData(previous_data, data):
    if len(previous_data) > 9:
        previous_data.pop(0)
    previous_data.append(data)

def isSameSign(a, b):
    if a == 0 and b == 0: return True
    return a * b > 0

def locateScrew(data, positions):
    if len(positions) < 2: return False
    current_position = positions[-1]
    min_combined_distance = float('inf')
    closest_screw = None
    for screw in screw_map:
        space_distance = np.sqrt(
            (current_position[0] - screw['position']['x'])**2 +
            (current_position[1] - screw['position']['y'])**2
        )
        quaternion_offset = abs(data['quaternion']['x'] - screw['quaternion']['x']) + abs(data['quaternion']['y'] - screw['quaternion']['y'])
        # 将空间距离和四元数角度偏差结合起来，得到当前态势与 map 中各颗螺丝的综合偏差
        combined_distance = space_distance + quaternion_offset * 0.1
        print(f"index: %d, space_distance: %.3f, quaternion_offset: %.3f, combined_distance: %.3f" % (screw_map.index(screw), space_distance, quaternion_offset, combined_distance))
        if combined_distance < min_combined_distance:
            min_combined_distance = combined_distance
            closest_screw = screw
    if closest_screw is not None:
        index = screw_map.index(closest_screw)
        print(f"closest_screw: {closest_screw}, index: {index}")
        x_aligned = isSameSign(current_position[0], closest_screw['position']['x'])
        y_aligned = isSameSign(current_position[1], closest_screw['position']['y'])
        if x_aligned and y_aligned:
            return index
    return False
     
inited = False
init_position_manually = False
def atInitialPosition(data):
    # 斜着放，即初始位置
    global inited, init_position_manually
    if init_position_manually:
        init_position_manually = False
        return True
    isStanding = data['offset']['x'] == 0 and data['offset']['y'] == 0 and data['offset']['z'] == 0
    at_initial_position = isStanding and abs(data['angle']['y']+47)<7 and abs(data['angle']['x'])<20 and abs(data['angle']['z'])<20
    if not inited and at_initial_position:
        inited = True
    return at_initial_position




# 1.累计偏移量到地图位置
def accumulate_offset_to_position(offset, positions, standing):
    new_position = standing.copy()

    if offset['x'] == 0:
        standing[0] = positions[-1][0]

    if offset['y'] == 0:
        standing[1] = positions[-1][1]
    
    new_position[0] = standing[0] + offset['x']
    new_position[1] = standing[1] + offset['y']
    
    return new_position

last_trigger_time = 0
screw_tightening = False
# 2.判断是否符合拧螺丝要求
def requirement_process(data, previous_data, positions):
    global screw_map, last_trigger_time, screw_tightening, inited
    turningPreviousData(previous_data, data)
    if len(previous_data) < 10: return False
    
    # 保持 X、Y 轴稳定
    xy_stable = all(abs(data['gravity_accel']['x']) < 2 and abs(data['gravity_accel']['y']) < 2 for data in previous_data)

    # 3.定位
    located_index = locateScrew(data, positions)
    print(f"located: {located_index}, xy_stable: {xy_stable}, left: {len(screw_map)}")
    if located_index and xy_stable:
        # 每次拧螺丝只有重置后才能再次拧
        if screw_tightening and inited:
            # 4. 拧螺丝
            screw_map.pop(located_index)
            print(f"screwd, {len(screw_map)} left")
            inited = False
            if len(screw_map) < 1:
                print("done")
                return True
    return False

def parse_data():
    positions = [[0, 0, 0]]
    standing = [0, 0, 0]

    previous_data = []

    filename = f"logs/imu_{time.strftime('%Y%m%d%H%M%S')}.csv"
    with open(filename, 'w', newline='') as csvfile:
        # 记录在 csv 中
        writer = csv.writer(csvfile)
        writer.writerow(['position_x', 'position_y', 'offset_x', 'offset_y', 'offset_z', 'angle_x', 'angle_y', 'angle_z', 'gravity_accel_x', 'gravity_accel_y', 'gravity_accel_z'])
        for data in read_data():
            if data is None: continue
            new_position = accumulate_offset_to_position(data['offset'], positions, standing)
            # writer.writerow([new_position[0], new_position[1], data['offset']['x'], data['offset']['y'], data['offset']['z'], data['angle']['x'], data['angle']['y'], data['angle']['z'], data['gravity_accel']['x'], data['gravity_accel']['y'], data['gravity_accel']['z']])
            # 初始位置重置坐标系
            if atInitialPosition(data): new_position = [0, 0, 0]
            print("new_position: %.3f, %.3f, %.3f" % (new_position[0], new_position[1], new_position[2]))
            positions.append(new_position)
            ok = requirement_process(data, previous_data, positions)
            if ok:
                yield 'DONE'
                break

def start_moving_for(map):
    global screw_map
    screw_map = map
    for text_snippet in parse_data():
        yield text_snippet


def simulate_screw_tightening_for_3s():
    global screw_tightening
    screw_tightening = not screw_tightening
    print(f"screw_tightening: {screw_tightening}")

def desktop_coordinate_system_to_zero():
    global init_position_manually
    init_position_manually = True
    