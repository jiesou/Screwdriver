import json
import time
from quart import Blueprint, Response, current_app, request, stream_with_context
from server.units import res

from imu.communication import z_axes_to_zero
from processor import ProcessorAPI
import traceback

api_bp = Blueprint('api', __name__)

processor_api = ProcessorAPI()

@api_bp.route('/reset_z_axes')
def reset_z_axes():
    result = z_axes_to_zero()
    return res(current_app, result)

@api_bp.route('/start_moving', methods=['POST'])
async def start_moving():
    processor_api.set_screws(await request.get_json())
    def generate():
        yield "{}\n"
        try:
            for data_snippet in processor_api.handle_start_moving():
                # 每个数据片段转换为JSON并添加换行符
                yield json.dumps(data_snippet) + "\n"
        except Exception:
            traceback.print_exc()
        except GeneratorExit:
            print("客户端断开连接")
            raise

    return Response(generate(), headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
        'Content-Type': 'text/event-stream'
    })


@api_bp.route('/simulate_screw_tightening')
def simulate_screw_tightening():
    processor_api.current_api.current_processor.is_working = not processor_api.current_api.current_processor.is_working
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
        processor_api.current_api.current_processor.is_working = True
        return "Data received", 200
    except json.JSONDecodeError:
        return json.dumps({}), 400
