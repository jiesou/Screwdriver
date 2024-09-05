from flask import Blueprint, current_app
from server.units import res
from imu import parse_data
from imu.communication import z_axes_to_zero

api_bp = Blueprint('api', __name__)

@api_bp.route('/z_axes_to_zero')
def handle_z_axes_to_zero():
    z_axes_to_zero()
    return res(current_app, handle_z_axes_to_zero())

@api_bp.route('/parse_data')
def handle_parse_data():
    parse_data()
    return res(current_app, handle_z_axes_to_zero())

