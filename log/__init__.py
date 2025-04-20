import os
import sys
import config
# 获取主目录路径
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(CURRENT_DIR)

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
