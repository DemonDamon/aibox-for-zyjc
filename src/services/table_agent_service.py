# Date    : 2024/6/26 14:47
# File    : table_agent_service.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com


import os
import random
import re
import time

import pandas as pd
from collections import defaultdict

from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_experimental.tools import PythonAstREPLTool
from langchain_community.chat_models import QianfanChatEndpoint

import settings
from services.qwen_langchain_service import Qwen
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
        self.table_agent = self.build_table_agent()

        intentcls_prompts = read_yaml(os.path.join(SRC_PATH, "prompts/intentcls.yml"))
        intentcls_prompt_version = 20240701
        self.intentcls_prompt = intentcls_prompts["specific_prompt_template"][0][intentcls_prompt_version]

        chitchat_prompts = read_yaml(os.path.join(SRC_PATH, "prompts/chitchat.yml"))
        chitchat_prompt_version = 20240701
        self.chitchat_prompt = chitchat_prompts["specific_prompt_template"][0][chitchat_prompt_version]

    def intent_cls(self, query):
        # message = [
        #     ("system", self.intentcls_prompt),
        #     ("user", query)
        # ]
        llm_input = self.intentcls_prompt.replace("{query}", query)
        if self.llm_model == "qianfan":
            return self.llm.invoke(llm_input)
        else:
            raise ValueError(f"{self.llm_model} not support")

    def build_table_agent(self):
        # 数据
        logger.info("Loading data...")
        df = pd.read_excel("../tests/data/黑龙江省年度地区生产总值.xlsx")

        # 工具
        # tool = PythonAstREPLTool(locals={"df": df})
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

    async def _stream(self, agent, prompt):
        msg = ''
        final = False
        is_print_thought = False
        is_print_action = False
        is_print_start_thought = False
        is_start_final = False
        async for event in agent.astream_events(prompt, version="v1"):
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
                    logger.info("!!!!"+content)
                    # yield str(content)

                    # content = content.replace("Thoug", "思考过程")
                    # if "Thoug" in msg and "ht" in content:
                    #     content = content.replace("ht", "")
                    # content = content.replace("Action Input", "工具输入")
                    # content = content.replace("Action", "执行工具")
                    # content = content.replace("Final Answer", "最终结论")
                    # logger.info("!!!! - " + content)
                    # for _ in str(content):
                    #     yield _

                    if not is_print_start_thought and "Thoug" in msg:
                        is_print_start_thought = True
                        for _ in random.choice(let_me_think):
                            yield _
                            time.sleep(0.1)

                    if not is_print_thought and "Thought:" in msg and "Action:" in msg:
                        # _pattern = r"Thought:\s*(.*?)\s*Action:"
                        # _match = re.search(_pattern, msg, re.DOTALL)
                        # if _match:
                        #     for _ in _match.group(1):
                        #         yield _
                        # else:
                        #     for _ in "让我再思考一下，请稍等 ...\n":
                        #         yield _
                        is_print_thought = True

                    if not is_print_action and "Action:" in msg:
                        is_print_action = True

                        # _pattern = r"Action:\s*(.*?)\s*Final Answer:"
                        # _match = re.search(_pattern, msg, re.DOTALL)
                        # if _match:
                        #     for _ in _match.group(1):
                        #         yield _

                        for _ in random.choice(let_me_try):
                            yield _
                            time.sleep(0.1)

                    if is_start_final:
                        for _ in content:
                            yield _
                            time.sleep(0.1)

                    if not is_start_final and "Final Answer:" in content:
                        is_start_final = True
                        _msg = msg.split("Final Answer:")[1].lstrip()
                        for _ in _msg:
                            yield _
                            time.sleep(0.1)

                    # if not final and "Final Answer:" in msg:
                    #     _msg = msg.split("Final Answer:")[1].lstrip()
                    #     if _msg:
                    #         # 存放历史消息
                    #         # session.messages.append(Message(role="assistant", content=_msg))
                    #         # # 最多存放5组对话
                    #         # if len(session.messages) > 10:
                    #         #     del session.messages[0:2]
                    #         yield _msg
                    #     final = True
                    # elif final:
                    #     yield content

    async def _stream_chitchat(self, llm, prompt):
        async for event in llm.astream_events(prompt, version="v1"):
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
                    logger.info("!!!!"+content)
                    for _ in content:
                        yield _
                        time.sleep(0.1)

    def __call__(self, request_data, streaming=False):
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
        # prompt = f"要求：" \
        #          f"1. 请使用工具python_repl_ast" \
        #          f"2. 用中文回答" \
        #          f"3. 计算前先导入pandas库" \
        #          f"4. 思考过程只需要给出简明扼要的逻辑，且不要提及用到`pandas`和`dataframe`等字眼" \
        #          f"5. 思考过程不要提及使用到工具，以及数据细节" \
        #          f"6. 在最终结论的时候，如果涉及趋势分析，给出可能的原因分析" \
        #          f"" \
        #          f"现在用户的输入是：{query}"
        prompt = f"要求：" \
                 f"1. 请使用工具python_repl_ast" \
                 f"2. 用中文回答" \
                 f"3. 计算前先导入pandas库" \
                 f"4. 思考过程只需要给出简明扼要的逻辑，且不要提及用到`pandas`和`dataframe`等字眼" \
                 f"5. 思考过程不要提及使用到工具，以及数据细节" \
                 f"6. 如果涉及趋势分析，在Final Answer要给出可能的原因分析" \
                 f"" \
                 f"现在用户的输入是：{query}"
        # 存放用户消息
        session.messages.append(Message(role="user", content=prompt))
        if streaming:
            intent_cls = self.intent_cls(query)
            if "table_analysis" in intent_cls.content:
                return self._stream(self.table_agent, prompt)
            else:
                # 闲聊意图
                return self._stream_chitchat(self.llm, self.chitchat_prompt.replace("{query}", query))
        else:
            return self.table_agent.run(prompt)
