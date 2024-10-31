import json
import time
from flask import Blueprint, current_app, stream_with_context, request
from server.units import res

from imu.communication import z_axes_to_zero
from processor import ProcessorAPI

api_bp = Blueprint('api', __name__)

processor_api = ProcessorAPI([])

@api_bp.route('/reset_z_axes')
def reset_z_axes():
    result = z_axes_to_zero()
    return res(current_app, result)

@api_bp.route('/start_moving', methods=['POST'])
def start_moving():
    global processor_api
    processor_api = ProcessorAPI(json.loads(request.data))
    def stream():
        yield ""
        for data_snippet in processor_api.handle_start_moving():
            try:
                yield json.dumps(data_snippet) + "\n"
            except (GeneratorExit, ConnectionResetError, BrokenPipeError):
                print("exited")
                break
    return stream_with_context(stream())

@api_bp.route('/simulate_screw_tightening')
def simulate_screw_tightening():
    processor_api.current_api.is_working = True
    return res(current_app)

@api_bp.route('/reset_desktop_coordinate_system')
def reset_desktop_coordinate_system():
    processor_api.handle_reset_desktop_coordinate_system()
    return res(current_app)

@api_bp.route('/screw_data')
def screw_data():
    return res(current_app, processor_api.screw_map.screws)

@api_bp.route('/screw_tightening', methods=['POST'])
def current_data():
    try:
        data = request.data.decode('utf-8')
        processor_api.current_api.is_working = True
        return "Data received", 200
    except json.JSONDecodeError:
        return json.dumps({}), 400
