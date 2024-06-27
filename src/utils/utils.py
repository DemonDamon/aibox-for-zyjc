# !/usr/bin/env python
# -*- coding: utf-8 -*-
# =====================================================
# @File   ：utils
# @Date   ：2024/6/27 22:32
# @Author ：leemysw

# 2024/6/27 22:32   Create
# =====================================================

import os
import socket

ROOT_PATH = os.path.abspath(os.path.dirname(__file__)) + '/../'


def get_host_ip():
    ip = ''
    host_name = ''
    # noinspection PyBroadException
    try:
        sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sc.connect(('8.8.8.8', 80))
        ip = sc.getsockname()[0]
        host_name = socket.gethostname()
        sc.close()
    except Exception:
        pass
    return ip, host_name


def abspath(r_path):
    path = os.path.abspath(os.path.join(ROOT_PATH, r_path))
    sh_path = '/'.join(path.split('\\'))

    return sh_path
