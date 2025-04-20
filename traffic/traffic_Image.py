# # -*- coding:utf-8 -*-
# import ssl, socket, threading, zlib, brotli, gzip, os, datetime, sqlite3, queue,sys
# # 当前脚本所在的目录
# current_dir = os.path.dirname(os.path.abspath(__file__))
# # 获取上级目录
# parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.append(parent_dir)
# from cryptography import x509
# from cryptography.x509.oid import NameOID
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import serialization, hashes
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.primitives.serialization import load_pem_private_key
# import pyautogui as pg
# from  pynput.mouse import Button
# from pynput.keyboard import Controller, Key
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
# # 连接数据库, 返回连接数据库句柄
# # path: 数据库地址
# def create_connection(path):
#     # 每个线程独立创建数据库连接
#     conn = sqlite3.connect(path, check_same_thread=False)
#     return conn
#
#
# def is_gzip(data):
#     return data.startswith(b'\x1f\x8b')
#
# # header中字段可能是大写可能是消息, 可能是开头大写, 其他都小写, 这个方法, 就是当赋值的字段查不出来对应的值, 会增加其他大小写的字段格式
# # headerDict: 头, dict格式           field: 头对应的字段, str类型
# def getDictFiledValue(headerDict, field):
#     value = headerDict.get(field)
#     if value == None :
#         valueLower = headerDict.get(field.lower())
#         if valueLower == None :
#             return None
#         else:
#             return valueLower
#     else:
#         return value
#
#
# # 获取目标服务器的证书并解析 CN 和 SAN
# def get_cert_info(domain, port):
#
#     # ctx = ssl.create_default_context()
#     # 创建一个 SSL 上下文，禁用证书验证
#     # ctx = ssl.create_default_context()
#     # 启用不安全的旧版握手支持, 这个需要python 和 openssl版本合适才能使用, 最好改下环境, 使用这个
#     # ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
#     ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#     # 尝试启用较宽松的选项 启用 TLS 1.0 和 TLS 1.1（通过清除禁用标志）
#     ctx.options &= ~ssl.OP_NO_TLSv1  # 启用 TLS 1.0（如果必须）
#     ctx.options &= ~ssl.OP_NO_TLSv1_1  # 启用 TLS 1.1（如果必须）
#     ctx.check_hostname = False
#     ctx.verify_mode = ssl.CERT_NONE
#     # ctx.options |= ssl.OP_NO_TLSv1
#     # ctx.options |= ssl.OP_NO_TLSv1_1
#     with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
#         s.settimeout(5)
#         try:
#             s.connect((domain, port))
#         except socket.gaierror as e:
#             print(f"域名解析失败: {domain}, 错误信息: {e}")
#             return None, None
#         except ConnectionRefusedError as e:
#             print(f"目标服务器拒绝连接: {domain}:{port}, 错误信息: {e}")
#             return None, None
#         except TimeoutError as e:
#             print(f"连接 {domain}:{port} 超时: {e}")
#             return None, None
#         except Exception as e:
#             print(f"连接 {domain}:{port} 失败: {e}")
#             return None, None
#         try:
#             cert = s.getpeercert(True)
#             x509_cert = x509.load_der_x509_certificate(cert)
#             cn = x509_cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
#             san = x509_cert.extensions.get_extension_for_oid(
#                 x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value.get_values_for_type(x509.DNSName)
#         except Exception as e:
#             print(f"获取证书信息失败: {e}")
#             return None, None
#     return cn, san
#
#
# # 从 .pem 文件中读取根证书
# def load_root_certificate_and_key(root_cert_path, root_key_path, password=None):
#     # 读取根证书
#     with open(root_cert_path, "rb") as f:
#         root_cert = x509.load_pem_x509_certificate(f.read(), default_backend())
#
#     # 读取根证书的私钥
#     with open(root_key_path, "rb") as f:
#         root_key = serialization.load_pem_private_key(
#             f.read(),
#             password=password.encode() if password else None,
#             backend=default_backend()
#         )
#
#     return root_cert, root_key
#
#
# # 生成伪造的服务器证书
# def create_fake_cert(domain, cn, san):
#     if domain in cert_cache :
#         return globalCertPath + f"{domain}.pem", globalCertPath + f"{domain}_key.pem"
#     else:
#         common_name = cn
#         san_list = san
#         # 私钥、动态生成证书位置位置
#         # private_key_path = "C:\\Users\\sanyo\\Desktop\\updowndeletefile\\root_ca_key.pem"
#         # fake_cert_file_path = "D:\\新建文件夹\\domain_dynamic_ca.pem"
#         root_cert_path = globalCertPath + "root_ca.pem"
#         root_key_path = globalCertPath + "root_ca_key.pem"
#         root_cert, root_key = load_root_certificate_and_key(root_cert_path, root_key_path, password=None)
#         # # 从文件加载固定的私钥
#         # with open(private_key_path, "rb") as key_file:
#         #     private_key = serialization.load_pem_private_key(
#         #         key_file.read(),
#         #         password=None,
#         #         backend=default_backend()
#         #     )
#
#         # 生成服务器私钥
#         key = rsa.generate_private_key(
#             public_exponent=65537,
#             key_size=2048,
#             backend=default_backend()
#         )
#
#         # subject = issuer = x509.Name([
#         subject = x509.Name([
#             x509.NameAttribute(NameOID.COUNTRY_NAME, u"CH"),
#             x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"BeiJing"),
#             x509.NameAttribute(NameOID.LOCALITY_NAME, u"BeiJing"),
#             x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"TestMitm"),
#             x509.NameAttribute(NameOID.COMMON_NAME, common_name),
#         ])
#         cert_builder = x509.CertificateBuilder().subject_name(
#             subject
#         ).issuer_name(
#             # issuer
#             root_cert.issuer
#         ).public_key(
#             # private_key.public_key()
#             key.public_key()
#         ).serial_number(
#             x509.random_serial_number()
#         ).not_valid_before(
#             datetime.datetime.utcnow()
#         ).not_valid_after(
#             datetime.datetime.utcnow() + datetime.timedelta(days=365)  # 证书有效期一年
#         )
#         # 添加 SAN 扩展
#         san_objects = [x509.DNSName(dns_name) for dns_name in san_list]
#         cert_builder = cert_builder.add_extension(
#             x509.SubjectAlternativeName(san_objects),
#             critical=False
#         )
#         # 签署证书
#         # certificate = cert_builder.sign(private_key, hashes.SHA256(), default_backend())
#         certificate = cert_builder.sign(root_key, hashes.SHA256(), default_backend())
#         # 保存服务器证书和私钥
#         with open(globalCertPath + f"{domain}.pem", "wb") as f:
#             f.write(certificate.public_bytes(serialization.Encoding.PEM))
#
#         with open(globalCertPath + f"{domain}_key.pem", "wb") as f:
#             f.write(key.private_bytes(
#                 encoding=serialization.Encoding.PEM,
#                 format=serialization.PrivateFormat.TraditionalOpenSSL,
#                 encryption_algorithm=serialization.NoEncryption()  # 如果不想加密私钥
#             ))
#         cert_cache[domain] = ''
#         return globalCertPath + f"{domain}.pem", globalCertPath + f"{domain}_key.pem"
#
#
#
# # 响应头 Transfer-Encoding: chunked, 响应体太大不会一块响应回来, 会发多个响应包, 而每个响应包前边都会有一个数字(str), 这个数字
# # 实际是16进制, 表示当前这个响应体的包长度。因为这个原因，我们获得的整个相应包实际上是多个包的组合。所以如果响应体被压缩了比如gzip、br等,
# # 使用方法解压会报错, 当前方法就是, 整理这个原始的响应体, 剔除不需要的数字
# # body: 请求、响应体, 如果Transfer-Encoding: chunked, 需要使用当前方法重新处理, 才能解压
# def decode_chunked_body(body):
#     decoded_body = b""
#     while body:
#         # 读取每个块的长度（以16进制表示，直到遇到\r\n）
#         # length_str, rest = body.split(b"\r\n", 1)
#         try:
#             length_str, rest = body.split(b"\r\n", 1)
#         except ValueError as e:
#             # 捕获并处理解包错误
#             print(f"Error unpacking response: {e}")
#         # 获得响应体中的数字(代表后边数据的长度), 因为是str, 转成int类型16进制
#         length = int(length_str, 16)
#         # 如果没有这个数字, 那不做处理了
#         if length == 0:
#             break
#         # 读取块的数据, length代表后边的长度, 获取这部分, 就是响应体的实际内容
#         chunk_data = rest[:length]
#         # 返回值是decoded_body, 这个是整理好的值, 无数字
#         decoded_body += chunk_data
#         # 移除已经读取的部分，准备读取下一个块
#         # 数据格式 3932\r\n\x01\xfc\xff\x03\x00TUUU\r\n0\r\n\r\n, 可能是这样的, 其中\r\n0\r\n\r\n整个响应的截至符
#         # 3932是一个16进制数字, 这个不要, \r\n是回车换行符, 不要, 跳过
#         body = rest[length+2:]  # +2 跳过 \r\n
#     return decoded_body
#
#
#
# # 对压缩的body进行解压缩
# # headers: 头, 是个dict             rawBody: 请求响应体, bytes类型
# def decompress_response(headers, rawBody):
#     if rawBody == b''  : return rawBody, 'bytes'
#     elif rawBody == '' : return rawBody, 'str'
#     # 获得头信息
#     contentType = getDictFiledValue(headers, 'Content-Type')
#     print('contentType...', contentType)
#     # 响应中contentType中涉及上传接口的头value
#     uploadFile = ['image/gif', 'image/jpeg', 'image/png', 'application/pdf','application/msword',
#                   'application/vnd.ms-excel','application/zip','application/octet-stream']
#     # 获得头信息, 体的压缩方式
#     contentEncoding = getDictFiledValue(headers, 'Content-Encoding')
#     # 查询头是否有Transfer-Encoding, 可能响应体是分块传输
#     transferEncoding = getDictFiledValue(headers, 'Transfer-Encoding')
#     # 判断content类型, 如果是上传类型, 也就是文件, 直接返回bytes
#     if contentType != None and contentType in uploadFile:
#         # 为None, 说明没有压缩
#         if contentEncoding == None:
#             # 如果是chunked, 需要需要整理原报文
#             if transferEncoding == 'chunked':
#                 rawBody = decode_chunked_body(rawBody)
#             return rawBody, 'bytes'
#         else:
#             # 判断请求或响应体压缩方式
#             if contentEncoding.lower() == 'gzip' or is_gzip(rawBody):
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 # 对gizp解压
#                 return gzip.decompress(rawBody), 'bytes'
#             elif contentEncoding.lower() == 'deflate':
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 return zlib.decompress(rawBody, wbits=zlib.MAX_WBITS), 'bytes'
#             elif contentEncoding.lower() == 'br':
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 return brotli.decompress(rawBody), 'bytes'
#             elif contentEncoding.lower() == 'identity' or contentEncoding == '':
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 return rawBody, 'bytes'
#             else:
#                 raise ValueError(f"Unsupported Content-Encoding: {contentEncoding}")
#     else:
#         # 为None, 说明没有压缩
#         if contentEncoding == None:
#             # 如果是chunked, 需要需要整理原报文
#             if transferEncoding == 'chunked':
#                 rawBody = decode_chunked_body(rawBody)
#             return rawBody.decode('utf-8'), 'str'
#         else:
#             # 判断请求或响应体压缩方式
#             if contentEncoding.lower() == 'gzip' or is_gzip(rawBody):
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 # 对gizp解压
#                 rawStr = gzip.decompress(rawBody).decode('utf-8')
#                 # 判断响应体是否为空
#                 if rawStr == '':
#                     return '响应体体为空', 'str'
#                 else:
#                     return rawStr, 'str'
#             elif contentEncoding.lower() == 'deflate':
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 rawStr = zlib.decompress(rawBody, wbits=zlib.MAX_WBITS).decode('utf-8')
#                 # 判断响应体是否为空
#                 if rawStr == '':
#                     return '响应体体为空', 'str'
#                 else:
#                     return rawStr, 'str'
#             elif contentEncoding.lower() == 'br':
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 rawStr = brotli.decompress(rawBody).decode('utf-8')
#                 # 判断响应体是否为空
#                 if rawStr == '':
#                     return '响应体体为空', 'str'
#                 else:
#                     return rawStr, 'str'
#             elif contentEncoding.lower() == 'identity' or contentEncoding == '':
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 rawStr = rawBody.decode('utf-8')
#                 # 判断响应体是否为空
#                 if rawStr == '':
#                     return '响应体体为空', 'str'
#                 else:
#                     return rawStr, 'str'
#             else:
#                 raise ValueError(f"Unsupported Content-Encoding: {contentEncoding}")
#
#
#
# # 对压缩的body进行解压缩
# # headers: 头, 是个dict             rawBody: 请求响应体, bytes类型
# def decompress_request(headers, rawBody):
#     if rawBody == b'' : return rawBody, 'bytes'
#     elif rawBody == '' : return rawBody, 'str'
#     # 获得头信息
#     contentType = getDictFiledValue(headers, 'Content-Type')
#     # 响应中contentType中涉及上传接口的头value
#     uploadFile = ['image/gif','image/jpeg','image/png','application/pdf','application/msword',
#                   'application/vnd.ms-excel','application/zip','application/octet-stream','multipart/form-data']
#     # 获得头信息, 体的压缩方式
#     contentEncoding = getDictFiledValue(headers, 'Content-Encoding')
#     # 查询头是否有Transfer-Encoding, 可能响应体是分块传输
#     transferEncoding = getDictFiledValue(headers, 'Transfer-Encoding')
#     # 判断content类型, 如果是上传类型, 也就是文件, 直接返回bytes
#     if contentType != None and contentType in uploadFile:
#         # 为None, 说明没有压缩
#         if contentEncoding == None:
#             # 如果是chunked, 需要需要整理原报文
#             if transferEncoding == 'chunked':
#                 rawBody = decode_chunked_body(rawBody)
#             return rawBody, 'bytes'
#         else:
#             # 判断请求或响应体压缩方式
#             if contentEncoding.lower() == 'gzip' or is_gzip(rawBody):
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 # 对gizp解压
#                 return gzip.decompress(rawBody), 'bytes'
#             elif contentEncoding.lower() == 'deflate':
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 return zlib.decompress(rawBody, wbits=zlib.MAX_WBITS), 'bytes'
#             elif contentEncoding.lower() == 'br':
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 return brotli.decompress(rawBody), 'bytes'
#             elif contentEncoding.lower() == 'identity' or contentEncoding == '':
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 return rawBody, 'bytes'
#             else:
#                 raise ValueError(f"Unsupported Content-Encoding: {contentEncoding}")
#     else:
#         # 为None, 说明没有压缩
#         if contentEncoding == None :
#             # 如果是chunked, 需要需要整理原报文
#             if transferEncoding == 'chunked':
#                 rawBody = decode_chunked_body(rawBody)
#             return rawBody.decode('utf-8'), 'str'
#         else:
#             # 判断请求或响应体压缩方式
#             if contentEncoding.lower() == 'gzip' or is_gzip(rawBody):
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked' :
#                     rawBody = decode_chunked_body(rawBody)
#                 # 对gizp解压
#                 rawStr = gzip.decompress(rawBody).decode('utf-8')
#                 # 判断响应体是否为空
#                 if rawStr == '':
#                     return '响应体体为空', 'str'
#                 else:
#                     return rawStr, 'str'
#             elif contentEncoding.lower() == 'deflate':
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 rawStr = zlib.decompress(rawBody, wbits=zlib.MAX_WBITS).decode('utf-8')
#                 # 判断响应体是否为空
#                 if rawStr == '':
#                     return '响应体体为空', 'str'
#                 else:
#                     return rawStr, 'str'
#             elif contentEncoding.lower() == 'br':
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 rawStr = brotli.decompress(rawBody).decode('utf-8')
#                 # 判断响应体是否为空
#                 if rawStr == '':
#                     return '响应体体为空', 'str'
#                 else:
#                     return rawStr, 'str'
#             elif contentEncoding.lower() == 'identity' or contentEncoding == ''  :
#                 # 如果是chunked, 需要需要整理原报文
#                 if transferEncoding == 'chunked':
#                     rawBody = decode_chunked_body(rawBody)
#                 rawStr = rawBody.decode('utf-8')
#                 # 判断响应体是否为空
#                 if rawStr == '':
#                     return '响应体体为空', 'str'
#                 else:
#                     return rawStr, 'str'
#             else:
#                 raise ValueError(f"Unsupported Content-Encoding: {contentEncoding}")
#
#
#
# #############################################################
# # 写入数据库有个问题, 写入str, 写入bytes, 这个需要区分下######################### ,
# #
# #############################################################
# # 解析http的信息
# # firstLineHeaderReq: 请求行, str类型    headerReq: 请求头, dict类型     rawReqBody: 请求体, bytes类型
# # firstLineHeaderRes: 相应行行, str类型    headerRes: 响应头, dict类型     rawResBody: 响应体, bytes类型
# # def parseHttp(firstLineHeaderReq, headerReq, rawReqBody, firstLineHeaderRes, headerRes, rawResBody, dataBaseConn):
# # (addr, create_connection('C:\数据库\DataBase.db'),request_id, firstLineHeaderReq, headerReq, rawReqBody,firstLineHeaderRes, headerRes, rawResBody, timeStamp , https)
# def parseHttp(addr, dataBaseConnFack, request_id, firstLineHeaderReq, headerReq, rawReqBody, firstLineHeaderRes, headerRes, rawResBody, timeStamp):
#     item_dataBase = ['发起ip地址', '请求地址', '请求方式', '代理工具', '请求头', '请求体', '响应头',
#                      '响应体', '工号', '目录', '加密密钥', '发送时间']
#     # sql语句, 写入sqlite数据库
#     sql_table_insert = 'INSERT INTO ACTIVITY (LOCAL_SOURCE_IP,TARGET_URL,HTTP_METHOD,PROXY_TOOL,REQ_HEADERS,REQ_BODY,' \
#                        'RES_HEADERS,RES_BODY,WORK_NUM,SAME_DIRECTORY,ENCRYPT_DECRYPT_KEY,SEND_DATETIME) ' \
#                        'VALUES(?,?,?,?,?,?,?,?,?,?,?,?)'
#     # 从优先级队列中提取并写入数据库
#     # temp_queue = queue.PriorityQueue()
#     # while not priority_queue.empty():
#     #     request_id, firstLineHeaderReq, headerReq, rawReqBody, \
#     #     firstLineHeaderRes, headerRes, rawResBody, timeStamp = priority_queue.get()
#         # if firstLineHeaderReq != '' and headerReq != {} and firstLineHeaderRes != '' and headerRes != {} :
#     with lock:
#         # 请求方法、请求地址、协议和版本
#         try:
#             dataBaseConn = create_connection(globalDatabasePath)
#             method, url, protocol = firstLineHeaderReq.split(' ')
#             host = getDictFiledValue(headerReq, 'Host')
#             full_url = f"http://{host}{url}"
#         except ValueError as e:
#             print('parseHttp...firstLineHeaderReq切割捕获报错', firstLineHeaderReq)
#             print(f"Error unpacking response: {e}")
#         print('请求地址: ', full_url)
#         print('请求方法: ', method)
#         print('协议和版本: ', protocol)
#         print('请求头集合:\n', headerReq)
#         item_dataBase[0] = str(addr)
#         item_dataBase[1] = full_url
#         item_dataBase[2] = method
#         item_dataBase[4] = str(headerReq)
#         handleReq = decompress_request(headerReq, rawReqBody)
#         print('请求体:\n', handleReq[0].strip())
#         item_dataBase[5] = handleReq[0]
#         # protocol, code, code_description = firstLineHeaderRes.split(' ', 2)
#         try:
#             protocol, code, code_description = firstLineHeaderRes.split(' ', 2)
#         except ValueError as e:
#             print('parseHttp...firstLineHeaderRes切割捕获报错', firstLineHeaderRes)
#             print(f"Error unpacking response: {e}")
#         print('响应头协议和版本:', protocol)
#         print('响应状态码:', code)
#         print('响应状态码表述:', code_description)
#         print('响应头集合:\n', headerRes)
#         item_dataBase[6] = str(headerRes)
#         if code not in ['304']:
#             handleRes = decompress_response(headerRes, rawResBody)
#             # 将str类型响应体赋值给list第7个元素
#             item_dataBase[7] = handleRes[0]
#             print('响应体:\n', handleRes[0].strip())
#         else:
#             # 将str类型响应体赋值给list第7个元素
#             item_dataBase[7] = ''
#             print('响应体:\n', '')
#
#         # 增加时间戳
#         item_dataBase[11] = timeStamp
#         # item_dataBase[11] = str(datetime.datetime.now())
#
#         # 将list格式转为 tuple
#         dataBaseConn.execute(sql_table_insert, tuple(item_dataBase))
#         dataBaseConn.commit()
#         dataBaseConn.close()
#         # else:
#         #     # 如果响应尚未到达，将项放回队列
#         #     temp_queue.put((request_id, firstLineHeaderReq, headerReq, rawReqBody,
#         #                     firstLineHeaderRes, headerRes, rawResBody))
#
#     # print(f"Received response:\n{response.decode()}")
#
#     # except Exception :
#     #     print('报错, 可能无法写入数据库!!!')
#
#
# #############################################################
# # 写入数据库有个问题, 写入str, 写入bytes, 这个需要区分下######################### ,
# #
# #############################################################
# # 解析http的信息
# # firstLineHeaderReq: 请求行, str类型    headerReq: 请求头, dict类型     rawReqBody: 请求体, bytes类型
# # firstLineHeaderRes: 相应行行, str类型    headerRes: 响应头, dict类型     rawResBody: 响应体, bytes类型
# # def parseHttp(firstLineHeaderReq, headerReq, rawReqBody, firstLineHeaderRes, headerRes, rawResBody, dataBaseConn):
# # (addr, create_connection('C:\数据库\DataBase.db'),request_id, firstLineHeaderReq, headerReq, rawReqBody,firstLineHeaderRes, headerRes, rawResBody, timeStamp , https)
# def parseHttps(addr, dataBaseConnFack, request_id, firstLineHeaderReq, headerReq, rawReqBody, firstLineHeaderRes, headerRes, rawResBody, timeStamp):
#     item_dataBase = ['发起ip地址', '请求地址', '请求方式', '代理工具', '请求头', '请求体', '响应头',
#                      '响应体', '工号', '目录', '加密密钥', '发送时间']
#     # sql语句, 写入sqlite数据库
#     sql_table_insert = 'INSERT INTO ACTIVITY (LOCAL_SOURCE_IP,TARGET_URL,HTTP_METHOD,PROXY_TOOL,REQ_HEADERS,REQ_BODY,' \
#                        'RES_HEADERS,RES_BODY,WORK_NUM,SAME_DIRECTORY,ENCRYPT_DECRYPT_KEY,SEND_DATETIME) ' \
#                        'VALUES(?,?,?,?,?,?,?,?,?,?,?,?)'
#
#     with lock:
#         dataBaseConn = create_connection(globalDatabasePath)
#         # 请求方法、请求地址、协议和版本
#         try:
#             print(firstLineHeaderReq)
#             method, url, protocol = firstLineHeaderReq.split(' ')
#             host = getDictFiledValue(headerReq, 'Host')
#             full_url = f"https://{host}{url}"
#         except ValueError as e:
#             print('parseHttp...firstLineHeaderReq切割捕获报错', firstLineHeaderReq)
#             print(f"Error unpacking response: {e}")
#         print('请求地址: ', full_url)
#         print('请求方法: ', method)
#         print('协议和版本: ', protocol)
#         print('请求头集合:\n', headerReq)
#         item_dataBase[0] = str(addr)
#         item_dataBase[1] = full_url
#         item_dataBase[2] = method
#         item_dataBase[4] = str(headerReq)
#         handleReq = decompress_request(headerReq, rawReqBody)
#         print('请求体:\n', handleReq[0].strip())
#         item_dataBase[5] = handleReq[0]
#         # protocol, code, code_description = firstLineHeaderRes.split(' ', 2)
#         try:
#             protocol, code, code_description = firstLineHeaderRes.split(' ', 2)
#         except ValueError as e:
#             print('parseHttp...firstLineHeaderRes切割捕获报错', firstLineHeaderRes)
#             print(f"Error unpacking response: {e}")
#         print('响应头协议和版本:', protocol)
#         print('响应状态码:', code)
#         print('响应状态码表述:', code_description)
#         print('响应头集合:\n', headerRes)
#         item_dataBase[6] = str(headerRes)
#         if code not in ['304']:
#             handleRes = decompress_response(headerRes, rawResBody)
#             # 将str类型响应体赋值给list第7个元素
#             item_dataBase[7] = handleRes[0]
#             print('响应体:\n', handleRes[0].strip())
#         else:
#             # 将str类型响应体赋值给list第7个元素
#             item_dataBase[7] = ''
#             print('响应体:\n', '')
#
#         # 增加时间戳
#         item_dataBase[11] = timeStamp
#         # item_dataBase[11] = str(datetime.datetime.now())
#
#         # 将list格式转为 tuple
#         dataBaseConn.execute(sql_table_insert, tuple(item_dataBase))
#         dataBaseConn.commit()
#         dataBaseConn.close()
#
#
#
# # 根据id, 更新请求、响应报文, 到队列中
# # request_id: 一个数字, 标示序列位置       reqitem1: 请求行   reqitem2请求头   reqitem3: 请求体
# # resitem1: 响应行      resitem2: 响应头   resitem3: 响应体
# def update_in_queue(request_id, reqitem1, reqitem2, reqitem3, resitem1, resitem2, resitem3):
#     # 更新优先级队列中的响应
#     temp_queue = queue.PriorityQueue()
#
#     while not priority_queue.empty():
#         item = priority_queue.get()
#         if item[0] == request_id:
#             # 找到匹配的请求，更新响应
#             temp_queue.put((request_id, reqitem1, reqitem2, reqitem3, resitem1, resitem2, resitem3))
#         else:
#             # 未找到匹配的请求，保持队列原样
#             temp_queue.put(item)
#
#     # 将更新后的队列内容放回主队列
#     while not temp_queue.empty():
#         priority_queue.put(temp_queue.get())
#
#
# # # 读取获得的请求报文、响应报文, 通过头提供的信息, 读取多有报文, 切割出头和体, 方法发返回一个list, 包含4个元素
# # # 元素1: 完整的报文, 包含行、头、体, bytes类型    元素2: 头的第一行, str类型    元素3: 头集合, dict类型     元素4: 体, bytes类型
# # # sock: 就是socket
# # # httpReqData: 默认为空, 因为第一次http请求, 在clientHandle方法已经获得, 无需再读取, 如果不为空, 说明需要重新读取, 而如果是第一次http请求
# # # 那不需要读取, 直接可以操作
# # # isReqRes: 是请求还是响应, 默认False, 就是响应, True是请求
# # def receive_all(sock, firstHttpReqData= '', isReqRes=False):
# #     # 缓存, 一次读取报文的长度, 默认大小4096
# #     buffer_size = 4096
# #     # 报文所有, 包括行、头、体等所有
# #     raw = b''
# #     # 不是第一次http客户端请求数据
# #     if firstHttpReqData == '':
# #         # 获得socket的数据, 可能是请求或者响应
# #         data = sock.recv(buffer_size)
# #         # 获取请求头, 因为头可能很长, 没有出现头和体的分隔符, 也就是\r\n\r\n
# #         # 因为切割是遇到的第一个\r\n\r\n, 那么如果等于1, 说明请求头没有读取完整, 更没法切割头和体
# #         # 如果等于2, 说明\r\n\r\n出现了, 那么可以切割头和体了, 现在目的就是切出头, 体留着下边在处理, 因为while条件不能等于2, 所以不循环了
# #         # 因为是碰到第一个\r\n\r\n, 开始切割, 那么不可能大于2
# #         while len(data.split(b'\r\n\r\n', 1)) != 2:
# #             data += sock.recv(buffer_size)
# #         # 通过\r\n\r\n, 切割出头
# #         # headers_raw, body_raw = data.split(b'\r\n\r\n', 1)
# #         try:
# #             headers_raw, body_raw = data.split(b'\r\n\r\n', 1)
# #         except ValueError as e:
# #             print('receive_all..if.捕获异常', data)
# #             # 捕获并处理解包错误
# #             print(f"Error unpacking response: {e}")
# #     else:
# #         # 第一次http客户端请求数据
# #         # 通过\r\n\r\n, 切割出头
# #         # headers_raw, body_raw = firstHttpReqData.split(b'\r\n\r\n', 1)
# #         try:
# #             print('firstHttpReqData.....11111', firstHttpReqData)
# #             headers_raw, body_raw = firstHttpReqData.split(b'\r\n\r\n', 1)
# #         except ValueError as e:
# #             print('receive_all..else.捕获异常', data)
# #             # 捕获并处理解包错误
# #             print(f"Error unpacking response: {e}")
# #         data = firstHttpReqData
# #     # print(raw)
# #     # 请求头转str
# #     headers_str = headers_raw.decode('utf-8')
# #     # 获得请求头集合 , headers_str[0]第一行为请求行
# #     headers_list = headers_str.split('\r\n')
# #     # 设置全局变量, 得到请求头信息
# #     headers_dict = {}
# #     for _ in headers_list[1:]:
# #         key, value = _.split(':', 1)
# #         headers_dict[key.strip()] = value.strip()
# #     # 对响应状态码, 不做响应体解析, 统一返回 b''
# #     if isReqRes == False :
# #         status = headers_list[0].split(' ', 2)
# #         if status[1] in ['304'] :
# #             # raw: 完整的报文, 包含行、头、体, bytes类型    headers_list[0]: 头的第一行, str类型
# #             # headers_dict: 头集合, dict类型     body_raw: 体, bytes类型
# #             raw += data
# #             return raw, headers_list[0], headers_dict, b''
# #     if getDictFiledValue(headers_dict, 'Transfer-Encoding') == 'chunked':
# #         # data就是收到的请求, 赋值给request, request会发送给服务端
# #         raw += data
# #         while True:
# #             # 这是判断是否出现响应体的截至符
# #             if body_raw[len(body_raw) - 7:] == b'\r\n0\r\n\r\n':
# #                 break
# #             # 接收数据
# #             data = sock.recv(buffer_size)
# #             # 拼接请求体
# #             body_raw += data
# #             # 拼接request给服务端
# #             raw += data
# #     else:
# #         contentLength = getDictFiledValue(headers_dict, 'Content-Length')
# #         if contentLength != None and getDictFiledValue(headers_dict, 'Transfer-Encoding') == None:
# #             contentLength_int = int(contentLength)
# #             # data就是收到的请求, 赋值给request, request会返回给客户端
# #             raw += data
# #             while len(body_raw) < contentLength_int:
# #                 # 接收数据
# #                 data = sock.recv(contentLength_int - len(body_raw))
# #                 # 拼接请求体
# #                 body_raw += data
# #                 # 拼接request给服务端
# #                 raw += data
# #         else:
# #             # 拼接request给服务端
# #             raw += data
# #     # raw: 完整的报文, 包含行、头、体, bytes类型    headers_list[0]: 头的第一行, str类型
# #     # headers_dict: 头集合, dict类型     body_raw: 体, bytes类型
# #     return raw, headers_list[0], headers_dict, body_raw
#
#
# # 第一次请求处理请求报文
# # sock: 处理socket的对象   firstHttpReqData: 第一次获得的报文
# def receive_firstHttpReqData_request(sock, firstHttpReqData):
#     # 缓存, 一次读取报文的长度, 默认大小4096
#     buffer_size = 4096
#     # 报文所有, 包括行、头、体等所有
#     raw = b''
#     # 第一次http客户端请求数据
#     # 通过\r\n\r\n, 切割出头
#     try:
#         print('firstHttpReqData.....11111', firstHttpReqData)
#         headers_raw, body_raw = firstHttpReqData.split(b'\r\n\r\n', 1)
#     except ValueError as e:
#         # print('receive_all..else.捕获异常', data)
#         # 捕获并处理解包错误
#         print(f"Error unpacking response: {e}")
#     data = firstHttpReqData
#     # print(raw)
#     # 请求头转str
#     headers_str = headers_raw.decode('utf-8')
#     # 获得请求头集合 , headers_str[0]第一行为请求行
#     headers_list = headers_str.split('\r\n')
#     # 设置全局变量, 得到请求头信息
#     headers_dict = {}
#     for _ in headers_list[1:]:
#         key, value = _.split(':', 1)
#         headers_dict[key.strip()] = value.strip()
#     if getDictFiledValue(headers_dict, 'Transfer-Encoding') == 'chunked':
#         # data就是收到的请求, 赋值给request, request会发送给服务端
#         raw += data
#         while True:
#             # 这是判断是否出现响应体的截至符
#             if body_raw[len(body_raw) - 7:] == b'\r\n0\r\n\r\n':
#                 break
#             # 接收数据
#             data = sock.recv(buffer_size)
#             # 拼接请求体
#             body_raw += data
#             # 拼接request给服务端
#             raw += data
#     else:
#         contentLength = getDictFiledValue(headers_dict, 'Content-Length')
#         if contentLength != None and getDictFiledValue(headers_dict, 'Transfer-Encoding') == None:
#             contentLength_int = int(contentLength)
#             # data就是收到的请求, 赋值给request, request会返回给客户端
#             raw += data
#             while len(body_raw) < contentLength_int:
#                 # 接收数据
#                 data = sock.recv(contentLength_int - len(body_raw))
#                 # 拼接请求体
#                 body_raw += data
#                 # 拼接request给服务端
#                 raw += data
#         else:
#             # 拼接request给服务端
#             raw += data
#     # raw: 完整的报文, 包含行、头、体, bytes类型    headers_list[0]: 头的第一行, str类型
#     # headers_dict: 头集合, dict类型     body_raw: 体, bytes类型
#     return raw, headers_list[0], headers_dict, body_raw
#
#
# # 非首次请求报文处理
# # sock: 处理socket的对象
# def receive_request(sock):
#     # 缓存, 一次读取报文的长度, 默认大小4096
#     buffer_size = 4096
#     # 报文所有, 包括行、头、体等所有
#     raw = b''
#     # 不是第一次http客户端请求数据
#     # 获得socket的数据, 可能是请求或者响应
#     data = sock.recv(buffer_size)
#     # 获取请求头, 因为头可能很长, 没有出现头和体的分隔符, 也就是\r\n\r\n
#     # 因为切割是遇到的第一个\r\n\r\n, 那么如果等于1, 说明请求头没有读取完整, 更没法切割头和体
#     # 如果等于2, 说明\r\n\r\n出现了, 那么可以切割头和体了, 现在目的就是切出头, 体留着下边在处理, 因为while条件不能等于2, 所以不循环了
#     # 因为是碰到第一个\r\n\r\n, 开始切割, 那么不可能大于2
#     while len(data.split(b'\r\n\r\n', 1)) != 2:
#         data += sock.recv(buffer_size)
#     # 通过\r\n\r\n, 切割出头
#     # headers_raw, body_raw = data.split(b'\r\n\r\n', 1)
#     try:
#         headers_raw, body_raw = data.split(b'\r\n\r\n', 1)
#     except ValueError as e:
#         print('receive_all..if.捕获异常', data)
#         # 捕获并处理解包错误
#         print(f"Error unpacking response: {e}")
#     # print(raw)
#     # 请求头转str
#     headers_str = headers_raw.decode('utf-8')
#     # 获得请求头集合 , headers_str[0]第一行为请求行
#     headers_list = headers_str.split('\r\n')
#     # 设置全局变量, 得到请求头信息
#     headers_dict = {}
#     for _ in headers_list[1:]:
#         key, value = _.split(':', 1)
#         headers_dict[key.strip()] = value.strip()
#
#     if getDictFiledValue(headers_dict, 'Transfer-Encoding') == 'chunked':
#         # data就是收到的请求, 赋值给request, request会发送给服务端
#         raw += data
#         while True:
#             # 这是判断是否出现响应体的截至符
#             if body_raw[len(body_raw) - 7:] == b'\r\n0\r\n\r\n':
#                 break
#             # 接收数据
#             data = sock.recv(buffer_size)
#             # 拼接请求体
#             body_raw += data
#             # 拼接request给服务端
#             raw += data
#     else:
#         contentLength = getDictFiledValue(headers_dict, 'Content-Length')
#         if contentLength != None and getDictFiledValue(headers_dict, 'Transfer-Encoding') == None:
#             contentLength_int = int(contentLength)
#             # data就是收到的请求, 赋值给request, request会返回给客户端
#             raw += data
#             while len(body_raw) < contentLength_int:
#                 # 接收数据
#                 data = sock.recv(contentLength_int - len(body_raw))
#                 # 拼接请求体
#                 body_raw += data
#                 # 拼接request给服务端
#                 raw += data
#         else:
#             # 拼接request给服务端
#             raw += data
#     # raw: 完整的报文, 包含行、头、体, bytes类型    headers_list[0]: 头的第一行, str类型
#     # headers_dict: 头集合, dict类型     body_raw: 体, bytes类型
#     return raw, headers_list[0], headers_dict, body_raw
#
#
# # 处理响应报文
# # sock: 处理socket的对象
# def receive_response(sock):
#     # 缓存, 一次读取报文的长度, 默认大小4096
#     buffer_size = 4096
#     # 报文所有, 包括行、头、体等所有
#     raw = b''
#     # 获得socket的数据, 可能是请求或者响应
#     data = sock.recv(buffer_size)
#     # 获取请求头, 因为头可能很长, 没有出现头和体的分隔符, 也就是\r\n\r\n
#     # 因为切割是遇到的第一个\r\n\r\n, 那么如果等于1, 说明请求头没有读取完整, 更没法切割头和体
#     # 如果等于2, 说明\r\n\r\n出现了, 那么可以切割头和体了, 现在目的就是切出头, 体留着下边在处理, 因为while条件不能等于2, 所以不循环了
#     # 因为是碰到第一个\r\n\r\n, 开始切割, 那么不可能大于2
#     while len(data.split(b'\r\n\r\n', 1)) != 2:
#         data += sock.recv(buffer_size)
#     # 通过\r\n\r\n, 切割出头
#     # headers_raw, body_raw = data.split(b'\r\n\r\n', 1)
#     try:
#         headers_raw, body_raw = data.split(b'\r\n\r\n', 1)
#     except ValueError as e:
#         print('receive_all..if.捕获异常', data)
#         # 捕获并处理解包错误
#         print(f"Error unpacking response: {e}")
#     # print(raw)
#     # 请求头转str
#     headers_str = headers_raw.decode('utf-8')
#     # 获得请求头集合 , headers_str[0]第一行为请求行
#     headers_list = headers_str.split('\r\n')
#     # 设置全局变量, 得到请求头信息
#     headers_dict = {}
#     for _ in headers_list[1:]:
#         key, value = _.split(':', 1)
#         headers_dict[key.strip()] = value.strip()
#
#     status = headers_list[0].split(' ', 2)
#     if status[1] in ['304']:
#         # raw: 完整的报文, 包含行、头、体, bytes类型    headers_list[0]: 头的第一行, str类型
#         # headers_dict: 头集合, dict类型     body_raw: 体, bytes类型
#         raw += data
#         return raw, headers_list[0], headers_dict, b''
#
#     if getDictFiledValue(headers_dict, 'Transfer-Encoding') == 'chunked':
#         # data就是收到的请求, 赋值给request, request会发送给服务端
#         raw += data
#         while True:
#             # 这是判断是否出现响应体的截至符
#             if body_raw[len(body_raw) - 7:] == b'\r\n0\r\n\r\n':
#                 break
#             # 接收数据
#             data = sock.recv(buffer_size)
#             # 拼接请求体
#             body_raw += data
#             # 拼接request给服务端
#             raw += data
#     else:
#         contentLength = getDictFiledValue(headers_dict, 'Content-Length')
#         if contentLength != None and getDictFiledValue(headers_dict, 'Transfer-Encoding') == None:
#             contentLength_int = int(contentLength)
#             # data就是收到的请求, 赋值给request, request会返回给客户端
#             raw += data
#             while len(body_raw) < contentLength_int:
#                 # 接收数据
#                 data = sock.recv(contentLength_int - len(body_raw))
#                 # 拼接请求体
#                 body_raw += data
#                 # 拼接request给服务端
#                 raw += data
#         else:
#             # 拼接request给服务端
#             raw += data
#     # raw: 完整的报文, 包含行、头、体, bytes类型    headers_list[0]: 头的第一行, str类型
#     # headers_dict: 头集合, dict类型     body_raw: 体, bytes类型
#     return raw, headers_list[0], headers_dict, body_raw
#
#
# # 给一个header(dict类型), 返回header中的host和端口
# # headers: 请求头, dict类型
# def getHostPort(headers):
#     # # 因为Host是http协议头发送请求必填项, 获得原始Host, 提取发送需要的host, 端口, 为发送请求使用
#     # headerHostValue = reqestData[2].get('Host')
#     # if headerHostValue == None:
#     #     headerHostValue = reqestData[2].get('host')
#     headerHostValue = getDictFiledValue(headers, 'Host')
#     if ':' in headerHostValue:
#         remote_host, remote_port = headerHostValue.split(':')
#         remote_host = remote_host.strip()
#         remote_port = int(remote_port)
#     else:
#         remote_host = headerHostValue.strip()
#         remote_port = 80
#         # remote_port = 443 if request.startswith(b'CONNECT') else 80
#     return remote_host, remote_port
#
#
# # 处理http, 因为http都是明文, 无需处理证书问题, 最终目的直接将报文写入到sqlite数据库中
# # client_socket: 代理监听到的客户端的socket       data: 代理读取的来自client的请求报文
# # conn: 连接sqlite数据库的引用
# def handle_http(client_socket, addr, data, time_queue, https=False):
#     global request_counter
#     with lock:
#         # 全局计数器request_counter，默认值为0, 将request_counter当前值赋值给current_request_id
#         # current_request_id会作为参数写入到queue中, 而队列也会参照数字大小来提取接口
#         current_request_id = request_counter
#         request_counter += 1
#     # reqestData 是一个list, reqestData[0]: 全部报文包括行、头、体, bytes类型     reqestData[1]: 头的第一行, str类型
#     # reqestData[2]: 头, dict类型     reqestData[3]: 报文体, bytes类型
#     # reqestData = receive_all(client_socket, firstHttpReqData=data, isReqRes=True)
#     reqestData = receive_firstHttpReqData_request(client_socket, data)
#
#     with lock:
#         # 根据请求头, 获得host和端口
#         remote_host, remote_port = getHostPort(reqestData[2])
#     # 处理HTTP请求
#     remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     remote_socket.connect((remote_host, remote_port))
#     # 把处理好的, 从客户端发送的请求, 发送给真正的服务端
#     remote_socket.sendall(reqestData[0])
#     # responseData 是一个list,  responseData[0]: 全部报文包括行、头、体, bytes类型     responseData[1]: 头的第一行, str类型
#     # responseData[2]: 头, dict类型     responseData[3]: 报文体, bytes类型
#     # responseData = receive_all(remote_socket)
#     responseData = receive_response(remote_socket)
#     # 把处理好的, 从真服务端响应会的结果, 响应给客户端
#     client_socket.sendall(responseData[0])
#     screenShotTime = time_queue.get()
#     with lock:
#         # 将请求数据和唯一请求ID一起放入优先级队列
#         priority_queue.put((current_request_id, reqestData[1], reqestData[2], reqestData[3],
#                             responseData[1], responseData[2], responseData[3], screenShotTime))
#     # with lock:
#     #     # 解析http报文, 找出请求地址、请求方式、请求头、请求体、响应头、响应体等
#     #     # parseHttp(addr, conn, https)
#     #     parseHttp(addr, create_connection('C:\数据库\DataBase.db'), https)
#     while not priority_queue.empty():
#         request_id, firstLineHeaderReq, headerReq, rawReqBody, \
#         firstLineHeaderRes, headerRes, rawResBody, timeStamp = priority_queue.get()
#         parseHttp(addr, '', request_id, firstLineHeaderReq, headerReq, rawReqBody,firstLineHeaderRes, headerRes, rawResBody, timeStamp)
#
#     client_socket.close()
#     remote_socket.close()
#
#
#
# # https第一次连接, 会发送包含connect url 请求头, 这些并不是https发送的实际请求, 是建立https的必要步骤, 通过这一步, 先获得访问的地址和端口
# # data: 通过上一步读取的请求, bytes类型
# def clientHello(data):
#     # 通过\r\n\r\n, 切割出请求头
#     req_headers_raw, req_body_raw = data.split(b'\r\n\r\n', 1)
#     # 请求头转str
#     req_headers_str = req_headers_raw.decode('utf-8')
#     # 获得请求头集合 , req_headers_str[0]第一行为请求行
#     reqhead_list = req_headers_str.split('\r\n')
#     # 请求方法、请求地址、协议和版本
#     connect, urlPort, protocol = reqhead_list[0].split(' ')
#     url, port = urlPort.split(':', 1)
#     print('请求地址端口: ', urlPort)
#     return url, int(port)
#
#
# # 代理处理https, 解密https内容, 现在最终功能是将请求、响应报文写入到sqlite数据库中
# # client_socket: 代理监听到的客户端的socket     data: 初步获得报文数据, 因为https第一步握手, 不包含真正的通信的报文信息
# # conn: 连接sqlite数据库的引用
# def handle_https(client_socket, addr, data, time_queue, https=True):
#     global request_counter
#     with lock:
#         # 处理https第一步的报文信息, 非真正的https通信报文, 通过第一步获得url和端口
#         url, port = clientHello(data)
#         # 全局计数器request_counter，默认值为0, 将request_counter当前值赋值给current_request_id
#         # current_request_id会作为参数写入到queue中, 而队列也会参照数字大小来提取接口
#         current_request_id = request_counter
#         request_counter += 1
#
#     # 从目标服务器获取 CN 和 SAN
#     cn, san = get_cert_info(url, port)
#
#     # 接收客户端的 HTTPS 请求, 第一步要建立连接, 需要回复客户端已经连接了
#     client_socket.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
#     server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#     # context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
#     with lock:
#         # 使用提取到的 CN 和 SAN 生成伪造证书
#         fake_cert_file_path, private_key_path = create_fake_cert(url, cn, san)
#         # 加载证书、密钥
#         server_context.load_cert_chain(certfile=fake_cert_file_path, keyfile=private_key_path)
#
#         # 包装原client_socket, 升级为https, 当前socket为服务端
#         ssl_client_socket = server_context.wrap_socket(client_socket, server_side=True)
#     # 生成客户端socket, 访问client_socket访问的服务端地址
#     # with socket.create_connection((url, 443)) as remote_socket:
#     with socket.create_connection((url, port)) as remote_socket:
#         # client_context = ssl.create_default_context()
#         # 启用不安全的旧版握手支持
#         # client_context.options |= ssl.OP_LEGACY_SERVER_CONNECT
#         client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#         # 启用 TLS 1.0 和 TLS 1.1（通过清除禁用标志）
#         client_context.options &= ~ssl.OP_NO_TLSv1
#         client_context.options &= ~ssl.OP_NO_TLSv1_1
#         client_context.check_hostname = False  # 禁用主机名检查
#         client_context.verify_mode = ssl.CERT_NONE  # 忽略服务器证书验证
#         # # 修改其他兼容性设置
#         # client_context.options |= ssl.OP_NO_TLSv1
#         # client_context.options |= ssl.OP_NO_TLSv1_1
#         try:
#             with client_context.wrap_socket(remote_socket, server_hostname=url) as ssl_remote_socket:
#                 # 获得客户端发来的报文
#                 # client_request = receive_all(ssl_client_socket, isReqRes=True)
#                 client_request = receive_request(ssl_client_socket)
#                 # print(f"HTTPS Request:\n{client_request}\n")
#                 ssl_remote_socket.sendall(client_request[0])
#                 # 4. 接收服务器的响应
#                 # server_response = receive_all(ssl_remote_socket)
#                 server_response = receive_response(ssl_remote_socket)
#                 # print(f"HTTPS Request:\n{server_response}\n")
#                 # 5. 将响应返回给客户端
#                 ssl_client_socket.sendall(server_response[0])
#                 screenShotTime = time_queue.get()
#                 with lock:
#                     # 将请求数据和唯一请求ID一起放入优先级队列
#                     priority_queue.put((current_request_id, client_request[1], client_request[2], client_request[3],
#                                         server_response[1], server_response[2], server_response[3], screenShotTime))
#                     # # 更新优先级队列中的响应
#                     # update_in_queue(current_request_id, client_request[1], client_request[2], client_request[3],
#                     #                server_response[1], server_response[2], server_response[3])
#         except ssl.SSLError as e:
#             print(f"SSL 错误: {e}")
#         except ConnectionResetError as e:
#             print(f"连接重置错误: {e}")
#         except Exception as e:
#             print(f"其他错误: {e}")
#     while not priority_queue.empty():
#         request_id, firstLineHeaderReq, headerReq, rawReqBody, \
#         firstLineHeaderRes, headerRes, rawResBody, timeStamp = priority_queue.get()
#     # with lock:
#         # 解析请求、响应, 对请求、响应报文进行处理
#         # parseHttp(addr, conn, https)
#         # parseHttps(addr, create_connection('C:\数据库\DataBase.db'),request_id, firstLineHeaderReq, headerReq, rawReqBody,firstLineHeaderRes, headerRes, rawResBody, timeStamp)
#         parseHttps(addr, '', request_id, firstLineHeaderReq, headerReq, rawReqBody,firstLineHeaderRes, headerRes, rawResBody, timeStamp)
#     # 关闭连接
#     ssl_client_socket.close()
#
#
# # 方法处理, 从客户端发送的请求, 现只处理http和https请求
# # client_socket: 代理监听客户端获得的socket                addr: 客户端发送的地址    conn: 连接sqlite数据库的引用
# def handle_client(client_socket, addr, time_queue):
#     # try:
#         print(f"客户端地址端口 {addr}")
#         # client_socket连接客户端socket, 读取请求结果
#         data = client_socket.recv(4096)
#         # 获取请求头, 因为头可能很长, 没有出现头和体的分隔符, 也就是\r\n\r\n
#         # 因为切割是遇到的第一个\r\n\r\n, 那么如果等于1, 说明请求头没有读取完整, 更没法切割头和体
#         # 如果等于2, 说明\r\n\r\n出现了, 那么可以切割头和体了, 现在目的就是切出头, 体留着下边在处理, 因为while条件不能等于2, 所以不循环了
#         # 因为是碰到第一个\r\n\r\n, 开始切割, 那么不可能大于2
#         while len(data.split(b'\r\n\r\n', 1)) != 2:
#             data += client_socket.recv(4096)
#         # screenShotTime = time_queue.get()
#         # print('screenShotTime.......', screenShotTime)
#         # 处理HTTPS请求
#         if data.startswith(b'CONNECT'):
#             # 处理HTTPS请求
#             handle_https(client_socket, addr, data, time_queue, https=True)
#         else:
#             # 处理HTTP请求
#             handle_http(client_socket, addr, data, time_queue)
#     # except Exception as e:
#     #     print(f"Error handling client {addr}: {e}")
#     # finally:
#     #     client_socket.close()
#
#
#
# def mitm_proxy(time_queue):
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind(('127.0.0.1', 8081))
#     server_socket.listen(5)
#     print("Proxy server listening on port 8081")
#     while True:
#         client_socket, addr = server_socket.accept()
#         # 为每个客户端连接启动一个新线程
#         # client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, conn))
#         client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, time_queue))
#         client_thread.start()
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
# # 设置全局变量, 记录比对的初始时间
# global recordTime
# # 初次加载的默认初始时间
# recordTime = '2024-06-29 21:10:35.796266'
# # 鼠标键盘点击间隔
# interval = 1.5
# # 创建一个全局锁
# lock = threading.Lock()
# # 缓存证书密钥位置
# cert_cache = {}
# # 优先级队列
# priority_queue = queue.PriorityQueue()
# # 请求全局计数器
# request_counter = 0
#
#
# if __name__ == "__main__":
#
#     params = sys.argv[1:][0]  # 获取命令行参数
#     # print(params)
#     # params = '百度'
#     createAllDir = [f'{parent_dir}/testcase/{params}/数据库截图/截图/image',
#                     f'{parent_dir}/testcase/{params}/数据库截图/截图/label',
#                     f'{parent_dir}/testcase/{params}/数据库截图/数据库',
#                     f'{parent_dir}/mitm/temp_certificate_key']
#     # 遍历目录, 生成对应目录
#     for item_dir in createAllDir:
#         if not os.path.isdir(item_dir):
#             os.makedirs(item_dir)
#     print('当前测试系统,各测试类型文件夹生成完成!!!')
#     # 将报文数据存储到数据库的地址
#     globalDatabasePath = f'{parent_dir}/testcase/{params}/数据库截图/数据库/DataBase.db'
#     # 抓包使用的中间认证书和密钥
#     globalCertPath = f'{parent_dir}/mitm/temp_certificate_key/'
#     # globalScreenShotPath = 'C:/数据库/截图'
#
#     # 截图和点击位置存储的路径
#     # parentPath = parent_dir
#
#     # 判断数据库是否存在
#     if os.path.exists(globalDatabasePath):
#         conn = sqlite3.connect(globalDatabasePath, check_same_thread=False)
#     else:
#         open(globalDatabasePath, 'w').close()
#         sql_table_create = 'CREATE TABLE IF NOT EXISTS ACTIVITY (ID INTEGER PRIMARY KEY AUTOINCREMENT, LOCAL_SOURCE_IP, ' \
#                            'TARGET_URL, HTTP_METHOD, PROXY_TOOL, REQ_HEADERS, REQ_BODY, RES_HEADERS, RES_BODY, WORK_NUM, ' \
#                            'SAME_DIRECTORY, ENCRYPT_DECRYPT_KEY, SEND_DATETIME)'
#         conn = sqlite3.connect(globalDatabasePath, check_same_thread=False)
#         cursor = conn.cursor()
#         cursor.execute(sql_table_create)
#         cursor.close()
#         conn.commit()
#     conn.close()
#     from multiprocessing import Process, Queue
#
#     timestamp_queue = Queue()
#
#     # 启动监听进程
#     listener_process = Process(target=listener, args=(timestamp_queue,params))
#     listener_process.start()
#
#     # # 启动抓包进程
#     # packet_capture_process = Process(target=mitm_proxy, args=(timestamp_queue,))
#     # packet_capture_process.start()
#     mitm_proxy(timestamp_queue)



from util.yaml_util import read_yaml
import asyncio
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
from traffic.image_mitm_addon import saveToSQLite_image_traffic
from config import *


async def start_mitmproxy_async(redisPort,system, queue):
    # 读取获得globalConfig.yaml中的存储字段, 这个字段用来存放对应功能的黑名单、白名单
    globalConfigData = read_yaml(f"{ROOT_DIR}/config/globalConfig.yaml")
    global_proxy = globalConfigData.get('global_proxy')
    global_proxy_port = globalConfigData.get('global_proxy_port')
    # 配置 mitmproxy
    options = Options(
        listen_host=global_proxy,
        listen_port=int(global_proxy_port),
        ssl_insecure=True
    )
    mitm = DumpMaster(options)
    mitm.addons.add(saveToSQLite_image_traffic(redisPort,system))
    try:
        queue.put('启动抓包功能')
        await mitm.run()
    except KeyboardInterrupt:
        # print("MITMProxy 停止")
        await mitm.shutdown()
        queue.put('启动抓包功能停止！！！')


# 截图抓包功能, 启动抓包功能
# redisPort: 启动redis端口    system: 系统名
def start_listener(redisPort,system, queue):
    asyncio.run(start_mitmproxy_async(redisPort, system, queue))
