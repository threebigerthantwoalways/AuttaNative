import sqlite3
import json
import redis
from config import *
from mitmproxy.http import HTTPFlow
from threading import Lock

# 截图抓包功能, 启动抓包功能使用的插件, 用来将报文写入到数据库中
class saveToSQLite_image_traffic :
    def __init__(self, redisPort, system):
        self.db_dir = os.path.join(ROOT_DIR, 'testcase', f'{system}','数据库截图','数据库')
        self.db_path = os.path.join(ROOT_DIR, 'testcase', f'{system}','数据库截图','数据库','DataBase.db')
        self.redisPort = redisPort
        self.redis_image_traffic = redis.Redis(host="localhost", port=self.redisPort, decode_responses=True)
        # 临时存储请求数据，key 为 flow.id
        self.pending_flows = {}
        self.lock = Lock()  # 线程锁保护数据库操作
        # 初始化数据库
        self.init_db()


    def init_db(self):
        if os.path.exists(self.db_path) :
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        else:
            # 初始化文件夹, 初始化数据库
            if not os.path.exists(self.db_path):
                if os.path.exists(self.db_dir):
                    open(self.db_path, 'w').close()
                else:
                    os.makedirs(self.db_dir, exist_ok=True)
                    open(self.db_path, 'w').close()
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            with self.conn:
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS ACTIVITY (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        LOCAL_SOURCE_IP TEXT,
                        TARGET_URL TEXT,
                        HTTP_METHOD TEXT,
                        BURP_TOOL TEXT DEFAULT 'proxy',
                        REQ_HEADERS TEXT,
                        REQ_BODY BLOB,
                        RES_HEADERS TEXT,
                        RES_BODY BLOB,
                        WORK_NUM TEXT DEFAULT '工程师',
                        SAME_DIRECTORY TEXT DEFAULT 'mulu',
                        ENCRYPT_DECRYPT_KEY TEXT DEFAULT 'key',
                        SEND_DATETIME TEXT
                    )
                ''')

    def request(self, flow: HTTPFlow):
        """处理 HTTP 请求"""
        self.process_traffic(flow, is_request=True)

    def response(self, flow: HTTPFlow):
        """处理 HTTP 响应"""
        self.process_traffic(flow, is_request=False)

    def process_traffic(self, flow: HTTPFlow, is_request: bool):
        """
                处理流量数据。
        """
        try:
            if is_request:
                """处理流量并写入数据库"""
                try:
                    timestamp = self.redis_image_traffic.get('timestamp')
                    print(f"从 Redis 读取: {timestamp} -> {timestamp}")
                except redis.exceptions.ConnectionError as e:
                    print(f"无法读取 Redis: {e}")
                # 请求数据处理
                self.pending_flows[flow.id] = {
                    "LOCAL_SOURCE_IP": flow.client_conn.peername[0],
                    "TARGET_URL": flow.request.url,
                    "HTTP_METHOD": flow.request.method,
                    "REQ_HEADERS": json.dumps(dict(flow.request.headers)),
                    "REQ_BODY": self.process_body(flow.request.content, flow.request.headers),
                    "SEND_DATETIME": timestamp,  # 时间戳需要从外部获取
                }
            else:
                # 响应数据处理
                if flow.id in self.pending_flows:
                    # 更新响应相关字段
                    self.pending_flows[flow.id].update({
                        "RES_HEADERS": json.dumps(dict(flow.response.headers)),
                        "RES_BODY": self.process_body(flow.response.content, flow.response.headers)
                    })
                    # 将完整数据存储到数据库
                    self.insert_to_db(self.pending_flows.pop(flow.id))
                else:
                    print(f"无法匹配响应，flow.id: {flow.id}")
        except Exception as e:
            print(f"处理流量时出错: {e}")


    def process_body(self, body: bytes, headers: dict) -> bytes | str:
        """处理请求体或响应体，根据 Content-Type 决定存储方式"""
        if not body:
            return None

        content_type = headers.get("Content-Type", "").lower()
        if any(ct in content_type for ct in ["text/plain", "text/html", "application/json", "application/xml"]):
            # 如果是文本类型，直接存储为字符串
            return body.decode("utf-8", errors="ignore")
        elif any(ct in content_type for ct in [
            "application/octet-stream", "application/zip", "image/gif", "image/jpeg", "image/png",
            "application/msword", "application/vnd.ms-excel", "application/pdf"
        ]):
            # 如果是文件类型，存储为 bytes
            return body
        else:
            # 默认作为字符串存储
            return body.decode("utf-8", errors="ignore")

    def insert_to_db(self, data: dict):
        with self.lock:  # 线程安全操作
            """
            插入数据到 SQLite 数据库。
            """
            try:
                self.conn.execute('''
                    INSERT INTO ACTIVITY (
                        LOCAL_SOURCE_IP, TARGET_URL, HTTP_METHOD, REQ_HEADERS,
                        REQ_BODY, RES_HEADERS, RES_BODY, SEND_DATETIME
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.get("LOCAL_SOURCE_IP"),
                    data.get("TARGET_URL"),
                    data.get("HTTP_METHOD"),
                    data.get("REQ_HEADERS"),
                    data.get("REQ_BODY"),
                    data.get("RES_HEADERS"),
                    data.get("RES_BODY"),
                    data.get("SEND_DATETIME"),
                ))
                self.conn.commit()
            except Exception as e:
                print(f"数据库插入失败: {e}")

    def done(self):
        """
        关闭数据库连接。
        """
        self.conn.close()

# addons = [
#     SaveToSQLite(r"E:\PyCharm_Community_Edition_2020.2.1_Project\auttaNative\mitm\traffic.db")  # 数据库路径
# ]

# import datetime
# from cryptography import x509
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.primitives import serialization
#
# # 1. 加载 CA 证书和私钥
# with open("E:/PyCharm_Community_Edition_2020.2.1_Project/auttaNative/mitm/temp_certificate_key/root_ca.pem", "rb") as ca_cert_file:
#     ca_cert_bytes = ca_cert_file.read()
#     ca_cert = x509.load_pem_x509_certificate(ca_cert_bytes, default_backend())
#
# with open("E:/PyCharm_Community_Edition_2020.2.1_Project/auttaNative/mitm/temp_certificate_key/root_ca_key.pem", "rb") as ca_key_file:
#     ca_private_key = serialization.load_pem_private_key(
#         ca_key_file.read(),
#         password=None,  # 如果私钥有密码，这里设置
#         backend=default_backend()
#     )
#
# # 2. 生成私钥
# private_key = rsa.generate_private_key(
#     public_exponent=65537,
#     key_size=2048,
#     backend=default_backend()
# )
#
# # 3. 生成 CSR
# csr = x509.CertificateSigningRequest.build(
#     builder=x509.CertificateSigningRequestBuilder()
#     .subject_name(x509.Name([
#         # 添加证书的主体信息，如国家、组织、部门等
#         x509.NameAttribute(x509.oid.NameOID.COUNTRY_NAME, u"CN"),
#         x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, u"TestMitmn"),
#         x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, u"your.domain.com")
#     ]))
#     .add_extension(
#         x509.BasicConstraints(ca=False, path_length=None),
#         critical=True
#     )
#     .sign(private_key, hashes.SHA256(), default_backend())
# )
#
# # 4. 使用 CA 证书签发叶子证书
# certificate = x509.CertificateBuilder().subject_name(
#     csr.subject
# ).issuer_name(
#     ca_cert.subject
# ).public_key(
#     private_key.public_key()
# ).serial_number(
#     x509.random_serial_number()
# ).not_valid_before(
#     datetime.utcnow()
# ).not_valid_after(
#     datetime.utcnow() + datetime.timedelta(days=365)
# ).add_extension(
#     x509.BasicConstraints(ca=False, path_length=None),
#     critical=True
# ).sign(ca_private_key, hashes.SHA256(), default_backend())
#
# # 5. 保存叶子证书
# with open("certificate.pem", "wb") as f:
#     f.write(certificate.public_bytes(encoding=serialization.Encoding.PEM))