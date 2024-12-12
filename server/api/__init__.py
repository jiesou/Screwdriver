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
    data = await request.get_json()
    processor_api.set_screws(data['screws'])
    processor_api.imu_api.processor.h = data['h']
    processor_api.imu_api.processor.center_point = data['center_point']
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

@api_bp.route('/screw_tightening')
def screw_tightening():
    print(11)
    processor_api.current_api.processor.is_working = not processor_api.current_api.processor.is_working
    return res(current_app, None)

@api_bp.route('/start_record', methods=['POST'])
async def start_record():
    def generate():
        yield "{}\n"
        try:
            for data_snippet in processor_api.handle_start_moving():
                # 只需要位置和是否拧螺丝两个状态
                yield json.dumps({
                    "position": data_snippet["position"],
                    "is_screw_tightening": data_snippet["is_screw_tightening"]
                }) + "\n"
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
