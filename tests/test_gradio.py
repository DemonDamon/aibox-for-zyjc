import sys
import os

# 获取当前文件的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 假设src目录与tests目录同级
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)

import io
import gradio as gr
import pandas as pd

from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_experimental.tools import PythonAstREPLTool
from services.qwen_langchain_service import Qwen
from langchain.chat_models import QianfanChatEndpoint

import logging


SUPPORTED_POSTFIX = ['.xlsx', '.xls', '.csv']

# 配置日志模块
logging.basicConfig(
    level=logging.INFO,  # 设置最低日志级别为INFO
    format='%(asctime)s [%(levelname)s] %(message)s',  # 日志格式化字符串
    datefmt='%Y-%m-%d %H:%M:%S',  # 时间格式
    handlers=[  # 设置日志处理器
        logging.FileHandler('app.log', mode='w'),  # 将日志输出到文件
        logging.StreamHandler(sys.stdout)  # 同时将日志输出到控制台（stdout）
    ]
)

# 获取名为当前模块的logger实例
logger = logging.getLogger(__name__)


def clear_conversation(*args):
    """清空对话历史"""
    global conversation_history
    conversation_history = ""
    logger.info("对话历史已清空")


def get_file_extension(filename):
    """
    获取文件名的后缀名（扩展名）。

    参数:
    filename (str): 完整的文件名，包括后缀名。

    返回:
    str: 文件的后缀名（带点）。如果文件名没有后缀，则返回空字符串。
    """
    dot_position = filename.rfind('.')  # 查找最后一个点的位置
    if dot_position == -1 or dot_position == 0:  # 如果找不到点，或者点是文件名的第一个字符，则认为没有后缀名
        return ""
    else:
        return filename[dot_position:]  # 返回点及之后的部分，即后缀名


def get_llm(model_choice):
    logger.info(f"选择模型{model_choice}")

    if model_choice == "Qwen":
        return Qwen(
            model="Qwen1.5-32B-Chat-GPTQ-Int4",
            endpoint_url="http://192.168.32.113:7820/aibox/v1/llm/chat/completions",
            stream=True
        )
    elif model_choice == "Qianfan":
        return QianfanChatEndpoint(
            model="ERNIE-4.0-8K",
            temperature=0.2,
            timeout=30,
            api_key="gp0NggdSwB8F7VXnqHLRrHPv",
            secret_key="KqZ0IGJiQIypzwTVJRFcBajF3WjIJbOt",
            top_p="0.8",
            streaming=True
        )


def capture_output(func):
    def wrapper(*args, **kwargs):
        # 创建StringIO对象
        captured_output = io.StringIO()
        # 保存原始的stdout
        sys.stdout = captured_output

        try:
            # 运行函数
            result = func(*args, **kwargs)
            # 获取捕获的输出
            output = captured_output.getvalue()
            return result, output
        finally:
            # 恢复原始的stdout
            sys.stdout = sys.__stdout__

    return wrapper


# 初始化对话历史
conversation_history = ""


@capture_output
def analyze_table(file, local_file, question, model_choice):
    global conversation_history

    if file:
        file_name = file.name
    elif local_file:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(curr_dir, "data", local_file)
    else:
        raise ValueError("请上传文件或选择本地文件")

    logger.info(f"当前上传文件为：{file}")
    logger.info(f"当前选择的表格文件为：{local_file}")

    file_ext = get_file_extension(file_name)
    if file_ext not in SUPPORTED_POSTFIX:
        raise ValueError("只支持xlsx、xls和csv格式的文件")

    if file_ext == ".xlsx" or file_ext == ".xls":
        # 读取上传的Excel文件
        df = pd.read_excel(file_name)
    elif file_ext == ".csv":
        # 读取上传的CSV文件
        df = pd.read_csv(file_name)

    # 获取选择的LLM
    llm = get_llm(model_choice)

    # 工具
    tool = PythonAstREPLTool(locals={"df": df})

    # 定义agent
    agent = create_pandas_dataframe_agent(llm, df, verbose=True,
                                          allow_dangerous_code=True,
                                          agent_executor_kwargs={
                                              "handle_parsing_errors": True})

    try:
        # prompt = f"{question}；要求：1. 请使用工具python_repl_ast；2. 用中文回答"
        prompt = f"用户：{question}"
        output = agent.run(conversation_history + prompt)
        conversation_history += f"{prompt}\n助手：{output}\n"

        logger.info(conversation_history)

        return output

    except ValueError as e:
        return f"错误：{str(e)}"


local_table_list = os.listdir("data")

# # 创建可交互的File组件，绑定change事件
# file_upload = gr.File(interactive=True, label="上传Excel文件").change(clear_conversation, inputs=None, outputs=None)
# dropdown_table = gr.Dropdown(choices=local_table_list, label="选择本地数据表", interactive=True).change(clear_conversation, inputs=None, outputs=None)

# 创建Gradio界面
iface = gr.Interface(
    fn=analyze_table,
    inputs=[
        gr.File(label="上传Excel文件"),
        gr.Dropdown(choices=local_table_list, label="选择本地数据表"),  # 实际应用中此处需动态填充
        gr.Textbox(label="输入你的问题"),
        gr.Radio(["Qwen", "Qianfan"], label="选择模型", value="Qwen")
    ],
    outputs=[
        gr.Textbox(label="回答"),
        gr.Textbox(label="处理过程", lines=10)
    ],
    title="TableAgent - 表格问答助手",
    description="上传一个Excel文件，选择模型，然后问一个关于表格数据的问题。"
)

# 启动应用
if __name__ == "__main__":
    iface.launch()
