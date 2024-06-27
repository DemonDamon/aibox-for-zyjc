# Date    : 2024/6/26 14:48
# File    : table_agent_api.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com


from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

# 假设这里导入实际的依赖或逻辑处理函数
# from .dependencies import get_table_agent_service
from src.models import TableQARequest, TableQAResponse
from src.settings.dev import *

api_router = APIRouter()


@api_router.post("/table-agent", response_model=TableQAResponse, name="获取表信息")
async def table_qa(self, request: TableQARequest):
    """
    示例：获取表代理的信息
    """
    # 实际的逻辑处理，比如调用服务

    return TableQAResponse(code=SUCCESS_CODE,
                           success=True,
                           data=ResponseData(
                                requestId=request_data.requestId,
                                resultType=request_data.sendType,
                                base64=encoded_data
                            )
                         )


