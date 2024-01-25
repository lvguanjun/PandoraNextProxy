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

conversation_meta_route = "/backend-api/conversation/{conversation_id}"


@app.get(models_route)
async def proxy_route(request: Request):
    # 向目标URL发送请求
    target_url = TARGET_HOST + models_route
    resp = requests.get(
        target_url, params=request.query_params, headers=request.headers
    )
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
    else:
        return Response(
            content=resp.content, status_code=resp.status_code, headers=resp.headers
        )
    # 更新响应数据
    data["models"].append(mobile_model)
    content = json.dumps(data)
    # 返回更新后的响应
    resp.headers["content-length"] = str(len(content))
    return Response(content=content, status_code=200, headers=resp.headers)


@app.get(conversation_meta_route)
async def proxy_conversation_route(request: Request, conversation_id: str):
    # 向目标URL发送请求
    target_url = TARGET_HOST + conversation_meta_route.format(
        conversation_id=conversation_id
    )
    resp = requests.get(
        target_url, params=request.query_params, headers=request.headers
    )

    if resp.status_code == 200:
        data = resp.json()
        # 遍历所有的mapping，如果找到 "model_slug": "gpt-4"，则将其改为 "gpt-4-mobile"
        for node in data["mapping"].values():
            if message := node.get("message"):
                if metadata := message.get("metadata"):
                    if metadata.get("model_slug") == "gpt-4":
                        metadata["model_slug"] = "gpt-4-mobile"

        # 更新响应数据
        content = json.dumps(data)
        # 更新响应头
        resp.headers["content-length"] = str(len(content))
        return Response(content=content, status_code=200, headers=resp.headers)
    else:
        # 如果响应状态码不是200，直接返回原始响应
        return Response(
            content=resp.content, status_code=resp.status_code, headers=resp.headers
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8345)
