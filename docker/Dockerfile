ARG FROM_IMAGE_NAME=python:3.10.13

FROM ${FROM_IMAGE_NAME}

LABEL authors="leemysw"

WORKDIR /opt/app

COPY agents.py  /usr/local/lib/python3.10/site-packages/langchain_core/agents.py

COPY requirements.txt .

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    pip install -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .


ENTRYPOINT []