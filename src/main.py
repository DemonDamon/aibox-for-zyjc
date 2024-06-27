# Date    : 2024/6/26 14:51
# File    : main.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com


import uvicorn
from fastapi import FastAPI

import settings.dev as settings
from src.api_routers.table_agent_api import api_router as table_agent_api_router


# 创建App
app = FastAPI(
    debug=True,
    title=settings.PROJECT_NAME
)

# 注册路由
app.include_router(table_agent_api_router,
                   prefix="/cmict", tags=["Table Agent APIs"])


if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        lifespan=settings.LIFESPAN
    )
