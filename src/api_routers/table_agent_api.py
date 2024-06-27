# Date    : 2024/6/26 14:48
# File    : table_agent_api.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com

from typing import Union
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from utils.sse import EventSourceResponse, ServerSentEvent

from models.table_agent import RequestModel, ResponseModel, ResponseData
from settings.dev import *

import pandas as pd

from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_experimental.tools import PythonAstREPLTool

api_router = APIRouter()


def read_and_send(query):
    # 根目录在src，去src/services下查看
    from services.qwen_langchain_service import Qwen

    # 数据
    df = pd.read_excel("../tests/data/gdp.xlsx")

    # 工具
    tool = PythonAstREPLTool(locals={"df": df})
    # tool.invoke("df['GDP(万亿)'].mean()")

    # 定义模型参数和初始化Qwen模型
    model_name = "Qwen1.5-32B-Chat-GPTQ-Int4"
    endpoint_url = "http://192.168.32.113:7820/aibox/v1/llm/chat/completions"
    llm = Qwen(model=model_name, endpoint_url=endpoint_url, stream=True)

    # 定义agent
    agent = create_pandas_dataframe_agent(llm, df, verbose=True,
                                          allow_dangerous_code=True,
                                          agent_executor_kwargs={"handle_parsing_errors": True})

    # 初始化对话历史
    conversation_history = ""
    prompt = f"{query}；要求：1. 请使用工具python_repl_ast；2. 用中文回答"
    output = agent.run(prompt)
    return output


async def mock_streaming_data(request_data):
    query = request_data.query
    output = read_and_send(query)
    for i in output:
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
    # output = "你好，我是表格助手，请问有什么可以帮助您？"
    if request_data.streaming:
        generator = mock_streaming_data(request_data)
        return EventSourceResponse(generator, media_type="text/event-stream")
    else:
        query = request_data.query
        output = read_and_send(query)
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
