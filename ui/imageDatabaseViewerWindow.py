import os,platform,win32api,sys,traceback
# 当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上级目录
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
import sqlite3, math, json
from ruamel.yaml import YAML
import glob
# from datetime import datetime
from PySide6 import QtCore
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QWidget, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog,
    QSpinBox, QDateTimeEdit, QHeaderView, QSplitter, QSizePolicy, QScrollArea, QCheckBox,
    QTreeWidget, QTreeWidgetItem, QDialog, QMessageBox, QMenu, QFormLayout, QTextEdit
)
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QDateTime, QPoint
from config import *
from ui.woker import *

def global_exception_handler(exctype, value, tb):
    # 打印异常类型和信息
    print(f"捕获异常: {exctype.__name__}")
    print(f"捕获异常信息: {value}")

    # 提取并打印异常发生的具体行号和代码内容
    tb_details = traceback.extract_tb(tb)
    for tb_item in tb_details:
        filename = tb_item.filename
        lineno = tb_item.lineno
        funcname = tb_item.name
        code_line = tb_item.line
        print(f"异常发生于文件: {filename}, 行号: {lineno}, 函数: {funcname}")
        print(f"代码内容: {code_line}")

    # 打印完整的堆栈信息
    print("完整堆栈信息:")
    traceback.print_tb(tb)



# 处理table中选择cell, 鼠标右键, 处理点击选项
class dataLoaderThread(QThread):
    result_toast = Signal(list)  # 定义一个信号，用于传递toast数据, 元素0是提示信息, 元素1是持续时间

    # self.db_system: 数据库搜索选择系统   self.db_name: 选择的数据库  row: 点击cell的行 col: 点击cell的列
    # save_txt_path: 保存文件的地址  execType, self.db_system_name, self.db_name, key, alias
    def __init__(self, execType, params) :
        super().__init__()
        self.execType = execType  # 执行哪个方法
        self.save_type = params[0] # 保存方式
        self.cell_field_selected_keys = params[1] # 勾选字段、数据库ID、点击的cell所处数据库字段位置
        self.db_system_name = params[2]   # 使用到的数据库系统名
        self.db_name = params[3]          # 查询使用到的数据库名


    def run(self):
        if self.execType == 'save_blackList' :
            # 读取获得globalConfig.yaml中的存储字段, 这个字段用来存放对应功能的黑名单、白名单
            save_field = read_yaml(f"{ROOT_DIR}/config/globalConfig.yaml").get('allTestedSetting')[self.save_type]
            # 如果点击的选项包含'字段'
            if 'URL字段' in self.save_type :
                # 读取globalConfig.yaml中的值, 用来找到黑名单中的字段
                allSystemYamlData = read_yaml(f"{ROOT_DIR}/config/{self.db_system_name}dataConfig.yaml")
                databasePath = f"{ROOT_DIR}/testcase/{self.db_system_name}/数据库截图/数据库/{self.db_name}"
                url = self.loadDataBase_Many(databasePath, self.cell_field_selected_keys[0][1])[0][2]
                from urllib import parse
                params = parse.urlparse(url)
                # 剔除? , 只保留原始请求地址
                new_url = params.scheme + '://' + params.netloc + params.path
                # 临时存一下需要存入到黑名单中的字段
                temp_all_field = []
                # 通过字段获得dataConfig.yaml中对应的名单值, 是一个list
                save_field_value = allSystemYamlData[0].get(save_field)
                # 这个url是否存在于名单中, 默认为true, 也就是不存在
                noHaveUrlField = True
                # 将需要存储到名单中的字段, 放入到变量temp_all_field中, 用来来进行校验, 是否存储到Yaml中
                for item in self.cell_field_selected_keys:
                    temp_all_field.append(item[0])
                for inside_item in save_field_value:
                    # 遍历字段对应的值, 中的每个原始, 判断是否是dict, inside_item可能是一个dict或者str
                    if isinstance(inside_item, dict):
                        # 如果当前元素是dict, 当前字段是否包含在dict中
                        inside_item_value = inside_item.get(new_url)
                        if inside_item_value:
                            # 有这个url的字段
                            noHaveUrlField = False
                            for item in self.cell_field_selected_keys:
                                # 当前字段是否在list中
                                if item[0] not in inside_item_value:
                                    inside_item_value.append(item[0])
                    # 如果dict中有这个url，也就是字段, 不需要再循环了, 直接退出
                    if noHaveUrlField == False:
                        break
                # 名单中没有dict中包含 newUrl字段
                if noHaveUrlField :
                    temp = {}
                    temp[new_url] = temp_all_field
                    save_field_value.append(temp)
                # 新数据写入dataConfig.yaml中
                yaml = YAML()
                with open(f"{ROOT_DIR}/config/{self.db_system_name}dataConfig.yaml", 'w', encoding="utf-8") as f:
                    yaml.dump(allSystemYamlData, f)
                # 存入到yaml中, 我需要再校验, 读取这个文件
                save_field_value_new = read_yaml(f"{ROOT_DIR}/config/{self.db_system_name}dataConfig.yaml")[0].get(save_field)
                # 是否写入到yaml中, 默认为False, 也就是没有写入到yaml中
                haveWrite = False
                # 存储在yaml中save_field_value_new,是一个list
                for item in save_field_value_new :
                    # 存储的可能是str, 也可能是dict, 当前存储是URL字段类型, 也就是 { "URL": ["字段1", "字段2"]}
                    if isinstance(item, dict) :
                        # 获得url对应的list
                        item_value = item.get(new_url)
                        if item_value :
                            # 循环所有元素, 比较是否包含在item_value中, 如果有一个不存在写入yaml失败
                            for ii in temp_all_field :
                                if ii not in item_value :
                                    print('写入yaml数据失败!!!')
                                    break
                            # 如果经过循环, temp_all_field中每个元素, 都存在于在对应的yaml中url对应的[]中
                            if not haveWrite :
                                haveWrite = True
                    if haveWrite :
                        break
                if haveWrite :
                    self.result_toast.emit(['写入数据成功!!!', 2000])
                else:
                    self.result_toast.emit(['写入数据失败!!!', 2000])
            elif 'URL' in self.save_type :
                # 读取globalConfig.yaml中的值, 用来找到黑名单中的字段
                allSystemYamlData = read_yaml(f"{ROOT_DIR}/config/{self.db_system_name}dataConfig.yaml")
                databasePath = f"{ROOT_DIR}/testcase/{self.db_system_name}/数据库截图/数据库/{self.db_name}"
                try:
                    url = self.loadDataBase_Many(databasePath, self.cell_field_selected_keys[0][1])[0][2]
                except Exception as e :
                    self.result_toast.emit(['存储失败, 请任意勾选字段,勾选字段不会存储,只存URL!!!', 5000])
                from urllib import parse
                params = parse.urlparse(url)
                # 剔除? , 只保留原始请求地址
                new_url = params.scheme + '://' + params.netloc + params.path
                # 通过字段获得dataConfig.yaml中对应的名单值, 是一个list
                save_field_value = allSystemYamlData[0].get(save_field)
                # 判断url是否在名单中
                if new_url not in save_field_value :
                    save_field_value.append(new_url)
                # 新数据写入dataConfig.yaml中
                yaml = YAML()
                with open(f"{ROOT_DIR}/config/{self.db_system_name}dataConfig.yaml", 'w', encoding="utf-8") as f:
                    yaml.dump(allSystemYamlData, f)
                # 存入到yaml中, 我需要再校验, 读取这个文件
                allSystemYamlData_new = read_yaml(f"{ROOT_DIR}/config/{self.db_system_name}dataConfig.yaml")
                # 通过字段获得dataConfig.yaml中对应的名单值, 是一个list
                save_field_value_new = allSystemYamlData_new[0].get(save_field)
                # 读取写入好的dataConfig.yaml,
                if new_url in save_field_value_new :
                    self.result_toast.emit(['写入数据成功!!!', 2000])
                else:
                    self.result_toast.emit(['写入数据失败!!!', 2000])
            elif '字段' in self.save_type:
                # 读取globalConfig.yaml中的值, 用来找到黑名单中的字段
                allSystemYamlData = read_yaml(f"{ROOT_DIR}/config/{self.db_system_name}dataConfig.yaml")
                # 临时存一下需要存入到黑名单中的字段
                temp_all_field = []
                # 通过字段获得dataConfig.yaml中对应的名单值, 是一个list
                save_field_value = allSystemYamlData[0].get(save_field)
                # 遍历元素, 将第一个元素也就是字段, 写入到temp_all_field用于判断是否存储成功
                # item[0] 如果没有在原值中, 添加进list即可
                for item in self.cell_field_selected_keys:
                    temp_all_field.append(item[0])
                    if item[0] not in save_field_value :
                        save_field_value.append(item[0])
                # 覆盖写入原来yaml文件中
                yaml = YAML()
                with open(f"{ROOT_DIR}/config/{self.db_system_name}dataConfig.yaml", 'w', encoding="utf-8") as f:
                    yaml.dump(allSystemYamlData, f)
                # 读取写入的文件, 获得新文件中存储名单中的字段, 所对应的值, 使用temp_all_field存储的值, 也就是字段, 逐个匹配是否
                # 包含在其中
                allSystemYamlData_new = read_yaml(f"{ROOT_DIR}/config/{self.db_system_name}dataConfig.yaml")
                save_field_value_new = allSystemYamlData_new[0].get(save_field)
                haveWrite = True
                for item in temp_all_field :
                    if item not in save_field_value_new :
                        print('写入yaml数据失败!!!')
                        haveWrite = False
                        self.result_toast.emit(['失败,字段未全部写入数据!!!', 2000])
                        break
                if haveWrite :
                    self.result_toast.emit(['写入数据成功!!!', 2000])


    def loadDataBase_Many(self, dataBasePath, num):
        splitName = os.path.splitext(dataBasePath)
        splitName_len = len(splitName) - 1
        if splitName[splitName_len] == '.db':
            # 读取sqlite数据
            db = sqlite3.connect(dataBasePath)
            # db.text_factory = lambda  x: str(x,'gbk','ignore')
            db.text_factory = str
            # 创建游标curson来执行execute SQL语句
            cursor = db.cursor()
            if num != '':
                sql_search = 'select * from activity where id={}'.format(num)
            # 查询表明  SEND_DATETIME
            cursor.execute(sql_search)
            data = cursor.fetchall()
            cursor.close()
            db.close()
            return data



# 处理table中选择cell, 鼠标右键, 处理点击选项
class writeReadDataLoaderThread(QThread):
    result_toast = Signal(list)  # 定义一个信号，用于传递toast数据, 元素0是提示信息, 元素1是持续时间

    # self.db_system: 数据库搜索选择系统   self.db_name: 选择的数据库  row: 点击cell的行 col: 点击cell的列
    # save_txt_path: 保存文件的地址  execType, self.db_system_name, self.db_name, key, alias
    def __init__(self, execType, db_system, db_name, key, alias) :
        super().__init__()
        self.execType = execType  # 执行哪个方法
        self.db_system_combo = db_system  # 数据库搜索选择系统
        self.db_name = db_name  # 选择的数据库
        self.key = key  # 点击展示数据库表的信息
        self.alias = alias  # 点击cell的信息


    def run(self):
        if self.execType == 'save_alias' :
            aliases_path = f"{ROOT_DIR}/testcase/{self.db_system_combo}/aliases.yaml"
            if os.path.exists(aliases_path):
                aliasesAll = read_yaml(aliases_path)
                aliasesAll[self.key] = self.alias
                yaml = YAML()
                with open(aliases_path, 'w', encoding="utf-8") as f:
                    yaml.dump(aliasesAll, f)
                self.result_toast.emit(['别名存储成功!!!', 1000])
            else:
                temp = {self.key: self.alias}
                yaml = YAML()
                with open(aliases_path, 'w', encoding="utf-8") as f:
                    yaml.dump(temp, f)
                # print(f"保存别名: {key} -> {alias}")
                self.result_toast.emit(['别名存储成功!!!', 1000])



# 处理table中选择cell, 鼠标右键, 处理点击选项
class rightMouseMenuLoaderThread(QThread):
    result_toast = Signal(list)  # 定义一个信号，用于传递toast数据, 元素0是提示信息, 元素1是持续时间

    # self.db_system_combo: 数据库搜索选择系统   self.db_name: 选择的数据库  row: 点击cell的行 col: 点击cell的列
    # save_txt_path: 保存文件的地址
    def __init__(self, db_system_combo, db_name, table, pos, save_txt_path) :
        super().__init__()
        self.db_system_combo = db_system_combo  # 数据库搜索选择系统
        self.db_name = db_name  # 选择的数据库
        self.table = table  # 点击展示数据库表的信息
        self.pos = pos  # 点击cell的信息
        self.save_txt_path = save_txt_path  # 保存文件的地址


    def run(self):
        # 获得展示数据库table中的cell, 获得点击具体位置
        index = self.table.indexAt(self.pos)
        row, col = index.row(), index.column()
        # 第一列是勾选框, 不要下载
        if col == 0 :
            self.result_toast.emit(['当前值为空,无法下载！！！', 1000])
        else:
            data_id = self.table.item(row, 1).text()  # 获得数据库中ID, 方便提供下载, 因为数据库值太大, 只展示10000个字符
            # 通过行列数字, 查询对应的字段
            data_position_field = {1: 'ID', 2: 'LOCAL_SOURCE_IP', 3: 'TARGET_URL', 4: 'HTTP_METHOD', 5: 'BURP_TOOL',
                                   6: 'REQ_HEADERS', 7: 'REQ_BODY', 8: 'RES_HEADERS', 9: 'RES_BODY', 10: 'WORK_NUM',
                                   11: 'SAME_DIRECTORY', 12: 'ENCRYPT_DECRYPT_KEY', 13: 'SEND_DATETIME'}
            import datetime
            # 将文本写入文件
            current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            result = self.query_field_by_id(f'{ROOT_DIR}/testcase/{self.db_system_combo}/数据库截图/数据库/{self.db_name}',
                                            int(data_id),
                                            data_position_field.get(int(col)),
                                            f'{self.save_txt_path}/{current_time}_data.txt')
            self.result_toast.emit([result, 1000])



    def query_field_by_id(self, db_path, record_id, field_name, output_file):
        """
        根据 ID 查询 SQLite 数据库中指定字段的值，并将结果写入 txt 文件。

        :param db_path: 数据库文件路径
        :param record_id: 需要查询的 ID
        :param field_name: 需要查询的字段
        :param output_file: 结果存入的 txt 文件路径
        """
        # 允许查询的字段（除了 ID）
        valid_fields = [
            'LOCAL_SOURCE_IP', 'TARGET_URL', 'HTTP_METHOD', 'BURP_TOOL', 'REQ_HEADERS',
            'REQ_BODY', 'RES_HEADERS', 'RES_BODY', 'WORK_NUM', 'SAME_DIRECTORY',
            'ENCRYPT_DECRYPT_KEY', 'SEND_DATETIME'
        ]

        if field_name not in valid_fields:
            # raise ValueError(f"字段 {field_name} 不在允许的查询范围内！")
            return '当前字段不在允许的查询范围内！'
        try:
            # 连接 SQLite 数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 构造 SQL 语句
            sql = f"SELECT {field_name} FROM ACTIVITY WHERE ID = ?"
            cursor.execute(sql, (record_id,))
            result = cursor.fetchone()

            if result:
                data = str(result[0])  # 取出查询结果
                # 将结果写入 txt 文件
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(data)
                return "查询结果已写入文件!!!"
            else:
                return "未找到对应值,无法写入文件!!!"

        except sqlite3.Error as e:
            return f"数据库错误: {e}"
        finally:
            cursor.close()
            conn.close()



class CustomDialog(QDialog):
    def __init__(self, parent=None, title="提示信息", message="请确定操作"):
        super().__init__(parent)

        # 设置对话框
        self.setWindowTitle(title)
        self.setGeometry(150, 150, 100, 100)

        # 添加按钮
        self.add_button = QPushButton("原接口追加", self)
        self.overwrite_button = QPushButton("新增覆盖接口", self)
        self.cancel_button = QPushButton("取消", self)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.add_button)
        layout.addWidget(self.overwrite_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        # 连接按钮信号
        self.add_button.clicked.connect(self.on_add)
        self.overwrite_button.clicked.connect(self.on_overwrite)
        self.cancel_button.clicked.connect(self.on_cancel)

        # 初始化选择结果
        self.selected_action = None

    def on_add(self):
        self.selected_action = "add"
        self.accept()  # 关闭对话框并返回 QDialog.Accepted

    def on_overwrite(self):
        self.selected_action = "overwrite"
        self.accept()  # 关闭对话框并返回 QDialog.Accepted

    def on_cancel(self):
        self.selected_action = "cancel"
        self.reject()  # 关闭对话框并返回 QDialog.Rejected

    def get_selected_action(self):
        # 返回用户选择的操作
        return self.selected_action



class searchSceneLoaderThread(QThread):
    result_toast = Signal(list)  # 定义一个信号，用于传递toast数据, 元素0是提示信息, 元素1是持续时间
    result_image = Signal(list)  # 定义一个信号，用于传递图片地址数据, 每个元素都是图片绝对路径
    result_db = Signal(list)  # 定义一个信号，用于传递查询出的数据库数据
    result_len = Signal(int)  # 定义一个信号，用于传递查询出的数据库数据


    def __init__(self, systemName, type_combo, scene_combo_row1, db_system_combo, db_file_combo) :
        super().__init__()
        self.systemName_image = systemName # 图片搜索选择系统
        self.type_combo_image = type_combo # 图片搜索选择图片类型
        self.scene_combo_row1 = scene_combo_row1  # 查询业务关联使用的下拉框
        self.db_system_combo = db_system_combo  # 数据库搜索选择系统
        self.db_file_combo = db_file_combo  # 数据库搜索选择数据库


    def run(self):
        # 获得图片查询选择的系统
        system_combo = self.systemName_image.currentText()
        # 获得选择的图片类型
        image_type_combo = self.type_combo_image.currentText()
        # 查询业务关联使用的下拉框
        scene_combo_row1 = self.scene_combo_row1.currentText()
        # 获得数据库查询选择系统
        db_system_combo = self.db_system_combo.currentText()
        # 获得数据库查询选择数据库名
        db_file_combo = self.db_file_combo.currentText()
        if system_combo == '全部测试系统' :
            # 将读取到的数据通过信号发送回主线程
            self.result_toast.emit(['选择图片查询系统!!!', 7000])
        elif image_type_combo == '全部图片类型' :
            # 将读取到的数据通过信号发送回主线程
            self.result_toast.emit(['选择图片查询类型!!!', 3000])
        elif scene_combo_row1 == '全部业务类型'  :
            # 将读取到的数据通过信号发送回主线程
            self.result_toast.emit(['选择展示关联图片接口业务类型！！！', 3000])
        elif db_system_combo == '全部测试系统'   :
            # 将读取到的数据通过信号发送回主线程
            self.result_toast.emit(['选择数据库查询系统！！！', 3000])
        else:
            # 获得存储yaml内容
            data = read_yaml(f"{ROOT_DIR}/testcase/{system_combo}/pic_flow.yaml")
            print(data)
            # 通过下拉框中的选项获得内容
            scene_option = data.get(scene_combo_row1)
            if data.get(scene_combo_row1):
                # 图片文件夹路径
                picDir = read_yaml(f"{ROOT_DIR}/config/globalConfig.yaml").get('allImageType')[image_type_combo]
                temp_image = []
                temp_db_id = []
                for item in scene_option.keys():
                    temp_image.append(f"{ROOT_DIR}/testcase/{system_combo}/数据库截图/截图/{picDir}/{item}")
                    if temp_db_id == [] :
                        # 获得存储的接口, 是一个list
                        temp_db_id = scene_option.get(item)
                    else:
                        temp_db_id = temp_db_id + scene_option.get(item)
                if len(temp_image) == 0 :
                    # 将读取到的数据通过信号发送回主线程
                    self.result_toast.emit(['图片不存在请确定配置或者存储数据损坏！！！', 3000])
                self.result_image.emit(temp_image)
                # 生成sql语句 db_file_combo
                search_sql_params = self.generate_sql_query_safe(temp_db_id)
                # 拼接数据库地址
                db_path = f"{ROOT_DIR}/testcase/{system_combo}/数据库截图/数据库/{db_file_combo}"
                # 使用sql语句查询数据库
                db_data = self.loadDataBase_ids(db_path, search_sql_params[0], search_sql_params[1])
                if len(db_data) == 0 :
                    # 将读取到的数据通过信号发送回主线程
                    self.result_toast.emit(['接口数据不存在或者存储文件数据损坏！！！', 3000])
                self.result_db.emit(db_data)
                self.result_len.emit(len(db_data))


    def generate_sql_query_safe(self, id_list):
        # 计算包含数据库ID的list
        idDate_len = len(id_list)
        # 不为0, 表示有数据
        if idDate_len != 0 :
            placeholders = ", ".join(["?"] * idDate_len )  # 生成 (?, ?, ?, ?)
            sql = f"SELECT * FROM ACTIVITY WHERE ID IN ({placeholders})"
            return sql, id_list  # 返回 SQL 和参数列表
        else:
            return None


    def loadDataBase_ids(self, dataBasePath, sql_search, params):
        splitName = os.path.splitext(dataBasePath)
        splitName_len = len(splitName) - 1
        if splitName[splitName_len] == '.db':
            # 读取sqlite数据
            db = sqlite3.connect(dataBasePath)
            # db.text_factory = lambda  x: str(x,'gbk','ignore')
            db.text_factory = str
            # 创建游标curson来执行execute SQL语句
            cursor = db.cursor()
            # 查询表明
            cursor.execute(sql_search, params)
            data = cursor.fetchall()
            cursor.close()
            db.close()
            return data





class get_system_scene(QThread):
    result_scene = Signal(list)  # 定义一个信号，用于传递读取到的数据

    def __init__(self, systemName) :
        super().__init__()
        self.systemName = systemName


    def run(self):
        # 生成业务、图片、接口关联的yaml地址
        pic_flow_path = f"{ROOT_DIR}/testcase/{self.systemName}/pic_flow.yaml"
        # 读取文件内容
        data_again = read_yaml(pic_flow_path)
        # 将业务名写入到list中, 发回给主线程
        all_scene = []
        for item in data_again.keys():
            all_scene.append(item)
        # 将读取到的数据通过信号发送回主线程
        self.result_scene.emit(all_scene)


class ImageLoaderThread(QThread):
    """ 图片加载线程   """
    images_loaded = Signal(list)
    db_results_loaded = Signal(set)
    db_results_len = Signal(int)


    def __init__(self, folder_path, start_time, end_time, keyword, search_type_combo_value, image_checkbox,
                 db_system_name, db_name, page_size, current_page, db_qTree_selected_items, db_num_id_value,
                 db_num_start_value, db_num_end_value, db_start_time_value, db_end_time_value, db_search_type_value) :
        super().__init__()
        self.folder_path = folder_path
        self.start_time = start_time
        self.end_time = end_time
        self.keyword = keyword
        self.search_type = search_type_combo_value
        self.image_checkbox = image_checkbox
        self.db_system_name = db_system_name
        self.db_name = db_name
        self.page_size = page_size
        self.current_page = current_page
        self.offset = (self.current_page - 1) * self.page_size
        self.db_qTree_selected_items = db_qTree_selected_items
        self.db_num_id_value = db_num_id_value
        self.db_num_start_value = db_num_start_value
        self.db_num_end_value = db_num_end_value
        self.db_start_time_value = db_start_time_value
        self.db_end_time_value = db_end_time_value
        self.db_search_type_value = db_search_type_value


    def run(self):
        filtered_images = []

        if self.search_type == "图片查询方式":
            filtered_images = [os.path.join(self.folder_path, filename) for filename in os.listdir(self.folder_path)]
            if self.image_checkbox :
                pic_path = os.path.basename(filtered_images[0])
                pic_timeStamp = os.path.splitext(pic_path)[0].replace('+', ':').replace('_', '.')
                # 将图片名作为数据库查询参数添加到里边, 无论通过界面如何修改, 都会修改为图片的名
                if len(self.db_qTree_selected_items) == 0 :
                    self.db_qTree_selected_items = [('SEND_DATETIME', pic_timeStamp)]
                else:
                    noHave = True
                    for i in self.db_qTree_selected_items :
                        if i[0] == 'SEND_DATETIME' :
                            i[1] = pic_timeStamp
                            noHave = False
                            break
                    if noHave :
                        self.db_qTree_selected_items.append(('SEND_DATETIME', pic_timeStamp))

                results, total_page = self.search_database(self.db_system_name,
                            self.db_name, self.db_num_id_value, self.db_qTree_selected_items, self.offset,self.page_size,
                            self.db_num_start_value,self.db_num_end_value, self.db_start_time_value, self.db_end_time_value, self.db_search_type_value)
        elif self.search_type == "关键字查询" :
            filtered_images = self.filter_files_by_time_and_keyword(self.folder_path, keyword=self.keyword)
            if self.image_checkbox :
                pic_path = os.path.basename(filtered_images[0])
                pic_timeStamp = os.path.splitext(pic_path)[0].replace('+', ':').replace('_', '.')

                # 将图片名作为数据库查询参数添加到里边, 无论通过界面如何修改, 都会修改为图片的名
                if len(self.db_qTree_selected_items) == 0 :
                    self.db_qTree_selected_items = [('SEND_DATETIME', pic_timeStamp)]
                else:
                    noHave = True
                    for i in self.db_qTree_selected_items :
                        if i[0] == 'SEND_DATETIME' :
                            i[1] = pic_timeStamp
                            noHave = False
                            break
                    if noHave :
                        self.db_qTree_selected_items.append(('SEND_DATETIME', pic_timeStamp))

                results, total_page = self.search_database(self.db_system_name,
                    self.db_name, self.db_num_id_value, self.db_qTree_selected_items, self.offset, self.page_size,
                    self.db_num_start_value, self.db_num_end_value, self.db_start_time_value, self.db_end_time_value,
                    self.db_search_type_value)
        elif self.search_type == "时间区间查询" :
            from datetime import datetime
            dt_start = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
            dt_end = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M:%S")
            import datetime
            start = datetime.datetime(dt_start.year, dt_start.month, dt_start.day, dt_start.hour, dt_start.minute)
            end = datetime.datetime(dt_end.year, dt_end.month, dt_end.day, dt_end.hour, dt_end.minute)
            filtered_images = self.filter_files_by_time_and_keyword(self.folder_path, start_time=start,
                                                                    end_time=end)
            if self.image_checkbox :
                pic_path = os.path.basename(filtered_images[0])
                pic_timeStamp = os.path.splitext(pic_path)[0].replace('+', ':').replace('_', '.')
                # 将图片名作为数据库查询参数添加到里边, 无论通过界面如何修改, 都会修改为图片的名
                if len(self.db_qTree_selected_items) == 0 :
                    self.db_qTree_selected_items = [('SEND_DATETIME', pic_timeStamp)]
                else:
                    noHave = True
                    for i in self.db_qTree_selected_items :
                        if i[0] == 'SEND_DATETIME' :
                            i[1] = pic_timeStamp
                            noHave = False
                            break
                    if noHave :
                        self.db_qTree_selected_items.append(('SEND_DATETIME', pic_timeStamp))

                results, total_page = self.search_database(
                    self.db_system_name,
                    self.db_name, self.db_num_id_value, self.db_qTree_selected_items, self.offset, self.page_size,
                    self.db_num_start_value, self.db_num_end_value, self.db_start_time_value, self.db_end_time_value,
                    self.db_search_type_value)
        if len(filtered_images) > 100:
            filtered_images = filtered_images[:100]

        self.images_loaded.emit(filtered_images)
        if self.image_checkbox :
            self.db_results_len.emit(total_page)
            self.db_results_loaded.emit(results)




    def search_database(self, system, db_name, num_id, qTree_selected_items, offset, page_size, num_start, num_end, start_time, end_time, search_type):
        if not self.db_name:
            return [] , 0
        results, total_page = [], 0
        if search_type == 'ID查询' :
            results = self.loadDataBase_id(f"{ROOT_DIR}/testcase/{system}/数据库截图/数据库/{db_name}", num_id)
            total_page = [[1]]
        elif search_type == 'ID区间查询' :
            (query_sql, query_params), (count_sql, count_params) = self.generate_sql_query(qTree_selected_items,
                                offset, page_size, id_range=(num_start, num_end), time_range=None)
            results = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{system}/数据库截图/数据库/{db_name}", query_sql, query_params)
            total_page = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{system}/数据库截图/数据库/{db_name}", count_sql, count_params)
        elif search_type == '时间区间查询' :
            (query_sql, query_params), (count_sql, count_params) = self.generate_sql_query(qTree_selected_items,
                                offset, page_size,id_range=None,time_range=(start_time, end_time))
            results = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{system}/数据库截图/数据库/{db_name}", query_sql,
                                            query_params)
            total_page = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{system}/数据库截图/数据库/{db_name}", count_sql,
                                               count_params)
        elif search_type == '数据库查询方式' :
            (query_sql, query_params), (count_sql, count_params) = self.generate_sql_query(qTree_selected_items,
                                                        offset, page_size, id_range=None, time_range=None)
            results = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{system}/数据库截图/数据库/{db_name}", query_sql, query_params)
            total_page = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{system}/数据库截图/数据库/{db_name}", count_sql,
                                               count_params)
        return results, total_page



    def filter_files_by_time_and_keyword(self, folder_path, start_time=None, end_time=None, keyword=None):
        """
        查询符合条件的文件：
        1. 仅指定时间区间，返回时间符合的文件
        2. 指定时间区间 + 关键字，返回时间符合且文件名包含关键字的文件
        3. 仅指定关键字，返回文件名包含关键字的文件

        :param folder_path: 要搜索的文件夹路径
        :param start_time: 开始时间 (datetime 对象)，可选
        :param end_time: 结束时间 (datetime 对象)，可选
        :param keyword: 需要匹配的关键字，可选
        :return: 符合条件的文件列表
        """

        if not os.path.isdir(folder_path):
            print("路径不存在或不是文件夹")
            return []

        files = os.listdir(folder_path)
        matched_files = []

        # 转换时间到时间戳
        start_timestamp = start_time.timestamp() if start_time else None
        end_timestamp = end_time.timestamp() if end_time else None

        for file in files:
            file_path = os.path.join(folder_path, file)

            # 确保是文件
            if not os.path.isfile(file_path):
                continue

            # 获取文件创建时间（时间戳）
            file_ctime = os.stat(file_path).st_ctime

            # **条件判断**
            match_time = (start_timestamp is None or file_ctime >= start_timestamp) and \
                         (end_timestamp is None or file_ctime <= end_timestamp)
            match_keyword = keyword is None or keyword in file

            if match_time and match_keyword:
                matched_files.append(file_path)

        return matched_files


    def loadDataBase_ALL(self, dataBasePath, sql_search, params):
        splitName = os.path.splitext(dataBasePath)
        splitName_len = len(splitName) - 1
        if splitName[splitName_len] == '.db':
            # 读取sqlite数据
            db = sqlite3.connect(dataBasePath)
            # db.text_factory = lambda  x: str(x,'gbk','ignore')
            db.text_factory = str
            # 创建游标curson来执行execute SQL语句
            cursor = db.cursor()
            # 查询表明
            cursor.execute(sql_search, params)
            data = cursor.fetchall()
            cursor.close()
            db.close()
            return data


    def generate_sql_query(self, filters, offset, page_size, id_range=None, time_range=None):
        """
        生成 SQLite 分页查询 SQL 语句

        :param filters: list[set] - 过滤条件，每个 set 包含 (字段名, 关键字)
        :param page: int - 查询的页数（默认第 1 页）
        :param page_size: int - 每页显示条数（默认 15 条）
        :param id_range: tuple - ID 区间 (最小ID, 最大ID)
        :param time_range: tuple - 时间戳区间 (起始时间, 结束时间)
        :return: SQL 语句和参数
        """

        base_sql = """
                SELECT * FROM activity
              """
        # 统计总数 SQL 语句
        count_sql = "SELECT COUNT(*) FROM activity"
        # 过滤条件
        conditions = []
        params = []

        # 动态添加过滤条件
        for field, value in filters:
            if field in ["REQ_BODY", "RES_BODY"]:  # BLOB 类型需要转换
                conditions.append(f"CAST({field} AS TEXT) LIKE ?")
            else:
                conditions.append(f"{field} LIKE ?")
            params.append(f"%{value}%")  # 模糊查询匹配

        # ID 区间过滤
        if id_range:
            conditions.append("ID BETWEEN ? AND ?")
            params.extend(id_range)

        # 时间戳区间过滤
        if time_range:
            conditions.append("SEND_DATETIME BETWEEN ? AND ?")
            params.extend(time_range)

        # # 组合 WHERE 子句
        # if conditions:
        #     sql += " WHERE " + " AND ".join(conditions)
        # 组合 WHERE 子句
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        # 生成完整 SQL 语句
        query_sql = base_sql + where_clause + " LIMIT ? OFFSET ?"
        count_sql = count_sql + where_clause  # 统计总数不需要分页
        query_params = params + [page_size, offset]
        count_params = params  # 统计总数的参数和查询相同
        # 分页
        # offset = (page - 1) * page_size
        # sql += " LIMIT ? OFFSET ?"
        # params.extend([page_size, offset])

        # return sql, params
        return (query_sql, query_params), (count_sql, count_params)

    def loadDataBase_id(self, dataBasePath, num):
        splitName = os.path.splitext(dataBasePath)
        splitName_len = len(splitName) - 1
        if splitName[splitName_len] == '.db':
            # 读取sqlite数据
            db = sqlite3.connect(dataBasePath)
            # db.text_factory = lambda  x: str(x,'gbk','ignore')
            db.text_factory = str
            # 创建游标curson来执行execute SQL语句
            cursor = db.cursor()
            if num != '':
                sql_search = 'select * from activity where id={}'.format(num)
            # 查询表明  SEND_DATETIME
            cursor.execute(sql_search)
            data = cursor.fetchall()
            cursor.close()
            db.close()
            return data


class DatabaseQueryThread(QThread):
    """ 数据库查询线程 """
    results_loaded = Signal(set)
    results_len = Signal(int)
    images_loaded = Signal(list)

    def __init__(self, dataSet, pageSize, currentPage, qTree_selected_items, search_type, db_checkbox, db_selected_id, image_folder):
        super().__init__()
        self.system = dataSet[0] # 系统名
        self.db_name = dataSet[1] # 数据库名
        self.field = dataSet[2] # 这个字段应该没用了 ！！！！！！！！！！！！！
        # self.value = dataSet[3]
        self.num_start = int(dataSet[3])
        self.num_end = int(dataSet[4])
        self.num_id = int(dataSet[5])
        self.start_time = dataSet[6]
        self.end_time = dataSet[7]
        self.page_size = pageSize
        self.current_page = currentPage
        self.offset = (self.current_page - 1) * self.page_size
        self.qTree_selected_items = qTree_selected_items
        self.search_type = search_type # 查询数据库的方式
        self.db_checkbox = db_checkbox # 通过数据库报文查询图片
        self.db_selected_id = db_selected_id # 通过数据库报文查询图片, 勾选的报文ID
        self.image_folder = image_folder # 查询图片的绝对路径

    def run(self):

        if self.db_checkbox :
            filtered_images = []
            for item in self.db_selected_id :
                reItem = item[1].replace(':','+').replace('.','_')
                pic = self.image_folder + f'/{reItem}.png'
                if os.path.exists(pic) :
                    filtered_images.append(pic)
            self.images_loaded.emit(filtered_images)
        else:
            if not self.db_name:
                self.results_loaded.emit([])
                return

            if self.search_type == 'ID查询' :
                results = self.loadDataBase_id(f"{ROOT_DIR}/testcase/{self.system}/数据库截图/数据库/{self.db_name}", self.num_id)
                total_page = [[1]]
            elif self.search_type == 'ID区间查询' :
                (query_sql, query_params), (count_sql, count_params) = self.generate_sql_query(self.qTree_selected_items,
                                    self.offset, self.page_size, id_range=(self.num_start, self.num_end), time_range=None)
                results = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{self.system}/数据库截图/数据库/{self.db_name}", query_sql, query_params)
                total_page = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{self.system}/数据库截图/数据库/{self.db_name}", count_sql, count_params)
            elif self.search_type == '时间区间查询' :
                (query_sql, query_params), (count_sql, count_params) = self.generate_sql_query(self.qTree_selected_items,
                                    self.offset, self.page_size,id_range=None,time_range=(self.start_time, self.end_time))
                results = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{self.system}/数据库截图/数据库/{self.db_name}", query_sql,
                                                query_params)
                total_page = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{self.system}/数据库截图/数据库/{self.db_name}", count_sql,
                                                   count_params)
            elif self.search_type == '数据库查询方式' :
                (query_sql, query_params), (count_sql, count_params) = self.generate_sql_query(self.qTree_selected_items,
                                                            self.offset, self.page_size, id_range=None, time_range=None)
                results = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{self.system}/数据库截图/数据库/{self.db_name}", query_sql, query_params)
                total_page = self.loadDataBase_ALL(f"{ROOT_DIR}/testcase/{self.system}/数据库截图/数据库/{self.db_name}", count_sql,
                                                   count_params)
            self.results_len.emit(total_page[0][0])
            self.results_loaded.emit(results)


    def loadDataBase_ALL(self, dataBasePath, sql_search, params):
        splitName = os.path.splitext(dataBasePath)
        splitName_len = len(splitName) - 1
        if splitName[splitName_len] == '.db':
            # 读取sqlite数据
            db = sqlite3.connect(dataBasePath)
            # db.text_factory = lambda  x: str(x,'gbk','ignore')
            db.text_factory = str
            # 创建游标curson来执行execute SQL语句
            cursor = db.cursor()
            # 查询表明
            cursor.execute(sql_search, params)
            data = cursor.fetchall()
            cursor.close()
            db.close()
            return data

    def loadDataBase_id(self, dataBasePath, num):
        splitName = os.path.splitext(dataBasePath)
        splitName_len = len(splitName) - 1
        if splitName[splitName_len] == '.db':
            # 读取sqlite数据
            db = sqlite3.connect(dataBasePath)
            # db.text_factory = lambda  x: str(x,'gbk','ignore')
            db.text_factory = str
            # 创建游标curson来执行execute SQL语句
            cursor = db.cursor()
            if num != '':
                sql_search = 'select * from activity where id={}'.format(num)
            # 查询表明  SEND_DATETIME
            cursor.execute(sql_search)
            data = cursor.fetchall()
            cursor.close()
            db.close()
            return data


    def generate_sql_query(self, filters, offset, page_size, id_range=None, time_range=None):
        """
        生成 SQLite 分页查询 SQL 语句

        :param filters: list[set] - 过滤条件，每个 set 包含 (字段名, 关键字)
        :param page: int - 查询的页数（默认第 1 页）
        :param page_size: int - 每页显示条数（默认 15 条）
        :param id_range: tuple - ID 区间 (最小ID, 最大ID)
        :param time_range: tuple - 时间戳区间 (起始时间, 结束时间)
        :return: SQL 语句和参数
        """

        base_sql = """
                SELECT * FROM activity
              """
        # 统计总数 SQL 语句
        count_sql = "SELECT COUNT(*) FROM activity"
        # 过滤条件
        conditions = []
        params = []

        # 动态添加过滤条件
        for field, value in filters:
            if field in ["REQ_BODY", "RES_BODY"]:  # BLOB 类型需要转换
                conditions.append(f"CAST({field} AS TEXT) LIKE ?")
            else:
                conditions.append(f"{field} LIKE ?")
            params.append(f"%{value}%")  # 模糊查询匹配

        # ID 区间过滤
        if id_range:
            conditions.append("ID BETWEEN ? AND ?")
            params.extend(id_range)

        # 时间戳区间过滤
        if time_range:
            conditions.append("SEND_DATETIME BETWEEN ? AND ?")
            params.extend(time_range)

        # 组合 WHERE 子句
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        # 生成完整 SQL 语句
        query_sql = base_sql + where_clause + " LIMIT ? OFFSET ?"
        count_sql = count_sql + where_clause  # 统计总数不需要分页
        query_params = params + [page_size, offset]
        count_params = params  # 统计总数的参数和查询相同

        return (query_sql, query_params), (count_sql, count_params)


# 通过数据库的table, 获得数据库中ID, 将用户输入的业务场景、图片名、数据库ID, 写入到pic_flow.yaml中
class labelIntoYamlThread(QThread):
    """ 数据库查询线程 """
    results = Signal(list) # toast提示, 元素0, 提示信息, 元素1, 提示时间
    results_all_scene = Signal(list)


    def __init__(self, scene_input, image_name_label, image_system_combo, db_selected_id, action ):
        super().__init__()
        self.scene_input = scene_input # 业务名称输入框,输入内容
        self.image_name_label = image_name_label # 图片名
        self.system_combo = image_system_combo  # 图片系统名
        self.db_selected_id = db_selected_id # 勾选的数据ID集合[('ID', '时间戳')]
        self.action = action # 选择是添加还是覆盖原数据, add添加, overwrite覆盖 # 处理覆盖, 最终需要保留原来的值, 才能判断是否写入成功, 覆盖是原值+新值
        self.origin_flow_id = action # 选择是添加还是覆盖原数据, add添加, overwrite覆盖 # 处理覆盖, 最终需要保留原来的值, 才能判断是否写入成功, 覆盖是原值+新值


    def run(self):
        # flow_Id = self.getIds(self.table)
        flow_Id = []
        if len(self.db_selected_id) != 0 :
            for item in self.db_selected_id :
                flow_Id.append(str(item[0]))
        yaml = YAML()
        # 生成业务、图片、接口关联的yaml地址
        pic_flow_path = f"{ROOT_DIR}/testcase/{self.system_combo}/pic_flow.yaml"
        real_image_name = self.image_name_label.replace('图片名: ', '')

        # 判断文件是否存在
        if os.path.exists(pic_flow_path):
            # 有这个文件, 读取文件内容
            data = read_yaml(pic_flow_path)
            # 将场景、图片名、接口写入yaml中, 无论data中是否包含当前业务、图片名、接口,都写入，存在就覆盖掉
            if self.action == 'add':
                # 获得原值, 拼接新值
                self.origin_flow_id = data.get(self.scene_input).get(real_image_name)
                data[self.scene_input] = {real_image_name: self.origin_flow_id + flow_Id}
            elif self.action == 'overwrite':
                data[self.scene_input] = {real_image_name: flow_Id}

        else:
            # 没有这个文件, 直接生成业务、图片、接口绑定的状态, { '业务名': {'图片名': ['接口ID 1','接口ID 2', .....] } }
            data = {}
            temp = {real_image_name: flow_Id}
            data[self.scene_input] = temp
        # 将业务、图片、接口进行绑定, 写入yaml文件中
        with open(pic_flow_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)
        # 读取pic_flow.yaml, 校验是否存入了值
        data_again = read_yaml(pic_flow_path)
        if self.action == 'add':
            # 获得原值, 拼接新值
            if data_again.get(self.scene_input) == {real_image_name: self.origin_flow_id + flow_Id}:
                all_scene = []
                for item in data_again.keys():
                    all_scene.append(item)
                self.results.emit(['当前业务、图片、接口存储成功', 2000])
                self.results_all_scene.emit(all_scene)
            else:
                self.results.emit(['当前业务、图片、接口存储失败', 2000])
        elif self.action == 'overwrite':
            if data_again.get(self.scene_input) == {real_image_name: flow_Id}:
                all_scene = []
                for item in data_again.keys():
                    all_scene.append(item)
                self.results.emit(['当前业务、图片、接口存储成功', 2000])
                self.results_all_scene.emit(all_scene)
            else:
                self.results.emit(['当前业务、图片、接口存储失败', 2000])

        self.origin_flow_id = []

    # # 通过table获得数据库中的ID, 当前方法返回一个list, 就是包含所有的数据库ID
    # # table: 数据库table
    # def getIds(self, table):
    #     flow_Id = []
    #     for row in range(table.rowCount()):
    #         item = table.item(row, 1)  # "ID" 列在索引 1
    #         if item is not None:  # 确保单元格不是空的
    #             flow_Id.append(item.text())
    #     return flow_Id


class ImageDatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.global_data = None
        # 当前图片数据
        self.pixmap = None  # 先不加载图片
        self.original_image_label = None  # 用来label大小
        self.current_scale = 1.0  # 默认缩放比例
        self.image_name = '' # 展示图片的名字
        self.setWindowTitle("图片和数据库查看器")
        self.showMaximized()
        # self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)  # 置顶窗口
        # self.is_pinned = True  # 置顶状态
        screenSize = self.get_screen_size()
        self.setGeometry(50, 50, int(screenSize[0]*0.7), int(screenSize[1]*0.7))  # 占屏幕约60%
        # **窗口右上角按钮**
        pin_action = QAction("📌", self)
        pin_action.triggered.connect(self.toggle_pin)
        self.menuBar().addAction(pin_action)

        # **主界面**
        main_layout = QVBoxLayout()

        # 新建工厂
        self.get_all_system = Worker_get_all_system()
        self.get_all_system.finished.connect(self.update_all_combobox)
        self.get_all_system.start()

        # **顶部控件（可换行）**
        self.create_top_controls()
        main_layout.addLayout(self.top_controls)

        # **可拖拽分割线**
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # **左侧 图片展示**
        self.image_label = QLabel("图片展示区域")
        # self.image_label.setFixedSize(800, 600)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black; background: #eee;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 当前图片数据

        left_layout = QVBoxLayout()
        left_zoom = QHBoxLayout()
        left_zoom.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        # **新增缩放按钮**
        self.image_name_label = QLabel('图片名')
        self.zoom_in_button = QPushButton("放大")
        self.zoom_out_button = QPushButton("缩小")
        self.prev_btn = QPushButton("⬅ 上一张")
        self.next_btn = QPushButton("下一张 ➡")
        # 绑定按钮事件
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.prev_btn.clicked.connect(self.prev_image)
        self.next_btn.clicked.connect(self.next_image)
        left_zoom.addWidget(self.image_name_label)
        left_zoom.addWidget(self.zoom_in_button)
        left_zoom.addWidget(self.zoom_out_button)
        left_zoom.addWidget(self.prev_btn)
        left_zoom.addWidget(self.next_btn)
        left_layout.addLayout(left_zoom)
        # 业务输入框、确定业务按键、生成业务名称下拉框、查询业务名称按键
        left_controls_row1 = QHBoxLayout()

        self.sure_scene_input = QLineEdit()
        self.sure_scene_input.setFixedWidth(200)
        self.sure_scene_input.setPlaceholderText("业务名称")
        self.sure_scene_btn = QPushButton("关联业务图片勾选接口")

        self.sure_scene_btn.clicked.connect(
            lambda: self.show_three_option_dialog(
                dialog_title="提示信息",
                dialog_message="请确定操作",
                options=["add", "overwrite"],
                confirm_callback=self.sure_scene
            )
        )

        self.scene_combo_row1 = QComboBox(self)
        self.scene_combo_row1.currentIndexChanged.connect(self.set_text_sure_scene_input)

        self.search_scene_btn = QPushButton("显示关联")
        self.search_scene_btn.clicked.connect(self.search_scene)
        left_controls_row1.addWidget(self.sure_scene_input)
        left_controls_row1.addWidget(self.sure_scene_btn)
        left_controls_row1.addWidget(self.scene_combo_row1)
        left_controls_row1.addWidget(self.search_scene_btn)
        # 业务下拉框、对当前业务执行功能下拉框、执行按键
        left_controls_row2 = QHBoxLayout()
        # left_controls_row2.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        self.scene_combo_row2 = QComboBox(self)
        # 功能类型
        self.exec_scene_combo = QComboBox(self)  # 对当前业务执行操作
        #
        self.exec_scene_btn = QPushButton("执行操作")

        self.exec_scene_btn.clicked.connect(
            lambda: self.show_dialog(
                dialog_title="提示信息",
                dialog_message="请确定操作",
                confirm_callback=self.exec_scene
            )
        )

        left_controls_row2.addWidget(self.scene_combo_row2)
        left_controls_row2.addWidget(self.exec_scene_combo)
        left_controls_row2.addWidget(self.exec_scene_btn)
        left_layout.addLayout(left_controls_row1)
        left_layout.addLayout(left_controls_row2)
        left_layout.addWidget(self.image_label)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # **右侧 数据库展示**
        self.table = QTableWidget(15, 14)
        self.table.setColumnWidth(0, 50)  # 固定列宽
        self.table.setColumnWidth(1, 50)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 250)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 200)
        self.table.setColumnWidth(7, 200)
        self.table.setColumnWidth(8, 200)
        self.table.setColumnWidth(9, 200)
        self.table.setColumnWidth(10, 150)
        self.table.setColumnWidth(11, 200)
        self.table.setColumnWidth(12, 200)
        self.table.setColumnWidth(13, 200)
        self.table.setHorizontalHeaderLabels(["选择", "ID", "LOCAL_SOURCE_IP", "TARGET_URL", "HTTP_METHOD",
                                              "BURP_TOOL", "REQ_HEADERS", "REQ_BODY", "RES_HEADERS",
                                              "RES_BODY", "WORK_NUM", "SAME_DIRECTORY",
                                              "ENCRYPT_DECRYPT_KEY", "SEND_DATETIME"])
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cell_field_selected_keys = [] # 用来存储勾选字段和对应值, 数据格式 [ [解析出勾选的字段, 数据库id值, 当前cell值对应数据库字段 ] ]
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 允许右键菜单
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.table.customContextMenuRequested.connect(self.show_context_menu)
        # 让列宽固定，不随内容变化
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        # 绑定事件
        self.table.cellClicked.connect(self.show_detail_dialog)
        # 点击右键鼠标的选项
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # **数据库表格嵌套在滚动区域**
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.table)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # 开启横向滚动条
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.right_layout = QVBoxLayout()

        # 分页控件
        self.page_size = 15  # 每页显示10条
        self.current_page = 1  # 当前页
        self.total_pages = 1  # 总页数
        self.max_page_buttons = 5  # 只显示最多 5 个分页按钮
        self.pagination_layout = QHBoxLayout()
        self.pagination_layout.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        self.page_buttons = []  # 存储分页按钮
        # 跳转控件
        self.page_label = QLabel("跳转到:")
        self.page_label.setFixedWidth(50)
        self.page_label.setFixedHeight(30)
        self.page_input = QLineEdit()
        self.page_input.setFixedWidth(50)
        self.page_input.setFixedHeight(30)
        self.jump_button = QPushButton("跳转")
        self.jump_button.setFixedWidth(50)
        self.jump_button.setFixedHeight(30)
        self.jump_button.clicked.connect(self.jump_page)
        self.pagination_layout.addWidget(self.page_label)
        self.pagination_layout.addWidget(self.page_input)
        self.pagination_layout.addWidget(self.jump_button)

        # right_layout.addWidget(self.table)
        right_widget = QWidget()
        self.right_layout.addWidget(self.scroll_area)
        self.right_layout.addLayout(self.pagination_layout)
        right_widget.setLayout(self.right_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.image_list = []
        self.current_image_index = 0 # 从1开始还有一个下拉框title

        self.db_system_name = ''  # 数据库系统名
        self.db_name = ''  # 数据库名
        self.db_filter_field = ''  # 数据库过滤字段中的值
        self.db_num_id_value = ''  # 数据库只查询数据库单个ID的ID值
        self.db_num_start_value = ''  # 数据库ID区间查询, 开始ID
        self.db_num_end_value = ''  # 数据库ID区间查询, 结束ID
        self.db_start_time_value = '' # 数据库查询开始时间
        self.db_end_time_value = ''     # 数据库查询结束时间
        self.db_search_type_value = ''  # 数据库查询类型
        self.db_qTree_selected_items = []  # 数据库过滤的字段和值, 存入到list中
        self.total_divid_page = 1  # 总分页数量
        self.db_selected_id = [] # 数据库中接口显示,勾选框, 勾选的id
        self.get_system_scene_thread = None # 获得当前系统包含业务
        self.labelIntoYaml_thread = None # 将业务名写入到 pic_flow.yaml 文件中线程
        self.searchScene_thread = None # 查询 pic_flow.yaml 文件内容线程
        self.aliases = {} # 系统中的别名
        # 存储黑白名单使用的下拉框选项, 默认为 '存储类型'
        self.save_type_white_black_list = '存储类型'


    def create_top_controls(self):
        """ 创建顶部控件，支持自动换行 """
        self.top_controls = QVBoxLayout()
        row1 = QHBoxLayout()
        row1.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        row2 = QHBoxLayout()
        row2.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        height = 30
        self.system_combo = QComboBox()
        self.system_combo.setFixedWidth(120)
        self.system_combo.setFixedHeight(height)
        self.system_combo.currentIndexChanged.connect(self.image_system_combo_change)
        self.type_combo = QComboBox()
        self.type_combo.setFixedWidth(200)
        self.type_combo.setFixedHeight(height)
        self.search_type_combo = QComboBox()
        self.search_type_combo.setFixedWidth(200)
        self.search_type_combo.setFixedHeight(height)
        self.search_type_combo.currentIndexChanged.connect(self.search_type_combo_selected)
        self.search_result_combo = QComboBox()
        self.search_result_combo.setFixedWidth(200)
        self.search_result_combo.setFixedHeight(height)
        self.search_result_combo.currentIndexChanged.connect(self.search_result_combo_selected)
        self.keyword_input = QLineEdit('图片关键字')
        self.keyword_input.hide()
        self.keyword_input.setFixedWidth(150)
        self.keyword_input.setFixedHeight(height)
        self.time_start = QDateTimeEdit()
        self.time_start.hide()
        self.time_start.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.time_start.setDateTime(QDateTime.currentDateTime())
        self.time_start.setFixedWidth(160)
        self.time_start.setFixedHeight(height)
        self.time_end = QDateTimeEdit()
        self.time_end.hide()
        self.time_end.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.time_end.setDateTime(QDateTime.currentDateTime())
        self.time_end.setFixedWidth(160)
        self.time_end.setFixedHeight(height)
        self.search_image_btn = QPushButton("查询图片")
        self.search_image_btn.setFixedWidth(100)
        self.search_image_btn.setFixedHeight(height)
        self.search_image_btn.clicked.connect(self.search_images)
        # 创建勾选框, 勾选后, 进入查询图片的同时, 查询对应接口报文
        self.image_checkbox = QCheckBox("通过图片查接口", self)
        self.image_checkbox.setChecked(False)  # 默认未勾选
        # 监听勾选状态变化
        self.image_checkbox.stateChanged.connect(self.checkbox_state)

        # 单独查询数据库下拉框
        self.db_system_combo = QComboBox()
        self.db_system_combo.setFixedWidth(120)
        self.db_system_combo.setFixedHeight(height)
        self.db_system_combo.currentIndexChanged.connect(self.update_all_database_combobox)
        self.db_file_combo = QComboBox()
        self.db_file_combo.setFixedWidth(200)
        self.db_file_combo.setFixedHeight(height)
        self.db_field_combo = QComboBox()
        self.db_field_combo.setEditable(False)  # 让下拉框不可手动输入
        self.db_field_combo.setFixedWidth(300)
        self.db_field_combo.setFixedHeight(height)
        # 创建 QTreeWidget 作为下拉列表, 过滤字段
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(2)  # 两列：勾选框 + 输入框
        self.tree_widget.setHeaderHidden(True)  # 隐藏表头
        # 让 QComboBox 使用 QTreeWidget 作为弹出窗口
        self.db_field_combo.setModel(self.tree_widget.model())
        self.db_field_combo.setView(self.tree_widget)
        self.items = []  # 存储 (复选框, 输入框) 组件
        # 监听 item 点击，确保正确更新复选框状态
        self.tree_widget.itemPressed.connect(self.toggle_checkbox)

        self.db_search_type_combo = QComboBox()
        self.db_search_type_combo.setFixedWidth(120)
        self.db_search_type_combo.setFixedHeight(height)
        self.db_search_type_combo.currentIndexChanged.connect(self.update_db_search_type_combobox)

        # 单独查询ID输入框
        self.db_num_id = QSpinBox()
        self.db_num_id.setMaximum(9999999)  # 设置更大的数值上限
        self.db_num_id.setMinimum(1)  # 可选：设置负数最小值
        self.db_num_id.setFixedWidth(100)
        self.db_num_id.setFixedHeight(height)
        self.db_num_id.hide()
        # ID区间查询开始输入框
        self.db_num_start = QSpinBox()
        self.db_num_start.setMaximum(9999998)  # 设置更大的数值上限
        self.db_num_start.setMinimum(1)  # 可选：设置负数最小值
        self.db_num_start.setFixedWidth(100)
        self.db_num_start.setFixedHeight(height)
        self.db_num_start.hide()
        # ID区间查询结束输入框
        self.db_num_end = QSpinBox()
        self.db_num_end.setMaximum(9999999)  # 设置更大的数值上限
        self.db_num_end.setMinimum(2)  # 可选：设置负数最小值
        self.db_num_end.setFixedWidth(100)
        self.db_num_end.setFixedHeight(height)
        self.db_num_end.hide()
        # 时间开始输入框
        self.db_time_start = QDateTimeEdit()
        self.db_time_start.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.db_time_start.setDateTime(QDateTime.currentDateTime())
        self.db_time_start.setFixedWidth(160)
        self.db_time_start.setFixedHeight(height)
        self.db_time_start.hide()
        # 时间结束输入框
        self.db_time_end = QDateTimeEdit()
        self.db_time_end.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.db_time_end.setDateTime(QDateTime.currentDateTime())
        self.db_time_end.setFixedWidth(160)
        self.db_time_end.setFixedHeight(height)
        self.db_time_end.hide()
        self.db_search_btn = QPushButton("查询数据库")
        self.db_search_btn.setFixedWidth(70)
        self.db_search_btn.setFixedHeight(height)
        self.db_search_btn.clicked.connect(self.search_database)
        # 创建勾选框, 勾选后, 进入查询图片的同时, 查询对应接口报文
        self.db_checkbox = QCheckBox("通过接口查图片", self)
        self.db_checkbox.setChecked(False)  # 默认未勾选
        # 监听勾选状态变化
        self.db_checkbox.stateChanged.connect(self.checkbox_state)

        row1.addWidget(self.system_combo)
        row1.addWidget(self.type_combo)
        row1.addWidget(self.search_type_combo)
        row1.addWidget(self.search_result_combo)
        row1.addWidget(self.keyword_input)
        row1.addWidget(self.time_start)
        row1.addWidget(self.time_end)
        row1.addWidget(self.search_image_btn)
        row1.addWidget(self.image_checkbox)

        row2.addWidget(self.db_system_combo)
        row2.addWidget(self.db_file_combo)
        row2.addWidget(self.db_field_combo)
        row2.addWidget(self.db_search_type_combo)
        # row2.addWidget(self.db_input)
        row2.addWidget(self.db_num_id)
        row2.addWidget(self.db_num_start)
        row2.addWidget(self.db_num_end)
        row2.addWidget(self.db_time_start)
        row2.addWidget(self.db_time_end)
        row2.addWidget(self.db_search_btn)
        row2.addWidget(self.db_checkbox)

        self.top_controls.addLayout(row1)
        self.top_controls.addLayout(row2)

    # 置顶窗口功能
    def toggle_pin(self):
        """ 置顶窗口 """
        self.setWindowFlag(Qt.WindowStaysOnTopHint, not self.windowFlags() & Qt.WindowStaysOnTopHint)
        self.show()

    # 查询存储图片功能
    def search_images(self):
        self.show_toast('勿动,数据加载中!!!', 3000)
        """ 启动线程加载图片 """
        system = self.system_combo.currentText()
        picDir = self.global_data.get('allImageType')[self.type_combo.currentText()]
        image_folder = f"{ROOT_DIR}/testcase/{system}/数据库截图/截图/{picDir}/"
        keyword = self.keyword_input.text()
        start_time = self.time_start.dateTime().toPython().strftime("%Y-%m-%d %H:%M:%S")
        end_time = self.time_end.dateTime().toPython().strftime("%Y-%m-%d %H:%M:%S")
        search_type_combo_value = self.search_type_combo.currentText()
        image_checkbox = self.image_checkbox.isChecked()
        #
        if image_checkbox :
            # 数据库查询
            """ 启动线程查询数据库self.db_field_combo """
            self.db_system_name = self.db_system_combo.currentText()  # 系统名
            self.db_name = self.db_file_combo.currentText()  # 数据库名
            self.db_num_id_value = self.db_num_id.value()  # 只查询数据库单个ID的ID值
            self.db_num_start_value = self.db_num_start.value()  # ID区间查询, 开始ID
            self.db_num_end_value = self.db_num_end.value()  # ID区间查询, 结束ID
            self.db_start_time_value = self.db_time_start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            self.db_end_time_value = self.db_time_end.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            self.db_search_type_value = self.db_search_type_combo.currentText()  # 查询类型
            """ 获取被勾选的选项及其输入框内容 """
            # 点击查询重置勾选选项
            self.db_qTree_selected_items = []
            for item, input_field in self.items:

                if item.checkState(0) == Qt.Checked:  # 判断是否勾选
                    self.db_qTree_selected_items.append((item.text(0), input_field.text()))
        # 如果有正在运行的线程，先终止
        if hasattr(self, "image_loader_thread") and self.image_loader_thread.isRunning():
            self.image_loader_thread.terminate()  # 强制终止旧线程（如果任务重，可以用信号优雅终止）
        # 只要点击查询按键, 重置, 当前页为1
        self.current_page = 1
        self.image_loader_thread = ImageLoaderThread(image_folder, start_time, end_time, keyword,
            search_type_combo_value, image_checkbox, self.db_system_name, self.db_name, self.page_size, self.current_page,
            self.db_qTree_selected_items, self.db_num_id_value, self.db_num_start_value, self.db_num_end_value,
            self.db_start_time_value, self.db_end_time_value, self.db_search_type_value )

        self.image_loader_thread.images_loaded.connect(self.load_images)
        self.image_loader_thread.db_results_loaded.connect(self.load_database_results)
        self.image_loader_thread.db_results_len.connect(self.update_pagination)
        self.image_loader_thread.start()

    # 通过信号槽查询符合要求图片名, 当前方法加载符合条件图片名, images就是信号槽响应回的数据
    def load_images(self, images):
        self.image_list = []
        self.image_list = images
        # 查询一次就会重新复位图片展示位置
        self.current_image_index = 0
        self.search_result_combo.clear()
        self.search_result_combo.addItems(['全部图片搜索结果'] + self.image_list)
        iamge_index = self.image_list[self.current_image_index]
        self.show_image(iamge_index)
        # 设置图片名
        self.image_name_label.setText('图片名: ' + os.path.basename(iamge_index).strip())


    def search_database(self):
        self.show_toast('勿动,数据加载中!!!', 3000)
        """ 启动线程查询数据库self.db_field_combo """
        self.db_system_name = self.db_system_combo.currentText() # 系统名
        self.db_name = self.db_file_combo.currentText() # 数据库名
        self.db_filter_field = self.db_field_combo.currentText() # 过滤字段中的值
        # value = self.db_input.text()
        self.db_num_id_value = self.db_num_id.value() # 只查询数据库单个ID的ID值
        self.db_num_start_value = self.db_num_start.value() # ID区间查询, 开始ID
        self.db_num_end_value = self.db_num_end.value()  # ID区间查询, 结束ID
        # self.db_start_time_value = self.db_time_start.dateTime().toPython()
        self.db_start_time_value = self.db_time_start.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        # self.db_end_time_value = self.db_time_end.dateTime().toPython()
        self.db_end_time_value = self.db_time_end.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.db_search_type_value = self.db_search_type_combo.currentText()  # 查询类型
        # 图片属性, 获得系统、图片类型, 追钟生成绝对路径
        system = self.system_combo.currentText()
        try:
            picDir = self.global_data.get('allImageType')[self.type_combo.currentText()]
            image_folder = f"{ROOT_DIR}/testcase/{system}/数据库截图/截图/{picDir}/"
        except Exception as e:
            image_folder = ''

        """ 获取被勾选的选项及其输入框内容 """
        # 点击查询重置勾选选项
        self.db_qTree_selected_items = []
        for item, input_field in self.items:

            if item.checkState(0) == Qt.Checked:  # 判断是否勾选
                self.db_qTree_selected_items.append((item.text(0), input_field.text()))


        # 如果有正在运行的线程，先终止
        if hasattr(self, "db_thread") and self.db_thread.isRunning():
            self.db_thread.terminate()  # 强制终止旧线程（如果任务重，可以用信号优雅终止）
        # 只要点击查询按键, 重置, 当前页为1
        self.current_page = 1
        self.db_thread = DatabaseQueryThread((self.db_system_name, self.db_name, self.db_filter_field,
                        self.db_num_start_value, self.db_num_end_value, self.db_num_id_value,self.db_start_time_value,
                        self.db_end_time_value),self.page_size,self.current_page, self.db_qTree_selected_items,
                        self.db_search_type_value, self.db_checkbox.isChecked(), self.db_selected_id, image_folder)
        self.db_thread.results_loaded.connect(self.load_database_results)
        self.db_thread.results_len.connect(self.update_pagination)
        self.db_thread.images_loaded.connect(self.load_images)
        self.db_thread.start()

    def load_database_results(self, results):
        self.table.setRowCount(len(results))
        for row_idx, row in enumerate(results):
            checkbox = QCheckBox()
            # checkbox.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置居中对齐
            # self.table.setCellWidget(row_idx, 0, checkbox)
            # 使用 QHBoxLayout 来控制勾选框的位置
            layout = QHBoxLayout()
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置布局居中对齐
            layout.setContentsMargins(0, 0, 0, 0)  # 去掉布局的外边距

            # 将布局设置为表格单元格的控件
            widget = QWidget()
            widget.setLayout(layout)
            self.table.setCellWidget(row_idx, 0, widget)  # 将包含布局的 widget 添加到表格中

            for col_idx, col in enumerate(row):
                self.table.setItem(row_idx, col_idx+1, QTableWidgetItem(str(col)[:10000]))

            # 连接勾选框的状态改变信号
            checkbox.stateChanged.connect(lambda _, row=row: self.on_checkbox_changed(row))


    def on_checkbox_changed(self, row):
        """勾选框状态改变时的回调"""
        # 获取当前选中行的ID
        selected_id = (row[0], row[12])  # 假设ID是元组的第二个元素

        # 如果之前已有选中的勾选框，取消勾选
        if selected_id  in self.db_selected_id:
            self.db_selected_id.remove(selected_id)
        else:
            # 更新当前选中的ID
            self.db_selected_id.append(selected_id)
        print(f"当前选中的ID: {self.db_selected_id}")


    # def deselect_previous_checkbox(self):
    #     """取消勾选之前的勾选框"""
    #     for row_idx in range(self.table.rowCount()):
    #         checkbox = self.table.cellWidget(row_idx, 0)  # 获取勾选框
    #         if checkbox and checkbox.isChecked():
    #             checkbox.setChecked(False)


    def update_pagination(self,totalPage):
        """更新分页按钮（仅在总页数变化时重建 UI）"""
        new_total_divid_page = self.custom_divide(totalPage, self.page_size)

        # 如果总页数没变，不需要重新创建分页按钮
        if new_total_divid_page == self.total_divid_page:
            # 只更新选中状态
            for btn in self.page_buttons:
                if btn.text() != '...' :
                    btn.setChecked(int(btn.text()) == self.current_page)
            return

        self.total_divid_page = new_total_divid_page

        # 清空旧的分页按钮
        for btn in self.page_buttons:
            btn.deleteLater()
        self.page_buttons.clear()

        # 重新创建分页按钮
        for page in range(1, min(self.total_divid_page + 1, 6)):  # 只显示前5页 + "..."
            btn = QPushButton(str(page))
            btn.setFixedWidth(50)
            btn.setCheckable(True)
            btn.setChecked(page == self.current_page)
            btn.clicked.connect(lambda _, p=page: self.goto_page(p))
            self.page_buttons.append(btn)
            self.pagination_layout.addWidget(btn)

        if self.total_divid_page > 5:
            # 添加 "..."
            btn = QPushButton("...")
            btn.setFixedWidth(50)
            btn.setCheckable(False)
            self.page_buttons.append(btn)
            self.pagination_layout.addWidget(btn)

            # 添加最后一页按钮
            btn = QPushButton(str(self.total_divid_page))
            btn.setFixedWidth(50)
            btn.setCheckable(True)
            btn.setChecked(self.total_divid_page == self.current_page)
            btn.clicked.connect(lambda _, p=self.total_divid_page: self.goto_page(p))
            self.page_buttons.append(btn)
            self.pagination_layout.addWidget(btn)


    # 处理分页, 通过输入总数据量和每页数据展示数量, 相除获得分页数量
    # a: 数据总量    b: 每页展示数据量
    def custom_divide(self, a, b):
        if b == 0:
            raise ValueError("除数不能为 0")

        result = a / b

        if result < 1:
            return 1
        else:
            return math.ceil(result)

    # 确定业务场景
    def sure_scene(self,action):

        self.show_toast('勿动开始存储', 1000)
        # 填写到"业务名称"输入框中的内容
        sure_scene_input = self.sure_scene_input.text().strip()
        if sure_scene_input == '' or self.system_combo.currentText() == '' or self.image_name_label.text() == '' :
            self.show_toast('未选下拉框中选项或未填写业务名称', 1500)
        else:
            # 启动信号槽, 写入yaml中
            self.labelIntoYaml_thread = labelIntoYamlThread(sure_scene_input, self.image_name_label.text(), # 选择的图片名
                                                            self.system_combo.currentText(), # 选择的系统
                                                            self.db_selected_id, action ) # 勾选的数据ID集合[('ID', '时间戳')]
            self.labelIntoYaml_thread.results.connect(self.sure_scene_toast)
            self.labelIntoYaml_thread.results_all_scene.connect(self.update_scene_combobox)
            self.labelIntoYaml_thread.start()


    # 确定业务场景
    def exec_scene(self):
        self.show_toast('勿动系统操作中!!!', 1000)
        # 选择的业务类型
        scene_combo_row2 = self.scene_combo_row2.currentText()
        if scene_combo_row2 != '全部业务类型' :
            # 执行的当前业务类型, 实现的功能
            exec_scene_combo = self.exec_scene_combo.currentText()
            if exec_scene_combo != '功能类型' :
                system_dataConfig_path = f"{ROOT_DIR}/config/{self.db_system_combo.currentText()}dataConfig.yaml"
                system_dataConfig_path_backup = f"{ROOT_DIR}/config/{self.db_system_combo.currentText()}dataConfig_scenario_create_case_backup.yaml"
                data = read_yaml(system_dataConfig_path)
                # 备份一个原数据, 方便回溯
                yaml = YAML()
                with open(system_dataConfig_path_backup, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f)
                # 修改场景scenario_create_case中的值, 代表进行场景用例生成或者其他功能, 并覆盖保存原有的dataConfig.yaml中
                data[0]['scenario_create_case'] = [[scene_combo_row2, scene_combo_row2]]
                with open(system_dataConfig_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f)
                # 再次读取文件, 校验值是否写入
                data_again = read_yaml(system_dataConfig_path)
                if data_again[0]['scenario_create_case'] == [scene_combo_row2] :
                    self.show_toast('数据保存成功,开始执行功能!!!', 2000)
                else:
                    self.show_toast('测试场景数据保存失败, 无法执行功能!!!', 2000)
            else:
                self.show_toast('请选择功能类型!!!', 2000)
            # file_path = QFileDialog.getExistingDirectory(self, "选择保存目录")
            # print(file_path)
        else:
            self.show_toast('请选择业务类型!!!', 2000)




    def show_dialog(self, dialog_title, dialog_message, confirm_callback):
        """显示吐司和提示框
        Args:
            dialog_title (str): 提示框标题
            dialog_message (str): 提示框内容
            confirm_callback (callable): 确定按钮回调函数
        """
        # 显示吐司
        # self.show_toast(toast_message)
        # 显示提示框
        reply = QMessageBox.question(
            self,
            dialog_title,
            dialog_message,
            QMessageBox.Ok | QMessageBox.Cancel
        )

        # 点击确定时调用回调函数
        if reply == QMessageBox.Ok and confirm_callback:
            confirm_callback()


    def show_three_option_dialog(self, dialog_title, dialog_message, options, confirm_callback):
        """
        显示 Toast 提示和自定义对话框
        :param dialog_title: 对话框标题
        :param dialog_message: 对话框内容
        :param confirm_callback: 确认后的回调函数
        """
        # 创建自定义对话框
        dialog = CustomDialog(self, dialog_title, dialog_message)
        if dialog.exec() == QDialog.Accepted:
            action = dialog.get_selected_action()
            if action in options:
                confirm_callback(action)  # 执行回调函数，并传递用户选择的动作


    # 通过下拉框中的选项, 选项未自定义业务类型, 通过这个自定义业务类型, 查出与之绑定的图片名和接口
    def set_text_sure_scene_input(self):
        # 获得业务类型, 选择的值
        text = self.scene_combo_row1.currentText()
        if text != '全部业务类型' :
            # 更新输入框的内容, 方便用户不用手动填写
            self.sure_scene_input.setText(text)

    # 通过下拉框中的选项, 选项未自定义业务类型, 通过这个自定义业务类型, 查出与之绑定的图片名和接口
    def search_scene(self):
        # 启动信号槽, 读取yaml中数据
        # self.system_combo 图片搜索选择系统, self.type_combo 图片搜索选择图片类型  self.scene_combo_row1 查询业务关联使用的下拉框
        # self.db_system_combo 数据库搜索选择系统   self.db_file_combo 选择的数据库
        self.searchScene_thread = searchSceneLoaderThread(self.system_combo, self.type_combo, self.scene_combo_row1,
                                                          self.db_system_combo, self.db_file_combo )
        self.searchScene_thread.result_toast.connect(self.sure_scene_toast)
        self.searchScene_thread.result_image.connect(self.load_images)

        self.searchScene_thread.result_db.connect(self.load_database_results)
        self.searchScene_thread.result_len.connect(self.update_pagination)
        self.searchScene_thread.start()


    # 确定后弹出toast
    def sure_scene_toast(self, result):
        self.show_toast(result[0], result[1])

    # 点击cell右键, 点击选项
    # pos: 点击的位置
    def show_context_menu(self, pos: QPoint):
        """右键菜单"""
        menu = QMenu(self)
        action_show = menu.addAction("下载内容")
        action = menu.exec(self.table.mapToGlobal(pos))

        if action == action_show:
            # 打开文件保存对话框
            save_txt_path = QFileDialog.getExistingDirectory(self, "选择保存目录")
            # self.db_system_combo: 数据库搜索选择系统   self.db_name: 选择的数据库  row: 点击cell的行 col: 点击cell的列
            # save_txt_path: 保存文件的地址
            self.rightMouse_Menu = rightMouseMenuLoaderThread(self.db_system_name, self.db_name, self.table, pos,
                                                              save_txt_path)
            self.rightMouse_Menu.result_toast.connect(self.sure_scene_toast)
            self.rightMouse_Menu.start()



    # 展示对话框, 会对json格式进行解析
    # pos_or_row: 行列位置
    def show_detail_dialog(self, pos_or_row, col=None):
        """弹出对话框，展示完整内容"""
        if isinstance(pos_or_row, QPoint):  # 右键菜单触发
            index = self.table.indexAt(pos_or_row)
            row, col = index.row(), index.column()
        else:  # 单元格点击触发
            row = pos_or_row

        if col is None or row < 0:
            return

        data_id = self.table.item(row, 1).text()  # 获得数据库中ID, 方便提供下载, 因为数据库值太大, 只展示10000个字符
        data_position_field = {0: 'ID', 1: 'LOCAL_SOURCE_IP', 2: 'TARGET_URL', 3: 'HTTP_METHOD', 4: 'BURP_TOOL',
                               5: 'REQ_HEADERS',6: 'REQ_BODY', 7: 'RES_HEADERS', 8: 'RES_BODY', 9: 'WORK_NUM',
                               10: 'SAME_DIRECTORY', 11: 'ENCRYPT_DECRYPT_KEY', 12: 'SEND_DATETIME'}

        item = self.table.item(row, col)
        if not item:
            return

        content = item.text()

        dialog = QDialog(self)
        dialog.setWindowTitle("展示内容")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowCloseButtonHint)  # 移除右上角叉号
        dialog.resize(600, 500)

        layout = QVBoxLayout()

        # **第一部分**：下拉框 + 输入框 + 按钮
        option_layout = QHBoxLayout()
        dropdown = QComboBox()
        # 自定义存储类型, 第一部分使用
        custom_save_list_type = ["自定义别名",
                          "权限测试白名单URL", "权限测试白名单URL字段", "权限测试白名单字段", "权限测试黑名单URL", "权限测试黑名单URL字段", "权限测试黑名单字段",
                          "权限测试白名单URL(equal)", "权限测试白名单URL字段(equal)", "权限测试白名单字段(equal)", "权限测试黑名单URL(equal)",
                          "权限测试黑名单URL字段(equal)", "权限测试黑名单字段(equal)",
                          "sql测试白名单URL", "sql测试白名单URL字段", "sql测试白名单字段", "sql测试黑名单URL", "sql测试黑名单URL字段", "sql测试黑名单字段",
                          "sql测试白名单URL(equal)", "sql测试白名单URL字段(equal)", "sql测试白名单字段(equal)", "sql测试黑名单URL(equal)",
                          "sql测试黑名单URL字段(equal)", "sql测试黑名单字段(equal)",
                          "xss测试白名单URL", "xss测试白名单URL字段", "xss测试白名单字段", "xss测试黑名单URL", "xss测试黑名单URL字段", "xss测试黑名单字段",
                          "xss测试白名单URL(equal)", "xss测试白名单URL字段(equal)", "xss测试白名单字段(equal)", "xss测试黑名单URL(equal)",
                          "xss测试黑名单URL字段(equal)", "xss测试黑名单字段(equal)",
                          "边界值测试白名单URL", "边界值测试白名单URL字段", "边界值测试白名单字段", "边界值测试黑名单URL", "边界值测试黑名单URL字段", "边界值测试黑名单字段",
                          "边界值测试白名单URL(equal)", "边界值测试白名单URL字段(equal)", "边界值测试白名单字段(equal)", "边界值测试黑名单URL(equal)",
                          "边界值测试黑名单URL字段(equal)", "边界值测试黑名单字段(equal)",
                          "下载地址测试白名单URL", "下载地址测试黑名单URL", "下载地址测试白名单URL(equal)", "下载地址测试黑名单URL(equal)",
                          "下载字段测试白名单URL", "下载字段测试白名单URL字段", "下载字段测试白名单字段", "下载字段测试黑名单URL", "下载字段测试黑名单URL字段",
                          "下载字段测试黑名单字段",
                          "下载字段测试白名单URL(equal)", "下载字段测试白名单URL字段(equal)", "下载字段测试白名单字段(equal)", "下载字段测试黑名单URL(equal)",
                          "下载字段测试黑名单URL字段(equal)", "下载字段测试黑名单字段(equal)",
                          "上传多文件测试白名单URL", "上传多文件测试黑名单URL", "上传多文件测试白名单URL(equal)", "上传多文件测试黑名单URL(equal)",
                          "上传字段测试白名单URL", "上传字段测试白名单URL字段", "上传字段测试白名单字段", "上传字段测试黑名单URL", "上传字段测试黑名单URL字段",
                          "上传字段测试黑名单字段",
                          "上传字段测试白名单URL(equal)", "上传字段测试白名单URL字段(equal)", "上传字段测试白名单字段(equal)", "上传字段测试黑名单URL(equal)",
                          "上传字段测试黑名单URL字段(equal)", "上传字段测试黑名单字段(equal)"
                          ]
        dropdown.addItems(custom_save_list_type)
        input1 = QLineEdit()
        input2 = QLineEdit()
        btn_confirm = QPushButton("确定")
        # input2.setVisible(False)  # 初始隐藏第二个输入框

        def on_dropdown_change(index):
            input1.clear()
            input2.clear()
            self.save_type_white_black_list = dropdown.currentText()
            if dropdown.currentText() == "自定义别名":
                input1.setVisible(True)
                input2.setVisible(True)
            else:
                input2.setVisible(False)

        dropdown.currentIndexChanged.connect(on_dropdown_change)

        def save_custom_setting():
            key = input1.text().strip()
            alias = input2.text().strip()
            content_display_dropdown = dropdown.currentText()
            if content_display_dropdown == "自定义别名":
                # self.db_system_combo
                self.rightMouse_Menu = writeReadDataLoaderThread('save_alias', self.db_system_name, self.db_name, key, alias)
                self.rightMouse_Menu.result_toast.connect(self.sure_scene_toast)
                self.rightMouse_Menu.start()
            else:
                print(f"自定义黑名单字段: {key}")
                print(self.save_type_white_black_list)
                print(dropdown.currentText())
                self.save_blackList = dataLoaderThread('save_blackList', (self.save_type_white_black_list,
                                                                          [[key, data_id, '']],
                                                                          self.db_system_name, self.db_name))
                self.save_blackList.result_toast.connect(self.sure_scene_toast)
                self.save_blackList.start()

        btn_confirm.clicked.connect(save_custom_setting)
        option_layout.addWidget(dropdown)
        option_layout.addWidget(input1)
        option_layout.addWidget(input2)
        option_layout.addWidget(btn_confirm)

        # **第二部分**：原始数据
        original_content_label = QLabel("原始数据：")
        original_content = QTextEdit(content)
        original_content.setReadOnly(True)

        # **第三部分**：JSON 解析 + 复选框 + 别名显示
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QFormLayout()  # 逐行展示 JSON 数据

        # 用来处理 url
        if col == 3 :
            from urllib import parse
            bodyParams = parse.urlparse(content)
            changeDict = parse.parse_qs(bodyParams.query)
            if changeDict != {}:
                result = {}
                for key in changeDict.keys():
                    result[key] = changeDict.get(key)[0]
                if result == {}:
                    content_layout.addRow(QLabel("非 JSON 数据"))
                else:
                    aliases_path = f"{ROOT_DIR}/testcase/{self.db_system_combo.currentText()}/aliases.yaml"
                    if os.path.exists(aliases_path):
                        self.aliases = read_yaml(aliases_path)
                    else:
                        yaml = YAML()
                        with open(aliases_path, 'w') as f:
                            yaml.dump({}, f)
                        self.aliases = {}

                    for key, value in result.items():
                        row_layout = QHBoxLayout()
                        checkbox = QCheckBox(key)

                        alias_label = QLabel(self.aliases.get(key))
                        # alias_label = QLabel('')
                        print(key)
                        # print(self.aliases.get(key))
                        alias_label.setStyleSheet("color: gray; font-style: italic; margin-right: 10px;")

                        key_label = QLabel(f"{key}:")
                        key_label.setStyleSheet("font-weight: bold; margin-right: 10px;")

                        value_label = QLabel(str(value))
                        value_label.setWordWrap(True)
                        value_label.setStyleSheet("margin-left: 10px;")

                        row_layout.addWidget(checkbox)
                        row_layout.addWidget(alias_label)
                        row_layout.addWidget(value_label)
                        content_layout.addRow(row_layout)  # 使用表单布局更紧凑f
                        checkbox.stateChanged.connect(
                            lambda state, k=key, data_id=data_id, data_position_field=data_position_field[col]:
                            self.handle_checkbox(state, k, data_id, data_position_field))
        else:
            # 用来处理 头或者体
            try:
                data = json.loads(content)
                if isinstance(data, dict):  # JSON 处理
                    aliases_path = f"{ROOT_DIR}/testcase/{self.db_system_combo.currentText()}/aliases.yaml"
                    if os.path.exists(aliases_path):
                        self.aliases = read_yaml(aliases_path)
                    else:
                        yaml = YAML()
                        with open(aliases_path, 'w') as f:
                            yaml.dump({}, f)
                        self.aliases = {}
                    for key, value in data.items():
                        row_layout = QHBoxLayout()
                        checkbox = QCheckBox(key)

                        alias_label = QLabel(self.aliases.get(key))
                        alias_label.setStyleSheet("color: gray; font-style: italic; margin-right: 10px;")

                        key_label = QLabel(f"{key}:")
                        key_label.setStyleSheet("font-weight: bold; margin-right: 10px;")

                        value_label = QLabel(str(value))
                        value_label.setWordWrap(True)
                        value_label.setStyleSheet("margin-left: 10px;")

                        row_layout.addWidget(checkbox)
                        row_layout.addWidget(alias_label)
                        row_layout.addWidget(value_label)
                        # row_layout.addWidget(QLabel(str(value)))
                        content_layout.addRow(row_layout)  # 使用表单布局更紧凑
                        checkbox.stateChanged.connect(
                            lambda state, k=key, data_id=data_id, data_position_field=data_position_field[col]:
                                                        self.handle_checkbox(state, k, data_id, data_position_field))
                else:
                    # label = QLabel(content)
                    # label.setWordWrap(True)
                    # content_layout.addRow(label)
                    content_layout.addRow(QLabel("非 JSON 数据"))

            except json.JSONDecodeError:
                content_layout.addRow(QLabel("无法解析 JSON"))
                # pass
                # label = QLabel(content)
                # label.setWordWrap(True)
                # content_layout.addRow(label)

        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)

        # layout.addWidget(scroll_area)

        layout.addLayout(option_layout)
        layout.addWidget(original_content_label)
        layout.addWidget(original_content)
        layout.addWidget(scroll_area)

        # 按钮区域
        button_layout = QHBoxLayout()
        # 选择存储方式的下拉框
        save_type_dropdown = QComboBox()
        save_list_type = ["存储类型",
        "权限测试白名单URL", "权限测试白名单URL字段", "权限测试白名单字段","权限测试黑名单URL", "权限测试黑名单URL字段", "权限测试黑名单字段",
        "权限测试白名单URL(equal)", "权限测试白名单URL字段(equal)", "权限测试白名单字段(equal)", "权限测试黑名单URL(equal)", "权限测试黑名单URL字段(equal)", "权限测试黑名单字段(equal)",
        "sql测试白名单URL", "sql测试白名单URL字段", "sql测试白名单字段", "sql测试黑名单URL", "sql测试黑名单URL字段", "sql测试黑名单字段",
        "sql测试白名单URL(equal)", "sql测试白名单URL字段(equal)", "sql测试白名单字段(equal)","sql测试黑名单URL(equal)", "sql测试黑名单URL字段(equal)", "sql测试黑名单字段(equal)",
        "xss测试白名单URL", "xss测试白名单URL字段", "xss测试白名单字段", "xss测试黑名单URL", "xss测试黑名单URL字段", "xss测试黑名单字段",
        "xss测试白名单URL(equal)", "xss测试白名单URL字段(equal)", "xss测试白名单字段(equal)", "xss测试黑名单URL(equal)", "xss测试黑名单URL字段(equal)", "xss测试黑名单字段(equal)",
        "边界值测试白名单URL", "边界值测试白名单URL字段", "边界值测试白名单字段", "边界值测试黑名单URL", "边界值测试黑名单URL字段", "边界值测试黑名单字段",
        "边界值测试白名单URL(equal)", "边界值测试白名单URL字段(equal)", "边界值测试白名单字段(equal)", "边界值测试黑名单URL(equal)", "边界值测试黑名单URL字段(equal)", "边界值测试黑名单字段(equal)",
        "下载地址测试白名单URL", "下载地址测试黑名单URL", "下载地址测试白名单URL(equal)", "下载地址测试黑名单URL(equal)",
        "下载字段测试白名单URL", "下载字段测试白名单URL字段", "下载字段测试白名单字段", "下载字段测试黑名单URL", "下载字段测试黑名单URL字段", "下载字段测试黑名单字段",
        "下载字段测试白名单URL(equal)", "下载字段测试白名单URL字段(equal)", "下载字段测试白名单字段(equal)", "下载字段测试黑名单URL(equal)", "下载字段测试黑名单URL字段(equal)", "下载字段测试黑名单字段(equal)",
        "上传多文件测试白名单URL", "上传多文件测试黑名单URL", "上传多文件测试白名单URL(equal)", "上传多文件测试黑名单URL(equal)",
        "上传字段测试白名单URL", "上传字段测试白名单URL字段", "上传字段测试白名单字段", "上传字段测试黑名单URL", "上传字段测试黑名单URL字段", "上传字段测试黑名单字段",
        "上传字段测试白名单URL(equal)", "上传字段测试白名单URL字段(equal)", "上传字段测试白名单字段(equal)", "上传字段测试黑名单URL(equal)", "上传字段测试黑名单URL字段(equal)", "上传字段测试黑名单字段(equal)"
                                    ]
        save_type_dropdown.addItems(save_list_type)
        btn_confirm_save = QPushButton("确认")
        btn_cancel = QPushButton("取消")

        def on_save_type_dropdown_change():
            self.save_type_white_black_list = save_type_dropdown.currentText()

        save_type_dropdown.currentIndexChanged.connect(on_save_type_dropdown_change)
        # 点击保存, 调用方法
        btn_confirm_save.clicked.connect(lambda: self.confirm_selection(dialog, self.save_type_white_black_list))
        # 点击取消
        btn_cancel.clicked.connect(dialog.close)

        button_layout.addWidget(save_type_dropdown)
        button_layout.addWidget(btn_confirm_save)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()


    # 点击cell, 如果是json, 字段左侧有勾选框, 勾选勾选框, 会将勾选字段、数据库id、cell在数据库中的字段
    def handle_checkbox(self, state, key, data_id, data_position_field):
        """勾选复选框时，存储选中的 Key"""
        if state == 2:
            if key not in self.cell_field_selected_keys:
                temp = [key, data_id, data_position_field]
                self.cell_field_selected_keys.append(temp)
        elif state == 0:
            temp = [key, data_id, data_position_field]
            self.cell_field_selected_keys.remove(temp)


    # 点击cell, 如果是json, 点击确认会触发这个方法
    def confirm_selection(self, dialog, save_type):

        """ 弹出确认框，用户点击确定后调用 another_method """
        msg_box = QMessageBox()
        msg_box.setText("确定要执行操作吗？")
        msg_box.setWindowTitle("确认操作")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        # 显示弹窗并获取用户点击的按钮
        result = msg_box.exec()
        if result == QMessageBox.Ok:
            # 下拉框第一个选项就是 '存储类型'
            if save_type == '存储类型' :
                self.show_toast('请选择存储类型!!!', 2000)
            else:
                self.save_blackList = dataLoaderThread('save_blackList', (save_type, self.cell_field_selected_keys,
                                                                          self.db_system_name, self.db_name))
                self.save_blackList.result_toast.connect(self.sure_scene_toast)
                self.save_blackList.start()
                dialog.accept()
                self.cell_field_selected_keys = []









    # 更新已生成业务名的上拉框
    def update_scene_combobox(self, data):
        self.scene_combo_row1.clear()
        self.scene_combo_row1.addItems(['全部业务类型'] + data)
        self.scene_combo_row2.clear()
        self.scene_combo_row2.addItems(['全部业务类型'] + data)


    # 点击按键"上一张", 将list中的位置增减1, 这样就可以对应的展示图片
    def prev_image(self):
        """ 上一张图片 """
        if self.current_image_index > 0:
            self.current_image_index -= 1
            # 展示上一张图片
            iamge_index = self.image_list[self.current_image_index]
            self.show_image_prev_next(iamge_index)
            # 设置图片名
            self.image_name_label.setText('图片名: ' + os.path.basename(iamge_index).strip())
            image_checkbox = self.image_checkbox.isChecked()
            #
            if image_checkbox:
                self.show_toast('勿动,数据加载中!!!', 3000)
                pic_path = os.path.basename(self.image_list[self.current_image_index])
                pic_timeStamp = os.path.splitext(pic_path)[0].replace('+', ':').replace('_', '.')
                """ 获取被勾选的选项及其输入框内容 """
                # 点击查询重置勾选选项
                self.db_qTree_selected_items = []
                for item, input_field in self.items:
                    if item.checkState(0) == Qt.Checked:  # 判断是否勾选
                        self.db_qTree_selected_items.append((item.text(0), input_field.text()))
                # 将图片名作为数据库查询参数添加到里边, 无论通过界面如何修改, 都会修改为图片的名
                if len(self.db_qTree_selected_items) == 0:
                    self.db_qTree_selected_items = [('SEND_DATETIME', pic_timeStamp)]
                else:
                    noHave = True
                    for i in self.db_qTree_selected_items:
                        if i[0] == 'SEND_DATETIME':
                            i[1] = pic_timeStamp
                            noHave = False
                            break
                    if noHave:
                        self.db_qTree_selected_items.append(('SEND_DATETIME', pic_timeStamp))
                # 如果有正在运行的线程，先终止
                if hasattr(self, "db_thread") and self.db_thread.isRunning():
                    self.db_thread.terminate()  # 强制终止旧线程（如果任务重，可以用信号优雅终止）
                self.db_system_name = self.db_system_combo.currentText()  # 系统名
                self.db_name = self.db_file_combo.currentText()  # 数据库名
                # 只要点击查询按键, 重置, 当前页为1
                # self.current_page = 1
                # if self.db_num_start_value or
                self.db_thread = DatabaseQueryThread((self.db_system_name, self.db_name, self.db_filter_field,
                                            self.db_num_start_value, self.db_num_end_value, self.db_num_id_value,
                                            self.db_start_time_value, self.db_end_time_value),self.page_size,
                                             self.current_page, self.db_qTree_selected_items, self.db_search_type_value, '','','')
                self.db_thread.results_loaded.connect(self.load_database_results)
                self.db_thread.results_len.connect(self.update_pagination)
                self.db_thread.start()


    # 点击按键"下一张", 将list中的位置增加1, 这样就可以对应的展示图片
    def next_image(self):
        """ 下一张图片 """
        if self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            # 展示下一张图片
            iamge_index = self.image_list[self.current_image_index]
            self.show_image_prev_next(iamge_index)
            # 设置图片名
            self.image_name_label.setText('图片名: ' + os.path.basename(iamge_index).strip())
            image_checkbox = self.image_checkbox.isChecked()
            #
            if image_checkbox:
                self.show_toast('勿动,数据加载中!!!', 3000)
                pic_path = os.path.basename(self.image_list[self.current_image_index])
                pic_timeStamp = os.path.splitext(pic_path)[0].replace('+', ':').replace('_', '.')
                """ 获取被勾选的选项及其输入框内容 """
                # 点击查询重置勾选选项
                self.db_qTree_selected_items = []
                for item, input_field in self.items:

                    if item.checkState(0) == Qt.Checked:  # 判断是否勾选
                        self.db_qTree_selected_items.append((item.text(0), input_field.text()))
                # 将图片名作为数据库查询参数添加到里边, 无论通过界面如何修改, 都会修改为图片的名
                if len(self.db_qTree_selected_items) == 0:
                    self.db_qTree_selected_items = [('SEND_DATETIME', pic_timeStamp)]
                else:
                    noHave = True
                    for i in self.db_qTree_selected_items:
                        if i[0] == 'SEND_DATETIME':
                            i[1] = pic_timeStamp
                            noHave = False
                            break
                    if noHave:
                        self.db_qTree_selected_items.append(('SEND_DATETIME', pic_timeStamp))
                # 如果有正在运行的线程，先终止
                if hasattr(self, "db_thread") and self.db_thread.isRunning():
                    self.db_thread.terminate()  # 强制终止旧线程（如果任务重，可以用信号优雅终止）
                # self.db_system_name = self.db_system_combo.currentText()  # 系统名
                # self.db_name = self.db_file_combo.currentText()  # 数据库名
                # 只要点击查询按键, 重置, 当前页为1
                # self.current_page = 1
                self.db_thread = DatabaseQueryThread((self.db_system_name, self.db_name, self.db_filter_field,
                                self.db_num_start_value, self.db_num_end_value, self.db_num_id_value,self.db_start_time_value,
                                            self.db_end_time_value),self.page_size,self.current_page,
                                             self.db_qTree_selected_items, self.db_search_type_value, '','','')
                self.db_thread.results_loaded.connect(self.load_database_results)
                self.db_thread.results_len.connect(self.update_pagination)
                self.db_thread.start()


    # 点击"下一张"、"上一张"专用图片展示方法, 保证图片在增大、减小时不会导致self.label_image变大, 同时图片展示区可以拖动
    def show_image_prev_next(self, image_path):
        """ 显示上一张/下一张图片 """
        if not os.path.exists(image_path):
            print(f"❌ 图片文件未找到: {image_path}")
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"❌ 无法加载图片: {image_path}")
            return

        self.original_pixmap = pixmap.copy()  # 记录原始图片
        # **获取 QLabel 当前大小（防止 QLabel 变大）**
        label_size = self.image_label.size()
        # **根据 QLabel 大小缩放图片**
        scaled_pixmap = self.original_pixmap.scaled(
            label_size,  # 适应 QLabel 当前大小
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)  # 图片居中显示
        # **让 QLabel 随 QSplitter 调整**
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)  # 关键代码
        # **保持 QLabel 不能无限变大**
        self.image_label.setMinimumSize(100, 100)  # 设置 QLabel 最小值，防止过小
        # self.image_label.setMaximumSize(self.splitter.sizes()[0], self.splitter.sizes()[1])
        # **触发界面更新**
        self.image_label.update()

    # 展示图片, image_path: 图片绝对路径
    def show_image(self, image_path):
        """ 显示图片 """
        if not os.path.exists(image_path):
            print(f"❌ 图片文件未找到: {image_path}")
            return

        # pixmap = QPixmap(image_path)
        self.pixmap = QPixmap(image_path)
        self.original_image_label = self.image_label.size()
        self.current_scale = 1.0  # 还原缩放比例
        if self.pixmap.isNull():
            print(f"❌ 无法加载图片: {image_path}")
            return

        # 调整图片大小，适应 QLabel
        self.image_label.setPixmap(self.pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
        # 让图片适应 QLabel 初始大小
        # self.update_image_size(init=True)

    # 图片放大
    def zoom_in(self):
        """放大图片"""
        if self.pixmap and self.current_scale < 2.0:  # 最大3倍
            self.current_scale += 0.1
            self.update_image_size()

    # 图片缩小
    def zoom_out(self):
        """缩小图片"""
        if self.pixmap and self.current_scale > 0.2:  # 最小0.2倍
            self.current_scale -= 0.1
            self.update_image_size()

    # 更新图片
    def update_image_size(self, init=False):
        """调整图片大小，仅缩放 pixmap，不改变 QLabel 大小"""
        if self.pixmap:
            # 计算新的图片尺寸，基于原始图片尺寸
            new_size = self.original_image_label * self.current_scale
            # 确保图片按原始尺寸比例缩放
            scaled_pixmap = self.pixmap.scaled(
                new_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            # 更新 QLabel 显示图片
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setAlignment(Qt.AlignCenter)

    # 查询图片获得图片名, 将图片名作为下拉框选项导入
    def search_type_combo_selected(self):
        search_type_combo_value = self.search_type_combo.currentText()
        if search_type_combo_value == "图片查询方式":
            self.keyword_input.hide()
            self.time_start.hide()
            self.time_end.hide()
        elif search_type_combo_value == "关键字查询" :
            self.keyword_input.show()
            self.time_start.hide()
            self.time_end.hide()
        elif search_type_combo_value == "时间区间查询" :
            self.keyword_input.hide()
            self.time_start.show()
            self.time_end.show()


    # 查询图片获得图片名, 将图片名作为下拉框选项导入
    def image_system_combo_change(self):
        systemName = self.system_combo.currentText()
        if systemName != '全部测试系统' :
            self.get_system_scene_thread = get_system_scene(systemName)
            self.get_system_scene_thread.result_scene.connect(self.update_scene_combobox)
            self.get_system_scene_thread.start()


    # 查询图片获得图片名, 将图片名作为下拉框选项导入
    def search_result_combo_selected(self):
        search_result_combo_value = self.search_result_combo.currentText()
        if search_result_combo_value != "全部图片搜索结果":
            self.show_image(search_result_combo_value)
            # 设置图片名
            self.image_name_label.setText('图片名: ' + os.path.basename(search_result_combo_value).strip())

    # 查询图片获得图片名, 将图片名作为下拉框选项导入
    # def update_all_database_combo_selected(self):
    #     search_result_combo_value = self.search_result_combo.currentText()
    #     if search_result_combo_value != "全部图片搜索结果":
    #         self.show_image(search_result_combo_value)


    # 获得当前系统屏幕大小
    def get_screen_size(self):
        if platform.system() == 'Windows':
            width, height = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
            return width, height
        else:
            width, height = (1200, 720)
            return width, height
            raise NotImplementedError("Unsupported platform")


    # 查询图片获得图片名, 将图片名作为下拉框选项导入  db_system_combo
    def update_all_database_combobox(self):
        # 获得当前数据库系统下拉框选择值
        system = self.db_system_combo.currentText()
        if system != '全部测试系统' :
            # 流量捕获中图片数据库查询, 图片选项中系统下拉框
            self.db_file_combo.clear()
            db_folder = f"{ROOT_DIR}/testcase/{system}/数据库截图/数据库/"
            # 获得文件夹所有文件
            try:
                allDb = os.listdir(db_folder)
                temp = []
                for item in allDb:
                    if item.endswith('.db'):
                        temp.append(item)
                # 添加到数据库名下拉框
                self.db_file_combo.addItems(['全部数据库'] + temp)
            except Exception as e :
                print('无目录')


    # 查询数据库,查询类型下拉框, 导入下拉框选项
    def update_db_search_type_combobox(self):
        # 获得当前数据库系统下拉框选择值
        db_system_type = self.db_search_type_combo.currentText()
        if db_system_type != '数据库查询方式' :
            if db_system_type == 'ID查询' :
                self.db_num_id.show()
                self.db_num_start.hide()
                self.db_num_end.hide()
                self.db_time_start.hide()
                self.db_time_end.hide()
            elif db_system_type == 'ID区间查询' :
                self.db_num_id.hide()
                self.db_num_start.show()
                self.db_num_end.show()
                self.db_time_start.hide()
                self.db_time_end.hide()
            elif db_system_type == '时间区间查询' :
                self.db_num_id.hide()
                self.db_num_start.hide()
                self.db_num_end.hide()
                self.db_time_start.show()
                self.db_time_end.show()
        else:
            self.db_num_id.hide()
            self.db_num_start.hide()
            self.db_num_end.hide()
            self.db_time_start.hide()
            self.db_time_end.hide()


    # 图片数据库查询, 更新下拉框中的选项内容
    def update_all_combobox(self, data):
        self.global_data = data
        # 流量捕获中图片数据库查询, 图片选项中系统下拉框
        self.system_combo.clear()
        self.system_combo.addItems(['全部测试系统'] + self.global_data.get('allTestedSystem'))
        self.type_combo.clear()
        temp = []
        # 获得所有字段值, 存入list中返回
        for item in self.global_data.get('allImageType').keys():
            temp.append(item)
        self.type_combo.addItems(['全部图片类型'] +temp)
        self.search_type_combo.clear()
        self.search_type_combo.addItems(['图片查询方式', '关键字查询', '时间区间查询'])
        self.search_result_combo.clear()
        self.search_result_combo.addItems(['全部图片搜索结果'])
        # 流量捕获中图片数据库查询, 数据库选项中系统下拉框
        self.db_system_combo.clear()
        self.db_system_combo.addItems(['全部测试系统'] + self.global_data.get('allTestedSystem'))
        # 数据库中的字段下拉框
        self.db_field_combo.clear()
        for option in ['数据库字段过滤'] + self.global_data.get('allDbField'):
            # 创建 QTreeWidgetItem 作为列表项
            item = QTreeWidgetItem(self.tree_widget)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # 允许勾选
            item.setCheckState(0, Qt.Unchecked)  # 默认未选中
            item.setText(0, option)

            # 在第二列添加 QLineEdit
            input_field = QLineEdit()
            self.tree_widget.setItemWidget(item, 1, input_field)

            self.items.append((item, input_field))  # 记录 item 和 input_field
        self.db_search_type_combo.addItems(['数据库查询方式','ID查询','ID区间查询','时间区间查询'])
        # self.db_field_combo.addItems(['全部数据库字段'] + self.global_data.get('allDbField'))
        # 图片与数据库查看器, 向功能类型下拉框中添加选项
        self.exec_scene_combo.clear()
        temp_createcase_type = []
        for item in self.global_data.get('allCreateTestcase').keys():
            temp_createcase_type.append(item)
        self.exec_scene_combo.addItems(['功能类型'] + temp_createcase_type)





    def goto_page(self, page):
        self.show_toast('勿动,数据加载中!!!', 3000)
        """跳转到指定页"""
        if 1 <= page <= self.total_divid_page:
            self.current_page = page
            print('跳转到指定页', self.current_page)
            # 如果有正在运行的线程，先终止
            if hasattr(self, "db_thread") and self.db_thread.isRunning():
                self.db_thread.terminate()  # 强制终止旧线程（如果任务重，可以用信号优雅终止）
            #
            self.db_thread = DatabaseQueryThread((self.db_system_name, self.db_name, self.db_filter_field,
                                                  self.db_num_start_value, self.db_num_end_value, self.db_num_id_value,
                                                  self.db_start_time_value, self.db_end_time_value), self.page_size,
                                                 self.current_page, self.db_qTree_selected_items,
                                                 self.db_search_type_value,'','','')

            self.db_thread.results_loaded.connect(self.load_database_results)
            # self.db_thread.results_len.connect(self.update_pagination_num)
            self.db_thread.start()


    def jump_page(self):
        self.show_toast('勿动,数据加载中!!!', 3000)
        page = int(self.page_input.text())
        """跳转到指定页"""
        if 1 <= page <= self.total_divid_page:
            self.current_page = page
            print('跳转到指定页', self.current_page)
            # 如果有正在运行的线程，先终止
            if hasattr(self, "db_thread") and self.db_thread.isRunning():
                self.db_thread.terminate()  # 强制终止旧线程（如果任务重，可以用信号优雅终止）
            self.db_thread = DatabaseQueryThread((self.db_system_name, self.db_name, self.db_filter_field,
                                                  self.db_num_start_value, self.db_num_end_value, self.db_num_id_value,
                                                  self.db_start_time_value, self.db_end_time_value), self.page_size,
                                                 self.current_page, self.db_qTree_selected_items,
                                                 self.db_search_type_value,'','','')
            self.db_thread.results_loaded.connect(self.load_database_results)
            # self.db_thread.results_len.connect(self.update_pagination_num)
            self.db_thread.start()

    def checkbox_state(self): # 数据库字段过滤
        if self.image_checkbox.isChecked() == True and self.db_checkbox.isChecked() == False:
            self.image_checkbox.show()
            self.db_checkbox.hide()
            self.search_type_combo.show()
            self.search_image_btn.show()
            self.db_search_btn.hide()
            self.db_search_type_combo.show()
            self.db_field_combo.show()
        elif self.image_checkbox.isChecked() == False and self.db_checkbox.isChecked() == True:
            self.image_checkbox.hide()
            self.db_checkbox.show()
            self.search_type_combo.hide()
            self.search_image_btn.hide()
            self.db_search_btn.show()
            self.db_search_type_combo.hide()
            self.db_field_combo.hide()
        elif self.image_checkbox.isChecked() == False and self.db_checkbox.isChecked() == False:
            self.image_checkbox.show()
            self.db_checkbox.show()
            self.search_type_combo.show()
            self.search_image_btn.show()
            self.db_search_btn.show()
            self.db_search_type_combo.show()
            self.db_field_combo.show()

    def toggle_checkbox(self, item, column):
        """ 手动切换 QTreeWidgetItem 的复选框状态 """
        # if column == 0:  # 只处理第一列的复选框点击
        if item.checkState(0) == Qt.Unchecked:
            item.setCheckState(0, Qt.Checked)
        else:
            item.setCheckState(0, Qt.Unchecked)

    # 展示toast
    # message: 提示信息    duringTime: 持续时间
    def show_toast(self, message, duringTime):
        """显示吐司消息

        Args:
            message (str): 吐司消息内容
        """
        toast = QLabel(message, self)
        toast.setStyleSheet(
            "background-color: black; color: white; padding: 5px; border-radius: 100px;")
        toast.setAlignment(Qt.AlignCenter)
        toast.setWindowFlags(Qt.ToolTip)
        toast.setGeometry(self.width() // 2 - 100, self.height() // 2 - 20, 400, 80)
        toast.show()

        # 设置自动关闭
        QTimer.singleShot(duringTime, toast.close)  # 2秒后自动关闭

    # 向上弹出下拉框
    # def showPopup(self):
    #     """重写 showPopup 事件，让 QComboBox 向上展开"""
    #     combo_rect = self.scene_combo.geometry()  # 获取 QComboBox 位置
    #     popup_height = self.scene_combo.view().sizeHint().height()  # 计算弹出高度
    #
    #     # 让下拉框在 QComboBox 的上方显示
    #     self.scene_combo.view().move(combo_rect.left(), combo_rect.top() - popup_height)
    #     super().showPopup()



if __name__ == "__main__":
    app = QApplication([])
    window = ImageDatabaseViewer()
    window.show()
    app.exec()




