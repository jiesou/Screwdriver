import numpy as np
from .communication import read_data

screw_plan = [
    { "x": 0.1, "y": 0 },
    { "x": 0.18, "y": 0 },
    { "x": 0.18, "y": 0.1 },
    { "x": 0.1, "y": 0.1 },
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
    position_x = positions[-1][0] if abs(positions[-1][0]) > 0.08 else 0
    position_y = positions[-1][1] if abs(positions[-1][1]) > 0.08 else 0
    x_aligned = isSameSign(position_x, plan['x']) 
    y_aligned = isSameSign(position_y, plan['y'])
    return x_aligned and y_aligned
     
inited = False
def atInitialPosition(data):
    # 斜着放，即初始位置
    global inited
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
    global screw_plan, last_trigger_time, screw_tightening, inited
    turningPreviousData(previous_data, data)
    if len(previous_data) < 10: return False, False, False
    
    # 保持 X、Y 轴稳定
    xy_stable = all(abs(data['gravity_accel']['x']) < 2 and abs(data['gravity_accel']['y']) < 2 for data in previous_data)

    # 保持方向朝下
    aligned = abs(data['angle']['x']) < 25 and abs(data['angle']['y']) < 25

    # 3.定位
    located = locateScrew(data, screw_plan[0], positions)
    print(f"located: {located}, xy_stable: {xy_stable}, aligned: {aligned}, screw_plan: {screw_plan[0]}, left: {len(screw_plan)}")
    if located and xy_stable and aligned:
        print(inited)
        if screw_tightening and inited:
            # 4. 拧螺丝
            screw_plan.pop(0)
            print(f"screwd, {len(screw_plan)} left")
            inited = False
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
        # 初始位置重置坐标系
        if atInitialPosition(data): new_position = [0, 0, 0]
        print("new_position: %.3f, %.3f, %.3f" % (new_position[0], new_position[1], new_position[2]))
        positions.append(new_position)
        located, xy_stable, aligned = requirement_process(data, previous_data, positions)
        yield f"located: {located}, xy_stable: {xy_stable}, aligned: {aligned}, screw_plan: {screw_plan[0]}, left: {len(screw_plan)}\n"


def simulate_screw_tightening_for_3s():
    global screw_tightening
    screw_tightening = not screw_tightening
    print(f"screw_tightening: {screw_tightening}")
