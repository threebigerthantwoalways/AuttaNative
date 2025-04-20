import os
import sys
# 当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上级目录
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
from PySide6.QtCore import QThread , Signal
from multiprocessing import Process, Pipe

class redisProcessThread(QThread):
    port_ready = Signal(int)  # 信号，传递 Redis 端口
    normal_signal = Signal(str)  # 信号，传递 Redis 端口
    error_signal = Signal(str)  # 信号，用于传递错误信息

    def __init__(self):
        super().__init__()
        self.parent_conn, self.child_conn = Pipe()
        self.redis_process = None  # 存储 Redis 进程对象
        self.running = True  # 控制线程运行状态
        self.port = None

    def run(self):
        try:
            # 启动 Redis 服务子进程
            self.redis_process = Process(target=self.run_redis, args=(self.child_conn,))
            self.redis_process.start()

            # 等待管道中的端口号
            if self.parent_conn.poll(timeout=120):  # 使用较长的超时时间
                self.port = self.parent_conn.recv()
                if self.port:
                    self.port_ready.emit(self.port)  # 发送成功信号
                else:
                    self.error_signal.emit("Redis 启动失败，端口未返回")
            else:
                self.error_signal.emit("Redis 启动超时")
        except Exception as e:
            self.error_signal.emit(f"Redis 进程出错: {e}")

    @staticmethod
    def run_redis(conn):
        """运行 Redis 服务，并返回启动的端口号"""
        from traffic.redis_autta import start_redis
        try:
            port, redis_process = start_redis()  # 假设返回端口号和进程对象
            conn.send(port)  # 发送端口号
            print('staticmethod打印端口', port)
        except Exception as e:
            conn.send(None)  # 出错时返回 None
        finally:
            if not conn.closed:
                conn.close()

    def stop(self):
        """停止 Redis 进程"""
        if self.redis_process:
            try:
                import redis
                # 使用 SHUTDOWN 命令优雅关闭
                r = redis.StrictRedis(host="127.0.0.1", port=self.port, decode_responses=True)
                r.shutdown()  # 如果 Redis 支持 SHUTDOWN
                print("Redis 服务已优雅关闭")
                self.normal_signal.emit('Redis 服务已优雅关闭')
            except Exception as e:
                print(f"无法使用 SHUTDOWN 关闭 Redis 服务: {e}")
                self.error_signal.emit(f"无法使用 SHUTDOWN 关闭 Redis 服务: {e}")
            finally:
                # 确保进程终止
                try:
                    if self.redis_process.is_alive() :
                        import psutil
                        parent = psutil.Process(self.redis_process.pid)
                        for child in parent.children(recursive=True):
                            child.terminate()
                        parent.terminate()
                        parent.wait()
                        # print("Redis 进程及其子进程已全部关闭")
                        self.normal_signal.emit('Redis 进程及其子进程已全部关闭')
                except Exception as e:
                    self.error_signal.emit(f"关闭 Redis 进程时出错: {e}")
                finally:
                    self.redis_process = None





class trafficThread(QThread):
    normal_signal = Signal(str)  # 信号，传递 Redis 端口
    error_signal = Signal(str)  # 信号，用于传递错误信息

    def __init__(self, systemName):
        super().__init__()
        self.parent_conn, self.child_conn = Pipe()
        self.listener_traffic_process = None  # 存储
        self.systemName = systemName  # 系统名
        self.running = True  # 控制线程运行状态
        self.port = None

    def run(self):
        try:
            from traffic.traffic import start_traffic
            self.normal_signal.emit("启动抓包功能!!!")
            # 启动 mitmproxy 子进程
            self.listener_traffic_process = Process(target=start_traffic, args=(self.systemName,))
            self.listener_traffic_process.start()
            # 检查进程是否正常启动
            if not self.listener_traffic_process.is_alive():
                self.error_signal.emit("抓包功能进程启动失败")
        except Exception as e:
            self.error_signal.emit(f"抓包功能启动出错: {e}")



    def stop(self):
        """停止 抓包 进程"""
        if self.listener_traffic_process and self.listener_traffic_process.is_alive():
            try:
                import psutil
                parent = psutil.Process(self.listener_traffic_process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                parent.wait()
                # print("抓包功能进程及其子进程已全部关闭")
                self.normal_signal.emit("抓包功能进程及其子进程已全部关闭")
            except psutil.NoSuchProcess:
                # print(f"进程 PID {self.listener_traffic_process.pid} 不存在，可能已经终止")
                self.error_signal.emit(f"进程 PID {self.listener_traffic_process.pid} 不存在，可能已经终止")
            except Exception as e:
                self.error_signal.emit(f"关闭抓包功能进程及其子进程出错: {e}")
            finally:
                self.listener_traffic_process = None
        else:
            # print("抓包功能进程未启动或已关闭")
            self.error_signal.emit("抓包功能进程未启动或已关闭")



class captureTrafficThread(QThread):
    normal_signal = Signal(str)  # 信号，传递 Redis 端口
    error_signal = Signal(str)  # 信号，用于传递错误信息

    def __init__(self, redis_port):
        super().__init__()
        self.parent_conn, self.child_conn = Pipe()
        self.listener_traffic_process = None  # 存储
        self.running = True  # 控制线程运行状态
        # self.addon_thread_queue = addon_thread_queue
        # self.pyside_addon_queue = pyside_addon_queue
        self.redis_port = redis_port


    def run(self):
        try:
            from traffic.capture_traffic import start_traffic
            self.normal_signal.emit("启动抓包功能!!!")
            # 启动 mitmproxy 子进程
            self.listener_traffic_process = Process(target=start_traffic, args=(self.redis_port,))
            self.listener_traffic_process.start()
            # 检查进程是否正常启动
            if not self.listener_traffic_process.is_alive():
                print("抓包功能进程启动失败")
                self.error_signal.emit("抓包功能进程启动失败")
        except Exception as e:
            self.error_signal.emit(f"抓包功能启动出错: {e}")
            print(f"抓包功能启动出错: {e}")

    # 关闭抓包进程
    def stop(self):
        """停止抓包进程"""
        if self.listener_traffic_process and self.listener_traffic_process.is_alive():
            try:
                import psutil
                parent = psutil.Process(self.listener_traffic_process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()  # 先尝试终止子进程
                parent.terminate()  # 终止主进程

                # 等待最多 3 秒
                parent.wait(timeout=3)

                # 如果还没退出，强制 kill
                if parent.is_running():
                    print("进程未退出，尝试 kill")
                    for child in parent.children(recursive=True):
                        child.kill()
                    parent.kill()

                self.normal_signal.emit("抓包功能进程及其子进程已全部关闭")
            except psutil.NoSuchProcess:
                self.error_signal.emit(f"进程 PID {self.listener_traffic_process.pid} 不存在，可能已经终止")
            except Exception as e:
                self.error_signal.emit(f"关闭抓包功能进程出错: {e}")
            finally:
                self.listener_traffic_process = None


# 监听消息队列中的报文数据, pyside会取出消息队列中的值, 显示在pyside6界面中
class captureQueueListenerThread(QThread):
    normal_signal = Signal(str)  # 信号，传递 Redis 端口
    error_signal = Signal(str)  # 信号，用于传递错误信息
    packet_signal = Signal(set)  # 用于将报文数据发送到主线程

    def __init__(self, addon_thread_queue):
        super().__init__()
        # self.queue = queue  # 获得的来自抓包插件写入的报文消息队列
        self.addon_thread_queue = addon_thread_queue
        self.listen_for_packets_running = True  # 监听消息队列中的报文, False为关闭监听, True为开启监听


    def run(self):
        # 在进程中监控报文，并通过信号传递给主线程
        self.normal_signal.emit('监听报文消息队列启动!!!')
        while self.listen_for_packets_running:
            try:
                packet = self.addon_thread_queue.get()
                self.packet_signal.emit(packet)  # 将抓到的报文发送到主线程
            except Exception as e:
                self.error_signal.emit(f"监听报文消息队列启动出错: {e}")


    def stop(self):
        self.listen_for_packets_running = False
        self.normal_signal.emit('监听报文消息队列关闭!!!')



# # 监听消息队列中的报文数据, 插件会用到里边的值, 值会经过处理重新返回给mitmproxy, 继续完成抓包过程
# class pysideQueueListenerThread(QThread):
#     normal_signal = Signal(str)  # 信号，传递 Redis 端口
#     error_signal = Signal(str)  # 信号，用于传递错误信息
#     packet_signal = Signal(object)  # 用于将报文数据发送到主线程
#
#     def __init__(self, pyside_addon_queue):
#         super().__init__()
#         self.pyside_addon_queue = pyside_addon_queue  # pyside6 写入的消息队列
#         self.listen_for_packets_running = True  # 监听消息队列中的报文, False为关闭监听, True为开启监听
#
#
#     def run(self):
#         # 在进程中监控报文，并通过信号传递给主线程
#         self.normal_signal.emit('启动监听pyside6消息队列线程!!!')
#         print('启动监听pyside6消息队列线程!!!')
#         while self.listen_for_packets_running:
#             try:
#                 print('启动监听pyside6消息队列线程!!!')
#                 packet = self.pyside_addon_queue.get()
#                 print(packet[0])
#                 # self.packet_signal.emit(packet[0])  # 将抓到的报文发送到主线程
#                 self.packet_signal.emit('11111111111111111111111111111111')  # 将抓到的报文发送到主线程
#             except Exception as e:
#                 self.error_signal.emit(f"监听报文消息队列启动出错: {e}")
#                 print(f"监听报文消息队列启动出错: {e}")
#
#
#     def stop(self):
#         self.listen_for_packets_running = False
#         self.normal_signal.emit('监听报文消息队列关闭!!!')



from PySide6.QtCore import QThread, Signal, QTimer

class pysideQueueListenerThread(QThread):
    packet_signal = Signal(object)

    def __init__(self, pyside_addon_queue):
        super().__init__()
        self.pyside_addon_queue = pyside_addon_queue
        self.listen_for_packets_running = True

    def run(self):
        print('启动监听 pyside6 消息队列线程!!!')
        while self.listen_for_packets_running:
            try:
                packet = self.pyside_addon_queue.get()
                print(f"收到数据: {packet}")
                QTimer.singleShot(0, lambda: self.packet_signal.emit(packet))  # ✅ **在主线程触发信号**
            except Exception as e:
                print(f"监听报文消息队列启动出错: {e}")

    def stop(self):
        self.listen_for_packets_running = False
        print("监听报文消息队列关闭!!!")



import threading


class redisListenerThread(QThread):
    """ 监听 Redis 频道的线程 """
    data_received = Signal(str)  # 发送信号到 UI
    stop_event = threading.Event()  # ✅ 使用 threading.Event 控制退出
    normal_signal = Signal(str)  # 信号 , 正确信息
    error_signal = Signal(str)  # 信号，用于传递错误信息

    def __init__(self, redis_port):
        super().__init__()
        self.redis_port = redis_port  # 存储 Redis 进程对象

    def run(self):
        self.normal_signal.emit("监听redis中 mitmproxy_channel 开始")
        import redis
        try:
            r = redis.StrictRedis(host="127.0.0.1", port=self.redis_port, decode_responses=True)
            pubsub = r.pubsub()
            pubsub.subscribe('mitmproxy_channel')  # 监听 mitmproxy 发送的报文

            while not self.stop_event.is_set():
                message = pubsub.get_message(timeout=1)  # 这里用 timeout=1，避免一直阻塞
                if message and message['type'] == 'message':
                    self.data_received.emit(message['data'])  # 发送数据给 UI 显示

            pubsub.unsubscribe('mitmproxy_channel')
            pubsub.close()
        except Exception as e:
            self.error_signal.emit(f"Redis 监听线程出错: {e}")

        self.normal_signal.emit("❌ Redis 监听线程已停止")

    def stop(self):
        """ 停止 Redis 监听线程 """
        self.normal_signal.emit('开始关闭监听 mitmproxy 写入 redis')
        self.stop_event.set()
        self.stop_event.clear()  # 清除标志，确保下次可以重新监听





class installCertificateThread(QThread):
    normal_signal = Signal(str)  #
    error_signal = Signal(str)  #

    def __init__(self, redis_port):
        super().__init__()
        self.parent_conn, self.child_conn = Pipe()
        self.listener_traffic_process = None  # 存储
        self.redis_port = redis_port


    def run(self):
        try:
            from traffic.install_certificate import start_traffic
            self.normal_signal.emit("证书安装功能启动, 请通过浏览器访问 http://mitm.it")
            # 启动 mitmproxy 子进程
            self.listener_traffic_process = Process(target=start_traffic)
            self.listener_traffic_process.start()
            # 检查进程是否正常启动
            if not self.listener_traffic_process.is_alive():
                print("证书安装功能启动失败")
                self.error_signal.emit("证书安装功能启动失败")
        except Exception as e:
            self.error_signal.emit(f"证书安装功能启动出错: {e}")
            print(f"证书安装功能启动出错: {e}")

    # 关闭抓包进程
    def stop(self):
        """停止抓包进程"""
        if self.listener_traffic_process and self.listener_traffic_process.is_alive():
            try:
                import psutil
                parent = psutil.Process(self.listener_traffic_process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()  # 先尝试终止子进程
                parent.terminate()  # 终止主进程

                # 等待最多 3 秒
                parent.wait(timeout=3)

                # 如果还没退出，强制 kill
                if parent.is_running():
                    print("进程未退出，尝试 kill")
                    for child in parent.children(recursive=True):
                        child.kill()
                    parent.kill()

                self.normal_signal.emit("证书安装功能进程及其子进程已全部关闭")
            except psutil.NoSuchProcess:
                self.error_signal.emit(f"进程 PID {self.listener_traffic_process.pid} 不存在，可能已经终止")
            except Exception as e:
                self.error_signal.emit(f"关闭证书安装功能进程出错: {e}")
            finally:
                self.listener_traffic_process = None







