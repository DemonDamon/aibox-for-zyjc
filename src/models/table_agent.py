# Date    : 2024/6/26 14:58
# File    : table_agent.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com


from pydantic import BaseModel, Field
from typing import Optional
from fastapi import UploadFile


class RequestModel(BaseModel):
    request_id: str = Field(..., description="单次请求id")
    session_id: str = Field(..., description="当前对话id")
    query: str = Field(..., max_length=2000, description="当前用户输入text，限制2k以内")
    table_file: Optional[UploadFile] = Field(None, description="二进制数据，如果传过来则针对当前表格进行问答，否则根据默认已传表格问答")

    class Config:
        arbitrary_types_allowed = True


# 定义响应的数据结构
class ResponseData(BaseModel):
    request_id: str = Field(..., description="单次请求id")
    session_id: str = Field(..., description="当前对话id")
    text: str = Field(..., max_length=2000, description="当前系统回复的text")


class ResponseModel(BaseModel):
    success: bool = Field(..., description="判断状态标识")
    code: str = Field(..., description="返回码")
    message: str = Field(..., description="具体信息")
    data: Optional[ResponseData] = None  # 数据对象
