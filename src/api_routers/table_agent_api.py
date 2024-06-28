# Date    : 2024/6/26 14:48
# File    : table_agent_api.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com

from typing import Union
from uuid import uuid4

from fastapi import APIRouter

import settings
from models.table_agent import RequestModel, ResponseData, ResponseModel
from services.table_agent_service import TableAgentService
from utils.sse import EventSourceResponse, ServerSentEvent
from utils.logger_utils import logger

api_router = APIRouter()
table_agent_service = TableAgentService()


async def streaming_data(output, request_data):
    async for i in output:
        data = ResponseModel(
            code=settings.SUCCESS_CODE,
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
        code=settings.SUCCESS_CODE,
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

    output = table_agent_service(request_data, streaming=request_data.streaming)
    if request_data.streaming:
        generator = streaming_data(output, request_data)
        return EventSourceResponse(generator, media_type="text/event-stream")
    else:
        return ResponseModel(
            code=settings.SUCCESS_CODE,
            success=True,
            message="success",
            data=ResponseData(
                request_id=request_data.request_id,
                session_id=request_data.session_id,
                result=output
            ).model_dump(exclude_unset=True)
        )
