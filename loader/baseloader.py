# !/usr/bin/env python
# -*- coding: utf-8 -*-
# =====================================================
# @File   : baseloader.py
# @Date   : 2024/5/13 9:54
# @Author : yuzhaohao
#
# 2024/02/01 1:14   Create
# =====================================================

from abc import ABC, abstractmethod
from typing import List


class FileLoader(ABC):
    def __init__(self, file_path):
        self.file_path = file_path
        self.document_list: List = []

    @abstractmethod
    def load(self) -> List:
        ...
