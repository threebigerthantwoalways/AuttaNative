import json,traceback
from ruamel.yaml import YAML
from collections import OrderedDict
from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QDialog, QMessageBox, QScrollArea, QWidget, QComboBox
)
from PySide6.QtCore import Qt,QTimer
from PySide6 import QtCore
from ui.woker import Worker_get_all_system, Worker_shell
from config import *
from util.yaml_util import read_yaml

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



class ParamEditor(QDialog):
    def __init__(self, system_value, yaml_path=None):
        super().__init__()
        self.yaml_data = OrderedDict()  # 使用有序字典保持顺序  system_value
        self.input_widgets = {}  # 存储字段和其对应的输入框信息
        self.globalConfig = read_yaml(ROOT_DIR + '/config/globalConfig.yaml')
        self.systemDataConfig = None
        self.currentSystemName = system_value
        self.currentSettingName = None
        self.loading_in_progress = False
        self.changeSystemName = False # 记录下拉框系统是否改变,改变重新加载对应系统yaml, 默认没变
        self.init_ui()

        # if yaml_path:
        self.load_yaml()

    def init_ui(self):
        # self.setWindowTitle("YAML 图形编辑器")
        # self.setFixedSize(800, 600)
        self.setWindowTitle("参数编辑")
        self.setFixedSize(900, 700)
        # 主布局
        main_layout = QVBoxLayout()


        # 第一行：下拉框 + 输入框
        first_row_layout = QHBoxLayout()
        first_row_layout.setAlignment(QtCore.Qt.AlignLeft)
        first_row_label = QLabel("参数配置:")
        self.combo_box_system = QComboBox()
        self.combo_box_system.setFixedWidth(400)
        self.combo_box_system.setFixedHeight(40)
        self.combo_box_data_arrange_analysis = QComboBox()
        self.combo_box_data_arrange_analysis.setFixedWidth(400)
        self.combo_box_data_arrange_analysis.setFixedHeight(40)

        # 点击下拉框后, 调用对应方法, 有些选项隐藏或者显示
        self.combo_box_system.currentIndexChanged.connect(self.combo_box_system_changed)
        self.combo_box_data_arrange_analysis.currentIndexChanged.connect(self.combo_box_data_arrange_analysis_changed)

        first_row_layout.addWidget(first_row_label)
        first_row_layout.addWidget(self.combo_box_system)
        first_row_layout.addWidget(self.combo_box_data_arrange_analysis)

        # 可滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # first_row_layout.setAlignment(QtCore.Qt.At)
        self.editor_container = QWidget()
        self.editor_layout = QVBoxLayout()
        self.editor_layout.setAlignment(Qt.AlignTop)
        self.editor_container.setLayout(self.editor_layout)
        scroll_area.setWidget(self.editor_container)

        # 保存和关闭按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        close_button = QPushButton("关闭")
        save_button.clicked.connect(self.save_yaml)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)

        # 主布局
        main_layout.addLayout(first_row_layout)
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # 新建工厂
        self.get_all_system = Worker_get_all_system()
        self.get_all_system.finished.connect(self.update_combobox)
        self.get_all_system.start()


    def load_yaml(self):
        """加载 YAML 文件"""
        if self.loading_in_progress:  # 如果已经在加载中，直接返回，防止重复调用
            return
        self.loading_in_progress = True  # 设置加载标志
        """加载 YAML 文件"""
        try:
            if self.currentSystemName  and self.currentSettingName :
                field = self.globalConfig['allTestedSetting'].get(f'{self.currentSettingName}')
                if not self.systemDataConfig:
                    self.systemDataConfig = read_yaml(ROOT_DIR + f'/config/{self.currentSystemName}dataConfig.yaml')
                if self.changeSystemName :
                    self.systemDataConfig = read_yaml(ROOT_DIR + f'/config/{self.currentSystemName}dataConfig.yaml')
                    self.changeSystemName = False
                value = self.systemDataConfig[0].get(field)
                self.yaml_data = {f'{self.currentSettingName}': value}
                self.clear_layout(self.editor_layout)
                self.generate_editor(self.yaml_data, self.editor_layout)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载 YAML 文件失败: {e}")
        finally:
            self.loading_in_progress = False  # 加载完成，重置标志位

    def save_yaml(self):
        """保存 YAML 文件"""
        try:
            updated_data = self.collect_data()
            yaml = YAML()
            yaml.default_flow_style = False
            yaml.allow_unicode = True
            yaml.explicit_start = False
            yaml.explicit_end = False

            # 更新到 systemDataConfig
            aaa = self.currentSettingName
            field = self.globalConfig['allTestedSetting'].get(aaa)
            self.systemDataConfig[0][field] = updated_data.get(aaa)
            # 备份dataConfig
            with open(ROOT_DIR + f'/config/{self.currentSystemName}dataConfig.yaml', "w", encoding="utf-8") as f:
                yaml.dump(self.systemDataConfig, f)
            # 写入文件
            with open(ROOT_DIR + f'/config/{self.currentSystemName}dataConfig.yaml', "w", encoding="utf-8") as f:
                yaml.dump(self.systemDataConfig, f)

            QMessageBox.information(self, "成功", "文件保存成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存 YAML 文件失败: {e}")

    def generate_editor(self, data, parent_layout):
        """根据 YAML 数据生成编辑界面"""
        for key, value in data.items():
            if isinstance(value, str) or isinstance(value, int):
                self.create_string_editor(key, value, parent_layout)
            elif isinstance(value, list):
                self.create_list_editor(key, value, parent_layout)
            elif isinstance(value, dict):
                # 确保即使是空字典，也能正确创建控件
                self.create_dict_editor(key, value if value else {}, parent_layout)

    def create_string_editor(self, key, value, layout):
        """生成字符串字段的编辑器"""
        row_layout = QHBoxLayout()
        key_label = QLabel(f"{key}:")
        value_input = QLineEdit()
        value_input.setText(str(value))
        row_layout.addWidget(key_label)
        row_layout.addWidget(value_input)
        layout.addLayout(row_layout)

        # 存储输入框引用
        self.input_widgets[key] = {"type": "str", "widget": value_input}

    def create_list_editor(self, key, value, layout):
        """生成列表字段的编辑器，支持添加字符串和字典项"""
        list_label = QLabel(f"{key}:")
        layout.addWidget(list_label)

        sub_layout = QVBoxLayout()
        sub_layout.setSpacing(10)
        layout.addLayout(sub_layout)

        self.input_widgets[key] = {"type": "list", "widgets": []}

        for item in value:
            self.add_list_item(key, item, sub_layout)

        # 添加列表项按钮（添加字符串）
        add_str_button = QPushButton("+ 添加列表项")
        add_str_button.clicked.connect(lambda: self.add_list_item(key, "", sub_layout))
        layout.addWidget(add_str_button)

        # 添加字典项按钮
        add_dict_button = QPushButton("+ 添加字典项")
        add_dict_button.clicked.connect(lambda: self.add_dict_item_to_list(key, sub_layout))
        layout.addWidget(add_dict_button)

    def add_list_item(self, key, value, layout):
        """为列表字段添加项：字符串 或 字典形式（左右两个输入框）"""
        row_layout = QHBoxLayout()

        # 如果是 dict，则展示为左右两个输入框
        if isinstance(value, dict) and len(value) == 1:
            k, v = list(value.items())[0]
            key_input = QLineEdit()
            key_input.setText(str(k))
            value_input = QLineEdit()
            value_input.setText(str(v))
            remove_button = QPushButton("-")

            row_layout.addWidget(key_input)
            row_layout.addWidget(value_input)
            row_layout.addWidget(remove_button)
            layout.addLayout(row_layout)

            def get_combined():
                return {key_input.text(): value_input.text()}

            self.input_widgets[key]["widgets"].append(get_combined)

            def remove():
                key_input.deleteLater()
                value_input.deleteLater()
                remove_button.deleteLater()
                layout.removeItem(row_layout)
                self.input_widgets[key]["widgets"].remove(get_combined)

            remove_button.clicked.connect(remove)

        else:
            # 普通字符串项
            item_input = QLineEdit()
            item_input.setText(str(value))
            remove_button = QPushButton("-")

            row_layout.addWidget(item_input)
            row_layout.addWidget(remove_button)
            layout.addLayout(row_layout)

            self.input_widgets[key]["widgets"].append(item_input)

            def remove():
                item_input.deleteLater()
                remove_button.deleteLater()
                layout.removeItem(row_layout)
                self.input_widgets[key]["widgets"].remove(item_input)

            remove_button.clicked.connect(remove)

    def add_dict_item_to_list(self, key, layout):
        """向列表添加字典项的左右输入框"""
        row_layout = QHBoxLayout()
        key_input = QLineEdit()
        value_input = QLineEdit()
        remove_button = QPushButton("-")

        row_layout.addWidget(key_input)
        row_layout.addWidget(value_input)
        row_layout.addWidget(remove_button)
        layout.addLayout(row_layout)

        # 存储为 dict 格式，组合为 json
        def get_combined():
            return json.dumps({key_input.text(): value_input.text()}, ensure_ascii=False)

        self.input_widgets[key]["widgets"].append(get_combined)

        def remove():
            key_input.deleteLater()
            value_input.deleteLater()
            remove_button.deleteLater()
            layout.removeItem(row_layout)
            self.input_widgets[key]["widgets"].remove(get_combined)

        remove_button.clicked.connect(remove)


    def create_dict_editor(self, key, value, layout):
        """生成字典字段的编辑器"""
        dict_label = QLabel(f"{key}:")
        layout.addWidget(dict_label)

        sub_layout = QVBoxLayout()
        layout.addLayout(sub_layout)

        self.input_widgets[key] = {"type": "dict", "widgets": {}}

        for k, v in value.items():
            self.add_dict_item(key, k, v, sub_layout)

        add_button = QPushButton("+ 添加字典项")
        add_button.clicked.connect(lambda: self.add_dict_item(key, "", "", sub_layout))
        layout.addWidget(add_button)


    def add_dict_item(self, key, sub_key, sub_value, layout):
        """为字典字段添加键值输入"""
        row_layout = QHBoxLayout()
        key_input = QLineEdit()
        key_input.setText(sub_key)
        value_input = QLineEdit()
        value_input.setText(str(sub_value))
        remove_button = QPushButton("-")

        row_layout.addWidget(key_input)
        row_layout.addWidget(value_input)
        row_layout.addWidget(remove_button)
        layout.addLayout(row_layout)

        self.input_widgets[key]["widgets"][key_input] = value_input

        def remove():
            key_input.deleteLater()
            value_input.deleteLater()
            remove_button.deleteLater()
            layout.removeItem(row_layout)
            del self.input_widgets[key]["widgets"][key_input]

        remove_button.clicked.connect(remove)



    def collect_data(self):
        """从输入控件收集数据，生成字典结构"""
        result = OrderedDict()
        import ast
        for key, item in self.input_widgets.items():
            if item["type"] == "str":
                try:
                    result[key] = ast.literal_eval(item["widget"].text())
                except:
                    result[key] = item["widget"].text()
                # result[key] = item["widget"].text()
            elif item["type"] == "list":
                items = []
                for widget in item["widgets"]:
                    if callable(widget):
                        # widget 是 lambda 返回 dict 的函数
                        try:
                            data = widget()
                            if isinstance(data, dict):
                                # 尝试解析字典中的值（例如 field2: '[1,2]' -> [1,2]）
                                parsed = {}
                                for k in data.keys():
                                    try:
                                        parsed[k] = ast.literal_eval(data.get(k))
                                    except:
                                        parsed[k] = data.get(k)
                                items.append(parsed)
                            else:
                                data = json.loads(widget())
                                if isinstance(data, dict):
                                    # 尝试解析字典中的值（例如 field2: '[1,2]' -> [1,2]）
                                    parsed = {}
                                    for k in data.keys():
                                        try:
                                            parsed[k] = ast.literal_eval(data.get(k))
                                        except:
                                            parsed[k] = data.get(k)
                                    items.append(parsed)
                                else:
                                    items.append(data)
                        except Exception as e:
                            print("Error in dict-list item:", e)
                            items.append({})
                    else:
                        text = widget.text()
                        try:
                            value = ast.literal_eval(text)
                        except:
                            value = text
                        items.append(value)
                result[key] = items
            elif item["type"] == "dict":
                d = {}
                for k_widget, v_widget in item["widgets"].items():
                    key_text = k_widget.text()
                    val_text = v_widget.text()
                    try:
                        value = ast.literal_eval(val_text)
                    except:
                        value = val_text
                    d[key_text] = value
                result[key] = d
        return result

    def _json(self, myjson):
        try:
            json.loads(myjson)
        except ValueError as e:
            return False
        return True


    def update_combobox(self, data):
        # 流量捕获, 系统下拉框
        self.combo_box_system.addItems([init_system_first_dropdown_option] + data.get('allTestedSystem'))
        temp = []
        # 获得所有字段值, 存入list中返回
        for item in data.get('allTestedSetting').keys():
            temp.append(item)
        # 接口自动化, 设置参数下拉框
        self.combo_box_data_arrange_analysis.addItems([init_setting_first_dropdown_option] + temp)


    # 系统下拉框选项改变触发该方法
    def combo_box_system_changed(self):
        temp_system = self.combo_box_system.currentText()
        if temp_system and temp_system != init_system_first_dropdown_option:
            self.currentSystemName = temp_system
            self.changeSystemName = True
            if self.currentSettingName and self.currentSettingName != init_setting_first_dropdown_option:
                if not self.loading_in_progress:
                    self.load_yaml()  # 调用加载方法

    def combo_box_data_arrange_analysis_changed(self):
        temp_setting = self.combo_box_data_arrange_analysis.currentText()
        if temp_setting and temp_setting != init_setting_first_dropdown_option:
            self.currentSettingName = temp_setting
            if self.currentSystemName and self.currentSystemName != init_system_first_dropdown_option:
                if not self.loading_in_progress:
                    self.load_yaml()  # 调用加载方法

    def clear_layout(self, layout):
        """递归清空布局中的所有子控件和子布局"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():  # 如果是控件，删除控件
                    widget = item.widget()
                    widget.deleteLater()
                    # 安全移除控件引用
                    self.remove_widget_from_dict(widget)
                elif item.layout():  # 如果是布局，递归清空子布局
                    self.clear_layout(item.layout())

    def remove_widget_from_dict(self, widget):
        """从 input_widgets 字典中移除控件引用"""
        keys_to_remove = []  # 缓存需要移除的键
        for key, config in self.input_widgets.items():
            if config["type"] == "str" and config["widget"] is widget:
                keys_to_remove.append(key)
            elif config["type"] == "list":
                if widget in config.get("widgets", []):
                    config["widgets"].remove(widget)
            elif config["type"] == "dict":
                # 确保安全移除
                for k, v in list(config["widgets"].items()):
                    if k == widget or v == widget:
                        del config["widgets"][k]

        # 在遍历后移除键，避免遍历过程中修改字典
        for key in keys_to_remove:
            del self.input_widgets[key]




