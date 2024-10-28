import json
import numpy as np
from .communication import read_data
import time
import csv
import copy

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
screw_map_input = [
    {"tag": "左", "position": {"x": 0.2, "y": 0.1, "offset": 0.07},
        "quaternion": {"x": 0, "y": 0}, "status": "等待中"},
    {"tag": "中", "position": {"x": 0.3, "y": 0.1, "offset": 0.1},
        "quaternion": {"x": 0, "y": 0}, "status": "等待中"},
    {"tag": "右", "position": {"x": 0.5, "y": 0.1, "offset": 0.1},
        "quaternion": {"x": 0, "y": 0}, "status": "等待中"},
]

screw_map = screw_map_input.copy()


def turningPreviousData(previous_data, data):
    if len(previous_data) > 9:
        previous_data.pop(0)
    previous_data.append(data)


def isSameSign(a, b):
    if a == 0 and b == 0:
        return True
    return a * b > 0

# 从大 map 中找在 offset 的范围内 覆盖到了 的螺丝
def filterScrewsinRange(screw_map, position):
    filtered_map = []
    for screw in screw_map:
        space_distance = np.sqrt(
            (position[0] - screw['position']['x'])**2 +
            (position[1] - screw['position']['y'])**2
        )
        if space_distance < screw['position']['offset']:
            filtered_map.append(screw)
    return filtered_map

# 在过滤后的 map 中找到 最近 的螺丝
def locateScrew(screw_map, position):
    current_min_combined_distance = float('inf')
    current_closest_screw = None
    for screw in screw_map:
        space_distance = np.sqrt(
            (position[0] - screw['position']['x'])**2 +
            (position[1] - screw['position']['y'])**2
        )
        combined_distance = space_distance
        print(f"SCREW: tag: %s, space_distance: %.3f, combined_distance: %.3f" % (screw['tag'], space_distance, combined_distance))
        if combined_distance < current_min_combined_distance:
            current_min_combined_distance = combined_distance
            current_closest_screw = screw
    # 返回最近的螺丝和距离
    return current_closest_screw

# 侦测到突变后，记录缓反次数，持续 10 次缓返，认为拧螺丝
angle_z_recovered_times = False
def isScrewTightening(previous_data):
    global screw_tightening, angle_z_recovered_times
    angle_z_history = [data['angle']['z'] for data in previous_data]

    screw_tightening = False
    if type(angle_z_recovered_times) == int:
        offset = angle_z_history[-1] - angle_z_history[-2]
        print(f"offset: {offset}")
        if offset == 0:
            pass
        elif 0 < offset < 4:
            angle_z_recovered_times += 1
            print(f"angle_z_decreased: {angle_z_recovered_times}")
        else:
            angle_z_recovered_times -= 1
            print(f"angle_z_decreased: {angle_z_recovered_times}")
        if angle_z_recovered_times > 6:
            # screw_tightening = True
            angle_z_recovered_times = False
            print("Detected screw tightening.！！！！！！！！！！！！！！！！")
        if angle_z_recovered_times < -1:
            screw_tightening = False
            angle_z_recovered_times = False
    # 取过去 3 次的中位数作为突变判断的基准
    median_angle_z = np.median(angle_z_history[-6:-3])
    if -10 < previous_data[-1]['angle']['z']-median_angle_z < -5:
        angle_z_recovered_times = 0
        print("angle['z'] increased significantly.")

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
    isStateValid = isStanding and abs(data['angle']['y']+50) < 7 and abs(data['angle']['x']) < 20 and abs(data['angle']['z']) < 20
    if not inited and isStateValid:
        inited = True
    return isStateValid



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
    screw_map = copy.deepcopy(screw_map_input)
    print(screw_map_input)
    turningPreviousData(previous_data, data)
    if len(previous_data) < 10: return False
    
    # 3. 记录分析拧螺丝状态
    isScrewTightening(previous_data)

    filtered_screw_map = filterScrewsinRange(screw_map, positions[-1])

    # 4.定位
    located_screw = locateScrew(filtered_screw_map, positions[-1])

    if located_screw: located_screw['status'] = "已定位"
    # 每次拧螺丝只有重置后才能再次拧
    if screw_tightening and inited:
        # 5. 拧螺丝
        screw_map.pop(screw_map.index(located_screw))
        print(f"screwd, {len(screw_map)} left")
        inited = False
        if len(screw_map) < 1:
            print("done")

    return {
        "located_screw": located_screw
    }

def parse_data():
    positions = [[0, 0, 0]]
    standing = [0, 0, 0]

    previous_data = []

    filename = f"logs/imu_{time.strftime('%Y%m%d%H%M%S')}.csv"
    with open(filename, 'w', newline='') as csvfile:
        # 记录在 csv 中
        writer = csv.writer(csvfile)
        writer.writerow(['position_x', 'position_y', 'offset_x', 'offset_y', 'offset_z', 'angle_x', 'angle_y', 'angle_z', 'angle_accel_x', 'angle_accel_y', 'angle_accel_z',
                        'gravity_accel_x', 'gravity_accel_y', 'gravity_accel_z'])
        for data in read_data():
            if data is None: continue
            new_position = accumulate_offset_to_position(data['offset'], positions, standing)
            writer.writerow([new_position[0], new_position[1], data['offset']['x'], data['offset']['y'], data['offset']['z'], data['angle']['x'], data['angle']['y'], data['angle']['z'], data['angle_accel']['x'], data['angle_accel']['y'], data['angle_accel']['z'],
                             data['gravity_accel']['x'], data['gravity_accel']['y'], data['gravity_accel']['z']])
            # 初始位置重置坐标系
            if atInitialPosition(data):
                new_position = [0, 0, 0]
            positions.append(new_position)

            state = requirement_process(data, previous_data, positions)

            yield {
                "position": new_position,
                "located_screw": state['located_screw'] if state else None,
                "offset": data['offset'],
                "angle": data['angle'],
                "angle_accel": data['angle_accel'],
                "gravity_accel": data['gravity_accel'],
            }


class api:
    def handle_start_moving():
        for state in parse_data():
            yield json.dumps(state)

    def handle_simulate_screw_tightening():
        global screw_tightening
        screw_tightening = not screw_tightening
        print(f"screw_tightening: {screw_tightening}")


    def handle_reset_desktop_coordinate_system():
        global init_position_manually
        init_position_manually = True

    def handle_screw_data():
        return json.dumps(screw_map)
