# !/usr/bin/env python
# -*- coding: utf-8 -*-
# =====================================================
# @File   : xlsx_loader.py.py
# @Date   : 2024/3/20 14:13
# @Author : yuzhaohao
#
# 2024/02/01 1:14   Create
# =====================================================

import openpyxl
import json

from .baseloader import FileLoader


# from apps.common.model import Document


class XlsxLoader(FileLoader):
    def __init__(self, filepath):
        super().__init__(filepath)
        self.content = ''

    def load_and_split(self, filepath=None):
        result_to_return = []

        if filepath is None:
            filepath = self.file_path
        wb = openpyxl.load_workbook(
            filename=filepath,
            read_only=True
        )
        sheet_names = wb.get_sheet_names()
        for sheet_name in sheet_names:
            sheet = wb[sheet_name]
            for row in sheet.values:
                str_row = ''
                for cell in row:
                    str_row += str(cell) + " "  # 每行的每格内容空格隔开
                str_row += '\n'  # 一行结束之后换行
                self.document_list.append(str_row)
        # json格式返回
        # row_content = []
        # row_heading_content = []
        # sheet_content = []
        # for sheet_name in sheet_names:
        #     sheet = wb[sheet_name]
        #     for i, row in enumerate(sheet.values):
        #         if i == 0:
        #             for cell in row:
        #                 row_heading_content.append(cell)
        #         else:
        #             for k, cell in enumerate(row):
        #                 row_content.append({row_heading_content[k]: cell})
        #     sheet_content.append(row_content)
        #     row_content = []
        #     self.document_list.append(
        #         Document(
        #             page_content=json.dumps(sheet_content, ensure_ascii=False),
        #             metadata={}
        #         )
        #     )
        #     sheet_content = []
        return self.document_list

    def load(self):
        return self.load_and_split()
