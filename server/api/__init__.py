import json
import time
from flask import Blueprint, current_app, stream_with_context, request
from server.units import res
from imu import API as ImuAPI
from imu.communication import z_axes_to_zero

api_bp = Blueprint('api', __name__)

imu_api = ImuAPI([])

@api_bp.route('/reset_z_axes')
def reset_z_axes():
    result = z_axes_to_zero()
    return res(current_app, result)

@api_bp.route('/start_moving', methods=['POST'])
def start_moving():
    global imu_api
    imu_api = ImuAPI(json.loads(request.data))
    def stream():
        yield ""
        for data_snippet in imu_api.handle_start_moving():
            yield (json.dumps(data_snippet) + "\n")
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
    return res(current_app, imu_api.get_screw_map())

@api_bp.route('/current_data', methods=['POST'])
def current_data():
    try:
        data = request.data.decode('utf-8')
        imu_api.set_current_data(json.loads(data))
        return "Data received", 200
    except json.JSONDecodeError:
        return json.dumps({}), 400
