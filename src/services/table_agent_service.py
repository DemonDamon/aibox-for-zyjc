# Date    : 2024/6/26 14:47
# File    : table_agent_service.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com


import os
import random
import asyncio

import pandas as pd

from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_experimental.agents.agent_toolkits.pandas.prompt import PREFIX
from langchain_openai.chat_models import ChatOpenAI

import settings
from utils.logger_utils import logger
from utils.utils import read_yaml
from models.llm import *

let_me_think = [
    "好的，请让我思考一下~ \n",
    "好的，请给我一点时间整理思路 ...\n",
    "好的，我需要仔细思考一下 ...\n",
    "好的，给我几秒钟来理清思路 ...\n",
    "好的，我正在深入思考 ...\n",
    "好的，我需要一点时间来消化这个问题 ...\n",
    "好的，让我稍微琢磨一下 ...\n",
    "好的，让我认真思考一下这个问题 ...\n",
    "好的，我在整理思路 ...\n",
    "好的，让我花点时间来仔细思考 ...\n",
    "好的，请给我些时间来思考这个问题 ...\n",
    "好的，让我认真地想一想 ...\n",
    "好的，我需要集中注意力来思考 ...\n"
]

let_me_try = [
    "我正在努力分析中，请稍等 ...\n",
    "我正在努力分析中，稍等片刻 ...\n",
    "我正在努力解决这个问题，马上就好 ...\n",
    "我正在尽力分析这个问题，请稍等 ...\n",
    "我正在尽力分析这个问题，马上就好 ...\n",
    "我正在尽力分析这个问题，请稍等片刻 ...\n",
    "我正在努力分析中，请稍等片刻 ...\n"
]

SRC_PATH = os.path.dirname(os.path.dirname(__file__))


class TableAgentService:
    def __init__(self):
        self.temperature = 0.5
        self.top_p = 0.85
        self.llm_name = "Qwen32"
        self.llm_qwen = ChatOpenAI(
            openai_api_base=settings.ENDPOINT_URL_32B,
            model=settings.MODEL_NAME_32B,
            openai_api_key="xxx",
            streaming=True,
            temperature=self.temperature,
            model_kwargs={"top_p": self.top_p}
        )
        self.llm_qianfan = QianfanChatEndpoint(
            model="ERNIE-4.0-8K",
            temperature=0.1,
            timeout=30,
            qianfan_ak="gp0NggdSwB8F7VXnqHLRrHPv",
            qianfan_sk="KqZ0IGJiQIypzwTVJRFcBajF3WjIJbOt",
            top_p=1,
            streaming=True
        )

        intentcls_prompts = read_yaml(os.path.join(SRC_PATH, "prompts/intentcls.yml"))
        intentcls_prompt_version = 20240701
        self.intentcls_prompt = intentcls_prompts["specific_prompt_template"][0][intentcls_prompt_version]

        chitchat_prompts = read_yaml(os.path.join(SRC_PATH, "prompts/chitchat.yml"))
        chitchat_prompt_version = 20240701
        self.chitchat_prompt = chitchat_prompts["specific_prompt_template"][0][chitchat_prompt_version]

        table_agent_prompts = read_yaml(os.path.join(SRC_PATH, "prompts/table_agent.yml"))
        table_agent_prompt_version = 20240704
        self.table_agent_prompt = table_agent_prompts["specific_prompt_template"][0][table_agent_prompt_version]

        self.sessions = Sessions()
        self.table_agent = self.build_table_agent(self.llm_qwen)

    def intent_cls(self, query):
        # message = [
        #     ("system", self.intentcls_prompt),
        #     ("user", query)
        # ]
        llm_input = self.intentcls_prompt.replace("{query}", query)
        return self.llm_qwen.invoke(llm_input)

    def build_table_agent(self, llm):
        # 数据
        logger.info("Loading data...")
        df = pd.read_excel("../tests/data/黑龙江省年度地区生产总值.xlsx")

        # 工具
        logger.info("Creating agent...")

        # 定义agent
        agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=True,
            allow_dangerous_code=True,
            agent_executor_kwargs={"handle_parsing_errors": True},
            number_of_head_rows=5,
            prefix=self.table_agent_prompt + PREFIX
        )
        logger.info("Agent created.")
        return agent

    def rebuild_table_agent(self, request_data):
        if request_data.model is None:
            request_data.model = self.llm_name

        if request_data.model == self.llm_name:
            return

        if request_data.model == "Qianfan":
            self.table_agent = self.build_table_agent(self.llm_qianfan)
            self.llm_name = "Qianfan"
        elif request_data.model == "Qwen32":
            self.llm_qwen = ChatOpenAI(
                openai_api_base=settings.ENDPOINT_URL_32B,
                model=settings.MODEL_NAME_32B,
                openai_api_key="xxx",
                streaming=True,
                temperature=self.temperature,
                model_kwargs={"top_p": self.top_p}
            )
            self.table_agent = self.build_table_agent(self.llm_qwen)
            self.llm_name = "Qwen32"
        elif request_data.model == "Qwen72":
            self.llm_qwen = ChatOpenAI(
                openai_api_base=settings.ENDPOINT_URL_72B,
                model=settings.MODEL_NAME_72B,
                openai_api_key="xxx",
                streaming=True,
                temperature=self.temperature,
                model_kwargs={"top_p": self.top_p}
            )
            self.table_agent = self.build_table_agent(self.llm_qwen)
            self.llm_name = "Qwen72"

    async def _stream(self, agent, prompt):
        msg = ''
        final = False
        is_print_thought = False
        is_print_action = False
        is_print_start_thought = False
        is_start_final = False
        async for event in agent.astream_events(prompt, version="v1"):
            kind = event["event"]
            kind_key = "on_chat_model_stream"
            if kind == kind_key:
                content = event['data']['chunk'].content
                if content:
                    msg += content

                    if not is_print_start_thought and "Thought" in msg:
                        for _ in random.choice(let_me_think):
                            yield _
                            await asyncio.sleep(0.1)
                        is_print_start_thought = True

                    # if not is_print_thought and "Thought:" in msg and "Action:" in msg:
                    #     # _pattern = r"Thought:\s*(.*?)\s*Action:"
                    #     # _match = re.search(_pattern, msg, re.DOTALL)
                    #     # if _match:
                    #     #     for _ in _match.group(1):
                    #     #         yield _
                    #     # else:
                    #     #     for _ in "让我再思考一下，请稍等 ...\n":
                    #     #         yield _
                    #     is_print_thought = True

                    # if not is_print_action and "Action:" in msg:
                    #     # _pattern = r"Action:\s*(.*?)\s*Final Answer:"
                    #     # _match = re.search(_pattern, msg, re.DOTALL)
                    #     # if _match:
                    #     #     for _ in _match.group(1):
                    #     #         yield _
                    #
                    #     for _ in random.choice(let_me_try):
                    #         yield _
                    #         await asyncio.sleep(0.1)
                    #
                    #     is_print_action = True
                    #
                    # if is_start_final:
                    #     for _ in content:
                    #         yield _
                    #         await asyncio.sleep(0.1)
                    #
                    # if "Final Answer:" in content:
                    #     _msg = msg.split("Final Answer:")[1].lstrip()
                    #     for _ in _msg:
                    #         yield _
                    # is_start_final = True

                    if not final and "Final Answer:" in msg:
                        _msg = msg.split("Final Answer:")[1].lstrip()
                        if _msg:
                            yield _msg
                        final = True
                    elif final:
                        yield content

    @staticmethod
    async def _stream_chitchat(llm, prompt):
        async for event in llm.astream_events(prompt, version="v1"):
            kind = event["event"]
            kind_key = "on_chat_model_stream"
            if kind == kind_key:
                content = event['data']['chunk'].content
                if content:
                    logger.info("!!!!" + content)
                    for _ in content:
                        yield _

    def __call__(self, request_data, streaming=False):

        # 重建agent
        self.rebuild_table_agent(request_data)

        # 初始化对话历史
        conversation_history = ""
        query = request_data.query
        # 获取session_id
        session_id = request_data.session_id
        if not isinstance(self.sessions.sessions.get(session_id, []), Session):
            self.sessions.sessions[session_id] = Session()
            session = self.sessions.sessions[session_id]
        else:
            session = self.sessions.sessions.get(session_id, [])
        # 存放用户消息
        session.messages.append(Message(role="user", content=query))
        if streaming:
            intent_cls = self.intent_cls(query)
            if "table_analysis" in intent_cls.content:
                return self._stream(self.table_agent, query)
            else:
                # 闲聊意图
                return self._stream_chitchat(self.llm_qwen, self.chitchat_prompt.replace("{query}", query))
        else:
            return self.table_agent.run(query)
