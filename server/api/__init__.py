import json
import time
from flask import Blueprint, current_app, stream_with_context, request
from server.units import res
from imu import API as ImuAPI
from imu.communication import z_axes_to_zero

api_bp = Blueprint('api', __name__)

imu_api = ImuAPI([
    {"tag": "左", "position": {"x": 0.2, "y": 0, "allow_offset": 0.07},
        "quaternion": {"x": 0, "y": 0}, "status": "等待中"},
    {"tag": "中", "position": {"x": 0.3, "y": 0, "allow_offset": 0.1},
        "quaternion": {"x": 0, "y": 0}, "status": "等待中"},
    {"tag": "右", "position": {"x": 0.5, "y": 0, "allow_offset": 0.1},
        "quaternion": {"x": 0, "y": 0}, "status": "等待中"},
])

@api_bp.route('/reset_z_axes')
def reset_z_axes():
    result = z_axes_to_zero()
    return res(current_app, result)

@api_bp.route('/start_moving')
def start_moving():
    def stream():
        yield ""
        for text_snippet in imu_api.handle_start_moving():
            yield (text_snippet + "\n")
    return stream_with_context(stream())

@api_bp.route('/simulate_screw_tightening')
def simulate_screw_tightening():
    imu_api.handle_simulate_screw_tightening()
    return res(current_app)


@api_bp.route('/reset_desktop_coordinate_system')
def reset_desktop_coordinate_system():
    imu_api.handle_reset_desktop_coordinate_system()
    return res(current_app)

@api_bp.route('/screw_data')
def screw_data():
    def stream():
        yield ""
        while True:
            text_snippet = imu_api.handle_screw_data()
            yield text_snippet + "\n"
            time.sleep(0.5)
    return stream_with_context(stream())


@api_bp.route('/current_data', methods=['POST'])
def current_data():
    try:
        data = request.data.decode('utf-8')
        imu_api.input_current_data(json.loads(data))
        return "Data received", 200
    except json.JSONDecodeError:
        return json.dumps({}), 400
