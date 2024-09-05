from flask import Flask, send_from_directory, stream_with_context, request, g
from werkzeug.exceptions import HTTPException
import os
from .units import res
from .api import api_bp

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 30
# 最大上传大小 30M

app.register_blueprint(api_bp, url_prefix='/api')


@app.errorhandler(HTTPException)
def http_error(e):
    response = res(app, {
        'code': e.code,
        'message': e.name})
    response.status = e.code
    return response

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:file>')
def static_ui(file):
    return send_from_directory('static', file)

@app.route('/api')
def api_index():
    return res(app, {
        'status': 'running',
        'version': '1.0.0'})

if __name__ == '__main__':
    app.run(port=3000, use_reloader=True)
