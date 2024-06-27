# Date    : 2024/6/26 19:22
# File    : test_qwen_api.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com


def test():
    import requests
    import json

    url = "http://192.168.32.113:7820/aibox/v1/llm/chat/completions"

    payload = json.dumps({
        "request_id": "test-jbjsax-89ujwbjdq-dbjdh8",
        "model": "Qwen1.5-32B-Chat-GPTQ-Int4",
        "messages": [
            {
                "role": "system",
                "content": "你是文员，负责提取客户提供的信息中的地址，地址输出要求按照以下格式，不要输出多余内容：xx省xx市xx区，成功：xx。如果提取到信息，请不要虚构，提示未找到地址"
            },
            {
                "role": "user",
                "content": "我的地址是广东省广州市天河区，可以办理宽带吗"
            }
        ],
        "stream": False,
        "max_tokens": 52
    })
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def test_2():
    from services.qwen_langchain_service import Qwen
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate

    # 定义模型参数
    model_name = "Qwen1.5-32B-Chat-GPTQ-Int4"
    endpoint_url = "http://192.168.32.113:7820/aibox/v1/llm/chat/completions"

    # 初始化Qwen模型
    qwen_llm = Qwen(model=model_name, endpoint_url=endpoint_url, stream=True)

    # 定义prompt模板
    template = """
    你是文员，负责提取客户提供的信息中的地址，地址输出要求按照以下格式，不要输出多余内容：xx省xx市xx区，成功：xx。如果提取到信息，请不要虚构，提示未找到地址

    {question}
    """

    prompt = PromptTemplate(template=template, input_variables=["question"])

    # 创建Chain
    chain = LLMChain(prompt=prompt, llm=qwen_llm)

    # 调用Chain来处理用户的问题
    question = "我的地址是广东省广州市天河区，可以办理宽带吗"
    response = chain.run(question)

    print(response)