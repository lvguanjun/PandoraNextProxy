#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2023/12/08 17:23:36
@Author  :   lvguanjun
@Desc    :   main.py
"""

import json
from copy import deepcopy

import requests
from fastapi import FastAPI, Request, Response

app = FastAPI()

# 目标服务器地址
TARGET_HOST = "http://localhost:8182"

models_route = "/backend-api/models"


@app.get(models_route)
async def proxy_route(request: Request):
    # 向目标URL发送请求
    target_url = TARGET_HOST + models_route
    headers = dict(request.headers)
    headers["authority"] = headers["host"]
    resp = requests.get(target_url, params=request.query_params, headers=headers)
    if resp.status_code != 200 or "GPT-4" not in resp.text:
        # 返回目标服务器的原始响应
        return Response(
            content=resp.content, status_code=resp.status_code, headers=resp.headers
        )

    data = resp.json()
    for model in data["models"]:
        if model["slug"] == "gpt-4":
            mobile_model = deepcopy(model)
            mobile_model["slug"] = "gpt-4-mobile"
            mobile_model["title"] = "GPT-4 Mobile"
            break
    # 更新响应数据
    data["models"].append(mobile_model)
    content = json.dumps(data)
    # 返回更新后的响应
    resp.headers["content-length"] = str(len(content))
    return Response(content=content, status_code=200, headers=resp.headers)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8345)
