# !/usr/bin/env python
# -*- coding: utf-8 -*-
# =====================================================
# @File   ：utils
# @Date   ：2024/6/27 22:32
# @Author ：leemysw

# 2024/6/27 22:32   Create
# =====================================================

import os
import yaml
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


def read_yaml(file_path):
    """
    读取并解析一个YAML文件。

    :param file_path: YAML文件的绝对路径。
    :return: 解析后的数据结构。
    """
    # # 验证文件路径参数
    # if not os.path.isabs(file_path) or '..' in file_path:
    #     # 以防止路径遍历攻击
    #     raise ValueError("文件路径不合法，禁止使用相对路径或 '..' ")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"无法找到文件: {file_path}")
    except PermissionError:
        raise PermissionError(f"没有权限读取文件: {file_path}")
    except yaml.YAMLError as e:
        # 可以进一步细化YAML错误处理
        raise ValueError(f"YAML文件格式错误: {file_path}") from e

    return data