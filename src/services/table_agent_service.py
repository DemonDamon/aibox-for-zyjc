# Date    : 2024/6/26 14:47
# File    : table_agent_service.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com

import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_experimental.tools import PythonAstREPLTool

import settings
from services.qwen_langchain_service import Qwen
from utils.logger_utils import logger


class TableAgentService:
    def __init__(self):
        self.llm = Qwen(model=settings.MODEL_NAME, endpoint_url=settings.ENDPOINT_URL, stream=True)
        self.agent = self.build_agent()

    def build_agent(self):
        # 数据
        logger.info("Loading data...")
        df = pd.read_excel("../tests/data/gdp.xlsx")

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
    async def _stream(agent, prompt):
        msg = ''
        final = False
        async for event in agent.astream_events(prompt, version="v1"):
            kind = event["event"]
            if kind == "on_llm_stream":
                msg += event['data']['chunk']
                if not final and "Final Answer:" in msg:
                    logger.info("Final Answer:")
                    _msg = msg.split("Final Answer:")[1].lstrip()
                    if _msg:
                        yield _msg
                    final = True
                elif final:
                    yield event['data']['chunk']

        logger.info("Stream ended.")

    def __call__(self, query, streaming=False):
        # 初始化对话历史
        conversation_history = ""
        prompt = f"{query}；要求：1. 请使用工具python_repl_ast；2. 用中文回答"
        if streaming:
            return self._stream(self.agent, prompt)
        else:
            return self.agent.run(prompt)
