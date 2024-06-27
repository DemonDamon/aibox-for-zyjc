# Date    : 2024/6/26 14:50
# File    : logger_utils.py
# Desc    : 
# Author  : Damon
# E-mail  : bingzhenli@hotmail.com

import os
import sys
import time
import logging
from typing import Optional
from logging import handlers
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

import settings
from utils.utils import get_host_ip, abspath


def setup_logger(
        name: str,
        save: Optional[bool] = False,
        filename: Optional[str] = None,
        mode: str = 'a',
        distributed_rank: bool = False,
        stdout: bool = True,
        socket: bool = False,
        rotating_size: bool = False,
        rotating_time: bool = False,
        level: str = 'debug',
        backupCount: int = 10,
        extra_fmt: Optional[str] = "",

):
    """
    日志模块

    :param level: 日志级别
    :param name: 日志名称
    :param filename: 日志文件名
    :param mode: 写模式
    :param distributed_rank: 是否分布式
    :param stdout: 是否终端输出
    :param save: 是否保存日志文件
    :param socket: 是否输出到socket
    :param rotating_size: 是否按文件大小切割
    :param rotating_time: 是都按日期切割
    :param backupCount: 保留日志文件个数
    :param extra_fmt: 额外的格式化
    :return:
    """

    if name in logging.Logger.manager.loggerDict.keys():
        return logging.getLogger(name)

    logger = logging.getLogger(name)
    level = level.upper()
    logger.setLevel(level)
    logger.propagate = False
    if distributed_rank:
        return logger

    # if settings.DEBUG:
    #     fmt = f"%(asctime)s -> %(levelname)-8s: %(module)-15s | %(lineno)-3d |{extra_fmt}%(message)s"
    # else:
    computer_ip, computer_name = get_host_ip()
    service_name = settings.PROJECT_NAME
    fmt = (f'%(asctime)s.%(msecs)03d|'
           f'{computer_ip}|{computer_name}|{service_name}|'
           f'p%(process)d|t%(thread)d|%(levelname)s|{extra_fmt}%(message)s')

    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    if stdout:
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    if socket:
        socketHandler = handlers.SocketHandler('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        socketHandler.setLevel(level)
        socketHandler.setFormatter(formatter)
        logger.addHandler(socketHandler)

    if save or filename:
        if filename is None:
            filename = time.strftime("%Y-%m-%d_%H.%M.%S", time.localtime()) + ".log"

        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        if rotating_time:
            # 每 1(interval) 天(when) 重写1个文件,保留7(backupCount) 个旧文件；when还可以是Y/m/H/M/S
            th = TimedRotatingFileHandler(filename, when='D', interval=1, backupCount=backupCount, encoding="UTF-8")
            th.setLevel(level)
            th.setFormatter(formatter)
            logger.addHandler(th)

        elif rotating_size:
            # 每 1024Bytes重写一个文件,保留2(backupCount) 个旧文件
            sh = RotatingFileHandler(filename, mode=mode, maxBytes=1024 * 1024, backupCount=backupCount,
                                     encoding="UTF-8")
            sh.setLevel(level)
            sh.setFormatter(formatter)
            logger.addHandler(sh)

        else:
            fh = logging.FileHandler(filename, mode=mode, encoding="UTF-8")
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

    return logger


logger = setup_logger(
    name="zyjc",
    filename=abspath("../logs/logger.log"),
    stdout=True,
    level="info",
    rotating_time=True,
    backupCount=60,
    extra_fmt="API|||"
)


def status_log(status, info_dict=None, server_type='API'):
    if info_dict is None:
        info_dict = {}
    showinfo = server_type + "|||"
    showinfo += str(status) + "|"
    for info_key, info_value in info_dict.items():
        info = str(info_key) + ":" + str(info_value) + "|"
        showinfo += info
    if "fail" in status or "error" in status:
        logger.warning(showinfo)
    elif "内部异常错误" in status:
        logger.error(showinfo)
    else:
        logger.info(showinfo)
