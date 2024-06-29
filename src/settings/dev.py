# Date    : 2024/6/26 14:50
# File    : dev.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com

import os

PROJECT_NAME = "龙政智搜"
HOST = "0.0.0.0"
PORT = 5001
DEBUG = True
LIFESPAN = "on"
ROOT_PATH = os.path.abspath(os.path.dirname(__file__)) + '/../'

MODEL_NAME = "Qwen1.5-32B-Chat-GPTQ-Int4"
ENDPOINT_URL = "http://192.168.32.113:7820/aibox/v1/llm/chat/completions"
#
# MODEL_NAME = "Qwen2-72B-Instruct-GPTQ-Int4"
# ENDPOINT_URL = "http://192.168.32.250:6822/aibox/v1/llm/chat/completions"

SUCCESS_CODE = "0000"

ERROR_CODE = "9999"
ERROR_REQUEST_PARAM = "01000101"  # 请求参数错误的错误代码
ERROR_REQUEST_TIMEOUT = "01000102"  # 请求超时的错误代码
ERROR_REQUEST_FORMAT = "01000103"  # 请求格式错误的错误代码
ERROR_SERVER_RESPONSE = "02000101"  # 服务器响应异常的错误代码
ERROR_SERVICE_UNAVAILABLE = "02000102"  # 系统服务不可用的错误代码
ERROR_FEATURE_CLOSED = "02000103"  # 功能未开放的错误代码
