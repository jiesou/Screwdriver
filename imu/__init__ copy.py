import numpy as np
from .communication import read_data

screw_plan = [
    { "x": 0.1, "y": 0 },
    { "x": 0.18, "y": 0 },
    { "x": 0.2, "y": 0.1 },
    { "x": 0.18, "y": 0.1 },
]


def turningPreviousData(previous_data, data):
    if len(previous_data) > 9:
        previous_data.pop(0)
    previous_data.append(data)

def isSameSign(a, b):
    if a == 0 and b == 0: return True
    return a * b > 0

def locateScrew(data, plan, positions):
    if len(positions) < 2: return False
    x_aligned = abs(positions[-1][0]-plan['x']) < 0.1
    y_aligned = abs(positions[-1][1]-plan['y']) < 0.1
    print(f"x_aligned: {positions[-1][0]-plan['x']}, y_aligned: {positions[-1][1]-plan['y']}")
    return x_aligned and y_aligned

# 1.累计偏移量到地图位置
def accumulate_offset_to_position(offset, positions, standing):
    new_position = standing.copy()

    if offset['x'] == 0:
        standing[0] = positions[-1][0]

    if offset['y'] == 0:
        standing[1] = positions[-1][1]
    
    new_position[0] = standing[0] + offset['x']
    new_position[1] = standing[1] + offset['y']
    
    print("new_position: %.3f, %.3f, %.3f; offset: %.3f, %.3f, %.3f" % (new_position[0], new_position[1], new_position[2], offset['x'], offset['y'], offset['z']))
    positions.append(new_position)
    return new_position

last_trigger_time = 0
screw_tightening = False
# 2.判断是否符合拧螺丝要求
def requirement_process(data, previous_data, positions):
    global screw_plan, last_trigger_time, screw_tightening
    turningPreviousData(previous_data, data)
    if len(previous_data) < 10: return False, False, False
    
    # 保持 X、Y 轴稳定
    xy_stable = all(abs(data['gravity_accel']['x']) < 1.5 and abs(data['gravity_accel']['y']) < 1.5 for data in previous_data)

    # 保持方向朝下
    aligned = abs(data['angle']['x']) < 25 and abs(data['angle']['y']) < 25

    # 3.定位
    located = locateScrew(data, screw_plan[0], positions)
    print(f"located: {located}, xy_stable: {xy_stable}, aligned: {aligned}, screw_plan: {screw_plan[0]}, left: {len(screw_plan)}")
    if located and xy_stable and aligned:
        print(screw_tightening)
        if screw_tightening:
            # 4. 拧螺丝
            screw_plan.pop(0)
            print(f"screwd, {len(screw_plan)} left")
            if len(screw_plan) < 1:
                print("done")
                exit()
    return located, xy_stable, aligned

def parse_data():
    positions = [[0, 0, 0]]
    standing = [0, 0, 0]

    previous_data = []
    last_trigger_time = 0

    # 处理 yield 数据
    for data in read_data():
        if data is None: continue
        new_position = accumulate_offset_to_position(data['offset'], positions, standing)
        located, xy_stable, aligned = requirement_process(data, previous_data, positions)
        yield f"located: {located}, xy_stable: {xy_stable}, aligned: {aligned}, screw_plan: {screw_plan[0]}, left: {len(screw_plan)}\n"


def simulate_screw_tightening_for_3s():
    global screw_tightening
    screw_tightening = not screw_tightening
    print(f"screw_tightening: {screw_tightening}")
