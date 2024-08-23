
# Date    : 2024/6/26 14:48
# File    : table_agent_api.py
# Desc    :
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com

from typing import Union
from uuid import uuid4

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

import settings
from models.table_agent import RequestModel, ResponseData, ResponseModel
from services.table_agent_service import TableAgentService
from utils.sse import EventSourceResponse, ServerSentEvent
from utils.logger_utils import logger

api_router = APIRouter()
table_agent_service = TableAgentService(qwen=False)


async def streaming_data(output, request_data):
    async for i in output:
        data = jsonable_encoder(ResponseModel(
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
        ), exclude_unset=True)
        yield ServerSentEvent(data=data)
    data = jsonable_encoder(ResponseModel(
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
    ), exclude_unset=True)
    yield ServerSentEvent(data=data)
    logger.info(f"streaming data end for request_id: {request_data.request_id}")


@api_router.post("/table-agent", response_model=Union[ResponseModel, str], name="获取表信息")
async def table_qa(request_data: RequestModel):
    """
    示例：获取表代理的信息
    """
    logger.info(f"request_data: {request_data}")

    output = table_agent_service(request_data, streaming=request_data.streaming)
    if request_data.streaming:
        generator = streaming_data(output, request_data)
        return EventSourceResponse(generator, media_type="text/event-stream")
    else:
        return ResponseModel(
            code=settings.SUCCESS_CODE,
            success=True,
            message="success",
            data=jsonable_encoder(
                ResponseData(
                    request_id=request_data.request_id,
                    session_id=request_data.session_id,
                    result=output
                ),
                exclude_unset=True
            )
        )
