from typing import Optional

import sys
import os


import requests
import pandas as pd

from langchain_community.llms import Ollama
from langchain_community.llms.moonshot import Moonshot
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.chat_models import ChatTongyi

from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_experimental.agents import create_csv_agent
from langchain_experimental.tools import PythonAstREPLTool
from langchain.agents import AgentExecutor, AgentType
from langchain_core.pydantic_v1 import BaseModel, Field

# 获取当前文件的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 假设src目录与tests目录同级
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)


def test_2():
    df = pd.read_excel("gdp.xlsx")

    tool = PythonAstREPLTool(locals={"df": df})
    tool.invoke("df['GDP(万亿)'].mean()")

    llm = QianfanChatEndpoint(
        model="ERNIE-4.0-8K",
        temperature=0.2,
        timeout=30,
        api_key="gp0NggdSwB8F7VXnqHLRrHPv",
        secret_key="KqZ0IGJiQIypzwTVJRFcBajF3WjIJbOt",
        top_p="0.8",
        streaming=True
    )

    agent = create_pandas_dataframe_agent(llm,
                                          df,
                                          verbose=True,
                                          allow_dangerous_code=True,
                                          handle_parsing_errors=True)

    conversation_history = ""  # 初始化对话历史

    while True:
        question = input("请输入你的问题(输入'esc'退出):\n【用户】: ")
        if question.lower() == "esc":
            print("对话结束,再见!")
            break

        try:
            prompt = f"{question}；要求：1. 请使用工具python_repl_ast；2. 用中文回答"
            output = agent.run(prompt)
            response = f"{output}"

            conversation_history += f"{prompt}\n{response}\n"
            print(f"【TableAgent】: {output}")
        except ValueError as e:
            print(f"\nError occurred: {e}")


def test_3():
    llm = Ollama(
        base_url='http://192.168.32.119:11434',
        model="qwen:32b"
    )
    # llm.invoke("告诉我一个笑话")

    messages = [("system", "你是一名AI助手。")]

    while True:
        question = input("【用户】:")

        if question.lower() == "esc":
            print("对话结束，再见!")
            break

        messages.append(("human", question))

        chunk_buffer = ""

        # 注意：代码中的`end=''`是为了让print不换行，`flush=True`则是立即输出缓冲区的内容，
        # 这样做可以让输出看起来像是实时的，适用于流式处理的场景。
        print("【助手】:", end='', flush=True)

        for chunk in llm.stream(messages):
            # 确保content属性存在，根据实际情况调整
            out = chunk.content.strip()
            chunk_buffer += out
            print(out, end='', flush=True)
        print("\n")
        messages.append(("assistant", chunk_buffer))


def test_4():
    # 根目录在src，去src/services下查看
    from services.qwen_langchain_service import Qwen

    # 数据
    df = pd.read_excel("gdp.xlsx")

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

    while True:
        question = input("请输入你的问题(输入'esc'退出):\n【用户】: ")
        if question.lower() == "esc":
            print("对话结束,再见!")
            break

        try:
            prompt = f"{question}；要求：1. 请使用工具python_repl_ast；2. 用中文回答"
            output = agent.run(prompt)
            response = f"{output}"

            conversation_history += f"{prompt}\n{response}\n"
            print(f"【TableAgent】: {output}")

        except ValueError as e:
            print(f"\nError occurred: {e}")


if __name__ == "__main__":
    test_4()
