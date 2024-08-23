# Date    : 2024/6/26 14:51
# File    : main.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com

import time

import uvicorn
from fastapi import FastAPI, Request

import settings
from api_routers.table_agent_api import api_router as table_agent_api_router
from utils.logger_utils import logger

# 创建App
app = FastAPI(
    debug=True,
    title=settings.PROJECT_NAME
)

# 注册路由
app.include_router(
    table_agent_api_router,
    prefix="/cmict",
    tags=["Table Agent APIs"]
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.url} -> process_time:{process_time}")
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        lifespan=settings.LIFESPAN
    )
