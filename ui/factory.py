import os,sys
sys.stdout.reconfigure(encoding='utf-8')
# 当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上级目录
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
from ui.woker import *


class AbstractFactory:

    def create_worker(self, param):
        pass


class ConcreteFactory(AbstractFactory):

    def create_worker(self, param):
        if param == 'system':
            return Worker_system()
        elif param == 'system_capture':
            return Worker_system_capture()
        elif param == 'setting' :
            return Worker_setting()
        elif param == 'run_create_testcase' :
            return Worker_run_create_testcase()
        elif param == 'run_test' :
            return Worker_run_test()
        elif param == 'data_arrange_analysis' :
            return Worker_data_arrange_analysis()

