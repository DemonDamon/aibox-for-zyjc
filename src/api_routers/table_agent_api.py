# Date    : 2024/6/26 14:48
# File    : table_agent_api.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com


from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from models.table_agent import RequestModel, ResponseModel, ResponseData
from settings.dev import *

api_router = APIRouter()


@api_router.post("/table-agent", response_model=ResponseModel, name="获取表信息")
async def table_qa(request_data: RequestModel):
    """
    示例：获取表代理的信息
    """
    # TODO: 实际的逻辑处理，比如调用服务
    output = "你好，我是表格助手，请问有什么可以帮助您？"

    return ResponseModel(
        code=SUCCESS_CODE,
        success=True,
        message="success",
        data=ResponseData(
            request_id=request_data.request_id,
            session_id=request_data.session_id,
            text=output
        ).model_dump()
    )
