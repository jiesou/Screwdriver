import os, json


def res(app, data):
    response = {}
    if isinstance(data, dict):
        response['code'] = data.pop("code", 200)
        if "message" in data: response['message'] = data.pop("message")
    if data:
        response['data'] = data

    res = app.json.response(response)
    res.status_code = response.get('code', 200)
    return res

def parse_body(req, default):
    # 根据请求的内容类型解析 body
    content_type = req.headers.get("Content-Type")
    if content_type == "application/json":
        data = req.get_json(silent=True) 
    elif content_type == "multipart/form-data":
        data = req.form.to_dict()
    else:
        data = req.get_json(force=True, silent=True)

    return data if data is not None else default

