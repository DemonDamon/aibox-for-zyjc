# !/usr/bin/env python
# -*- coding: utf-8 -*-
# =====================================================
# @File   : read_gdp.py
# @Date   : 2024/6/27 21:31
# @Author : yuzhaohao
#
# 2024/02/01 1:14   Create
# =====================================================


from loader.xlsx_loader import XlsxLoader


def read_dpg(filepath):
    loader = XlsxLoader(filepath)
    result = loader.load()
    result = ''.join(result)
    print(result)


if __name__ == '__main__':
    read_dpg(r"../tests/data/GDP.xlsx")
