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
    def __init__(self):
        # self.llm = Qwen(model=settings.MODEL_NAME, endpoint_url=settings.ENDPOINT_URL, stream=True)
        self.llm = QianfanChatEndpoint(
            model="ERNIE-4.0-8K",
            temperature=0.2,
            timeout=30,
            api_key="gp0NggdSwB8F7VXnqHLRrHPv",
            secret_key="KqZ0IGJiQIypzwTVJRFcBajF3WjIJbOt",
            top_p="0.8",
            streaming=True
        )
        self.sessions = Sessions()
        self.agent = self.build_agent()

    def build_agent(self):
        # 数据
        logger.info("Loading data...")
        df = pd.read_excel("../tests/data/统计年鉴-生产总值相关数据.xlsx")

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

    @staticmethod
    async def _stream(agent, session):

        msg = ''
        final = False
        async for event in agent.astream_events(session.messages, version="v1"):
            kind = event["event"]
            # if kind == "on_llm_stream":
            if kind == "on_chat_model_stream":
                if event['data']['chunk'].content:
                    print(f"打印输出：{event['data']['chunk'].content}")
                    msg += event['data']['chunk'].content
                if not final and "Final Answer:" in msg:
                    logger.info("Final Answer:")
                    _msg = msg.split("Final Answer:")[1].lstrip()
                    if _msg:
                        # 存放历史消息
                        session.messages.append(Message(role="assistant", content=_msg))
                        # 最多存放5组对话
                        if len(session.messages) > 10:
                            del session.messages[0:2]
                        yield _msg
                    final = True
                elif final:
                    yield event['data']['chunk'].content

        logger.info("Stream ended.")

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
