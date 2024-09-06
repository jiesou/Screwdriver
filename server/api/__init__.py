from flask import Blueprint, current_app, stream_with_context
from server.units import res
from imu import start_moving_for, simulate_screw_tightening_for_3s, desktop_coordinate_system_to_zero
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
        for text_snippet in start_moving_for([
            { "x": 0.1, "y": 0 },
            { "x": 0.18, "y": 0 },
            { "x": 0.18, "y": 0.1 },
            { "x": 0.1, "y": 0.1 },
        ]):
            yield text_snippet
    return stream_with_context(stream())

@api_bp.route('/simulate_screw_tightening')
def simulate_screw_tightening():
    simulate_screw_tightening_for_3s()
    return res(current_app)


@api_bp.route('/reset_desktop_coordinate_system')
def reset_desktop_coordinate_system():
    desktop_coordinate_system_to_zero()
    return res(current_app)
