import os,sys,platform,win32api,re,traceback
from ui.paramEditorWindow import ParamEditor
from multiprocessing import Process, Pipe
sys.stdout.reconfigure(encoding='utf-8')
# 当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上级目录
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import QComboBox, QLabel, QTextEdit, QCheckBox, \
    QVBoxLayout, QSizePolicy, QGroupBox, QMessageBox, QLineEdit, QScrollArea, QWidget, QHBoxLayout, QPushButton, \
    QDialog, QFormLayout, QDialogButtonBox
from ui.factory import ConcreteFactory
from ui.woker import *
import multiprocessing, socket
import json
from PySide6.QtGui import QAction





class ProxyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("代理设置")

        layout = QFormLayout()

        # 第一行: 代理地址 (下拉框)
        self.proxy_label = QLabel("代理地址:")
        self.proxy_combobox = QComboBox()
        self.proxy_combobox.addItems(self.get_local_ips())
        self.proxy_combobox.currentIndexChanged.connect(self.toggle_custom_proxy)

        # 第二行: 自定义代理地址 (输入框)
        self.custom_proxy_label = QLabel("自定义代理地址:")
        self.custom_proxy_input = QLineEdit()

        # 第三行: 端口 (输入框)
        self.port_label = QLabel("端口:")
        self.port_input = QLineEdit()

        # 按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.confirm_before_accept)
        self.button_box.rejected.connect(self.reject)

        # 添加到布局
        layout.addRow(self.proxy_label, self.proxy_combobox)
        layout.addRow(self.custom_proxy_label, self.custom_proxy_input)
        layout.addRow(self.port_label, self.port_input)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        self.toggle_custom_proxy()  # 初始化隐藏或显示自定义地址

    def toggle_custom_proxy(self):
        """根据选中的代理类型显示或隐藏自定义输入框"""
        if self.proxy_combobox.currentText() == "自定义代理地址":
            self.custom_proxy_label.show()
            self.custom_proxy_input.show()
        else:
            self.custom_proxy_label.hide()
            self.custom_proxy_input.hide()
            self.custom_proxy_input.setText("")

    def confirm_before_accept(self):
        """弹出确认框，用户确认后才执行提交"""
        reply = QMessageBox.question(
            self, "确认操作", "确定要提交代理设置吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.accept()  # 继续执行提交操作
        else:
            pass  # 用户点击“否”，窗口保持打开

    def get_inputs(self):
        return {
            "proxy": self.proxy_combobox.currentText(),
            "customizeProxy": self.custom_proxy_input.text(),
            "port": self.port_input.text(),
        }

    def get_local_ips(self):
        """获取本机所有IP地址（包括回环地址127.0.0.1）"""
        ip_list = ["自定义代理地址", "127.0.0.1"]
        hostname = socket.gethostname()
        try:
            # 获取本机IP地址
            ip_list.extend(socket.gethostbyname_ex(hostname)[2])
        except socket.gaierror:
            pass
        return list(set(ip_list))  # 去重



class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入信息")

        layout = QFormLayout()

        # 创建四个输入框
        self.system_name = QLineEdit()
        self.database_name = QLineEdit()
        self.filter_host = QLineEdit()
        self.load_mode = QLineEdit("loadAll")  # 默认值

        # 添加到布局中
        layout.addRow("新增系统名:", self.system_name)
        # layout.addRow("新增数据库名:", self.database_name)
        layout.addRow("过滤请求地址的host:", self.filter_host)
        # layout.addRow("数据库加载方式(默认loadAll):", self.load_mode)

        # 创建按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.confirm_before_accept)
        # self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def confirm_before_accept(self):
        """弹出确认框，用户确认后才关闭窗口"""
        reply = QMessageBox.question(
            self, "确认操作", "确定要提交输入信息吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.accept()  # 继续执行关闭窗口操作
        else:
            pass  # 用户点击“否”，不关闭窗口

    def get_inputs(self):
        return {
            "system_name": self.system_name.text(),
            # "database_name": self.database_name.text(),
            "url_host": self.filter_host.text(),
            "loaddatabase_type": self.load_mode.text()
        }


class MainWindow(QtWidgets.QMainWindow):
    action_result_signal = Signal(str)

    def __init__(self, token=None):
        super().__init__()
        self.token = token
        self.initUI()
        self.action_result_signal.connect(self.show_message)
        self.worker_shell_capture = None  # 初始化时设置为空
        self.worker_shell_data_arrange_analysis = None  # 初始化时设置为空
        self.queue = multiprocessing.Queue()  # 队列，用于子进程通信
        self.addon_thread_queue = multiprocessing.Queue()  # 插件和新启动的监听线程,用来存储两者交互使用的报文
        self.pyside_addon_queue = multiprocessing.Queue()  # pyside6和插件, 用来存储两者交互使用的报文
        # 启动redis线程,线程里会启动一个单独的进程
        self.redis_thread = None
        self.redis_port = None
        # 单独的展示拦截抓包功能, 使用的启动redist线程和对应的redis端口   redisListenerThread
        self.intercept_redis_thread = None
        self.intercept_redis_port = None
        # pyside6 启动监听 redis 写入的消息
        self.intercept_redis_listener_thread = None
        # 单独启动截图进程
        self.listener_image_process = None
        # 单独启动抓包线程
        self.traffic_thread = None
        # 既截图又抓包, 启动的截图的进程
        self.listener_iamge_image_traffic_process = None
        # 既截图又抓包, 启动的抓包的进程
        self.listener_traffic_image_traffic_process = None
        # 抓包功能,将报文显示在UI界面
        self.capture_traffic_thread = None
        # 安装证书启动线程
        self.install_certificate_thread = None
        # 抓包功能,将报文显示在UI界面, 监听写入到queue中的报文信息, 如果消息队列有报文, 会更新到界面中。拦截抓包功能使用,
        # 插件写入到队列中, pyside6会取这个线程监听得到的数据
        self.listener_capture_queue_packets_thread = None
        # 监听消息队列中的报文, False为关闭监听, True为开启监听
        # self.listen_for_packets_running = False
        # 请求还是响应
        self.capture_request_response_type = None
        # 抓包的时候有报文的唯一id, flow_id
        self.capture_flow_id = None
        # 为了针对 开启自动化测试, 方便关掉 开启自动化测试 而设计的, 不知道有没有对其他功能有影响
        self.worker_shell = None

    def initUI(self):
        self.setWindowTitle("Main Window")
        screenSize = self.get_screen_size()
        # self.setGeometry(100, 100, 1200, 720)  # 占屏幕约60%
        self.setGeometry(100, 50, int(screenSize[0]*0.7), int(screenSize[1]*0.7))  # 占屏幕约60%
        self.setStyleSheet("""
            QMainWindow { background-color: #f8f9fa; }
            QPushButton {
                background-color: #007BFF; color: white; font-size: 14px;
                padding: 8px 15px; border-radius: 5px;
            }
            QPushButton:hover { background-color: #0056b3; }
            QStatusBar { font-size: 14px; color: #333; }
        """)

        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)

        # 添加顶部按钮触发下拉框的效果
        dropdown_button = QtWidgets.QPushButton("选项")
        dropdown_menu = QtWidgets.QMenu()
        dropdown_menu.addAction("新建系统", self.option1_method)
        dropdown_menu.addAction("编辑代理", self.option2_method)
        dropdown_menu.addAction("Option 3", self.option3_method)
        dropdown_button.setMenu(dropdown_menu)
        # 绑定点击事件，使点击时弹出菜单
        dropdown_button.clicked.connect(
            lambda: dropdown_menu.popup(dropdown_button.mapToGlobal(QtCore.QPoint(0, dropdown_button.height()))))
        main_layout.addWidget(dropdown_button, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.tab_widget = QtWidgets.QTabWidget()

        # **窗口右上角按钮**
        pin_action = QAction("📌", self)
        pin_action.triggered.connect(self.toggle_pin)
        self.menuBar().addAction(pin_action)

        # 新建工厂
        self.get_all_system = Worker_get_all_system()
        self.get_all_system.finished.connect(self.update_all_combobox)
        self.get_all_system.start()
        # 显示加载中, 不加不行, 直接卡掉了
        self.label = QLabel('加载中...')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.show()  # 显示加载提示

        # 流量捕获布局
        capture = QtWidgets.QWidget()
        capture_layout = QtWidgets.QVBoxLayout(capture)
        # Add a spacer at the top to push widgets up
        capture_layout.setContentsMargins(10, 10, 10, 10)  # 控制顶部、左右、底部边距
        capture_layout.setSpacing(15)  # 控件之间的间距
        # 新建工厂
        self.factory = ConcreteFactory()
        # 下拉框, "全部测试系统"
        capture_row1_layout = QtWidgets.QHBoxLayout()
        capture_row1_layout.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        self.capture_dropdown = QtWidgets.QComboBox()

        # 点击下拉框后, 调用对应方法, 有些选项隐藏或者显示
        self.capture_dropdown.setFixedWidth(200)
        self.capture_dropdown.setFixedHeight(40)

        capture_row1_layout.addWidget(self.capture_dropdown)
        capture_layout.addLayout(capture_row1_layout, stretch=1)

        # 拦截和放过按钮
        self.capture_image_button = QtWidgets.QPushButton("自动化截图")
        self.capture_image_button.setFixedWidth(200)
        self.capture_image_button.setFixedHeight(40)
        self.capture_image_button.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_capture_image
        ))
        self.capture_traffic_button = QtWidgets.QPushButton("捕获流量存入数据库")
        self.capture_traffic_button.setFixedWidth(200)
        self.capture_traffic_button.setFixedHeight(40)
        self.capture_traffic_button.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_traffic
        ))
        self.capture_image_traffic_button = QtWidgets.QPushButton("自动化截图捕获流量")
        self.capture_image_traffic_button.setFixedWidth(200)
        self.capture_image_traffic_button.setFixedHeight(40)
        self.capture_image_traffic_button.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_capture_image_traffic
        ))
        self.capture_stop_button = QtWidgets.QPushButton("关闭已启动功能")
        self.capture_stop_button.setFixedWidth(200)
        self.capture_stop_button.setFixedHeight(40)
        # self.capture_stop_button.setEnabled(False)  # 初始状态为禁用
        self.capture_stop_button.hide()  # 初始状态为禁用
        self.capture_stop_button.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            # confirm_callback=self.run_shell_command_stop
            confirm_callback=self.run_shell_command_stop_traffic_image
        ))
        self.capture_set_proxy_button = QtWidgets.QPushButton("快捷设置代理端口")
        self.capture_set_proxy_button.setFixedWidth(200)
        self.capture_set_proxy_button.setFixedHeight(40)
        self.capture_set_proxy_button.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_set_proxy
        ))

        self.capture_unset_proxy_button = QtWidgets.QPushButton("关闭代理端口")
        self.capture_unset_proxy_button.setFixedWidth(200)
        self.capture_unset_proxy_button.setFixedHeight(40)
        self.capture_unset_proxy_button.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_unset_proxy
        ))
        capture_buttons_layout = QtWidgets.QHBoxLayout()
        capture_buttons_layout.addWidget(self.capture_image_button)
        capture_buttons_layout.addWidget(self.capture_traffic_button)
        capture_buttons_layout.addWidget(self.capture_image_traffic_button)
        capture_buttons_layout.addWidget(self.capture_stop_button)
        capture_buttons_layout.addWidget(self.capture_set_proxy_button)
        capture_buttons_layout.addWidget(self.capture_unset_proxy_button)
        capture_buttons_layout.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        capture_layout.addLayout(capture_buttons_layout)

        # 添加报文显示区域
        self.capture_message_display = QtWidgets.QTextEdit()
        self.capture_message_display.setReadOnly(False)
        capture_layout.addWidget(self.capture_message_display)
        self.tab_widget.addTab(capture, "流量捕获")

        # "请求响应拦截" 布局
        sheet_capture_single = QtWidgets.QWidget()
        capture_single_layout = QtWidgets.QVBoxLayout(sheet_capture_single)
        # 当前报文信息显示
        self.current_label = QLabel()
        self.current_label.setStyleSheet("font-size: 16px;")
        # 拦截和放过按钮
        self.intercept_button = QtWidgets.QPushButton("开始拦截")
        self.intercept_button.setFixedWidth(200)
        self.intercept_button.setFixedHeight(40)
        self.intercept_button.clicked.connect(self.toggle_intercept)

        self.allow_button = QtWidgets.QPushButton("发送拦截报文")
        self.allow_button.setFixedWidth(200)
        self.allow_button.setFixedHeight(40)
        self.allow_button.clicked.connect(self.pass_packet)

        self.intercept_set_proxy_button = QtWidgets.QPushButton("快捷设置代理端口")
        self.intercept_set_proxy_button.setFixedWidth(200)
        self.intercept_set_proxy_button.setFixedHeight(40)
        self.intercept_set_proxy_button.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_set_proxy
        ))

        self.intercept_unset_proxy_button = QtWidgets.QPushButton("关闭代理端口")
        self.intercept_unset_proxy_button.setFixedWidth(200)
        self.intercept_unset_proxy_button.setFixedHeight(40)
        self.intercept_unset_proxy_button.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_unset_proxy
        ))

        # 预先设置代理, 目的为了安装mitmproxy证书
        self.intercept_install_certificate_button = QtWidgets.QPushButton("请设置代理安装证书")
        self.intercept_install_certificate_button.setFixedWidth(200)
        self.intercept_install_certificate_button.setFixedHeight(40)
        self.intercept_install_certificate_button.clicked.connect(self.install_certificate)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(self.intercept_button)
        buttons_layout.addWidget(self.allow_button)
        buttons_layout.addWidget(self.intercept_set_proxy_button)
        buttons_layout.addWidget(self.intercept_unset_proxy_button)
        buttons_layout.addWidget(self.intercept_install_certificate_button)
        buttons_layout.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        capture_single_layout.addWidget(self.current_label)
        capture_single_layout.addLayout(buttons_layout)

        # 添加报文显示区域
        self.message_display = QtWidgets.QTextEdit()
        self.message_display.setReadOnly(False)
        # 设置 QTextEdit 的边框和自动换行
        self.message_display.setStyleSheet("border: 1px solid gray;")  # 确保右侧有边框
        self.message_display.setMaximumWidth(int(screenSize[0]))  # 限制最大宽度
        # 从mitmproxy插件存入消息队列中, 发送给pyside6中的所有消息, 默认为None, 在pyside6端, 存储到一个变量中, 方便发送给
        # mitmproxy插件, 需要携带原始数据使用
        # self.mitm_packet = None
        self.current_flow = None  # 保存当前的 flow 对象 , 这样帮助插件脚本识别请求响应, 对应的返回给服务端或者客户端
        self.flowId_url = {}  # 保存flowId和url关系, 因为flowId是请求响应报文唯一标识, 这样可以通过flowId找到响应报文的url
        capture_single_layout.addWidget(self.message_display)

        self.tab_widget.addTab(sheet_capture_single, "请求响应拦截")

        # "接口自动化"布局
        sheet1 = QtWidgets.QWidget()
        sheet1_layout = QtWidgets.QVBoxLayout(sheet1)
        # Add a spacer at the top to push widgets up
        sheet1_layout.setContentsMargins(10, 10, 10, 10)  # 控制顶部、左右、底部边距
        sheet1_layout.setSpacing(15)  # 控件之间的间距

        # 第二行：下拉框
        row2_layout = QtWidgets.QHBoxLayout()
        row2_layout.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        # 下拉框, "全部测试系统"
        self.dropdown = QtWidgets.QComboBox()

        # 点击下拉框后, 调用对应方法, 有些选项隐藏或者显示
        self.dropdown.currentIndexChanged.connect( self.on_dropdown_selected)
        self.dropdown.setFixedWidth(200)
        self.dropdown.setFixedHeight(40)

        self.modify_button = QtWidgets.QPushButton("配置参数")
        self.modify_button.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_modify_field_value
        ))
        self.modify_button.setFixedWidth(150)
        self.modify_button.setFixedHeight(40)

        row2_layout.addWidget(self.dropdown)
        row2_layout.addWidget(self.modify_button)
        sheet1_layout.addLayout(row2_layout, stretch=1)

        # 第四行: 下拉框、按键, 选择测试类型。调用工厂, 获得"生成接口"对应的对象, 更新下拉框内容, 初始化隐藏下拉框
        # 按键, "开始生成测试用例", 初始化隐藏
        row4_layout = QtWidgets.QHBoxLayout()
        row4_layout.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        self.dropdown_scenario = QtWidgets.QComboBox()
        # 点击下拉框后, 调用对应方法, 有些选项隐藏或者显示
        self.dropdown_scenario.currentIndexChanged.connect(self.on_dropdown_selected_scenario)
        self.dropdown_scenario.setFixedWidth(200)
        self.dropdown_scenario.setFixedHeight(40)
        self.dropdown_scenario.hide()
        # 测试用例生成类型
        self.dropdown_run_create_testcase = QtWidgets.QComboBox()
        # 点击下拉框后, 调用对应方法, 有些选项隐藏或者显示
        self.dropdown_run_create_testcase.currentIndexChanged.connect(self.on_dropdown_selected)
        self.dropdown_run_create_testcase.setFixedWidth(275)
        self.dropdown_run_create_testcase.setFixedHeight(40)
        self.dropdown_run_create_testcase.hide()
        self.run_create_testcase_button = QtWidgets.QPushButton("开始")
        self.run_create_testcase_button.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_create_testcase
        ))
        self.run_create_testcase_button.setFixedWidth(150)
        self.run_create_testcase_button.setFixedHeight(40)
        self.run_create_testcase_button.hide()
        self.max_lines = 10000  # 限制最大行数
        # 第四行: 按键, 选择测试类型。调用工厂, 获得"自动化测试类型"对应的对象, 更新下拉框内容, 初始化隐藏下拉框
        # 按键, "开始自动化测试", 初始化隐藏
        self.dropdown_run_test = QtWidgets.QComboBox()

        # 点击下拉框后, 调用对应方法, 有些选项隐藏或者显示
        self.dropdown_run_test.currentIndexChanged.connect(self.on_dropdown_selected)
        self.dropdown_run_test.setFixedWidth(275)
        self.dropdown_run_test.setFixedHeight(40)
        self.dropdown_run_test.hide()
        self.run_test_button = QtWidgets.QPushButton("开始自动化测试")
        self.run_test_button.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_run_testcase
        ))
        self.run_test_button.setFixedWidth(150)
        self.run_test_button.setFixedHeight(40)
        self.run_test_button.hide()

        self.run_test_button_closed = QtWidgets.QPushButton("关闭自动化测试")
        self.run_test_button_closed.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="关闭进程至少60秒请不要操作!!!",
            confirm_callback=self.run_shell_command_run_testcase_closed
        ))
        self.run_test_button_closed.setFixedWidth(150)
        self.run_test_button_closed.setFixedHeight(40)
        self.run_test_button_closed.hide()

        self.run_open_report_button = QtWidgets.QPushButton("打开测试报告所在文件夹")
        # self.run_open_report_button.clicked.connect(self.run_open_directory_report)
        self.run_open_report_button.setFixedWidth(180)
        self.run_open_report_button.setFixedHeight(40)
        self.run_open_report_button.hide()
        # 将四行控件存入layout, 将layout存入sheet1
        row4_layout.addWidget(self.dropdown_scenario)
        row4_layout.addWidget(self.dropdown_run_create_testcase)
        row4_layout.addWidget(self.run_create_testcase_button)
        sheet1_layout.addLayout(row4_layout, stretch=1)

        row5_layout = QtWidgets.QHBoxLayout()
        row5_layout.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        # B 下拉框容器 (隐藏时占位)
        self.search_testCaseName_container = QGroupBox("选择用例")
        self.search_testCaseName_layout = QVBoxLayout()
        # B 搜索框
        self.search_testCaseName_box = QLineEdit()
        self.search_testCaseName_box.setPlaceholderText("搜索用例...")
        self.search_testCaseName_box.textChanged.connect(self.filter_text_options)
        self.search_testCaseName_layout.addWidget(self.search_testCaseName_box)
        # 全选和全不选勾选框
        self.select_controls_layout = QHBoxLayout()
        self.select_controls_layout.setAlignment(QtCore.Qt.AlignLeft)  # 靠左对齐
        self.select_all_checkbox = QCheckBox("全选")
        self.select_all_checkbox.stateChanged.connect(self.select_all_options)

        self.select_controls_layout.addWidget(self.select_all_checkbox)
        self.search_testCaseName_layout.addLayout(self.select_controls_layout)
        # B 多选框区域
        self.multi_search_scroll_area = QScrollArea()
        self.multi_search_scroll_area.setWidgetResizable(True)
        self.case_name_content_widget = QWidget()
        self.case_scroll_layout = QVBoxLayout(self.case_name_content_widget)
        self.multi_search_scroll_area.setWidget(self.case_name_content_widget)
        self.search_testCaseName_layout.addWidget(self.multi_search_scroll_area)

        self.search_testCaseName_container.setLayout(self.search_testCaseName_layout)
        self.search_testCaseName_container.setVisible(False)
        row5_layout.addWidget(self.search_testCaseName_container)
        sheet1_layout.addLayout(row5_layout, 0)

        row6_layout = QVBoxLayout()
        # 显示打印日志框 QTextEdit
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        row6_layout.addWidget(self.output_text)
        sheet1_layout.addLayout(row6_layout, 0)

        # Add a stretch at the bottom to push the controls to the top
        # sheet1_layout.addStretch()
        self.tab_widget.addTab(sheet1, "接口自动化")

        # "数据分析" 布局
        sheet_data_arrange_analysis = QtWidgets.QWidget()
        data_arrange_analysis_layout = QtWidgets.QVBoxLayout(sheet_data_arrange_analysis)
        # Add a spacer at the top to push widgets up
        data_arrange_analysis_layout.setContentsMargins(10, 10, 10, 10)  # 控制顶部、左右、底部边距
        data_arrange_analysis_layout.setSpacing(15)  # 控件之间的间距
        row1_data_arrange_analysis_layout = QtWidgets.QHBoxLayout()
        # "数据分析" 布局, 系统名下拉框
        self.dropdown_system_data_arrange_analysis = QtWidgets.QComboBox()
        self.dropdown_system_data_arrange_analysis.setFixedWidth(200)
        self.dropdown_system_data_arrange_analysis.setFixedHeight(40)
        # "数据分析" 布局, 整理分析类型下拉框
        self.dropdown_data_arrange_analysis = QtWidgets.QComboBox()
        # 点击下拉框后, 调用对应方法, 有些选项隐藏或者显示
        self.dropdown_data_arrange_analysis.setFixedWidth(200)
        self.dropdown_data_arrange_analysis.setFixedHeight(40)
        # "数据分析" 布局, 选择"整理分析类型"后, 需要输入值的输入框
        self.input_data_arrange_analysis = QtWidgets.QLineEdit()
        self.input_data_arrange_analysis.setPlaceholderText("输入值")
        self.input_data_arrange_analysis.setFixedWidth(200)
        self.input_data_arrange_analysis.setFixedHeight(40)
        self.button_run_data_arrange_analysis = QtWidgets.QPushButton("开始数据整理分析")
        self.button_run_data_arrange_analysis.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_data_arrange_analysis
        ))
        self.button_run_data_arrange_analysis.setFixedWidth(200)
        self.button_run_data_arrange_analysis.setFixedHeight(40)
        self.button_stop_data_arrange_analysis = QtWidgets.QPushButton("关闭数据整理分析")
        self.button_stop_data_arrange_analysis.clicked.connect(lambda: self.show_toast_and_dialog(
            toast_message="按键已经点击,请勿频繁操作",
            dialog_title="提示信息",
            dialog_message="请确定操作",
            confirm_callback=self.run_shell_command_stop_data_arrange_analysis
        ))
        # self.query_input_button.clicked.connect(self.run_shell_command_query_field_value)
        self.button_stop_data_arrange_analysis.setFixedWidth(200)
        self.button_stop_data_arrange_analysis.setFixedHeight(40)
        self.button_stop_data_arrange_analysis.hide()

        self.button_open_data_arrange_analysis = QtWidgets.QPushButton("打开文件所在文件夹")
        self.button_open_data_arrange_analysis.clicked.connect(self.run_open_directory_report_data_arrange_analysis)
        self.button_open_data_arrange_analysis.setFixedWidth(200)
        self.button_open_data_arrange_analysis.setFixedHeight(40)

        self.button_data_arrange_analysis = QtWidgets.QPushButton("数据整理分析")
        self.button_data_arrange_analysis.clicked.connect(self.run_open_data_arrange_analysis_activity)
        self.button_data_arrange_analysis.setFixedWidth(200)
        self.button_data_arrange_analysis.setFixedHeight(40)

        # 将三行控件存入layout, 将layout存入sheet1
        row1_data_arrange_analysis_layout.addWidget(self.dropdown_system_data_arrange_analysis)
        row1_data_arrange_analysis_layout.addWidget(self.dropdown_data_arrange_analysis)
        row1_data_arrange_analysis_layout.addWidget(self.input_data_arrange_analysis)
        row1_data_arrange_analysis_layout.addWidget(self.button_run_data_arrange_analysis)
        row1_data_arrange_analysis_layout.addWidget(self.button_stop_data_arrange_analysis)
        row1_data_arrange_analysis_layout.addWidget(self.button_open_data_arrange_analysis)
        row1_data_arrange_analysis_layout.addWidget(self.button_data_arrange_analysis)
        row1_data_arrange_analysis_layout.setAlignment(QtCore.Qt.AlignLeft)
        data_arrange_analysis_layout.addLayout(row1_data_arrange_analysis_layout)

        # 添加报文显示区域
        row2_data_arrange_analysis_layout = QVBoxLayout()
        self.message_display_data_arrange_analysis = QTextEdit()
        self.message_display_data_arrange_analysis.setReadOnly(True)
        # data_arrange_analysis_layout.addWidget(self.message_display_data_arrange_analysis)
        row2_data_arrange_analysis_layout.addWidget(self.message_display_data_arrange_analysis)
        data_arrange_analysis_layout.addLayout(row2_data_arrange_analysis_layout)

        self.tab_widget.addTab(sheet_data_arrange_analysis, "数据整理分析")

        main_layout.addWidget(self.tab_widget)

        self.setCentralWidget(main_widget)

        # 定时器用于更新日志
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_log)
        # 因为点击 接口自动化sheet 中的所有测试系统, 会导致隐藏、显示文件, 同时也会启动多线程跟新下来选项, 为了方式没有必要的加载
        # 通过比对当前存储的系统名, 来决定是否重新加载下拉框中的选项, 特别针对场景选项框
        self.on_dropdown_selected_store_system_value = ''



    # 选项, 下拉按键, 新建系统 选项, 调用方法
    def option1_method(self):
        # 选项, 下拉按键, 新建系统 选项, 调用方法
        dialog = InputDialog(self)
        if dialog.exec():
            inputs = dialog.get_inputs()
            print("用户输入:", inputs)
            system_name = inputs.get('system_name')
            # 获取输入框的内容
            if system_name != '' and system_name != None:
                database_name = ROOT_DIR + f'/testcase/{system_name}/数据库截图/数据库/DataBase.db' # +inputs.get('database_name').strip()
                url_host = inputs.get('url_host').strip()
                loaddatabase_type = inputs.get('loaddatabase_type').strip()
                data = {'shellCommand': 'ftsi', 'system_name': system_name, 'database_name': database_name,
                        'url_host': url_host, 'loaddatabase_type': loaddatabase_type}
                self.woker_shell = Worker_shell(data)
                self.woker_shell.result_signal.connect(self.append_output_capture)
                self.woker_shell.error_signal.connect(self.append_output_capture)
                self.woker_shell.message_done.connect(self.update_combobox_capture)
                self.woker_shell.start()
        else:
            print("点击取消")

    # 选项, 下拉按键, 设置代理 选项, 调用方法
    def option2_method(self):
        """显示代理配置窗口"""
        dialog = ProxyDialog(self)
        if dialog.exec():
            inputs = dialog.get_inputs()
            print("用户输入:", inputs)
            # 测试用全局配置表globalConfig.yaml
            customizeProxy = inputs.get('customizeProxy')
            proxy = inputs.get('proxy')
            port = inputs.get('port')
            if not os.path.exists(f"{ROOT_DIR}/config/globalConfig.yaml"):
                if customizeProxy == '' or customizeProxy == None:
                    if proxy == '' or proxy == None :
                        self.show_toast('代理设置不能为空!!!')
                    else:
                        init_global_config[init_global_proxy] = proxy
                else:
                    init_global_config[init_global_proxy] = customizeProxy
                init_global_config[init_global_proxy_port] = port
                yaml = YAML()
                # yaml表是list，这样为了防止，字段中的值和系统中特殊标记的值重复，[1]中的才是存储字段和对应值的dict
                with open(f"{ROOT_DIR}/config/globalConfig.yaml", 'w', encoding='utf-8') as f:
                    yaml.dump(init_global_config, f)
            else:
                globalConfigData = read_yaml(f"{ROOT_DIR}/config/globalConfig.yaml")
                if customizeProxy == '' or customizeProxy == None:
                    if proxy == '' or proxy == None:
                        self.show_toast('代理设置不能为空!!!')
                    else:
                        globalConfigData[init_global_proxy] = proxy
                else:
                    globalConfigData[init_global_proxy] = customizeProxy
                globalConfigData[init_global_proxy_port] = port
                yaml = YAML()
                # yaml表是list，这样为了防止，字段中的值和系统中特殊标记的值重复，[1]中的才是存储字段和对应值的dict
                with open(f"{ROOT_DIR}/config/globalConfig.yaml", 'w', encoding='utf-8') as f:
                    yaml.dump(globalConfigData, f)
            # 读取一边, 校验值是否存入
            globalConfigData_again = read_yaml(f"{ROOT_DIR}/config/globalConfig.yaml")
            if customizeProxy == '' or customizeProxy == None:
                if proxy != '' and proxy != None:
                    if globalConfigData_again.get('global_proxy') == proxy and \
                            globalConfigData_again.get('global_proxy_port') == port:
                        self.show_toast('代理设置成功!!!')
                    else:
                        self.show_toast('代理设置失败!!!')
            else:
                if globalConfigData_again.get('global_proxy') == customizeProxy and \
                        globalConfigData_again.get('global_proxy_port') == port:
                    self.show_toast('代理设置成功!!!')
                else:
                    self.show_toast('代理设置失败!!!')
        else:
            print("点击取消")

    def option3_method(self):
        # Option 3 action logic
        pass


    # 置顶窗口功能
    def toggle_pin(self):
        """ 置顶窗口 """
        self.setWindowFlag(Qt.WindowStaysOnTopHint, not self.windowFlags() & Qt.WindowStaysOnTopHint)
        self.show()


    def on_dropdown_selected(self):
        selected_value = self.dropdown.currentText()
        if selected_value != "全部测试系统":
            # 接口自动化sheet , 如果系统名为空, 或者产生变更, 会重新加载业务场景下拉框
            if self.on_dropdown_selected_store_system_value == '' or \
                    self.on_dropdown_selected_store_system_value != selected_value:
                self.on_dropdown_selected_store_system_value = selected_value
                # 启动线程, 获得场景
                data = {'shellCommand': 'get_scenario', 'selected_dropdown_system_value': selected_value}
                self.woker_shell_scenario = Worker_shell_get_scenario(data)
                self.woker_shell_scenario.message_done.connect(self.update_dropdown_scenario)
                self.woker_shell_scenario.start()
            # 获取所有选项文本的列表
            selected_dropdown_run_create_testcase_value = self.dropdown_run_create_testcase.currentText()
            selected_dropdown_run_test_value = self.dropdown_run_test.currentText()
            if selected_dropdown_run_create_testcase_value != '生成接口' or \
                    selected_dropdown_run_test_value != '自动化测试类型':
                # 隐藏新增系统名行
                self.dropdown_scenario.show()
                self.dropdown_run_create_testcase.show()
                self.run_create_testcase_button.show()
                # self.dropdown_run_test.hide()
                # self.run_test_button.hide()
                # self.run_open_report_button.hide()
                self.output_text.show()
                if selected_dropdown_run_test_value != '自动化测试类型'  and \
                        selected_dropdown_run_test_value != '敏感信息测试' and \
                            selected_dropdown_run_test_value != '敏感信息测试(过滤重复)' :
                    # self.show_toast('自动化测试用例加载中')
                    # self.show_search_result()
                    self.run_create_testcase_button.hide()
                    self.dropdown_run_create_testcase.hide()
                if selected_dropdown_run_test_value == '自动化测试类型'  or \
                        selected_dropdown_run_test_value == '敏感信息测试' or \
                            selected_dropdown_run_test_value == '敏感信息测试(过滤重复)' :
                    self.search_testCaseName_container.setVisible(False)
            else:
                # 隐藏新增系统名行
                self.dropdown_scenario.show()
                self.dropdown_run_create_testcase.show()
                self.run_create_testcase_button.show()
                # self.dropdown_run_test.show()
                # self.run_test_button.show()
                # self.run_open_report_button.show()
                self.output_text.show()
                if selected_dropdown_run_test_value == '自动化测试类型' or \
                        selected_dropdown_run_test_value == '敏感信息测试' or \
                            selected_dropdown_run_test_value == '敏感信息测试(过滤重复)' :
                    self.search_testCaseName_container.setVisible(False)
                else:
                    self.search_testCaseName_container.setVisible(True)
                    self.dropdown_run_create_testcase.hide()
                    self.run_create_testcase_button.hide()
        else:
            # 显示新增系统名行
            self.dropdown_scenario.hide()
            self.dropdown_run_create_testcase.hide()
            self.run_create_testcase_button.hide()
            # self.dropdown_run_test.hide()
            # self.run_test_button.hide()
            # self.run_open_report_button.hide()
            self.output_text.hide()
            # self.search_testCaseName_container.setVisible(False)


    # 全部业务场景, 点击下拉框选项, 触发这个方法
    def on_dropdown_selected_scenario(self):
        # 下拉框选择的系统名
        selected_value = self.dropdown.currentText()
        if selected_value != "全部测试系统":
            # 获得 自动化测试类型 选项
            selected_dropdown_run_test_value = self.dropdown_run_test.currentText()
            # 获得 业务场景 选项
            dropdown_scenario_value = self.dropdown_scenario.currentText()
            if selected_dropdown_run_test_value not in ['自动化测试类型', '敏感信息测试', '敏感信息测试(过滤重复)'] and \
                    dropdown_scenario_value != '全部业务场景' :
                self.show_toast('自动化测试用例加载中')
                self.show_search_result()



    def show_message(self, message):
        self.statusBar().showMessage(message)
        QtWidgets.QMessageBox.information(self, "Info", message)


    def show_toast_and_dialog(self, toast_message, dialog_title, dialog_message, confirm_callback):
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

    def show_toast(self, message):
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
        QTimer.singleShot(3000, toast.close)  # 2秒后自动关闭



    def run_shell_command_capture_image(self):
        # 获取输入框的内容
        capture_dropdown_value = self.capture_dropdown.currentText()
        if capture_dropdown_value != '' and capture_dropdown_value != None and capture_dropdown_value != '全部测试系统':
            try:
                self.capture_image_button.hide()
                self.capture_traffic_button.hide()
                self.capture_image_traffic_button.hide()
                self.capture_set_proxy_button.hide()
                # self.capture_set_proxy_input.hide()
                self.capture_unset_proxy_button.hide()
                self.capture_stop_button.show()
                # 启动监听鼠标和键盘的子进程
                self.listener_image_process = Process(target=self.run_image_listener, args=(capture_dropdown_value,self.queue))
                self.listener_image_process.start()
                self.timer.start(300)  # 每 300 毫秒检查队列
            except Exception as e:
                self.append_output_capture(f"启动截图功能出错: {e}")
                # print("执行过程中出错:", e)
        else:
            self.show_toast('请选择正确测试系统!!!')

    # 点击截图按键开启一个进程, 进程调用当前方法, 当前方法启动截图功能脚本
    # system: 系统名   queue: 消息队列, 为了在QLineEdit中打印的日志
    @staticmethod
    def run_image_listener(system,queue):
        """运行鼠标和键盘监听功能"""
        from traffic.image import start_image_listener
        try:
            start_image_listener(system,queue)
        except Exception as e:
            queue.put(f"监听进程出错: {e}")
            # print(f"监听进程出错: {e}")

    # 截图功能, 更新QLineEdit中打印的日志
    def update_log(self):
        """更新日志到 QTextEdit"""
        while not self.queue.empty():
            log_message = self.queue.get()
            self.append_output_capture(log_message)

        if self.redis_thread == None and \
                self.listener_image_process == None and \
                self.traffic_thread == None and  \
                self.listener_iamge_image_traffic_process == None and \
                self.listener_traffic_image_traffic_process == None :
            self.timer.stop()
            self.append_output_capture('消息监听关闭!!!')


    # 截图抓包进程调用, 启动截图进程
    @staticmethod
    def run_listener_iamge_image_traffic(redisPort, system, queue):
        """运行鼠标和键盘监听功能"""
        from traffic.image_traffic import start_listener
        try:
            start_listener(redisPort, system, queue)
        except Exception as e:
            print(f"启动截图进程出错: {e}")


    # 截图抓包进程调用, 启动抓包进程
    @staticmethod
    def run_listener_traffic_image_traffic(redisPort, system, queue):
        """运行鼠标和键盘监听功能"""
        from traffic.traffic_Image import start_listener
        try:
            start_listener(redisPort, system, queue)
        except Exception as e:
            print(f"启动抓包进程出错: {e}")


    # 获得流量,单独抓包功能启动
    def run_shell_command_traffic(self):
        # 获取输入框的内容
        capture_dropdown_value = self.capture_dropdown.currentText()
        if capture_dropdown_value != '' and capture_dropdown_value != None and capture_dropdown_value != '全部测试系统':
            try:
                self.capture_image_button.hide()
                self.capture_traffic_button.hide()
                self.capture_image_traffic_button.hide()
                self.capture_set_proxy_button.hide()
                # self.capture_set_proxy_input.hide()
                self.capture_unset_proxy_button.hide()
                self.capture_stop_button.show()
                # 启动抓包线程
                from traffic.all_process_thread import trafficThread
                self.traffic_thread = trafficThread(capture_dropdown_value)
                self.traffic_thread.normal_signal.connect(self.on_run_traffic)
                self.traffic_thread.error_signal.connect(self.on_run_traffic_error)
                self.traffic_thread.start()
            except Exception as e:
                # print("执行过程中出错:", e)
                self.append_output_capture(f'启动抓包功能出错 : {e}')
        else:
            self.show_toast('请选择正确测试系统!!!')

    # 点击单独的抓包功能, 生成一个线程, 线程通过信号槽, 启动一个抓包进程。这个方法就是更新启动进程中的正常信息
    def on_run_traffic(self, msg):
        self.append_output_capture(f'{msg}')

    # 点击单独的抓包功能, 生成一个线程, 线程通过信号槽, 启动一个抓包进程。这个方法就是更新启动进程中的错误信息
    def on_run_traffic_error(self, error_msg):
        """处理 Redis 启动失败"""
        self.append_output_capture(f'抓包功能无法正常启动!!!{error_msg}')


    @staticmethod
    def run_traffic_listener(system):
        """运行 mitmproxy 抓包功能, 只抓包的方法"""
        from traffic.traffic import start_traffic
        try:
            start_traffic(system)
        except Exception as e:
            print(f"抓包进程出错: {e}")

    # 既截图又抓包功能
    def run_shell_command_capture_image_traffic(self):
        # 获取输入框的内容
        capture_dropdown_value = self.capture_dropdown.currentText()
        if capture_dropdown_value != '' and capture_dropdown_value != None and capture_dropdown_value != '全部测试系统':
            try:
                self.capture_image_button.hide()
                self.capture_traffic_button.hide()
                self.capture_image_traffic_button.hide()
                self.capture_set_proxy_button.hide()
                # self.capture_set_proxy_input.hide()失败
                self.capture_unset_proxy_button.hide()
                self.capture_stop_button.show()
                # 启动 Redis 线程
                from traffic.all_process_thread import redisProcessThread
                self.redis_thread = redisProcessThread()
                self.redis_thread.port_ready.connect(self.on_redis_ready)
                self.redis_thread.error_signal.connect(self.on_redis_error)
                self.redis_thread.start()
                self.timer.start(300)  # 每 300 毫秒检查队列
            except Exception as e:
                # print("执行过程中出错:", e)
                self.append_output_capture(f'启动redis出错 : {e}')
        else:
            self.show_toast('请选择正确测试系统!!!')


    # 点击启动截图抓包功能, 会开启一个线程, 线程使用信号槽, 首先启动redis, redis启动后, 会把端口号传给当前方法
    # 挡墙方法启动两个进程, 分别是截图进程和抓包进程
    # port: 启动redis使用的端口号
    def on_redis_ready(self, port):
        """Redis 启动成功"""
        self.redis_port = port
        # 判断是否启动redis成功, 并且给redis存入了一个初始值
        if self.redis_port != None:
            self.append_output_capture(f'redis环境正常,开启地址:127.0.0.1,端口:{self.redis_port}')

            # 启动监听鼠标和键盘的子进程
            self.listener_iamge_image_traffic_process = Process(target=self.run_listener_iamge_image_traffic,
                                            args=(self.redis_port, self.capture_dropdown.currentText(), self.queue))
            self.listener_iamge_image_traffic_process.start()

            # 启动
            self.listener_traffic_image_traffic_process = Process(target=self.run_listener_traffic_image_traffic,
                                            args=(self.redis_port, self.capture_dropdown.currentText(), self.queue))
            self.listener_traffic_image_traffic_process.start()
        else:
            self.append_output_capture(f'redis无法正常启动,无法开启截图抓包功能!!!')


    # 点击启动截图抓包功能, 会开启一个线程, 线程使用信号槽, 首先启动redis, 如果启动过程报错, 会将异常信息传递过来
    # error_msg: 无法启动redis的异常信息
    def on_redis_error(self, error_msg):
        """处理 Redis 启动失败"""
        self.append_output_capture(f'{error_msg}')



    # 点击拦截启动功能
    # port: 启动redis使用的端口号
    def intercept_redis_ready(self, port):
        """Redis 启动成功"""
        self.intercept_redis_port = port
        # 判断是否启动redis成功, 并且给redis存入了一个初始值
        if self.intercept_redis_port != None :
            self.on_run_capture_traffic(f'redis启动,端口 {self.intercept_redis_port} !!!')

            # 连接 Redis
            import redis
            self.redisPyside = redis.StrictRedis(host='127.0.0.1', port=self.intercept_redis_port, db=0, decode_responses=True)
            self.redisPyside.set("need", "True")  # 确保 mitmproxy 可以读取
            # 启动redis线程,监听redis
            from traffic.all_process_thread import redisListenerThread
            self.intercept_redis_listener_thread = redisListenerThread(self.intercept_redis_port)
            self.intercept_redis_listener_thread.normal_signal.connect(self.on_run_capture_traffic)
            self.intercept_redis_listener_thread.data_received.connect(self.display_redis_packets)
            self.intercept_redis_listener_thread.start()

            # 启动抓包线程
            from traffic.all_process_thread import captureTrafficThread
            self.capture_traffic_thread = captureTrafficThread(self.intercept_redis_port)
            self.capture_traffic_thread.normal_signal.connect(self.on_run_capture_traffic)
            self.capture_traffic_thread.error_signal.connect(self.on_run_capture_traffic_error)
            self.capture_traffic_thread.start()

        else:
            self.on_run_capture_traffic('redis未正常启动,未获得端口!!!')



    def run_shell_command_stop(self):

        if self.worker_shell_capture:
            try:
                if self.worker_shell_capture.process:
                    self.worker_shell_capture.stop()  # 调用 Worker 的停止方法
                self.worker_shell_capture.quit()
                self.worker_shell_capture.wait()
                self.worker_shell_capture = None
                self.append_output_capture('调用方法已终止')
                self.capture_image_button.show()
                self.capture_traffic_button.show()
                self.capture_image_traffic_button.show()
                self.capture_set_proxy_button.show()
                # self.capture_set_proxy_input.show()
                self.capture_unset_proxy_button.show()
                self.capture_stop_button.hide()
            except Exception as e:
                print(f"终止进程时发生错误: {str(e)}")
        else:
            print("没有正在运行的任务")



    def run_shell_command_stop_traffic_image(self):
        if self.traffic_thread :
            self.traffic_thread.stop()  # 调用自定义线程的 stop 方法
            self.traffic_thread.quit()  # 停止线程的事件循环
            self.traffic_thread.wait()  # 等待线程退出
            self.traffic_thread = None
            self.append_output_capture("抓包功能已经停止!!!")
            self.capture_image_button.show()
            self.capture_traffic_button.show()
            self.capture_image_traffic_button.show()
            self.capture_set_proxy_button.show()
            # self.capture_set_proxy_input.show()
            self.capture_unset_proxy_button.show()
            self.capture_stop_button.hide()
        if self.listener_traffic_image_traffic_process and self.listener_traffic_image_traffic_process.is_alive():
            self.listener_traffic_image_traffic_process.terminate()
            self.listener_traffic_image_traffic_process.join()
            self.listener_traffic_image_traffic_process = None
            self.append_output_capture('截图抓包中抓包功能已终止!!!')
            self.run_shell_command_unset_proxy()
            # self.append_output_capture('手动代理已关闭!!!')
            self.capture_image_button.show()
            self.capture_traffic_button.show()
            self.capture_image_traffic_button.show()
            self.capture_set_proxy_button.show()
            # self.capture_set_proxy_input.show()
            self.capture_unset_proxy_button.show()
            self.capture_stop_button.hide()
        if self.listener_image_process and self.listener_image_process.is_alive():
            self.listener_image_process.terminate()
            self.listener_image_process.join()
            self.listener_image_process = None
            self.append_output_capture('单独截图功能已终止!!!')
            self.capture_image_button.show()
            self.capture_traffic_button.show()
            self.capture_image_traffic_button.show()
            self.capture_set_proxy_button.show()
            # self.capture_set_proxy_input.show()
            self.capture_unset_proxy_button.show()
            self.capture_stop_button.hide()
        if self.listener_iamge_image_traffic_process and self.listener_iamge_image_traffic_process.is_alive():
            self.listener_iamge_image_traffic_process.terminate()
            self.listener_iamge_image_traffic_process.join()
            self.listener_iamge_image_traffic_process = None
            self.append_output_capture('截图抓包中截图功能已终止!!!')
            self.capture_image_button.show()
            self.capture_traffic_button.show()
            self.capture_image_traffic_button.show()
            self.capture_set_proxy_button.show()
            # self.capture_set_proxy_input.show()
            self.capture_unset_proxy_button.show()
            self.capture_stop_button.hide()
        if self.redis_thread :
            self.redis_thread.stop()  # 调用自定义线程的 stop 方法
            self.redis_thread.quit()  # 停止线程的事件循环
            self.redis_thread.wait()  # 等待线程退出
            self.redis_thread = None
            self.redis_port = None
            self.append_output_capture("Redis 服务已停止")
            self.capture_image_button.show()
            self.capture_traffic_button.show()
            self.capture_image_traffic_button.show()
            self.capture_set_proxy_button.show()
            # self.capture_set_proxy_input.show()
            self.capture_unset_proxy_button.show()
            self.capture_stop_button.hide()
        else:
            self.run_shell_command_unset_proxy()
            self.capture_image_button.show()
            self.capture_traffic_button.show()
            self.capture_image_traffic_button.show()
            self.capture_set_proxy_button.show()
            # self.capture_set_proxy_input.show()
            self.capture_unset_proxy_button.show()
            self.capture_stop_button.hide()
            # print("没有正在运行的任务")


    def run_shell_command_set_proxy(self):
        # 获取输入框的内容
        data = {'shellCommand': 'set_proxy'}
        self.woker_shell = Worker_shell(data)
        self.woker_shell.result_signal.connect(self.append_output_capture)
        self.woker_shell.error_signal.connect(self.append_output_capture)
        self.woker_shell.result_signal.connect(self.on_run_capture_traffic)
        self.woker_shell.error_signal.connect(self.on_run_capture_traffic_error)
        self.woker_shell.start()




    def run_shell_command_unset_proxy(self):
        data = {'shellCommand': 'unset_proxy'}
        self.woker_shell = Worker_shell(data)
        self.woker_shell.result_signal.connect(self.append_output_capture)
        self.woker_shell.error_signal.connect(self.append_output_capture)
        self.woker_shell.result_signal.connect(self.on_run_capture_traffic)
        self.woker_shell.error_signal.connect(self.on_run_capture_traffic_error)
        self.woker_shell.start()


    # 获得流量,单独抓包功能启动
    def toggle_intercept(self):
        """开始拦截/恢复按钮逻辑"""
        if self.intercept_button.text() == "开始拦截":
            try:
                self.intercept_install_certificate_button.hide()
                # 启动 Redis 线程
                from traffic.all_process_thread import redisProcessThread
                self.intercept_redis_thread = redisProcessThread()
                self.intercept_redis_thread.port_ready.connect(self.intercept_redis_ready)
                self.intercept_redis_thread.normal_signal.connect(self.listtener_queue_traffic)
                self.intercept_redis_thread.error_signal.connect(self.listtener_queue_traffic_error)
                self.intercept_redis_thread.start()
                # 修改按键文字
                self.intercept_button.setText("取消拦截")
                # self.intercept_button.setStyleSheet("background-color: gray;")
            except Exception as e:
                print("执行过程中出错:", e)
                self.message_display.append(f'启动抓包功能出错 : {e}')
        else:
            self.message_display.clear()
            if self.capture_traffic_thread:
                self.capture_traffic_thread.stop()  # 调用自定义线程的 stop 方法
                self.capture_traffic_thread.quit()  # 停止线程的事件循环
                QTimer.singleShot(5000, self.capture_traffic_thread.wait)  # 5 秒后检查线程状态
                self.capture_traffic_thread = None
                self.append_output_capture("抓包功能已经停止")
            if self.intercept_redis_listener_thread:
                self.intercept_redis_listener_thread.stop()  # 调用自定义线程的 stop 方法
                self.intercept_redis_listener_thread.quit()  # 停止线程的事件循环
                QTimer.singleShot(5000, self.intercept_redis_listener_thread.wait)  # 避免 UI 卡死
                self.intercept_redis_listener_thread = None
                self.append_output_capture("监听插件写入 redis 线程停止")

            if self.intercept_redis_thread :
                self.intercept_redis_thread.stop()  # 调用自定义线程的 stop 方法
                self.intercept_redis_thread.quit()  # 停止线程的事件循环
                self.intercept_redis_thread.wait()  # 等待线程退出
                self.intercept_redis_thread = None
                self.intercept_redis_port = None
                self.append_output_capture("Redis 服务已停止")
            else:
                self.message_display.append("没有抓包功能启动!!!")
            self.intercept_button.setText("开始拦截")
            self.intercept_install_certificate_button.show()

    # 获得流量,单独抓包功能启动
    def install_certificate(self):
        """开始拦截/恢复按钮逻辑"""
        if self.intercept_install_certificate_button.text() == "请设置代理安装证书":
            try:
                self.intercept_button.hide()
                self.allow_button.hide()
                # 启动抓包线程
                from traffic.all_process_thread import installCertificateThread
                self.install_certificate_thread = installCertificateThread(self.intercept_redis_port)
                self.install_certificate_thread.normal_signal.connect(self.on_run_capture_traffic)
                self.install_certificate_thread.error_signal.connect(self.on_run_capture_traffic_error)
                self.install_certificate_thread.start()
                # 修改按键文字
                self.intercept_install_certificate_button.setText("取消证书安装")
            except Exception as e:
                print("执行过程中出错:", e)
                self.message_display.append(f'启动抓包功能出错 : {e}')
        else:
            self.message_display.clear()
            if self.install_certificate_thread:
                self.install_certificate_thread.stop()  # 调用自定义线程的 stop 方法
                self.install_certificate_thread.quit()  # 停止线程的事件循环
                QTimer.singleShot(5000, self.install_certificate_thread.wait)  # 5 秒后检查线程状态
                self.install_certificate_thread = None
                self.append_output_capture("证书安装功能已经停止")
            else:
                self.message_display.append("没有证书安装功能启动!!!")
            self.intercept_install_certificate_button.setText("请设置代理安装证书")
            self.intercept_button.show()
            self.allow_button.show()


    # 点击单独的抓包功能, 生成一个线程, 线程通过信号槽, 启动一个抓包进程。这个方法就是更新启动进程中的正常信息
    def on_run_capture_traffic(self, msg):
        self.message_display.append(f'{msg}')

    # 点击单独的抓包功能, 生成一个线程, 线程通过信号槽, 启动一个抓包进程。这个方法就是更新启动进程中的错误信息
    def on_run_capture_traffic_error(self, error_msg):
        """处理 Redis 启动失败"""
        self.message_display.append(f'抓包功能无法正常启动!!!{error_msg}')


    # 生成一个监听插件写入到queue报文的线程, 线程通过信号槽。这个方法就是更新启动线程中的正常信息
    def listtener_queue_traffic(self, msg):
        self.message_display.append(f'{msg}')

    # 生成一个监听插件写入到queue报文的线程, 线程通过信号槽。这个方法就是更新启动线程中的错误信息
    def listtener_queue_traffic_error(self, error_msg):
        """处理 Redis 启动失败"""
        self.message_display.append(f'抓包功能无法正常启动!!!{error_msg}')

    # 监听来自抓包插件写入队列的报文
    def display_redis_packets(self, packet):
        """监听脚本插件写入到queue中的报文, """
        print('pyside6获得redis中的数据')
        packet = json.loads(packet)
        self.message_display.clear()
        # 记录从mitmproxy插件发送的原始值   self.current_label
        self.current_flow = packet
        print(packet)
        # 是请求还是响应
        mitm_requst_response = packet.get('mitm_requst_response')
        if mitm_requst_response == 'request' :
            # 通过self.flowId_url保存flowId和url 关系, 这样响应报文可以拿到这个值并跟新Qlabel
            full_url = packet.get('url')
            self.flowId_url[packet.get('flow_id')] = full_url
            if full_url != None :
                self.current_label.setText(f'请求地址: {full_url}')
            # 解析redis种存储的报文信息, 组成http报文格式
            request_line = f"{packet.get('method')} {packet.get('url_path')} {packet.get('http_version')}"
            request_headers = "\n".join([f"{k}: {v}" for k, v in packet.get('headers').items()])
            request_body = packet.get('body')
            if request_body == '' :
                self.message_display.setPlainText(f"{request_line}\n{request_headers}")
            else:
                self.message_display.setPlainText(f"{request_line}\n{request_headers}\n\n{request_body}")
        elif mitm_requst_response == 'response' :
            # 获得存储的url
            full_url = self.flowId_url.pop(packet.get('flow_id'), None)
            if full_url != None :
                self.current_label.setText(f'请求地址: {full_url}')
            # 组合成完整的响应行字符串
            response_line = f"{packet.get('http_version')} {packet.get('status_code')} {packet.get('reason')}"
            # response_headers = [(k.encode("utf-8"), v.encode("utf-8")) for k, v in packet.get('headers').items()]
            response_headers = "\n".join([f"{k}: {v}" for k, v in packet.get('headers').items()])
            response_body = packet.get('body')
            self.message_display.setPlainText(f"{response_line}\n{response_headers}\n\n{response_body}")



    # 点击放过,将修改过的或者未修改的报文,返回给插件,插件更新以后,发送给服务器或者客户端
    def pass_packet(self):
        toast = QLabel('发送当前报文!!!', self)
        toast.setStyleSheet(
            "background-color: black; color: white; padding: 5px; border-radius: 100px;")
        toast.setAlignment(Qt.AlignCenter)
        toast.setWindowFlags(Qt.ToolTip)
        toast.setGeometry(self.width() // 2 - 100, self.height() // 2 - 20, 100, 80)
        toast.show()
        # 设置自动关闭
        QTimer.singleShot(500, toast.close)  # 2秒后自动关闭
        """放过按钮逻辑"""
        modified_data = self.message_display.toPlainText()
        if modified_data != '' :
            # 在display_redis_packets方法中, 存储了一个原值的全局变量, dict类型, 里边存储了mitmproxy唯一标识flow_id
            # 取出flow_id, 和解析成dict中的数据存储到一块, 写入到redis中, mitmproxy插件拿出flow_id找出原值进行修改, 再恢复抓包
            flow_id = self.current_flow.get('flow_id')
            parse_http_message_dict = self.parse_http_message(modified_data, self.current_flow.get('mitm_requst_response'))
            parse_http_message_dict['flow_id'] = flow_id
            # 同样获得原始值, 是否进行了base64处理, 说明是二进制
            mitm_isBase64 = self.current_flow.get('mitm_isBase64')
            parse_http_message_dict['mitm_isBase64'] = mitm_isBase64
            self.redisPyside.publish('pyside_channel', json.dumps(parse_http_message_dict))  # 通知 mitmproxy 读取, 解析出http报文转str
            self.redisPyside.set("need", "True")  # 确保 mitmproxy 可以读取
            self.message_display.clear()
            self.current_label.clear()


    def parse_http_request(self, http_text):
        lines = http_text.split("\n")
        request_line = lines[0].split(" ")  # 第一行为请求行
        method, url_path, http_version = request_line[0], request_line[1], request_line[2]

        # 查找空行，分隔请求头和请求体
        empty_line_index = lines.index("") if "" in lines else len(lines)

        # 解析请求头
        headers = {}
        for line in lines[1:empty_line_index]:
            key, value = line.split(": ", 1)
            headers[key] = value

        # 解析请求体（如果有）
        body = "\n".join(lines[empty_line_index + 1:]) if empty_line_index + 1 < len(lines) else ""

        return {
            "method": method,
            "url_path": url_path,
            "http_version": http_version,
            "headers": headers,
            "body": body
        }


    def parse_http_response(self, http_text):
        lines = http_text.split("\n")
        response_line = lines[0].split(" ", 2)  # 第一行为响应行
        http_version, status_code, reason = response_line[0], response_line[1], response_line[2]

        # 查找空行，分隔响应头和响应体
        empty_line_index = lines.index("") if "" in lines else len(lines)

        # 解析响应头
        headers = {}
        for line in lines[1:empty_line_index]:
            key, value = line.split(": ", 1)
            headers[key] = value

        # 解析响应体（如果有）
        body = "\n".join(lines[empty_line_index + 1:]) if empty_line_index + 1 < len(lines) else ""

        return {
            "http_version": http_version,
            "status_code": status_code,
            "reason": reason,
            "headers": headers,
            "body": body
        }


    def parse_http_message(self, http_message: str, reqRes: str):
        """
        解析 HTTP 报文（请求 + 响应），返回请求和响应的字典
        """
        if reqRes == 'request' :
            request_dict = self.parse_http_request(http_message)
            # return request_dict
            return request_dict
        elif reqRes == 'response' :
            response_dict = self.parse_http_response(http_message)
            # return response_dict
            return response_dict



    def run_shell_command_modify_field_value(self):

        self.open_param_editor()





    def run_shell_command_create_testcase(self):
        # 获取下拉框系统名、选择选项, 获取输入框的内容
        selected_dropdown_system_value = self.dropdown.currentText()
        selected_dropdown_run_create_testcase_value = self.dropdown_run_create_testcase.currentText()
        if selected_dropdown_system_value not in  ['全部测试系统','',None] and \
                selected_dropdown_run_create_testcase_value not in ['生成接口','',None] :
            dropdown_scenario_value = self.dropdown_scenario.currentText()
            data = {'shellCommand': 'create_testcase', 'selected_dropdown_system_value': selected_dropdown_system_value,
                    'selected_dropdown_run_create_testcase_value': selected_dropdown_run_create_testcase_value,
                    'dropdown_scenario_value': dropdown_scenario_value}
            self.woker_shell = Worker_shell(data)
            self.woker_shell.result_signal.connect(self.append_output)
            self.woker_shell.error_signal.connect(self.append_output)
            self.woker_shell.start()


    def run_shell_command_run_testcase(self):
        # 获取下拉框系统名、选择选项, 获取输入框的内容
        selected_dropdown_system_value = self.dropdown.currentText()
        selected_dropdown_run_test_value = self.dropdown_run_test.currentText()
        if selected_dropdown_system_value not in  ['全部测试系统','',None] and \
                selected_dropdown_run_test_value not in ['自动化测试类型','',None] :
            # 获得业务场景下拉框中选择的选项值
            dropdown_scenario_value = self.dropdown_scenario.currentText()
            # 启动 开始自动化测试 隐藏按键
            self.run_test_button.hide()
            self.run_test_button_closed.show()
            self.search_testCaseName_container.setVisible(False)
            if selected_dropdown_run_test_value in ['敏感信息测试','敏感信息测试(过滤重复)','敏感信息存入过滤器'] :
                data = {'shellCommand': 'run_static',
                        'selected_dropdown_system_value': selected_dropdown_system_value,
                        'selected_dropdown_run_test_value': selected_dropdown_run_test_value,
                        'dropdown_scenario_value': dropdown_scenario_value}
                self.worker_shell = Worker_shell(data)
                self.worker_shell.result_signal.connect(self.append_output)
                self.worker_shell.error_signal.connect(self.append_output)
                self.worker_shell.start()
            else:
                # 获得选择用例名
                select_case_name_value = self.get_selected_options()
                if len(select_case_name_value) == 0 :
                    data = {'shellCommand': 'run_dynamic', 'selected_dropdown_system_value': selected_dropdown_system_value,
                            'selected_dropdown_run_test_value': selected_dropdown_run_test_value }
                    self.worker_shell = Worker_shell(data)
                    self.worker_shell.result_signal.connect(self.append_output)
                    self.worker_shell.error_signal.connect(self.append_output)
                    self.worker_shell.start()
                else:
                    data = {'shellCommand': 'run_dynamic_many',
                            'selected_dropdown_system_value': selected_dropdown_system_value,
                            'selected_dropdown_run_test_value': selected_dropdown_run_test_value,
                            'select_case_name_value': select_case_name_value}
                    self.worker_shell = Worker_shell(data)
                    self.worker_shell.result_signal.connect(self.append_output)
                    self.worker_shell.error_signal.connect(self.append_output)
                    self.worker_shell.start()


    # 按键 关闭自动化测试 触发方法
    def run_shell_command_run_testcase_closed(self):
        self.search_testCaseName_container.setVisible(True)
        """停止 Worker_shell 运行的进程"""
        if self.worker_shell and self.worker_shell.isRunning():

            self.worker_shell.finished_signal.connect(self._on_worker_finished)  # 注册回调
            self.worker_shell.stop()  # 终止子进程（异步）
        else:
            self._on_worker_finished()  # 如果线程本来就没跑，也执行清理



    def _on_worker_finished(self):
        print('线程结束后统一清理和 UI 恢复操作')
        """线程结束后统一清理和 UI 恢复操作"""
        self.worker_shell = None
        self.run_test_button.show()
        self.run_test_button_closed.hide()


    def run_open_directory_report(self):
        # 获取下拉框系统名、选择选项, 获取输入框的内容
        selected_dropdown_system_value = self.dropdown.currentText()
        if selected_dropdown_system_value != ''  and selected_dropdown_system_value != None:
            data = {'shellCommand': 'open_directory_report',
                    'selected_dropdown_system_value': selected_dropdown_system_value}
            self.woker_shell = Worker_shell(data)
            self.woker_shell.result_signal.connect(self.append_output)
            self.woker_shell.error_signal.connect(self.append_output)
            self.woker_shell.start()


    def run_open_directory_report_data_arrange_analysis(self):
        # 获取下拉框系统名、选择选项, 获取输入框的内容
        selected_dropdown_system_data_arrange_analysis_value = self.dropdown_system_data_arrange_analysis.currentText()
        selected_dropdown_data_arrange_analysis_value = self.dropdown_data_arrange_analysis.currentText()
        if selected_dropdown_system_data_arrange_analysis_value != '全部测试系统' and \
                selected_dropdown_system_data_arrange_analysis_value != '' and \
                selected_dropdown_system_data_arrange_analysis_value != None and \
                selected_dropdown_data_arrange_analysis_value != '整理分析类型' and \
                selected_dropdown_data_arrange_analysis_value != '' and \
                selected_dropdown_data_arrange_analysis_value != None:
            data = {'shellCommand': 'open_directory_report_data_arrange_analysis',
                    'selected_dropdown_system_data_arrange_analysis_value': selected_dropdown_system_data_arrange_analysis_value,
                    'selected_dropdown_data_arrange_analysis_value': selected_dropdown_data_arrange_analysis_value }
            self.woker_shell = Worker_shell(data)
            self.woker_shell.result_signal.connect(self.append_output_data_arrange_analysis)
            self.woker_shell.error_signal.connect(self.append_output_data_arrange_analysis)
            self.woker_shell.start()

    def run_open_data_arrange_analysis_activity(self):
        # 打开 ImageDatabaseViewer 界面
        from ui.imageDatabaseViewerWindow import ImageDatabaseViewer
        self.image_database_viewer = ImageDatabaseViewer()
        self.image_database_viewer.show()  # 使用 show 启动 QDialog 弹窗



    def run_shell_command_data_arrange_analysis(self):

        # 获取下拉框系统名、选择选项, 获取输入框的内容
        selected_dropdown_system_data_arrange_analysis_value = self.dropdown_system_data_arrange_analysis.currentText()
        selected_dropdown_data_arrange_analysis_value = self.dropdown_data_arrange_analysis.currentText()
        if selected_dropdown_system_data_arrange_analysis_value != '全部测试系统' and  \
                selected_dropdown_system_data_arrange_analysis_value != '' and \
                selected_dropdown_system_data_arrange_analysis_value != None and \
                selected_dropdown_data_arrange_analysis_value != '整理分析类型' and \
                selected_dropdown_data_arrange_analysis_value != ''  and \
                selected_dropdown_data_arrange_analysis_value != None :
            # 获取整理分析类型输入框的内容
            input_data_arrange_analysis_value = self.input_data_arrange_analysis.text().strip()
            if selected_dropdown_data_arrange_analysis_value == 'excel合并url(请求地址)' :
                if input_data_arrange_analysis_value == '' :
                    self.show_toast('请输入处理excel文件夹路径或者文件绝对路径')
                else:
                    data = {'shellCommand': 'run_data_arrange_analysis',
                            'selected_dropdown_system_data_arrange_analysis_value': selected_dropdown_system_data_arrange_analysis_value,
                            'selected_dropdown_data_arrange_analysis_value': selected_dropdown_data_arrange_analysis_value,
                            'input_data_arrange_analysis_value': input_data_arrange_analysis_value}
                    print('发送数据', data)
                    self.worker_shell_data_arrange_analysis = Worker_shell_data_arrange_analysis(data)
                    self.worker_shell_data_arrange_analysis.result_signal_data_arrange_analysis.connect(
                        self.append_output_data_arrange_analysis)
                    self.worker_shell_data_arrange_analysis.error_signal_data_arrange_analysis.connect(
                        self.append_output_data_arrange_analysis)
                    self.worker_shell_data_arrange_analysis.start()
                    self.input_data_arrange_analysis.hide()
                    self.button_run_data_arrange_analysis.hide()
                    self.button_stop_data_arrange_analysis.show()
                    self.button_open_data_arrange_analysis.hide()
            elif selected_dropdown_data_arrange_analysis_value == 'excel增加图片(截图中读取)' :
                if input_data_arrange_analysis_value == '':
                    self.show_toast('请输入处理excel文件绝对路径')
                else:
                    data = {'shellCommand': 'run_data_arrange_analysis',
                            'selected_dropdown_system_data_arrange_analysis_value': selected_dropdown_system_data_arrange_analysis_value,
                            'selected_dropdown_data_arrange_analysis_value': selected_dropdown_data_arrange_analysis_value,
                            'input_data_arrange_analysis_value': input_data_arrange_analysis_value}
                    self.worker_shell_data_arrange_analysis = Worker_shell_data_arrange_analysis(data)
                    self.worker_shell_data_arrange_analysis.result_signal_data_arrange_analysis.connect(
                        self.append_output_data_arrange_analysis)
                    self.worker_shell_data_arrange_analysis.error_signal_data_arrange_analysis.connect(
                        self.append_output_data_arrange_analysis)
                    self.worker_shell_data_arrange_analysis.start()
                    self.input_data_arrange_analysis.hide()
                    self.button_run_data_arrange_analysis.hide()
                    self.button_stop_data_arrange_analysis.show()
                    self.button_open_data_arrange_analysis.hide()
            else:
                data = {'shellCommand': 'run_data_arrange_analysis',
                        'selected_dropdown_system_data_arrange_analysis_value': selected_dropdown_system_data_arrange_analysis_value,
                        'selected_dropdown_data_arrange_analysis_value': selected_dropdown_data_arrange_analysis_value,
                        'input_data_arrange_analysis_value': input_data_arrange_analysis_value}
                self.worker_shell_data_arrange_analysis = Worker_shell_data_arrange_analysis(data)
                self.worker_shell_data_arrange_analysis.result_signal_data_arrange_analysis.connect(
                    self.append_output_data_arrange_analysis)
                self.worker_shell_data_arrange_analysis.error_signal_data_arrange_analysis.connect(
                    self.append_output_data_arrange_analysis)
                self.worker_shell_data_arrange_analysis.start()
                self.input_data_arrange_analysis.hide()
                self.button_run_data_arrange_analysis.hide()
                self.button_stop_data_arrange_analysis.show()
                self.button_open_data_arrange_analysis.hide()
        else:
            self.show_toast('请选择系统、选择类型!!!')


    def run_shell_command_stop_data_arrange_analysis(self):

        if self.worker_shell_data_arrange_analysis:
            try:
                if self.worker_shell_data_arrange_analysis.process:
                    self.worker_shell_data_arrange_analysis.stop()  # 调用 Worker 的停止方法
                self.input_data_arrange_analysis.show()
                self.button_run_data_arrange_analysis.show()
                self.button_stop_data_arrange_analysis.hide()
                self.button_open_data_arrange_analysis.show()
            except Exception as e:
                print(f"终止进程时发生错误: {str(e)}")
        else:
            print("没有正在运行的任务")


    def append_output(self, text):
        self.output_text.append(text)
        # 限制行数为 max_lines
        lines = self.output_text.toPlainText().split("\n")
        if len(lines) > self.max_lines:
            # 删除多余的行
            self.output_text.setPlainText("\n".join(lines[-self.max_lines:]))
            # 将光标移动到文本末尾
            self.output_text.moveCursor(self.output_text.textCursor().End)


    def append_output_capture(self, text):
        self.capture_message_display.append(text)
        # 限制行数为 max_lines
        lines = self.capture_message_display.toPlainText().split("\n")
        if len(lines) > self.max_lines:
            # 删除多余的行
            self.capture_message_display.setPlainText("\n".join(lines[-self.max_lines:]))
            # 将光标移动到文本末尾
            self.capture_message_display.moveCursor(self.capture_message_display.textCursor().End)


    def append_output_data_arrange_analysis(self, text):
        print(text)
        self.message_display_data_arrange_analysis.append(text)
        # 限制行数为 max_lines
        lines = self.message_display_data_arrange_analysis.toPlainText().split("\n")
        if len(lines) > self.max_lines:
            # 删除多余的行
            self.message_display_data_arrange_analysis.setPlainText("\n".join(lines[-self.max_lines:]))
            # 将光标移动到文本末尾
            self.message_display_data_arrange_analysis.moveCursor(self.message_display_data_arrange_analysis.textCursor().End)


    # sheet1 系统下拉框内容更新
    def update_combobox(self, data):
        # self.dropdown.addItems(data)
        self.update_all_combobox(data)
        self.label.hide()  # 隐藏加载提示

    # 流量捕获 系统下拉框内容更新
    def update_combobox_capture(self, data):
        # self.capture_dropdown.addItems(data)
        self.update_all_combobox(data)
        self.label.hide()  # 隐藏加载提示

    def update_combobox_setting(self, data):
        # self.dropdown_setting.addItems(data)
        self.label.hide()  # 隐藏加载提示 data_arrange_analysis

    def update_combobox_data_arrange_analysis(self, data):
        self.dropdown_data_arrange_analysis.addItems(data)
        self.label.hide()  # 隐藏加载提示

    def update_combobox_run_test(self, data):
        self.dropdown_run_test.addItems(data)
        self.label.hide()  # 隐藏加载提示

    def update_combobox_run_create_testcase(self, data):
        self.dropdown_run_create_testcase.addItems(data)
        self.label.hide()  # 隐藏加载提示


    # sheet1 系统下拉框内容更新
    def update_all_combobox(self, data):
        if isinstance(data, list) :
            self.capture_dropdown.clear()
            self.dropdown.clear()
            self.dropdown_system_data_arrange_analysis.clear()
            # 流量捕获, 系统下拉框
            self.capture_dropdown.addItems(data)
            # 接口自动化, 系统下拉框
            self.dropdown.addItems(data)
            # 数据整理分析, 系统下拉框
            self.dropdown_system_data_arrange_analysis.addItems(data)
        elif isinstance(data, dict) :
            self.capture_dropdown.clear()
            self.dropdown.clear()
            # self.dropdown_setting.clear()
            self.dropdown_run_create_testcase.clear()
            self.dropdown_run_test.clear()
            self.dropdown_system_data_arrange_analysis.clear()
            self.dropdown_data_arrange_analysis.clear()
            # 流量捕获, 系统下拉框
            self.capture_dropdown.addItems(['全部测试系统']+data.get('allTestedSystem'))
            # 接口自动化, 系统下拉框
            self.dropdown.addItems(['全部测试系统']+data.get('allTestedSystem'))
            temp = []
            # 获得所有字段值, 存入list中返回
            for item in data.get('allTestedSetting').keys():
                temp.append(item)
            # 接口自动化, 设置参数下拉框
            # self.dropdown_setting.addItems(['设置参数']+temp)
            temp = []
            # 获得所有字段值, 存入list中返回
            for item in data.get('allCreateTestcase').keys():
                temp.append(item)
            # 接口自动化, 生成用例类型下拉框
            self.dropdown_run_create_testcase.addItems(['生成接口']+temp)
            temp = []
            # 获得所有字段值, 存入list中返回
            for item in data.get('allTest').keys():
                temp.append(item)
            # 接口自动化, 自动化测试类型下拉框
            self.dropdown_run_test.addItems(['自动化测试类型']+temp)
            # 数据整理分析, 系统下拉框
            self.dropdown_system_data_arrange_analysis.addItems(['全部测试系统']+data.get('allTestedSystem'))
            temp = []
            for item in data.get('allArrangeAnalysis').keys():
                temp.append(item)
            # 数据整理分析, 系统下拉框
            self.dropdown_data_arrange_analysis.addItems(['整理分析类型']+temp)
        self.label.hide()  # 隐藏加载提示


    # sheet1 系统下拉框内容更新
    def update_dropdown_scenario(self, data):
        self.dropdown_scenario.clear()
        if data == [] :
            self.dropdown_scenario.addItems(['全部业务场景'])
        else:
            self.dropdown_scenario.addItems(data)
        # self.dropdown_scenario(data)
        self.label.hide()  # 隐藏加载提示


    def get_screen_size(self):
        if platform.system() == 'Windows':
            width, height = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
            return width, height
        else:
            width, height = (1200, 720)
            return width, height
            raise NotImplementedError("Unsupported platform")

    def show_search_result(self):
        # 启动线程, 获得场景
        data = {'shellCommand': 'get_testcase_name', 'selected_dropdown_system_value': self.dropdown.currentText(),
                'dropdown_run_test_value': self.dropdown_run_test.currentText(),
                'dropdown_scenario_value': self.dropdown_scenario.currentText() }
        self.woker_shell = Worker_shell(data)
        self.woker_shell.result_signal.connect(self.append_output_capture)
        self.woker_shell.error_signal.connect(self.append_output_capture)
        self.woker_shell.message_done.connect(self.load_py_files)
        self.woker_shell.start()
        # self.load_py_files()


    def load_py_files(self, py_files):
        """加载文件夹下所有 .py 文件名"""
        folder_path = ROOT_DIR + '/testcase/' + self.dropdown.currentText() + '/' + self.dropdown_run_test.currentText()   # 替换为目标文件夹路径
        # py_files = [f for f in os.listdir(folder_path) if f.endswith(".py")]

        # 清空旧选项
        for i in reversed(range(self.case_scroll_layout.count())):
            self.case_scroll_layout.itemAt(i).widget().deleteLater()

        # 添加新选项
        for file in py_files:
            checkbox = QCheckBox(file)
            self.case_scroll_layout.addWidget(checkbox)
            # 创建可点击的链接按钮
            link_button = QPushButton(file.replace('.py','.yaml'))
            link_button.setStyleSheet(
                """
                QPushButton {
                    text-align: left;
                    color: #000000;  /* 白色文字 */
                    background-color: #F0F0F0;  /* 红色背景 */
                    border-radius: 5px;  /* 圆角 */
                    padding: 5px 10px;  /* 内边距 */
                    text-decoration: underline;
                }
                QPushButton:hover {
                    background-color: #F0F0F0;  /* 鼠标悬停时的背景颜色 */
                }
                """
            )
            link_button.setCursor(Qt.PointingHandCursor)
            link_button.clicked.connect(lambda checked, f=file: self.open_file(folder_path, f))
            self.case_scroll_layout.addWidget(link_button)
        """显示 B 下拉框并加载 .py 文件名"""
        self.search_testCaseName_container.setVisible(True)


    def open_file(self, folder_path, file_name):
        """打开文件"""
        file_path = os.path.join(folder_path, file_name)
        if os.path.exists(file_path):
            # 获取目录路径
            dir_path = os.path.dirname(file_path)
            # 获得文件名(包括后缀)
            file_basename = os.path.basename(file_path)
            # 是list, 元素0文件名, 元素1文件后缀
            file_basename_suffix = os.path.splitext(file_basename)
            # 打开yaml文件
            os.startfile( os.path.join(dir_path, file_basename_suffix[0]) + '.yaml')
        else:
            self.show_toast(f"文件不存在: {file_path}")


    def filter_text_options(self):
        """根据搜索框内容过滤 B 下拉框选项"""
        search_text = self.search_testCaseName_box.text().lower()
        for i in range(self.case_scroll_layout.count()):
            checkbox = self.case_scroll_layout.itemAt(i).widget()
            checkbox.setVisible(search_text in checkbox.text().lower())


    def get_selected_options(self):
        """获取 B 下拉框中被勾选的选项名"""
        selected = []
        for i in range(self.case_scroll_layout.count()):
            checkbox = self.case_scroll_layout.itemAt(i).widget()
            if checkbox.isChecked():
                selected.append(checkbox.text())
        return selected

    def select_all_options(self, state):
        """全选 B 下拉框中的所有选项"""
        if state == 2 :
            # self.deselect_all_checkbox.setChecked(False)
            for i in range(self.case_scroll_layout.count()):
                checkbox = self.case_scroll_layout.itemAt(i).widget()
                # checkbox.setChecked(True)
                if checkbox.isVisible():  # 仅作用于搜索结果
                    checkbox.setChecked(True)
        elif state == 0 :
            self.select_all_checkbox.setChecked(False)
            for i in range(self.case_scroll_layout.count()):
                checkbox = self.case_scroll_layout.itemAt(i).widget()
                # checkbox.setChecked(False)
                if checkbox.isVisible():  # 仅作用于搜索结果
                    checkbox.setChecked(False)



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

    def open_param_editor(self):
        # 获取下拉框系统名、选择选项, 获取输入框的内容
        selected_dropdown_system_value = self.dropdown.currentText()
        # 打开参数编辑界面
        dialog = ParamEditor(selected_dropdown_system_value)
        dialog.exec_()


    def closeEvent(self, event):
        self.run_shell_command_stop_traffic_image()
        from datetime import datetime
        """捕获关闭事件并记录时间"""
        close_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Application closed at: {close_time}")
        super().closeEvent(event)

