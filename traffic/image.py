# # -*- coding:utf-8 -*-
# import datetime, threading, os, queue,sys
# # 当前脚本所在的目录
# current_dir = os.path.dirname(os.path.abspath(__file__))
# # 获取上级目录
# parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.append(parent_dir)
# import pyautogui as pg
# from  pynput.mouse import Button
# from pynput import mouse, keyboard
#
#
#
# # 使用时间戳命名图片.同时记录点击位置, 存入txt文件中
# # parentPath: 根路径,用来存储图片     task_queue_recordTime: 时间戳    mouseOrKeyboard: 键盘还是鼠标, 默认True鼠标
# # xPosition: 点击位置x轴,默认为空      yPosition: 点击位置y轴,默认为空
# def captureScreenShot(parentPath, task_queue_recordTime, mouseOrKeyboard=True, xPosition='', yPosition=''):
#     nowtime_replace = task_queue_recordTime.replace(':', '+')
#     if mouseOrKeyboard == True :
#         # print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
#         print('{0} at {1}'.format('Pressed Released', (xPosition, yPosition)))
#         pg.screenshot(parentPath + f'数据库截图/截图/image/{nowtime_replace}.png')
#         with open(parentPath + f'数据库截图/截图/label/{nowtime_replace}.txt', 'w') as f:
#             f.write(str(xPosition) + ' ' + str(yPosition))
#     else:
#         # print('{0} released'.format(key))
#         print('键盘 released')
#         pg.screenshot(parentPath + f'数据库截图/截图/image/{nowtime_replace}.png')
#         with open(parentPath + f'数据库截图/截图/label/{nowtime_replace}.txt', 'w') as f:
#             f.write('Key.enter')
#
# # 监听鼠标点击, 点击鼠标会有间隔, 点击的间隔如果大于设置的间隔, 会进行截图。如果小于, 不会触发方法.
# # 间隔时间是recordTime, 是一个全局变量, 有一个初始默认值
# # parentPath: 根路径,用来存储图片    x:点击位置x轴     y:点击位置y轴     button:按键,判断鼠标左右键     pressed: 是否点击
# # queue: 队列, 因为进程、线程问题, 时间戳写入队列, 抓包脚本获取这个值
# def on_click(parentPath, x, y, button, pressed, queue):
#     import datetime
#     nowtime = datetime.datetime.now()
#     global recordTime
#     if recordTime == '2024-06-29 21:10:35.796266':
#         if pressed and button == Button.left:
#             recordTime = str(nowtime)
#             # task_queue.put(('screenshot', 'mouse', x, y, recordTime))
#             queue.put(recordTime)
#             captureScreenShot(parentPath, recordTime, mouseOrKeyboard=True, xPosition=x, yPosition=y)
#     else:
#         from datetime import datetime
#         # str 转 datetime类型
#         recordTime_datetime = datetime.strptime(recordTime, '%Y-%m-%d %H:%M:%S.%f')
#         second = nowtime - recordTime_datetime
#         if second.seconds >= interval and pressed and button == Button.left:
#             recordTime = str(nowtime)
#             # task_queue.put(('screenshot', 'mouse', x, y, recordTime))
#             queue.put(recordTime)
#             captureScreenShot(parentPath, recordTime, mouseOrKeyboard=True, xPosition=x, yPosition=y)
#
#
# # 监听键盘enter按键点击,会生成一个时间戳写入到消息队列中,提供给抓包使用,会写入到数据库中
# # parentPath: 会有截图, 存储的根路径    key: 按键对象,用来判断enter按键使用      queue: 队列,存放时间戳
# def on_press(parentPath, key, queue):
#     # '点击按键时执行。'
#     if str(key) == 'Key.enter':
#         import datetime
#         nowtime = datetime.datetime.now()
#         global recordTime
#         if recordTime == '2024-06-29 21:10:35.796266':
#             recordTime = str(nowtime)
#             queue.put(recordTime)
#             captureScreenShot(parentPath, recordTime, mouseOrKeyboard=False)
#             # task_queue.put(('screenshot', 'keyboard', recordTime))
#         else:
#             from datetime import datetime
#             recordTime_datetime = datetime.strptime(recordTime, '%Y-%m-%d %H:%M:%S.%f')
#             second = nowtime - recordTime_datetime
#             if second.seconds >= interval:
#                 queue.put(recordTime)
#                 captureScreenShot(parentPath, recordTime, mouseOrKeyboard=False)
#                 # task_queue.put(('screenshot', 'keyboard', recordTime))
#
#
#
# # 监听进程
# def listener(queue,system):
#     # 设置鼠标监听器
#     mouse_listener = mouse.Listener(on_click=lambda x, y, button, pressed: on_click(parent_dir+'/testcase/'+system+'/', x, y, button, pressed, queue))
#     mouse_listener.start()
#     print('启动鼠标监听')
#     # 设置键盘监听器
#     keyboard_listener = keyboard.Listener(on_press=lambda key: on_press(parent_dir+'/testcase/'+system+'/', key, queue))
#     keyboard_listener.start()
#     keyboard_listener.join()
#     print('启动鼠标，键盘监听')
#
#

import os
import sys
import datetime
import pyautogui as pg
from pynput.mouse import Button
from pynput import mouse, keyboard
from config import *

# 当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上级目录
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

# 使用全局变量 recordTime
global recordTime
# 鼠标键盘点击间隔
interval = 1.5
# 默认初始时间
recordTime = "2024-06-29 21:10:35.796266"


# 只启动截图功能
def start_image_listener(system,queue):
    """启动鼠标键盘监听"""

    create_dirs = [
        os.path.join(ROOT_DIR, f"testcase/{system}/数据库截图/截图/image"),
        os.path.join(ROOT_DIR, f"testcase/{system}/数据库截图/截图/label"),
        os.path.join(ROOT_DIR, f"testcase/{system}/数据库截图/数据库")
        # os.path.join(ROOT_DIR, "mitm/temp_certificate_key"),
    ]
    for item_dir in create_dirs:
        os.makedirs(item_dir, exist_ok=True)
    print("监听鼠标键盘功能初始化完成!!!")
    queue.put('监听鼠标键盘功能初始化完成!!!')


    # 监听鼠标点击, 点击鼠标会有间隔, 点击的间隔如果大于设置的间隔, 会进行截图。如果小于, 不会触发方法.
    # 间隔时间是recordTime, 是一个全局变量, 有一个初始默认值
    # x:点击位置x轴     y:点击位置y轴     button:按键,判断鼠标左右键     pressed: 是否点击
    def on_click(x, y, button, pressed):
        """鼠标点击事件"""
        global recordTime
        nowtime = datetime.datetime.now()
        if pressed and button == Button.left:
            if recordTime == "2024-06-29 21:10:35.796266" or (
                nowtime - datetime.datetime.strptime(recordTime, "%Y-%m-%d %H:%M:%S.%f")
            ).total_seconds() >= interval:
                recordTime = str(nowtime)
                capture_screen_shot(ROOT_DIR, recordTime, mouseOrKeyboard=True, xPosition=x, yPosition=y)


    def on_key_press(key):
        """键盘按键事件"""
        global recordTime
        nowtime = datetime.datetime.now()
        if str(key) == "Key.enter":
            if recordTime == "2024-06-29 21:10:35.796266" or (
                nowtime - datetime.datetime.strptime(recordTime, "%Y-%m-%d %H:%M:%S.%f")
            ).total_seconds() >= interval:
                recordTime = str(nowtime)
                capture_screen_shot(ROOT_DIR, recordTime, mouseOrKeyboard=False)


    def capture_screen_shot(ROOT_DIR, task_queue_recordTime, mouseOrKeyboard=True, xPosition="", yPosition=""):
        """截图并记录点击位置"""
        nowtime_replace = task_queue_recordTime.replace(":", "+").replace(".", "_")
        img_path = os.path.join(ROOT_DIR, f"testcase/{system}/数据库截图/截图/image")
        label_path = os.path.join(ROOT_DIR, f"testcase/{system}/数据库截图/截图/label")

        if mouseOrKeyboard:
            print(f"鼠标点击位置: ({xPosition}, {yPosition})")
            pg.screenshot(os.path.join(img_path, f"{nowtime_replace}.png"))
            with open(os.path.join(label_path, f"{nowtime_replace}.txt"), "w") as f:
                f.write(f"{xPosition} {yPosition}")
        else:
            print("键盘按下: Enter")
            pg.screenshot(os.path.join(img_path, f"{nowtime_replace}.png"))
            with open(os.path.join(label_path, f"{nowtime_replace}.txt"), "w") as f:
                f.write("Key.enter")



    # 设置鼠标监听器
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    queue.put('鼠标监听已启动!!!')
    # print("鼠标监听已启动")

    # 设置键盘监听器
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    keyboard_listener.start()
    queue.put('键盘监听已启动!!!')
    # print("键盘监听已启动")

    mouse_listener.join()
    keyboard_listener.join()






# if __name__ == "__main__":
#
#     params = sys.argv[1:][0]  # 获取命令行参数
#
#     createAllDir = [f'{parent_dir}/testcase/{params}/数据库截图/截图/image',
#                     f'{parent_dir}/testcase/{params}/数据库截图/截图/label',
#                     f'{parent_dir}/testcase/{params}/数据库截图/数据库',
#                     f'{parent_dir}/mitm/temp_certificate_key']
#     # 遍历目录, 生成对应目录
#     for item_dir in createAllDir:
#         if not os.path.isdir(item_dir):
#             os.makedirs(item_dir)
#     print('当前测试系统,各测试类型文件夹生成完成!!!')
#
#
#     from multiprocessing import Process, Queue
#
#     timestamp_queue = Queue()
#
#     # 启动监听进程
#     listener_process = Process(target=listener, args=(timestamp_queue,params))
#     listener_process.start()










