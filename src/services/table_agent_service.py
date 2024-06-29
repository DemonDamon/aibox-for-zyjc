# Date    : 2024/6/26 14:47
# File    : table_agent_service.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com

import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_experimental.tools import PythonAstREPLTool
from langchain_community.chat_models import QianfanChatEndpoint
from collections import defaultdict
import settings
from services.qwen_langchain_service import Qwen
from utils.logger_utils import logger
from models.llm import *


class TableAgentService:
    def __init__(self, qwen=True):
        if qwen:
            self.llm_model = "qwen"
            self.llm = Qwen(model=settings.MODEL_NAME, endpoint_url=settings.ENDPOINT_URL, stream=False)
        else:
            self.llm_model = "qianfan"
            self.llm = QianfanChatEndpoint(
            model="ERNIE-4.0-8K",
            temperature=0.1,
            timeout=30,
            qianfan_ak="gp0NggdSwB8F7VXnqHLRrHPv",
            qianfan_sk="KqZ0IGJiQIypzwTVJRFcBajF3WjIJbOt",
            top_p=1,
            streaming=True
        )
        self.sessions = Sessions()
        self.agent = self.build_agent()

    def build_agent(self):
        # 数据
        logger.info("Loading data...")
        df = pd.read_excel("../tests/data/黑龙江省年度地区生产总值.xlsx")

        # 工具
        tool = PythonAstREPLTool(locals={"df": df})
        # tool.invoke("df['GDP(万亿)'].mean()")
        logger.info("Creating agent...")

        # 定义agent
        agent = create_pandas_dataframe_agent(
            self.llm,
            df,
            verbose=True,
            allow_dangerous_code=True,
            agent_executor_kwargs={"handle_parsing_errors": True}
        )
        logger.info("Agent created.")
        return agent

    async def _stream(self, agent, session):
        msg = ''
        final = False
        async for event in agent.astream_events(session.messages, version="v1"):
            kind = event["event"]
            if self.llm_model == "qwen":
                kind_key = "on_llm_stream"

            else:
                kind_key = "on_chat_model_stream"

            if kind == kind_key:
                if self.llm_model == "qwen":
                    content = event['data']['chunk']
                else:
                    content = event['data']['chunk'].content
                if content:
                    msg += content
                    yield content
                if not final and "Final Answer:" in msg:
                    _msg = msg.split("Final Answer:")[1].lstrip()
                    if _msg:
                        # 存放历史消息
                        session.messages.append(Message(role="assistant", content=_msg))
                        # 最多存放5组对话
                        if len(session.messages) > 10:
                            del session.messages[0:2]
                #         yield _msg
                #     final = True
                # elif final:
                #     yield content

    def __call__(self, request_data, streaming=False):
        # 初始化对话历史
        conversation_history = ""
        query = request_data.query
        # 获取session_id
        session_id = request_data.session_id
        if not isinstance(self.sessions.sessions.get(session_id, []), Session):
            self.sessions.sessions[session_id] = Session()
            session = self.sessions.sessions[session_id]
            print(session)
        else:
            session = self.sessions.sessions.get(session_id, [])
        prompt = f"{query}；要求：1. 请使用工具python_repl_ast；2. 用中文回答"
        # 存放用户消息
        session.messages.append(Message(role="user", content=prompt))
        if streaming:
            return self._stream(self.agent, session)
        else:
            return self.agent.run(prompt)
