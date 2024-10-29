import time
from flask import Blueprint, current_app, stream_with_context, request
from server.units import res
from imu import api as imu_api
from imu.communication import z_axes_to_zero

api_bp = Blueprint('api', __name__)

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
def receive_data():
    data = request.data.decode('utf-8')
    print(f"Received data: {data}")
    return "Data received", 200
