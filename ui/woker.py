import os,sys,winreg,re,psutil,time
sys.stdout.reconfigure(encoding='utf-8')
# 当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上级目录
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import  QLabel
from util.yaml_util import read_yaml
from config import *
import subprocess
from ruamel.yaml import YAML



class Worker_shell_get_scenario(QThread):
    message_done = Signal(list)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        exec = self.command['shellCommand']
        if exec == 'get_scenario':
            try:
                selected_dropdown_system_value = self.command['selected_dropdown_system_value']
                # 存储业务场景的文件路径
                pic_flow_path = f"{ROOT_DIR}/testcase/{selected_dropdown_system_value}/pic_flow.yaml"
                pic_flow_data = read_yaml(pic_flow_path)
                temp = []
                for item in pic_flow_data.keys():
                    temp.append(item)
                self.message_done.emit(['全部业务场景'] + temp)
            except Exception as e:
                self.message_done.emit([])



class Worker_get_all_system(QThread):
    finished = Signal(dict)  # 定义一个信号，用于传递读取到的数据

    def run(self):
        globalConfigPath = os.path.join(ROOT_DIR, 'config', 'globalConfig.yaml')
        # 测试用全局配置表globalConfig.yaml
        if not os.path.exists(globalConfigPath):
            # yaml表是list，这样为了防止，字段中的值和系统中特殊标记的值重复，[1]中的才是存储字段和对应值的dict
            yaml = YAML()
            with open(globalConfigPath, 'w', encoding='utf-8') as f:
                yaml.dump(init_global_config, f)
        # globalConfig.yaml 获得测试系统
        result = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
        # 将读取到的数据通过信号发送回主线程
        # self.finished.emit(['全部测试系统']+result['allTestedSystem'])
        self.finished.emit(result)




class Worker_system(QThread):
    finished = Signal(list)  # 定义一个信号，用于传递读取到的数据

    def run(self):
        # globalConfig.yaml 获得测试系统
        result = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
        # 将读取到的数据通过信号发送回主线程
        self.finished.emit(['全部测试系统']+result['allTestedSystem'])


class Worker_system_capture(QThread):
    finished = Signal(list)  # 定义一个信号，用于传递读取到的数据

    def run(self):
        # globalConfig.yaml 获得测试系统
        result = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
        # 将读取到的数据通过信号发送回主线程
        self.finished.emit(['全部测试系统']+result['allTestedSystem'])


class Worker_setting(QThread):
    finished = Signal(list)  # 定义一个信号，用于传递读取到的数据

    def run(self):
        # globalConfig.yaml 获得测试系统
        result = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
        temp = []
        # 获得所有字段值, 存入list中返回
        for item in result['allTestedSetting'].keys():
            temp.append(item)
        # 将读取到的数据通过信号发送回主线程
        self.finished.emit(['设置参数']+temp)


class Worker_run_create_testcase(QThread):
    finished = Signal(list)  # 定义一个信号，用于传递读取到的数据

    def run(self):
        # globalConfig.yaml 获得测试系统
        result = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
        temp = []
        # 获得所有字段值, 存入list中返回
        for item in result['allCreateTestcase'].keys() :
            temp.append(item)
        # 将读取到的数据通过信号发送回主线程
        self.finished.emit(['生成接口']+temp)


class Worker_run_test(QThread):
    finished = Signal(list)  # 定义一个信号，用于传递读取到的数据

    def run(self):
        # globalConfig.yaml 获得测试系统
        result = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
        temp = []
        # 获得所有字段值, 存入list中返回
        for item in result['allTest'].keys() :
            temp.append(item)
        # 将读取到的数据通过信号发送回主线程
        self.finished.emit(['自动化测试类型']+temp)


class Worker_data_arrange_analysis(QThread):
    finished = Signal(list)  # 定义一个信号，用于传递读取到的数据

    def run(self):
        # globalConfig.yaml 获得测试系统
        result = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
        temp = []
        for item in result['allArrangeAnalysis'].keys():
            temp.append(item)
        # 将读取到的数据通过信号发送回主线程
        self.finished.emit(['整理分析类型']+temp)



class Worker_shell(QThread):
    result_signal = Signal(str)  # 用于传递输出结果
    error_signal = Signal(str)  # 用于传递错误信息
    message_done = Signal(list)
    finished_signal = Signal()  # ✅ 新增信号：线程执行完毕或被关闭时触发, 暂时只有run_dynamic_many使用

    def __init__(self, command):
        super().__init__()
        self.command = command
        # 变量保存进程
        self.process = None

    def run(self):
        try:
            exec = self.command['shellCommand']
            if exec == 'ftsi' :
                system_name = self.command['system_name']
                if system_name != '' and system_name != None :
                    # 拼接新增系统shell命令
                    # execCommand = f'python {ROOT_DIR}/shellCommand.py ftsi {system_name}'
                    execCommand = f'python {ROOT_DIR}/log/autoSaveData_initialSystem_single.py {system_name}'
                    # 执行耗时的 shell 命令
                    result = subprocess.run(execCommand, shell=True, text=True, capture_output=True, encoding='utf-8')
                    if result.stdout:
                        self.result_signal.emit(result.stdout)
                        # 将读取到的数据通过信号发送回主线程
                        self.message_done.emit(['全部测试系统'] + read_yaml(ROOT_DIR + '/config/globalConfig.yaml')['allTestedSystem'])
                        # 拼接需要添加的数据库地址、过滤url中的host、数据库加载方式
                        database_name = self.command['database_name']
                        url_host = self.command['url_host']
                        loaddatabase_type = self.command['loaddatabase_type']
                        if database_name != None and database_name != '' :
                            # execCommand_insert_database_name = f'python {ROOT_DIR}/shellCommand.py sdp {system_name} {database_name}'
                            execCommand_insert_database_name = f'python {ROOT_DIR}/util/utils_appendDataConfigValue_single.py {system_name} {init_dataBasePath} {database_name}'
                            # 执行耗时的 shell 命令
                            result_insert_database_name = subprocess.run(execCommand_insert_database_name, shell=True,
                                                                         text=True, capture_output=True, encoding='utf-8')
                            if result_insert_database_name.stdout:
                                self.result_signal.emit(result_insert_database_name.stdout)
                            if result_insert_database_name.stderr :
                                self.error_signal.emit(result_insert_database_name.stderr)
                        if url_host != None and url_host != '' :
                            # execCommand_insert_url_host = f'python {ROOT_DIR}/shellCommand.py sfu {system_name} {url_host}'
                            execCommand_insert_url_host = f'python {ROOT_DIR}/util/utils_appendDataConfigValue_single.py {system_name} {init_filterUrl} {url_host}'
                            # 执行耗时的 shell 命令
                            result_insert_url_host = subprocess.run(execCommand_insert_url_host, shell=True,
                                                                         text=True, capture_output=True, encoding='utf-8')
                            if result_insert_url_host.stdout:
                                self.result_signal.emit(result_insert_url_host.stdout)
                            if result_insert_url_host.stderr :
                                self.error_signal.emit(result_insert_url_host.stderr)
                        if loaddatabase_type != None and loaddatabase_type != '' :
                            # execCommand_insert_loaddatabase_type = f'python {ROOT_DIR}/shellCommand.py ldt {system_name} {loaddatabase_type}'
                            execCommand_insert_loaddatabase_type = f'python {ROOT_DIR}/util/utils_appendDataConfigValue_single.py {system_name} {init_loadDataBaseType} {loaddatabase_type}'
                            # 执行耗时的 shell 命令
                            result_insert_loaddatabase_type = subprocess.run(execCommand_insert_loaddatabase_type, shell=True,
                                                                         text=True, capture_output=True, encoding='utf-8')
                            if result_insert_loaddatabase_type.stdout:
                                self.result_signal.emit(result_insert_loaddatabase_type.stdout)
                            if result_insert_loaddatabase_type.stderr :
                                self.error_signal.emit(result_insert_loaddatabase_type.stderr)
                    if result.stderr:
                        self.error_signal.emit(result.stderr)
            elif exec == 'setting_value' :
                selected_dropdown_system_value = self.command['selected_dropdown_system_value']
                selected_dropdown_setting_value = self.command['selected_dropdown_setting_value']
                if selected_dropdown_setting_value != '设置参数' and selected_dropdown_setting_value != '' and \
                        selected_dropdown_setting_value != None and \
                        selected_dropdown_system_value != '' and selected_dropdown_system_value != None:
                    # 获得输入框输入内容
                    setting_value = self.command['setting_value']
                    if selected_dropdown_setting_value == '数据库名' :
                        # execCommand_insert_database_name = f'python {ROOT_DIR}/shellCommand.py sdp {selected_dropdown_system_value} {setting_value}'
                        execCommand_insert_database_name = f'python {ROOT_DIR}/util/utils_appendDataConfigValue_single.py {selected_dropdown_system_value} {init_dataBasePath} {setting_value}'
                        # 执行耗时的 shell 命令
                        result_insert_database_name = subprocess.run(execCommand_insert_database_name, shell=True,
                                                                     text=True, capture_output=True, encoding='utf-8')
                        if result_insert_database_name.stdout:
                            self.result_signal.emit(result_insert_database_name.stdout)
                        if result_insert_database_name.stderr:
                            self.error_signal.emit(result_insert_database_name.stderr)
                    elif selected_dropdown_setting_value == '读取数据库过滤的Host' :
                        # execCommand_insert_url_host = f'python {ROOT_DIR}/shellCommand.py sfu {selected_dropdown_system_value} {setting_value}'
                        execCommand_insert_url_host = f'python {ROOT_DIR}/util/utils_appendDataConfigValue_single.py {selected_dropdown_system_value} {init_filterUrl} {setting_value}'
                        # 执行耗时的 shell 命令
                        result_insert_url_host = subprocess.run(execCommand_insert_url_host, shell=True,
                                                                text=True, capture_output=True, encoding='utf-8')
                        if result_insert_url_host.stdout:
                            self.result_signal.emit(result_insert_url_host.stdout)
                        if result_insert_url_host.stderr:
                            self.error_signal.emit(result_insert_url_host.stderr)
                    elif selected_dropdown_setting_value == '加载数据库方式' :
                        # execCommand_insert_loaddatabase_type = f'python {ROOT_DIR}/shellCommand.py ldt {selected_dropdown_system_value} {setting_value}'
                        execCommand_insert_loaddatabase_type = f'python {ROOT_DIR}/util/utils_appendDataConfigValue_single.py {selected_dropdown_system_value} {init_loadDataBaseType} {setting_value}'
                        # 执行耗时的 shell 命令
                        result_insert_loaddatabase_type = subprocess.run(execCommand_insert_loaddatabase_type,
                                                                         shell=True,
                                                                         text=True, capture_output=True,
                                                                         encoding='utf-8')
                        if result_insert_loaddatabase_type.stdout:
                            self.result_signal.emit(result_insert_loaddatabase_type.stdout)
                        if result_insert_loaddatabase_type.stderr:
                            self.error_signal.emit(result_insert_loaddatabase_type.stderr)
                    else:
                        # globalConfig.yaml 获得测试系统内容, 通过dict中的映射关系找到需要修改的字段
                        result_global = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
                        settingField = result_global['allTestedSetting'].get(selected_dropdown_setting_value)
                        if settingField:
                            self.result_signal.emit('获得globalConfig.yaml对应的字段值')
                        else:
                            self.error_signal.emit('读取globalConfig.yaml对应的字段值错误')
                        # 打开对应系统的dataConfig.yaml, 修改为输入框中的值
                        result_system = read_yaml(ROOT_DIR + f'/config/{selected_dropdown_system_value}dataConfig.yaml')
                        result_system[0][settingField] = setting_value
                        if result_system[0][settingField] == setting_value :
                            self.result_signal.emit('修改对应系统dataConfig.yaml对应字段值成功')
                            yaml = YAML()
                            with open(ROOT_DIR + f'/config/{selected_dropdown_system_value}dataConfig.yaml', 'w',
                                      encoding='utf-8') as f:
                                yaml.dump(result_system, f)
                            self.result_signal.emit('写入字段值到对应系统dataConfig.yaml中成功!!!')
                        else:
                            self.error_signal.emit('读取dataConfig.yaml对应的字段值错误')
            elif exec == 'query_setting_value':
                selected_dropdown_system_value = self.command['selected_dropdown_system_value']
                selected_dropdown_setting_value = self.command['selected_dropdown_setting_value']
                if selected_dropdown_setting_value != '设置参数' and selected_dropdown_setting_value != '' and \
                        selected_dropdown_setting_value != None and \
                        selected_dropdown_system_value != '' and selected_dropdown_system_value != None:
                    # globalConfig.yaml 获得测试系统
                    result_global = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
                    field_global = result_global['allTestedSetting'].get(selected_dropdown_setting_value)
                    result_system = read_yaml(ROOT_DIR + f'/config/{selected_dropdown_system_value}dataConfig.yaml')
                    value_system = result_system[0].get(field_global)
                    if value_system:
                        self.result_signal.emit(str(value_system))
                    else:
                        self.error_signal.emit(f'读取系统{selected_dropdown_system_value}中字段{selected_dropdown_setting_value}对应的值失败!!!')
            elif exec == 'create_testcase':
                yaml = YAML()
                selected_dropdown_system_value = self.command['selected_dropdown_system_value']
                selected_dropdown_run_create_testcase_value = self.command['selected_dropdown_run_create_testcase_value']
                if selected_dropdown_system_value not in ['全部测试系统', '', None] and \
                        selected_dropdown_run_create_testcase_value not in ['生成接口', '', None]:
                    # globalConfig.yaml 获得测试系统
                    globalConfig = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
                    # 将原yaml中全局测试变量值, 设置为选择系统
                    globalConfig['global_testSystem'] = selected_dropdown_system_value
                    # 生成测试类型都是中文, 将中文变成数字, 这样可以调用后边的方法
                    create_testcase_value_global = globalConfig['allCreateTestcase'].get(selected_dropdown_run_create_testcase_value)
                    # 修改好的Yaml覆盖写入到原文件
                    with open(ROOT_DIR + '/config/globalConfig.yaml', 'w', encoding='utf-8') as f:
                        yaml.dump(globalConfig, f)
                    # 业务场景选项选择的选项
                    dropdown_scenario_value = self.command['dropdown_scenario_value']
                    if dropdown_scenario_value == '全部业务场景' :
                        execCommand_create_testcase_type = f'python {ROOT_DIR}/log/autoCreate_single.py {create_testcase_value_global}'
                    else:
                        execCommand_create_testcase_type = f'python {ROOT_DIR}/log/autoCreate_single.py {create_testcase_value_global} --scenario {dropdown_scenario_value}'

                    """执行命令，并实时发送输出到信号"""
                    process = subprocess.Popen(
                        execCommand_create_testcase_type,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,encoding='utf-8'
                    )
                    # 实时读取 stdout 和 stderr
                    while True:
                        output = process.stdout.readline()
                        if output:
                            self.result_signal.emit(output.strip())  # 发送到主线程
                        elif process.poll() is not None:
                            break
                    # 捕获 stderr 错误信息
                    error_output = process.stderr.read()
                    if error_output:
                        self.error_signal.emit(error_output.strip())
            elif exec == 'run_dynamic':
                yaml = YAML()
                selected_dropdown_system_value = self.command['selected_dropdown_system_value']
                selected_dropdown_run_test_value = self.command['selected_dropdown_run_test_value']
                if selected_dropdown_system_value not in ['全部测试系统', '', None] and \
                        selected_dropdown_run_test_value not in ['自动化测试类型', '', None]:
                    # globalConfig.yaml 获得测试系统
                    globalConfig = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
                    # 将原yaml中全局测试变量值, 设置为选择系统
                    globalConfig['global_testSystem'] = selected_dropdown_system_value
                    # 生成测试类型都是中文, 将中文变成数字, 这样可以调用后边的方法
                    create_testcase_value_global = globalConfig['allTest'].get(selected_dropdown_run_test_value)
                    # 修改好的Yaml覆盖写入到原文件
                    with open(ROOT_DIR + '/config/globalConfig.yaml', 'w', encoding='utf-8') as f:
                        yaml.dump(globalConfig, f)
                    execCommand_run_test = f'python {ROOT_DIR}/log/testALlCase_single.py {create_testcase_value_global}'
                    """执行命令，并实时发送输出到信号"""
                    self.process = subprocess.Popen(
                        execCommand_run_test,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True, encoding='utf-8'
                    )
                    # 实时读取 stdout 和 stderr
                    while True:
                        output = self.process.stdout.readline()
                        if output:
                            self.result_signal.emit(output.strip())  # 发送到主线程
                        elif self.process.poll() is not None:
                            break
                    # 捕获 stderr 错误信息
                    error_output = self.process.stderr.read()
                    if error_output:
                        self.error_signal.emit(error_output.strip())
            elif exec == 'run_dynamic_many':
                try:
                    yaml = YAML()
                    selected_dropdown_system_value = self.command['selected_dropdown_system_value']
                    selected_dropdown_run_test_value = self.command['selected_dropdown_run_test_value']
                    select_case_name_value = self.command['select_case_name_value']
                    if selected_dropdown_system_value not in ['全部测试系统', '', None] and \
                            selected_dropdown_run_test_value not in ['自动化测试类型', '', None] and \
                            len(select_case_name_value) != 0:
                        # globalConfig.yaml 获得测试系统
                        globalConfig = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
                        # 将原yaml中全局测试变量值, 设置为选择系统
                        globalConfig['global_testSystem'] = selected_dropdown_system_value
                        # 生成测试类型都是中文, 将中文变成数字, 这样可以调用后边的方法
                        create_testcase_value_global = globalConfig['allTest'].get(selected_dropdown_run_test_value)
                        # 修改好的Yaml覆盖写入到原文件
                        with open(ROOT_DIR + '/config/globalConfig.yaml', 'w', encoding='utf-8') as f:
                            yaml.dump(globalConfig, f)
                        select_case_name = ' '.join(select_case_name_value)
                        execCommand_run_test = f'python {ROOT_DIR}/log/testManyCase_single.py {create_testcase_value_global} {select_case_name}'
                        # 增加判断, 因为subprocess.Popen 传递参数长度限制, 过长通过txt进行读取
                        if len(execCommand_run_test) > 6800 :
                            import pickle
                            # 将列表存储到 TXT 文件
                            with open(ROOT_DIR + '/log/temp.txt', "wb") as file:
                                pickle.dump(select_case_name_value, file)
                            execCommand_run_test = f'python {ROOT_DIR}/log/testManyCase_single.py {create_testcase_value_global} --file'
                        """执行命令，并实时发送输出到信号"""
                        self.process = subprocess.Popen(
                            execCommand_run_test,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True, encoding='utf-8',
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # ⚠ 只在 Windows 有效
                        )
                        # 实时读取 stdout 和 stderr
                        while True:
                            output = self.process.stdout.readline()
                            if output:
                                self.result_signal.emit(output.strip())  # 发送到主线程
                            elif self.process.poll() is  None:
                                break
                        # 捕获 stderr 错误信息
                        error_output = self.process.stderr.read()
                        if error_output:
                            self.error_signal.emit(error_output.strip())
                finally:
                    self.finished_signal.emit()  # ✅ 不论是否异常，退出时都发信号
            elif exec == 'run_static':
                try:
                    yaml = YAML()
                    selected_dropdown_system_value = self.command['selected_dropdown_system_value']
                    selected_dropdown_run_test_value = self.command['selected_dropdown_run_test_value']
                    if selected_dropdown_system_value not in ['全部测试系统', '', None] and \
                            selected_dropdown_run_test_value not in ['自动化测试类型', '', None]:
                        # globalConfig.yaml 获得测试系统
                        globalConfig = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
                        # 将原yaml中全局测试变量值, 设置为选择系统
                        globalConfig['global_testSystem'] = selected_dropdown_system_value
                        # 修改好的Yaml覆盖写入到原文件
                        with open(ROOT_DIR + '/config/globalConfig.yaml', 'w', encoding='utf-8') as f:
                            yaml.dump(globalConfig, f)
                        dropdown_scenario_value = self.command['dropdown_scenario_value']
                        if selected_dropdown_run_test_value == '敏感信息测试' :
                            if dropdown_scenario_value == '全部业务场景' :
                                execCommand_run_test = f'python {ROOT_DIR}/log/autoSensitive_single.py {selected_dropdown_system_value}'
                            else:
                                execCommand_run_test = f'python {ROOT_DIR}/log/autoSensitive_single.py {selected_dropdown_system_value} --scenario {dropdown_scenario_value}'
                        elif selected_dropdown_run_test_value == '敏感信息测试(过滤重复)' :
                            if dropdown_scenario_value == '全部业务场景':
                                execCommand_run_test = f'python {ROOT_DIR}/log/autoSensitive_single_whiteBlackList.py {selected_dropdown_system_value}'
                            else:
                                execCommand_run_test = f'python {ROOT_DIR}/log/autoSensitive_single_whiteBlackList.py {selected_dropdown_system_value} --scenario {dropdown_scenario_value}'
                        elif selected_dropdown_run_test_value == '敏感信息存入过滤器' :
                            execCommand_run_test = f'python {ROOT_DIR}/log/autoSensitiveData.py {selected_dropdown_system_value}'
                        """执行命令，并实时发送输出到信号"""
                        self.process = subprocess.Popen(
                            execCommand_run_test,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True, encoding='utf-8',
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # ⚠ 只在 Windows 有效
                        )
                        # 实时读取 stdout 和 stderr
                        while True:
                            output = self.process.stdout.readline()
                            if output:
                                self.result_signal.emit(output.strip())  # 发送到主线程
                            elif self.process.poll() is not None:
                                break
                        # 捕获 stderr 错误信息
                        error_output = self.process.stderr.read()
                        if error_output:
                            self.error_signal.emit(error_output.strip())
                finally:
                    self.finished_signal.emit()  # ✅ 不论是否异常，退出时都发信号
            elif exec == 'open_directory_report':
                selected_dropdown_system_value = self.command['selected_dropdown_system_value']
                if selected_dropdown_system_value != '' and selected_dropdown_system_value != None:
                    openPath = ROOT_DIR + f'/testcase/{selected_dropdown_system_value}/report'
                    try:
                        os.startfile(openPath)
                        self.result_signal.emit('打开文件夹成功')
                    except FileNotFoundError:
                        self.error_signal.emit('文件夹不存在或路径错误')
                    except PermissionError:
                        self.error_signal.emit('没有权限打开文件夹')
                    except Exception as e:
                        self.error_signal.emit(e)
            elif exec == 'set_proxy':
                # set_proxy_input_value = self.command['set_proxy_input_value']
                # 读取获得globalConfig.yaml中的存储字段, 这个字段用来存放对应功能的黑名单、白名单
                globalConfigData = read_yaml(f"{ROOT_DIR}/config/globalConfig.yaml")
                global_proxy = globalConfigData.get('global_proxy')
                global_proxy_port = globalConfigData.get('global_proxy_port')
                if global_proxy != '' and global_proxy != None and \
                        self.is_ip_port_format(f"{global_proxy}:{global_proxy_port}"):
                    setResult = self.set_proxy(f"{global_proxy}:{global_proxy_port}")
                    if '代理已设置为' in setResult :
                        self.result_signal.emit(setResult)
                    else:
                        self.error_signal.emit(setResult)
            elif exec == 'unset_proxy':
                unsetResult = self.disable_proxy()
                if '手动代理已关闭' in unsetResult:
                    self.result_signal.emit(unsetResult)
                else:
                    self.error_signal.emit(unsetResult)
            elif exec == 'capture_image_traffic':
                capture_dropdown_value = self.command['capture_dropdown_value']
                if capture_dropdown_value != '' and capture_dropdown_value != None and \
                        capture_dropdown_value != '全部测试系统':
                    execCommand_capture_image_traffic = f'python {ROOT_DIR}/mitm/trafficImage.py {capture_dropdown_value}'
                    """执行命令，并实时发送输出到信号"""
                    self.process = subprocess.Popen(
                        execCommand_capture_image_traffic,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True, encoding='utf-8'
                    )
                    # 实时读取 stdout 和 stderr
                    while True:
                        output = self.process.stdout.readline()
                        if output:
                            self.result_signal.emit(output.strip())  # 发送到主线程
                        elif self.process.poll() is not None:
                            break
                    # 捕获 stderr 错误信息
                    error_output = self.process.stderr.read()
                    if error_output:
                        self.error_signal.emit(error_output.strip())
            elif exec == 'open_directory_report_data_arrange_analysis':
                dropdown_system_data_arrange_analysis_value = self.command['selected_dropdown_system_data_arrange_analysis_value']
                dropdown_data_arrange_analysis_value = self.command['selected_dropdown_data_arrange_analysis_value']
                if dropdown_system_data_arrange_analysis_value != '全部测试系统' and \
                        dropdown_system_data_arrange_analysis_value != '' and \
                        dropdown_system_data_arrange_analysis_value != None and \
                        dropdown_data_arrange_analysis_value != '整理分析类型' and \
                        dropdown_data_arrange_analysis_value != '' and \
                        dropdown_data_arrange_analysis_value != None:
                    # originPicturePath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/数据库截图/截图/image/'
                    # originLabelPath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/数据库截图/截图/label/'
                    # originDrawPath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/数据库截图/截图/draw/'
                    if dropdown_data_arrange_analysis_value == '绘制图片(标注位置)':
                        openPath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/数据库截图/截图/draw/'
                    elif dropdown_data_arrange_analysis_value == 'excel合并url(请求地址)':
                        openPath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/testcase/report/'
                    elif dropdown_data_arrange_analysis_value == 'excel增加图片(截图中读取)':
                        openPath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/testcase/report/'
                    try:
                        os.startfile(openPath)
                        self.result_signal.emit('打开文件夹成功')
                    except FileNotFoundError:
                        self.error_signal.emit('文件夹不存在或路径错误,是不是没执行对应操作?')
                    except PermissionError:
                        self.error_signal.emit('没有权限打开文件夹')
                    except Exception as e:
                        self.error_signal.emit(e)
            elif exec == 'save_data_into_yaml':
                selected_dropdown_system_value = self.command['selected_dropdown_system_value']
                field_input_value = self.command['field_input_value']
                value_input_value = self.command['value_input_value']
                # 显示加载中, 不加不行, 直接卡掉了
                self.label = QLabel('加载中...')
                self.label.setAlignment(Qt.AlignCenter)
                self.label.show()  # 显示加载提示
                self.label.setText("加载中，请稍候...")
                self.label.setStyleSheet("color: blue; font-weight: bold;")
                result = read_yaml(ROOT_DIR + f'/config/{selected_dropdown_system_value}dataConfig.yaml')
                yaml = YAML()
                # 备份dataConfig.yaml
                with open(ROOT_DIR + f'/config/{selected_dropdown_system_value}dataConfig_editParams_backup.yaml', 'w',
                          encoding='utf-8') as f:
                    yaml.dump(result, f)
                data = {'urlHeader': {}, 'header': { field_input_value : value_input_value },
                        'urlHeaderScript': {}, 'headerScript': {}}
                result[0]['need_modifyReqHeader'] = data
                with open(ROOT_DIR + f'/config/{selected_dropdown_system_value}dataConfig.yaml', 'w',encoding='utf-8') as f:
                    yaml.dump(result, f)
                self.result_signal.emit('数据存储完成')
            elif exec == 'get_testcase_name':
                # 测试系统名
                selected_dropdown_system_value = self.command['selected_dropdown_system_value']
                # 测试类型名
                dropdown_run_test_value = self.command['dropdown_run_test_value']
                # 业务场景下拉框值
                dropdown_scenario_value = self.command['dropdown_scenario_value']
                """加载文件夹下所有 .py 文件名"""
                folder_path = ROOT_DIR + '/testcase/' + selected_dropdown_system_value + '/' + dropdown_run_test_value  # 替换为目标文件夹路径
                # 判断地址是否存在
                if os.path.exists(folder_path) :
                    py_files = [f for f in os.listdir(folder_path) if f.endswith(".py")]
                    if dropdown_scenario_value == '全部业务场景' :
                        self.message_done.emit(py_files)
                    else:
                        # globalConfig.yaml 获得测试系统
                        globalConfig = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
                        # 生成测试类型都是中文, 将中文变成数字, 这样可以调用后边的方法
                        create_testcase_value_global = globalConfig['allTest'].get(dropdown_run_test_value)
                        # 读取存储在scenario_testcase.yaml中, 对应业务场景下的对应测试类型下的测试用例
                        scenario_testcase_data = read_yaml(f"{ROOT_DIR}/testcase/{selected_dropdown_system_value}/scenario_testcase.yaml")
                        # 查询是否有当前场景, 得到测试类型和测试用例的数据
                        testType_testcase = scenario_testcase_data.get(dropdown_scenario_value)
                        if testType_testcase == None : # 为None就是没有, 返回所有用例, 返回提示信息
                            self.result_signal.emit('当前业务场景无对应测试用例, ！！！')
                        else:
                            testcase_name = testType_testcase.get(str(create_testcase_value_global)) # 获得当前类型下存储的测试用例
                            if testcase_name == None :
                                self.result_signal.emit('当前业务场景无对应测试用例, ！！！')
                            else:
                                # 判断下记录的用例名, 是否包含在所在文件夹下
                                temp = []
                                for item in testcase_name :
                                    if item in py_files :
                                        temp.append(item)
                                self.message_done.emit(temp)
                else:
                    self.result_signal.emit('当前业务场景无对应测试用例, ！！！')
        except Exception as e:
            self.error_signal.emit(f"运行命令时出错: {str(e)}")


    @staticmethod
    def set_proxy(proxy_address):
        try:
            # proxy_address = f"{proxy_ip}:{proxy_port}"

            # 打开注册表路径
            reg_key = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key, 0, winreg.KEY_SET_VALUE) as key:
                # 启用代理
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                # 设置代理地址
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_address)
                return f"代理已设置为 {proxy_address}"
        except Exception as e:
            return f"设置代理失败: {e}"


    def disable_proxy(self):
        try:
            # 注册表路径
            reg_key = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"

            # 打开注册表键
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key, 0, winreg.KEY_SET_VALUE) as key:
                # 设置 ProxyEnable 为 0（关闭代理）
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
                return "手动代理已关闭"
        except Exception as e:
            return f"关闭手动代理失败: {e}"

    @staticmethod
    def is_ip_port_format(s):
        # 正则表达式匹配 IPv4 地址和端口号
        pattern = r"^((25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.){3}" \
                  r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?):" \
                  r"([1-9][0-9]{0,4})$"

        # 判断是否匹配
        if re.match(pattern, s):
            # 提取端口号并验证范围（1-65535）
            ip, port = s.split(":")
            if 1 <= int(port) <= 65535:
                return True
        return False

    # 关闭进程
    def stop(self):
        # """终止子进程"""
        # if self.process and self.process.poll() is None:
        #     self.process.terminate()  # 终止进程
        #     self.process.wait()  # 等待进程退出
        print('进入stop方法')
        # import signal
        # if self.process and self.process.poll() is None:
        #     os.kill(self.process.pid, signal.CTRL_BREAK_EVENT)
        #     self.process.wait(timeout=5)
        # else:
        #     self.finished_signal.emit()  # ✅ 不论是否异常，退出时都发信号
        # self.process = None
        try:
            if self.process and self.process.poll() is None:
                print('进入进程判断  stop方法')
                try:
                    # 强制杀掉整个进程组，/T 表示杀掉子进程，/F 表示强制
                    subprocess.call(f"taskkill /PID {self.process.pid} /T /F", shell=True)
                except Exception as e:
                    print("taskkill failed:", e)
            else:
                self.finished_signal.emit()  # ✅ 不论是否异常，退出时都发信号
            self.process = None
        except Exception as e :
            self.error_signal.emit(f'关闭异常 : {e}')


class Worker_shell_capture(QThread):
    result_signal_capture = Signal(str)  # 用于传递输出结果
    error_signal_capture = Signal(str)  # 用于传递错误信息
    message_done_capture = Signal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command
        # 变量保存进程
        self.process = None

    def run(self):
        try:
            exec = self.command['shellCommand']
            if exec == 'capture_image_traffic':
                capture_dropdown_value = self.command['capture_dropdown_value']
                if capture_dropdown_value != '' and capture_dropdown_value != None and \
                        capture_dropdown_value != '全部测试系统':
                    execCommand_capture_image_traffic = f'python {ROOT_DIR}/mitm/trafficImage.py {capture_dropdown_value}'
                    """执行命令，并实时发送输出到信号"""
                    self.process = subprocess.Popen(
                        execCommand_capture_image_traffic,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True, encoding='utf-8'
                    )
                    # 实时读取 stdout 和 stderr
                    while self.process:
                        output = self.process.stdout.readline()
                        if output:
                            self.result_signal_capture.emit(output.strip())  # 发送到主线程
                        elif self.process.poll() is not None:
                            break
                    if self.process:
                        # 捕获 stderr 错误信息
                        error_output = self.process.stderr.read()
                        if error_output:
                            self.error_signal_capture.emit(error_output.strip())
            if exec == 'capture_image':
                capture_dropdown_value = self.command['capture_dropdown_value']
                if capture_dropdown_value != '' and capture_dropdown_value != None and \
                        capture_dropdown_value != '全部测试系统':
                    execCommand_capture_image_traffic = f'python {ROOT_DIR}/mitm/image.py {capture_dropdown_value}'
                    """执行命令，并实时发送输出到信号"""
                    self.process = subprocess.Popen(
                        execCommand_capture_image_traffic,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True, encoding='utf-8'
                    )
                    # 实时读取 stdout 和 stderr
                    while self.process:
                        output = self.process.stdout.readline()
                        if output:
                            self.result_signal_capture.emit(output.strip())  # 发送到主线程
                        elif self.process.poll() is not None:
                            break
                    if self.process:
                        # 捕获 stderr 错误信息
                        error_output = self.process.stderr.read()
                        if error_output:
                            self.error_signal_capture.emit(error_output.strip())
            if exec == 'capture_traffic':
                capture_dropdown_value = self.command['capture_dropdown_value']
                if capture_dropdown_value != '' and capture_dropdown_value != None and \
                        capture_dropdown_value != '全部测试系统':
                    execCommand_capture_image_traffic = f'python {ROOT_DIR}/mitm/traffic.py {capture_dropdown_value}'
                    """执行命令，并实时发送输出到信号"""
                    self.process = subprocess.Popen(
                        execCommand_capture_image_traffic,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True, encoding='utf-8'
                    )
                    # 实时读取 stdout 和 stderr
                    while self.process:
                        output = self.process.stdout.readline()
                        if output:
                            self.result_signal_capture.emit(output.strip())  # 发送到主线程
                        elif self.process.poll() is not None:
                            break
                    if self.process:
                        # 捕获 stderr 错误信息
                        error_output = self.process.stderr.read()
                        if error_output:
                            self.error_signal_capture.emit(error_output.strip())
        except Exception as e:
            self.error_signal_capture.emit(f"运行命令时出错: {str(e)}")


    def stop(self):
        if self.process:
            try:
                # 获取子进程的 PID
                parent_pid = self.process.pid
                # 使用 psutil 查找子进程树
                parent_process = psutil.Process(parent_pid)
                for child_process in parent_process.children(recursive=True):
                    child_process.terminate()
                parent_process.terminate()
                self.process.wait()  # 确保主进程退出
            except psutil.NoSuchProcess:
                pass
            finally:
                self.process = None


class Worker_shell_data_arrange_analysis(QThread):
    result_signal_data_arrange_analysis = Signal(str)  # 用于传递输出结果
    error_signal_data_arrange_analysis = Signal(str)  # 用于传递错误信息
    message_done_data_arrange_analysis = Signal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command
        # 变量保存进程
        self.process = None

    def run(self):
        try:
            exec = self.command['shellCommand']
            if exec == 'run_data_arrange_analysis':
                dropdown_system_data_arrange_analysis_value = self.command[
                    'selected_dropdown_system_data_arrange_analysis_value']
                dropdown_data_arrange_analysis_value = self.command['selected_dropdown_data_arrange_analysis_value']
                if dropdown_system_data_arrange_analysis_value != '全部测试系统' and \
                        dropdown_system_data_arrange_analysis_value != '' and \
                        dropdown_system_data_arrange_analysis_value != None and \
                        dropdown_data_arrange_analysis_value != '整理分析类型' and \
                        dropdown_data_arrange_analysis_value != '' and \
                        dropdown_data_arrange_analysis_value != None:
                    input_data_arrange_analysis_value = self.command['input_data_arrange_analysis_value']
                    if dropdown_data_arrange_analysis_value == '绘制图片(标注位置)':
                        scriptPath = f'{ROOT_DIR}/analysis/drawPicture.py'
                        # originPicturePath: 原始图片据对路径   originLabelPath: 原图片标签路径    originDrawPath: 绘制图片生成路径
                        originPicturePath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/数据库截图/截图/image/'
                        originLabelPath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/数据库截图/截图/label/'
                        originDrawPath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/数据库截图/截图/draw/'
                        execCommand_shell = f'python {scriptPath} {originPicturePath} {originLabelPath} {originDrawPath}'
                    elif dropdown_data_arrange_analysis_value == 'excel合并url(请求地址)':
                        scriptPath = f'{ROOT_DIR}/analysis/mergeAll.py'
                        now = time.localtime(time.time())
                        nowNum = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_' + str(
                            now.tm_hour) + '_' + str(
                            now.tm_min) + '_' + str(now.tm_sec)
                        newMergeFilePath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/report/整理后_自动化测试结果统计_{nowNum}.xlsx'
                        execCommand_shell = f'python {scriptPath} {input_data_arrange_analysis_value} {newMergeFilePath}'
                    elif dropdown_data_arrange_analysis_value == 'excel增加图片(截图中读取)':
                        scriptPath = f'{ROOT_DIR}/analysis/addImage.py'
                        now = time.localtime(time.time())
                        nowNum = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_' + str(
                            now.tm_hour) + '_' + str(
                            now.tm_min) + '_' + str(now.tm_sec)
                        parentPath = os.path.dirname(input_data_arrange_analysis_value)
                        addImageFilePath = f'{parentPath}/excel添加图片_{nowNum}.xlsx'
                        dataBasePath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/数据库截图/数据库'
                        drawPicturePath = f'{ROOT_DIR}/testcase/{dropdown_system_data_arrange_analysis_value}/数据库截图/截图/draw'
                        execCommand_shell = f'python {scriptPath} {input_data_arrange_analysis_value} {dataBasePath} {drawPicturePath} {addImageFilePath}'
                    """执行命令，并实时发送输出到信号"""
                    self.process = subprocess.Popen(
                        execCommand_shell,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True, encoding='utf-8', errors="ignore"
                    )
                    # 实时读取 stdout 和 stderr
                    while True:
                        output = self.process.stdout.readline()
                        if output:
                            self.result_signal_data_arrange_analysis.emit(output.strip())  # 发送到主线程
                        elif self.process.poll() is not None:
                            break
                    # 捕获 stderr 错误信息
                    error_output = self.process.stderr.read()
                    if error_output:
                        self.error_signal_data_arrange_analysis.emit(error_output.strip())
            if exec == 'capture_traffic':
                pass
        except Exception as e:
            self.error_signal_data_arrange_analysis.emit(f"运行命令时出错: {str(e)}")



    def stop(self):
        if self.process:
            try:
                # 获取子进程的 PID
                parent_pid = self.process.pid
                # 使用 psutil 查找子进程树
                parent_process = psutil.Process(parent_pid)
                for child_process in parent_process.children(recursive=True):
                    child_process.terminate()
                parent_process.terminate()
                self.process.wait()  # 确保主进程退出
            except psutil.NoSuchProcess:
                pass
            finally:
                self.process = None



