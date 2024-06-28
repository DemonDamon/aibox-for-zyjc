# Date    : 2024/6/26 14:57
# File    : llm.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com


from pydantic import BaseModel
from typing import Optional, Dict, List, Union, Literal


class Message(BaseModel):
    role: Literal['system', 'user', 'assistant'] = None
    content: str = ''


class Session(BaseModel):
    messages: List[Message] = []


class Sessions(BaseModel):
    sessions: Dict[str, Session] = {}
