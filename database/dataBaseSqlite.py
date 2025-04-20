# -*- coding:utf-8 -*-
import sqlite3,os,json,sys
sys.stdout.reconfigure(encoding='utf-8')
# 当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上级目录
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
from util.utils import lineHeaderTypes, pytestHeaderType, check_json_format, getMultipartFormDataParams,getCoding


# 读取数据库可能出现编码问题，可能解决的方法
# import sys
# reload(sys)
# sys.setdefaultencode('utf-8')


# # 输入任意参数.如果是json格式会转成字典，并返回。如果不是json格式，会返回false
# # myjson：输入的类似json字符
# def check_json_format(myjson):
#     try:
#         json_dict = json.loads(myjson)
#         if isinstance(json_dict, dict):
#             return json_dict
#         else:
#             return False
#     except:
#         try:
#             json_dict = json.loads(json.dumps(myjson,ensure_ascii=False))
#             if isinstance(json_dict,dict):
#                 return json_dict
#             else:
#                 return False
#         except:
#             return False

# 输入一个list, 每个元素是数据库id值, 通过id值, 拼接出sql语句.
# 如果id_list为空, 返回值为None. 如果不为空, 返回一个set, 元素0为语句, 参数部分是占位符, 元素1是list, 也就是元素0中占位符对应的值
# id_list: 输入的list, 每个元素是数据库id
def generate_sql_query_safe(id_list):
    # 计算包含数据库ID的list
    idDate_len = len(id_list)
    # 不为0, 表示有数据
    if idDate_len != 0:
        placeholders = ", ".join(["?"] * idDate_len)  # 生成 (?, ?, ?, ?)
        sql = f"SELECT * FROM ACTIVITY WHERE ID IN ({placeholders})"
        return sql, id_list  # 返回 SQL 和参数列表
    else:
        return None


# 通过generate_sql_query_safe返回的值, 元素0就是sql语句, 元素1是参数, 进行数据库查询
# dataBasePath: 数据库地址    sql_search: generate_sql_query_safe返回的值, 元素0就是sql语句
# params: generate_sql_query_safe返回的值, 元素1是参数
def loadDataBase_ids(dataBasePath, sql_search, params):
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


# 对企业行政管理服务平台的报文，进行加密解密，通过python调用enAndDecrypt.js加解密，使用node命令，所以本地必须安装node
# 如果加密或者解密的字符串长度大于50000个字符，因为太大，会在本地自动生成decryptData.txt(自己配置路径，存储明文) 、
# encryptData(自己配置路径，存储密文)，作为临时文件，来进行加解密
# value : 需要加解密内容   encrptDecrypt：加密还是解密, True为加密，False为解密
# key: sm4密钥值   path : 为加解密的js路径
def sm4crypt_qiyexingzhengfuwuguanlipingtai(value,encrptDecrypt):
    key = '1234567896123450'
    path = "C:/Users/w08265/Desktop/enAndDecrypt.js"
    if len(value) > 10000:
        if encrptDecrypt:
            with open('C:\\Users\\w08265\\Desktop\\decryptData.txt', 'w', encoding='utf-8') as f:
                f.write(value)
            value = 'too-long'
            command = 'node -e  "require(\\"%s\\").initencrypt(%s,%s)"' % (path, "'" + key + "'", "'" + value + "'")
        else:
            with open('C:\\Users\\w08265\\Desktop\\encryptData.txt', 'w', encoding='utf-8') as f:
                f.write(value)
            value = 'too-long'
            command = 'node -e  "require(\\"%s\\").initdecrypt(%s,%s)"' % (path, "'" + key + "'", "'" + value + "'")
    else:
        if encrptDecrypt:
            value = json.dumps(value)
            command = 'node -e  "require(\\"%s\\").initencrypt(%s,%s)"' % (path, "'" + key + "'", "'" + value + "'")
        else:
            command = 'node -e  "require(\\"%s\\").initdecrypt(%s,%s)"' % (path, "'" + key + "'", "'" + value + "'")
    pipline = os.popen(command)
    return pipline.buffer.read().decode('utf-8')


def loadDataBase_ALL(dataBasePath):
    print(dataBasePath)
    splitName = os.path.splitext(dataBasePath)
    splitName_len = len(splitName) - 1
    if splitName[splitName_len] == '.db':
        # 读取sqlite数据
        db = sqlite3.connect(dataBasePath)
        # db.text_factory = lambda  x: str(x,'gbk','ignore')
        db.text_factory = str
        # 创建游标curson来执行execute SQL语句
        cursor = db.cursor()
        sql_search = 'select * from activity '
        # sql_search = 'SELECT *, (SELECT COUNT(*) FROM activity WHERE TARGET_URL LIKE \'%.baidu%\' ) AS total_count FROM activity WHERE TARGET_URL LIKE \'%.baidu%\' LIMIT 10 OFFSET 3 '
        # sql_search = 'SELECT *, (SELECT COUNT(*) FROM activity WHERE TARGET_URL LIKE \'%.baidu%\' AND REQ_HEADERS LIKE \'%https://www.baidu.com%\'  AND CAST(RES_BODY AS TEXT)  LIKE \'%15618241642915896384%\') AS total_count FROM activity WHERE TARGET_URL LIKE \'%.baidu%\' AND REQ_HEADERS LIKE \'%https://www.baidu.com%\' AND CAST(RES_BODY AS TEXT) LIKE \'%15618241642915896384%\'  LIMIT 10 OFFSET 0 '

        # 查询表明
        cursor.execute(sql_search)
        data = cursor.fetchall()
        cursor.close()
        db.close()
        return  data

# 根据输入的字段, 和存储在对应字段下的值是否包含value, 来进行查询数据库
# dataBasePath: 数据库地址       field: sqlite的表activity中的字段      value: 包含的值, 包含的值会查询出来
def loadDataBase_fieldValue_ALL(dataBasePath, field, value):
    # splitName = os.path.splitext(dataBasePath)
    # splitName_len = len(splitName) - 1
    # if splitName[splitName_len] == '.db':
    if dataBasePath.endswith('.db') :
        # 读取sqlite数据
        db = sqlite3.connect(dataBasePath)
        # db.text_factory = lambda  x: str(x,'gbk','ignore')
        db.text_factory = str
        # 创建游标curson来执行execute SQL语句
        cursor = db.cursor()
        sql_search = 'select * from activity where ' + field + ' LIKE \'%' + value + '%\' '
        # 查询表明
        cursor.execute(sql_search)
        data = cursor.fetchall()
        cursor.close()
        db.close()
        print('数据库查询方式 : 所有数据(loadAll)')
        return  data


def loadDataBase_Many(dataBasePath, num, beginEndId, dataTime):
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
            print(f'数据库查询方式 : 一条数据, ID为{num}')
        elif beginEndId !='' and beginEndId != []:
            sql_search = 'select * from activity where id between {} and {}'.format(beginEndId[0], beginEndId[1])
            print(f'数据库查询方式 : ID区间, 开始{beginEndId[0]}, 结束{beginEndId[1]}')
        elif dataTime !='' or dataTime != []:
            # sql_search = 'select * from activity where SEND_DATETIME >={}  and SEND_DATETIME <={} '.format(dataTime[0],
            #                                                                                         dataTime[1])
            sql_search = 'select * from activity where SEND_DATETIME BETWEEN  {}  and {} '.format(dataTime[0],
                                                                                                           dataTime[1])
            print(f'数据库查询方式 : 时间区间, 开始{dataTime[0]}, 结束{dataTime[1]}')
        # 查询表明  SEND_DATETIME
        cursor.execute(sql_search)
        data = cursor.fetchall()
        cursor.close()
        db.close()
        return  data

def updateDataBase(dataBasePath, field, content, id):
    # try:
        # 读取sqlite数据
        db = sqlite3.connect(dataBasePath)
        db.text_factory = str
        # 创建游标curson来执行execute SQL语句
        cursor = db.cursor()
        # sql_update = 'update activity set {}={} where id={}'.format(field, content, id)
        sql_update = 'update activity set ' + field + '=' + '"'+ content + '"' +  '  where id=' + str(id)
        print(sql_update)
        # 查询表明
        cursor.execute(sql_update)
        db.commit()
        cursor.close()
        db.close()
        return '完成更新'
    # except Exception:
    #     print('连接失败或者更新失败')
    #     return '更新失败'

import re


def parse_multipart_form_data(body):
    # 从请求报文的开头提取 boundary（通常在报文开始的第一行）
    boundary_match = re.search(rb'--([^\r\n]+)', body)
    if not boundary_match:
        raise ValueError("无法找到 boundary")

    boundary = boundary_match.group(1)

    # 使用 boundary 分割报文的不同部分
    parts = body.split(b'--' + boundary)

    parsed_data = {
        'files': [],
        'fields': {}
    }

    for part in parts:
        # 跳过空的和结束符部分
        if not part or part == b'--' or part == b'--\r\n':
            continue

        # 分割 header 和 body（文件或字段内容）
        try:
            headers, body = part.split(b'\r\n\r\n', 1)
        except ValueError:
            continue  # 处理无效的部分

        # 提取文件名、字段名
        headers_str = headers.decode(errors='ignore')
        disposition = re.search(r'Content-Disposition: form-data; name="([^"]+)"(; filename="([^"]+)")?', headers_str)

        if not disposition:
            continue

        field_name = disposition.group(1)
        filename = disposition.group(3)

        if filename:
            # 这是文件部分
            filename = filename.strip()

            # 获取文件的Content-Type
            content_type_match = re.search(r'Content-Type: ([^;\r\n]+)', headers_str)
            content_type = content_type_match.group(1) if content_type_match else 'application/octet-stream'

            # 清除文件末尾的 \r\n-- 或者 \r\n
            file_content = body.rstrip(b'\r\n--')

            # 保存文件信息
            parsed_data['files'].append({
                'field_name': field_name,
                'filename': filename,
                'content_type': content_type,
                'file_content': file_content
            })
        else:
            # 这是普通字段部分
            value = body.strip(b'\r\n').decode()
            # 如果字段是重复的，使用列表存储所有值
            if field_name in parsed_data['fields']:
                if isinstance(parsed_data['fields'][field_name], list):
                    parsed_data['fields'][field_name].append(value)
                else:
                    parsed_data['fields'][field_name] = [parsed_data['fields'][field_name], value]
            else:
                parsed_data['fields'][field_name] = value

    return parsed_data

def save_file(file_info, output_dir):
    # 创建输出目录（如果不存在）
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 确定文件的保存路径
    filename = file_info['filename']
    full_path = os.path.join(output_dir, filename)

    # 如果文件名重复，添加一个后缀来避免覆盖
    base, ext = os.path.splitext(full_path)
    counter = 1
    while os.path.exists(full_path):
        full_path = f"{base}_{counter}{ext}"
        counter += 1

    # 将二进制文件内容保存到指定文件
    with open(full_path, 'wb') as f:
        f.write(file_info['file_content'])

    print(f"文件已保存为: {full_path}")
    return full_path


# if __name__ == '__main__':
#
#
#     path = r'E:\PyCharm_Community_Edition_2020.2.1_Project\auttaNative\testcase\上传文件测试\数据库截图\数据库\DataBase.db'
#
#     data = loadDataBase_Many(path, 4, '', '')
#     for item in data :
#         print(item[2])
#         print(type(item[6]),item[6])
#         print(item[7])
#         print(item[8])
#
#     from urllib import parse
#
#     params = parse.urlparse('https://go.microsoft.com/fwlink/?linkid=2171760&bucket=100')
#     # 剔除? , 只保留原始请求地址
#     new_url = params.scheme + '://' + params.netloc + params.path
#     print(new_url)




















