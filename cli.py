# -*- coding: utf-8 -*-
# @时间       : 2024/8/5 14:01
# @作者       : caishilong
# @文件名      : cli.py
# @项目名      : pc-test
# @Software   : PyCharm
"""
    cli
    命令行用法
"""
import sys
from chromedriver_manager import ChromeDriverManager


if __name__ == '__main__':
    """ 
    Usage:
    python -m chromedriver_manager -h
    python -m chromedriver_manager get <version>
    """
    cdm = ChromeDriverManager()
    # -v
    if len(sys.argv) == 2 and sys.argv[1] == '-h':
        print('Usage: python -m cli.py get <version> <dir_path>')

    # get <version>
    elif len(sys.argv) == 3 and sys.argv[1] == 'get':
        version = sys.argv[2]
        cdm.match_driver(version)


