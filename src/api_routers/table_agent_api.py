# Date    : 2024/6/26 14:48
# File    : table_agent_api.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com

from typing import Union
from uuid import uuid4

from fastapi import APIRouter

from models.table_agent import RequestModel, ResponseData, ResponseModel
from settings.dev import *
from utils.sse import EventSourceResponse, ServerSentEvent

api_router = APIRouter()


async def mock_streaming_data(request_data):
    """
    模拟数据流
    """
    for i in "你好，我是表格助手，请问有什么可以帮助您？":
        data = ResponseModel(
            code=SUCCESS_CODE,
            success=True,
            message="success",
            data=ResponseData(
                request_id=request_data.request_id,
                session_id=request_data.session_id,
                result=i,
                chunk_id=str(uuid4().hex),
                is_end=False,
            )
        ).model_dump_json(exclude_unset=True)
        yield ServerSentEvent(data=data)
    data = ResponseModel(
        code=SUCCESS_CODE,
        success=True,
        message="success",
        data=ResponseData(
            request_id=request_data.request_id,
            session_id=request_data.session_id,
            result="",
            chunk_id=str(uuid4().hex),
            is_end=True,
        )
    ).model_dump_json(exclude_unset=True)
    yield ServerSentEvent(data=data)
    yield ServerSentEvent(data="[DONE]", event="close")


@api_router.post("/table-agent", response_model=Union[ResponseModel, str], name="获取表信息")
async def table_qa(request_data: RequestModel):
    """
    示例：获取表代理的信息
    """
    # TODO: 实际的逻辑处理，比如调用服务
    output = "你好，我是表格助手，请问有什么可以帮助您？"
    if request_data.streaming:
        generator = mock_streaming_data(request_data)
        return EventSourceResponse(generator, media_type="text/event-stream")
    else:
        return ResponseModel(
            code=SUCCESS_CODE,
            success=True,
            message="success",
            data=ResponseData(
                request_id=request_data.request_id,
                session_id=request_data.session_id,
                result=output
            ).model_dump(exclude_unset=True)
        )
