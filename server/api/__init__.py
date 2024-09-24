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
            {"tag": 0, "position": {"x": -0.5, "y": -0.5, "offset": 0.2}, "quaternion": {"x": 0, "y": 0}},
            {"tag": 1, "position": {"x": 1.5, "y": 0, "offset": 0.2}, "quaternion": {"x": 0, "y": 0}}
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
