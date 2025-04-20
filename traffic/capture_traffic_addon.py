import mitmproxy.http
# from mitmproxy import ctx
# import base64
# from email.parser import BytesParser
# from email.policy import default
# import mimetypes
import sys,traceback
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email import message_from_bytes
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase  # 确保导入
from email import encoders  # 确保导入
import redis,json
from mitmproxy.http import Headers
import time
from queue import Queue


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

# 设置全局异常钩子
sys.excepthook = global_exception_handler




class interceptAddon:
    def __init__(self, redis_port):
        # self.packet_queue = packet_queue
        self.pending_flows = {}  # 存储被拦截的请求 / 响应
        # self.buffered_flows = []  # 临时存储无法写入到redis中的报文
        self.buffered_flows = Queue()  # 临时存储无法写入到redis中的报文
        # self.addon_thread_queue = addon_thread_queue
        # self.pyside_addon_queue = pyside_addon_queue
        self.finish_resume = False
        self.redis_port = redis_port
        self.redis_mitmproxy = redis.StrictRedis(host='127.0.0.1', port=self.redis_port, db=0, decode_responses=True)
        # 监听 PySide6 修改的报文
        self.pubsub = self.redis_mitmproxy.pubsub()
        self.pubsub.subscribe('pyside_channel')
        self.monitor_need_status()
        self.listen_for_modifications()
        # 启动监听queue中写入报文线程, pyside6使用这个队列数据
        # from traffic.all_process_thread import pysideQueueListenerThread
        # self.listener_pyside_queue_packets_thread = pysideQueueListenerThread(self.pyside_addon_queue)
        # self.listener_pyside_queue_packets_thread.normal_signal.connect(self.listtener_queue_traffic)
        # self.listener_pyside_queue_packets_thread.error_signal.connect(self.listtener_queue_traffic_error)
        # self.listener_pyside_queue_packets_thread.packet_signal.connect(self.handle_modified_message)
        # self.listener_pyside_queue_packets_thread.start()

    # def request(self, flow: mitmproxy.http.HTTPFlow):
    #     flow.intercept()  # 暂停请求，等待修改
    #     # 获取完整的请求 URL，包括协议、主机、端口和路径
    #     full_url = flow.request.pretty_url
    #     """拦截请求"""
    #     formatted_request, isBase64 = self.format_request(flow.request)
    #     self.addon_thread_queue.put(("request", formatted_request, flow.id, full_url, isBase64))
    #     self.pending_flows[flow.id] = flow  # 保存请求 flow
    #
    #     self.check_queue()


    # def response(self, flow: mitmproxy.http.HTTPFlow):
    #     flow.intercept()
    #     # 获取完整的请求 URL
    #     full_url = flow.request.pretty_url
    #     """拦截响应"""
    #     formatted_response, isBase64 = self.format_response(flow.response)
    #     self.addon_thread_queue.put(("response", formatted_response, flow.id, full_url, isBase64))
    #     self.pending_flows[flow.id] = flow  # 保存响应 flow
    #       # 暂停响应，等待修改
    #     self.check_queue()

    def listen_for_modifications(self):
        """ 监听 PySide6 存入的修改报文 """

        def run():
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    # modified_packet = self.redis_mitmproxy.get("pyside_channel")
                    # if modified_packet:
                    modified_packet = json.loads(message['data'])
                    print("📥 收到修改后的报文:")
                    self.handle_modified_message(modified_packet)

        import threading
        t = threading.Thread(target=run, daemon=True)
        t.start()


    def monitor_need_status(self):
        """ 监听 PySide6 存入的修改报文 """

        def run():
            while True:
                need_status = self.redis_mitmproxy.get("need")
                if need_status == "True" and  not self.buffered_flows.empty() :
                    data = self.buffered_flows.get()
                    self.redis_mitmproxy.publish("mitmproxy_channel", json.dumps(data))
                    self.redis_mitmproxy.set("need", "False")  # 确保 mitmproxy 可以读取
                    print('redis中need为True,从queue中取出第一个元素写入redis中')
                time.sleep(1)  # 轮询间隔

        import threading
        s = threading.Thread(target=run, daemon=True)
        s.start()


    def request(self, flow: mitmproxy.http.HTTPFlow):
        """
            拦截请求报文
            """
        # 暂停 mitmproxy，等待 PySide6 处理
        flow.intercept()
        print(f"🚦 请求报文已存入 Redis，抓包暂停")
        isBase64 = False
        try:
            body = flow.request.content.decode("utf-8")
        except Exception as e:
            print(e)
            try:
                body = flow.request.content.decode("gbk")
            except Exception as e:
                print(e)
                import base64
                body = base64.b64encode(flow.request.content).decode("utf-8")
                isBase64 = True
        # 通过唯一标识符,存入到dict中
        self.pending_flows[flow.id] = flow
        # 提取请求信息
        request_info = {
            'mitm_requst_response': 'request',          # 自定义一个类型, 是请求还是响应
            'mitm_isBase64': isBase64,    # 自定义一个类型, 请求体是否被进行Base64处理, 那边前端显示后需要再转会bytes给mitmproxy
            'method': flow.request.method,          # 请求方式
            'url': flow.request.url,                # 请求地址
            'url_path': flow.request.path,          # 请求路径
            "http_version": flow.request.http_version,  # 协议版本
            'headers': dict(flow.request.headers),  # 请求头, 改成dict类型
            'body': body,                           # 请求体
            'flow_id': flow.id                           # mitmproxy每个报文(区分请求响应)都有唯一id
        }
        self.buffered_flows.put(request_info)
        print('请求request_info存入queue')
        # need_status = self.redis_mitmproxy.get("need")
        # if need_status == "False":
        #     # 暂存数据，不写入 Redis
        #     self.buffered_flows.append(request_info)
        #     print('need为False请求request_info存入list')
        # else:
        #     # 存入 Redis 并暂停抓包
        #     self.redis_mitmproxy.publish('mitmproxy_channel', json.dumps(request_info))
        #     print('need为True请求request_info存入redis')
        # 将请求报文放入队列
        # self.addon_thread_queue.put(("request", request_info, isBase64))



    def response(self, flow: mitmproxy.http.HTTPFlow):
        """
            拦截响应报文
            """
        # 暂停 mitmproxy，等待 PySide6 处理
        flow.intercept()
        print(f"🚦 响应报文已存入 Redis，抓包暂停")
        isBase64 = False
        try:
            body = flow.response.content.decode("utf-8")
        except Exception as e:
            print(e)
            try:
                body = flow.response.content.decode("gbk")
            except Exception as e:
                print(e)
                import base64
                body = base64.b64encode(flow.response.content).decode("utf-8")
                isBase64 = True
        # 通过唯一标识符,存入到dict中
        self.pending_flows[flow.id] = flow
        # 提取响应信息
        response_info = {
            'mitm_requst_response': 'response',          # 自定义一个类型, 是请求还是响应
            'mitm_isBase64': isBase64,
            "status_code": flow.response.status_code,
            "reason": flow.response.reason,
            "http_version": flow.response.http_version,
            "headers": dict(flow.response.headers),
            "body": body,
            "flow_id": flow.id
        }
        self.buffered_flows.put(response_info)
        print('响应response_info存入queue')
        # need_status = self.redis_mitmproxy.get("need")
        # if need_status == "False":
        #     # 暂存数据，不写入 Redis
        #     self.buffered_flows.append(response_info)
        #     print('need为False响应response_info存入list')
        # else:
        #     # 存入 Redis 并暂停抓包
        #     self.redis_mitmproxy.publish('mitmproxy_channel', json.dumps(response_info))
        #     print('need为True响应response_info存入redis')
        # 将响应报文放入队列
        # self.addon_thread_queue.put(("response", response_info, isBase64))




    def handle_modified_message(self, modified_packet):
        """
        监听修改后的报文队列
        """
        # 从redis中获得pyside6存入的flow_id
        flow_id = modified_packet.get('flow_id')
        if flow_id != None :
            # 在插件拦截到报文的时候会存入到pending_flows中, 格式: {'flow_id': flow}
            origin_flow = self.pending_flows.pop(flow_id)
            # origin_flow.resume()
            # 从redis中获得pyside6存入的mitm_isBase64, 标识是否进行了base64编码
            mitm_isBase64 = modified_packet.get('mitm_isBase64')
            if origin_flow.request:  # 如果是请求报文
                origin_flow.request.method = modified_packet.get('method')
                origin_flow.request.path = modified_packet.get('url_path')
                origin_flow.request.http_version = modified_packet.get('http_version')
                origin_flow.request.headers = self.mitmHeader(modified_packet.get('headers'))
                if mitm_isBase64:
                    # origin_flow.request.content = base64.b64decode(modified_packet.get('body'))
                    pass
                else:
                    origin_flow.request.text = modified_packet.get('body')
            elif origin_flow.response:  # 如果是响应报文
                # flow.response.status_code = int(201)
                origin_flow.response.headers = self.mitmHeader(modified_packet.get('headers'))
                if mitm_isBase64:
                    # origin_flow.response.content = base64.b64decode(modified_packet.get('body'))
                    pass
                else:
                    origin_flow.response.text = modified_packet.get('body')
            origin_flow.resume()
        # print(self.pending_flows[modified_packet.get('id')])
        # self.pending_flows[modified_packet.get('id')].resume()
        # if len(modified_packet) == 3:
        #     flow, modified_message, isBase64 = pyside_queue
        #     print(flow)
        #     print(modified_message)
        #     print(isBase64)
        #     flow.resume()
            # if flow.request:  # 如果是请求报文
            #     if isBase64:
            #         flow.request = base64.b64decode(modified_message)
            #     else:
            #         flow.request.text = modified_message
            #
            # elif flow.response:  # 如果是响应报文
            #     if isBase64:
            #         flow.response = base64.b64decode(modified_message)
            #     else:
            #         flow.response.text = modified_message
            #     flow.resume()

    # 将可能是str、dict、list类型转成mitmproxya识别的bytes类型
    def mitmHeader(self, headers_data):
        # 处理 headers
        if isinstance(headers_data, str):
            try:
                headers_data = json.loads(headers_data)  # 解析 JSON 字符串
            except json.JSONDecodeError:
                print("Error: headers is not a valid JSON string")
                headers_data = {}

        if isinstance(headers_data, dict):
            headers_data = [(k.encode('utf-8'), v.encode('utf-8')) for k, v in headers_data.items()]
        elif isinstance(headers_data, list):
            headers_data = [
                (k.encode('utf-8'), v.encode('utf-8')) if isinstance(k, str) and isinstance(v, str) else (k, v) for k, v
                in headers_data]
        return Headers(headers_data)

    def check_queue(self):
        """监听 PyQt5 传来的修改后的报文"""
        # try:

        self.finish_resume = True
        # while not self.pyside_addon_queue.empty():
        while self.finish_resume and self.pyside_addon_queue.empty():
            packet_type, modified_packet, flow_id, isBase64 = self.pyside_addon_queue.get()

            if flow_id in self.pending_flows:
                flow = self.pending_flows.pop(flow_id)  # 取出 flow
                self.apply_modified_packet(flow, modified_packet, packet_type, isBase64)
        # except Exception as e:
        #     ctx.log.error(f"处理修改报文时出错: {e}")

    def apply_modified_packet(self, flow, modified_packet, packet_type, isBase64):
        """应用修改后的报文"""
        lines = modified_packet.split("\n")
        headers = {}
        body_index = 0
        for i, line in enumerate(lines):
            if line == "":  # 空行分隔头部和 body
                body_index = i + 1
                break
            if ": " in line:
                parts = line.split(": ", 1)
                if len(parts) == 2:
                    key, value = parts
                    headers[key.strip()] = value.strip()
        body = "".join(lines[body_index:])

        content_type = headers.get("Content-Type", "")

        # # 处理 Base64 编码的二进制数据
        # if isBase64 :
        #     body = base64.b64decode(body)  # 还原成 bytes
        # elif "multipart/form-data" in content_type:
        #     body = self.rebuild_multipart_data(flow.request.content, content_type, body)

        # packet_type 是请求还是响应
        if packet_type == "request":
            # 修改请求地址
            new_url = self.extract_new_url(modified_packet, flow)  # 假设你有一个方法提取修改后的 URL
            flow.request.url = new_url  # 更新请求的 URL
            # if "Host" not in headers:
            #     print("警告: 请求头中缺少 Host 头部, 可能导致请求失败")
            #     headers["Host"] = flow.request.host  # 确保 Host 头部存在
            # if "Content-Length" in headers:
            #     headers["Content-Length"] = str(len(str(body)))

            flow.request.headers.clear()
            # flow.request.headers.update(headers)
            from mitmproxy.http import Headers
            # 转换 headers 为 bytes
            headers_bytes = [(k.encode("utf-8"), v.encode("utf-8")) for k, v in headers.items()]
            flow.request.headers = Headers(headers_bytes)  # 修正 headers 类型
            # flow.request.text = body  # 更新请求

            # if isinstance(body, bytes):
            #     print('进入isinstance---bytes.....')
            #     flow.request.content = body
            # elif "multipart/form-data" in content_type :
            #     print('进入multipart/form-data-----bytes.....')
            #     flow.request.content = body
            # else:
            #     flow.request.text = body

            if isBase64 :
                flow.request.content  = base64.b64decode(body)
            else:
                flow.request.text = body
            self.finish_resume = False
            flow.resume()  # 继续请求

        elif packet_type == "response":
            flow.response.headers.clear()
            from mitmproxy.http import Headers
            # flow.response.headers.update(headers)
            headers_bytes = [(k.encode("utf-8"), v.encode("utf-8")) for k, v in headers.items()]
            flow.response.headers = Headers(headers_bytes)  # 修正 headers 类型
            # flow.response.text = body  # 更新响应
            # if isinstance(body, bytes):
            #     flow.response.content = body
            # else:
            #     flow.response.text = body

            if isBase64 :
                flow.response.content  = base64.b64decode(body)
            else:
                flow.response.text = body
            self.finish_resume = False
            flow.resume()  # 继续响应


    def format_request(self, request):
        """格式化 HTTP 请求"""
        request_line = f"{request.method} {request.path} HTTP/1.1"
        headers = "\n".join([f"{k}: {v}" for k, v in request.headers.items()])

        content_type = request.headers.get("Content-Type", "")
        body = request.content
        # 判断是否base64, 也就是文件类型数据
        isBase64 = False
        # 处理请求体
        if "multipart/form-data" in content_type:
            print('进入multipart/form-data解析请求报文,传递给pyside6')
            # body = self.parse_multipart_data(body, content_type)
            try:
                body = request.content.decode("utf-8")
            except Exception as e :
                try:
                    body = request.content.decode("gbk")
                except Exception as e:
                    body = base64.b64encode(request.content).decode("utf-8")
                    isBase64 = True
            return f"{request_line}\n{headers}\n\n{body}"
        elif body and not self.is_text(request):
            print('进入base64解析请求报文,传递给pyside6')
            body = base64.b64encode(request.content).decode("utf-8")  # 转换为 base64
            isBase64 = True
            return f"{request_line}\n{headers}\n\n{body}"
        else:
            print('进入文本解析请求报文,传递给pyside6')
            # body = request.text if request.content else ""
            try:
                body = request.content.decode("utf-8") if request.content else ""
            except Exception as e:
                try:
                    body = request.content.decode("gbk") if request.content else ""
                except Exception as e:
                    body = base64.b64encode(request.content).decode("utf-8")
            return f"{request_line}\n{headers}\n\n{body}" , isBase64
        # """格式化 HTTP 请求"""
        # request_line = f"{request.method} {request.path} HTTP/1.1"
        # headers = "\n".join([f"{k}: {v}" for k, v in request.headers.items()])
        # body = request.text if request.content else ""
        # return f"{request_line}\n{headers}\n\n{body}"

    def format_response(self, response):
        """格式化 HTTP 响应"""
        status_line = f"HTTP/1.1 {response.status_code} {response.reason}"
        headers = "\n".join([f"{k}: {v}" for k, v in response.headers.items()])
        # 判断是否base64, 也就是文件类型数据
        isBase64 = False
        # 处理响应体
        if response.content and not self.is_text(response):
            print('进入响应内容base64')
            body = base64.b64encode(response.content).decode("utf-8")  # 转换为 base64
            isBase64 = True
            return f"{status_line}\n{headers}\n\n{body}"
        else:
            print('进入文本类型')
            # body = response.text if response.content else ""
            try:
                body = response.content.decode("utf-8") if response.content else ""
            except Exception as e:
                try:
                    body = response.content.decode("gbk") if response.content else ""
                except Exception as e:
                    body = base64.b64encode(response.content).decode("utf-8")
                    isBase64 = True
            return f"{status_line}\n{headers}\n\n{body}", isBase64

        # """格式化 HTTP 响应"""
        # status_line = f"HTTP/1.1 {response.status_code} {response.reason}"
        # headers = "\n".join([f"{k}: {v}" for k, v in response.headers.items()])
        # body = response.text if response.content else ""
        # return f"{status_line}\n{headers}\n\n{body}"

    # def extract_new_url(self, modified_packet):
    #     """从修改后的报文中提取新的请求地址"""
    #     # 假设你的修改后的请求报文格式正确，且请求行在第一行
    #     first_line = modified_packet.split("\n")[0]
    #     # 请求行的格式通常是: [METHOD] [URL] [HTTP_VERSION]
    #     new_url = first_line.split(" ")[1]  # 提取请求地址
    #     return new_url



    def extract_new_url(self, modified_packet, flow):
        """ 从修改后的报文中提取新的请求地址 """
        lines = modified_packet.split("\n")
        first_line = lines[0].strip()

        if not first_line:
            print("错误: 无法提取 URL, 请求行为空")
            return flow.request.url  # 直接返回原始 URL 避免异常

        parts = first_line.split(" ")
        if len(parts) < 2:
            print("错误: 无法提取 URL, 请求行格式错误")
            return flow.request.url

        new_path = parts[1]
        from urllib.parse import urljoin
        new_url = urljoin(flow.request.url, new_path)  # 确保路径拼接正确
        return new_url

    def is_text(self, http_obj):
        """判断请求/响应是否是文本类型"""
        content_type = http_obj.headers.get("Content-Type", "")
        if content_type == '' :
            content_type = http_obj.headers.get("content-type", "")
        return "text" in content_type.lower() or "json" in content_type.lower() or "xml" in content_type.lower()

    # import email
    # import base64
    # from email import policy
    #
    # def parse_multipart_data(body: bytes, content_type: str):
    #     """解析 multipart/form-data，返回格式化后的数据，适用于 PySide6 显示"""
    #
    #     # 解析 boundary
    #     boundary = content_type.split("boundary=")[-1].encode()
    #
    #     # 解析 multipart
    #     msg = email.message_from_bytes(b"--" + boundary + b"\r\n" + body, policy=policy.default)
    #
    #     # 解析后的数据（适用于 UI 显示）
    #     formatted_data = []
    #
    #     for part in msg.walk():
    #         content_disposition = part.get("Content-Disposition", "")
    #         if not content_disposition:
    #             continue  # 跳过无效部分
    #
    #         if "filename=" in content_disposition:  # 处理文件
    #             filename = part.get_filename()
    #             file_content = part.get_payload(decode=True)  # 获取文件内容 (bytes)
    #             base64_content = base64.b64encode(file_content).decode("utf-8")  # Base64 编码
    #
    #             formatted_data.append(
    #                 f"--- 文件 ---\nFilename: {filename}\nContent-Disposition: {content_disposition}\nContent (Base64):\n{base64_content}\n")
    #
    #         else:  # 处理普通字段
    #             field_name = part.get_param("name", header="Content-Disposition")
    #             field_value = part.get_payload(decode=True).decode("utf-8")  # 转字符串
    #
    #             formatted_data.append(
    #                 f"--- 字段 ---\nName: {field_name}\nContent-Disposition: {content_disposition}\nValue:\n{field_value}\n")
    #
    #     return "\n".join(formatted_data)  # 适用于 UI 显示


    def rebuild_multipart_formdata(modified_text, content_type_header):
        """从 PySide6 界面的文本格式数据重建 multipart/form-data"""
        # 解析 boundary
        boundary = None
        if "boundary=" in content_type_header:
            boundary = content_type_header.split("boundary=")[-1].strip()
        if not boundary:
            boundary = "----WebKitFormBoundaryXYZ123"
            raise ValueError("Content-Type 头部缺少 boundary, 自动补充")

        # 创建 MIMEMultipart 对象
        msg = MIMEMultipart("form-data", boundary=boundary)

        lines = modified_text.split("\n")
        field_name = None
        file_name = None
        file_data = None

        for line in lines:
            if line.startswith("【字段】:"):  # 解析普通字段
                field_name = line.replace("【字段】:", "").strip()
            elif field_name and line.strip():
                part = MIMEText(line.strip())
                part.add_header("Content-Disposition", f'form-data; name="{field_name}"')
                msg.attach(part)
                field_name = None  # 重置
            elif line.startswith("【文件】:"):  # 解析文件
                file_name = line.replace("【文件】:", "").strip()
            elif file_name and line.strip():
                file_data = base64.b64decode(line.strip())  # Base64 解码
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file_data)
                encoders.encode_base64(part)  # 确保 `encoders` 正确使用
                part.add_header("Content-Disposition", f'form-data; name="{file_name}"; filename="{file_name}"')
                msg.attach(part)
                file_name = None  # 重置

        return msg.as_bytes()  # 返回 bytes 给 mitmproxy

    # def parse_multipart_data(self, content, content_type):
    #     """解析 multipart/form-data"""
    #     boundary = content_type.split("boundary=")[-1].encode()  # 获取 boundary
    #     parts = content.split(b"--" + boundary)
    #
    #     parsed_parts = []
    #     for part in parts:
    #         if not part.strip() or part.startswith(b"--"):
    #             continue  # 跳过空部分和结束标记
    #
    #         headers, body = part.split(b"\r\n\r\n", 1)  # 分割头部和内容
    #         headers = BytesParser(policy=default).parsebytes(headers + b"\r\n")
    #
    #         content_disposition = headers["Content-Disposition"]
    #         name = content_disposition.split("name=")[-1].strip('"')
    #         filename = headers.get_filename()
    #
    #         if filename:  # 说明是文件
    #             parsed_parts.append(f"[FILE] {filename} ({len(body)} bytes)")
    #         else:  # 文本字段
    #             parsed_parts.append(f"[TEXT] {name}: {body.decode(errors='ignore')}")
    #
    #     return "\n".join(parsed_parts)


    # def parse_multipart_data(content, content_type):
    #     """解析 multipart/form-data"""
    #     boundary = content_type.split("boundary=")[-1].encode()  # 获取 boundary
    #     parts = content.split(b"--" + boundary)
    #
    #     parsed_parts = []
    #     for part in parts:
    #         if not part.strip() or part.startswith(b"--"):
    #             continue  # 跳过空部分和结束标记
    #
    #         headers, body = part.split(b"\r\n\r\n", 1)  # 分割头部和内容
    #         headers = BytesParser(policy=default).parsebytes(headers + b"\r\n")
    #
    #         content_disposition = headers["Content-Disposition"]
    #         name = content_disposition.split("name=")[-1].strip('"')
    #         filename = headers.get_filename()
    #
    #         if filename:  # 说明是文件
    #             parsed_parts.append(f"[FILE] {filename} ({len(body)} bytes)")
    #         else:  # 文本字段
    #             parsed_parts.append(f"[TEXT] {name}: {body.decode(errors='ignore')}")
    #
    #     return "\n".join(parsed_parts)


    # def rebuild_multipart_data(self, original_content, content_type, modified_text):
    #     """重新构造 multipart/form-data"""
    #     boundary = content_type.split("boundary=")[-1].encode()
    #     parts = original_content.split(b"--" + boundary)
    #     new_parts = []
    #
    #     modified_lines = modified_text.split("\n")
    #     text_changes = {}
    #
    #     # 解析用户修改的文本字段
    #     for line in modified_lines:
    #         if line.startswith("[TEXT]"):
    #             key, value = line.replace("[TEXT] ", "").split(": ", 1)
    #             text_changes[key] = value.encode()
    #
    #     for part in parts:
    #         if not part.strip() or part.startswith(b"--"):
    #             continue
    #
    #         headers, body = part.split(b"\r\n\r\n", 1)
    #         headers_obj = BytesParser(policy=default).parsebytes(headers + b"\r\n")
    #
    #         content_disposition = headers_obj["Content-Disposition"]
    #         name = content_disposition.split("name=")[-1].strip('"')
    #
    #         if name in text_changes:
    #             new_body = text_changes[name]  # 替换修改后的文本值
    #         else:
    #             new_body = body  # 未修改的字段保持不变
    #
    #         new_parts.append(headers + b"\r\n\r\n" + new_body)
    #
    #     return b"--" + boundary + b"\r\n".join(new_parts) + b"--" + boundary + b"--\r\n"





    # 生成一个监听插件写入到queue报文的线程, 线程通过信号槽。这个方法就是更新启动线程中的正常信息
    def listtener_queue_traffic(self, msg):
        print(f'{msg}')

    # 生成一个监听插件写入到queue报文的线程, 线程通过信号槽。这个方法就是更新启动线程中的错误信息
    def listtener_queue_traffic_error(self, error_msg):
        """处理 Redis 启动失败"""
        print(f'抓包功能无法正常启动!!!{error_msg}')





