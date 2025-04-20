import os,sys,time,re, logging, openpyxl, json
sys.stdout.reconfigure(encoding='utf-8')
# 当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上级目录
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
# from ruamel import yaml
from util.yaml_util import read_yaml
from ast import literal_eval
from util import globalValue
from config import *
from ruamel.yaml import YAML

extension_map = {
        'text/plain': '.txt',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/msword': '.doc',
        'application/vnd.ms-excel': '.xls',
        'application/pdf': '.pdf',
        'image/png': '.png',
        'image/jpeg': '.jpeg',
        'image/jpg': '.jpg',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/zip': '.zip',
        'application/x-gzip': '.gz',
        'application/x-rar-compressed': '.rar',
        'image/gif': '.gif',
        'application/vnd.ms-powerpoint': '.ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
    }


#在响应体中获得每个字典中2个字段对应的值，将获得的两个值存入字典，再将字典存入list中，return回去这个list集合
# 响应报文: body = {{"aaa":"111","bbb":"222"},{"aaa":"333","bbb":"444"}}，使用getKeyValue(body,'aaa','bbb')以后，获得的值为[ {"111":"222"} , {"333":"444"} ]
#jsonStr:json字符串
#param1:想获得的值对应的字段
#param2:想获得的值对应的字段
def getKeyValue(jsonStr, param1, param2):
    data= []
    for item in json.loads(jsonStr):
        paramData= {}
        paramValue1= item[param1]
        paramValue2= item[param2]
        paramAllVaule= {paramValue1: paramValue2}
        paramData.update(paramAllVaule)
        data.append(paramData)
    return data

#在响应体中获得每个字典中1个字段对应的值。将获得的这个值进行切割分成两个值。将两个值存入字典，再将字典存入list中，return回
#jsonStr:json字符串
#param1:想获得的值对应的字段
#param2:开始分割符号
#param3:结束分割符号,如果无可以为空，""
def getKey(jsonStr, param1, param2, param3):
    data= []
    for item in json.loads(jsonStr):
        paramData= {}
        paramValue1= item[param1]
        paramValueSplit= paramValue1.split(param2)
        split0= paramValueSplit[0]
        split1= paramValueSplit[1]
        paramAllVaule= {split0: split1[0:len(split1)-1]}
        paramData.update(paramAllVaule)
        data.append(paramData)
    # print('打印data开始')
    # print(data)
    # print('打印data结束')
    return data

# 给方法参数一个list，例如:[{'aaa':'111','bbb':'222','ccc':'333','ddd':'444'},{'aaa':'555','bbb':'666','ccc':'777','ddd':'888'}]，
# 再给参数字段，可以输入多个。会响应一个list回来，里边是字段对应的值。例如:[['111', '555'], ['222', '666'], ['333', '777'], ['444', '888']]
# body:报文体，或者list数据
# *param:代表可以输入多个字段。例如: getAllValue(body, 'aaa','bbb','ccc','ddd') ，返回的值为:[['111', '555'], ['222', '666'], ['333', '777'], ['444', '888']]
def getAllKeyValue(body, *param):
    data= []
    for item_body in json.loads(body):
        item_data = []
        # print('打印param开始')
        # print(type(param))
        # print(param)
        # print('打印param结束')
        for item_field in  param:
            item_value = item_body[item_field]
            if item_value:
                item_data.append(item_value)
        data.append(item_data)
    return data

# 修改了getAllKeyValue，修改了参数不使用*param
# 给方法参数一个list，例如:[{'aaa':'111','bbb':'222','ccc':'333','ddd':'444'},{'aaa':'555','bbb':'666','ccc':'777','ddd':'888'}]，
# 再给参数字段，可以输入多个。会响应一个list回来，里边是字段对应的值。例如:[['111', '555'], ['222', '666'], ['333', '777'], ['444', '888']]
# body:报文体，或者list数据
# *param:代表可以输入多个字段。例如: getAllValue(body, 'aaa','bbb','ccc','ddd') ，返回的值为:[['111', '555'], ['222', '666'], ['333', '777'], ['444', '888']]
def getAllKeyValueUpdate(body, param):
    data = []
    for item_body in json.loads(body):
        item_data = []
        for item_field in param:
            item_value = item_body[item_field]
            if item_value:
                item_data.append(item_value)
        data.append(item_data)
    return data



#新添加，方法返回一个 [] ，通过key查找到的对应value值
# body:可以为json，或者 [{},{},{}]
# key:为{}中的字段
def getListMap_OneKeyVlue(body,key):
    data = []
    for item_body in json.loads(body):
        item_value = item_body[key]
        if item_value:
            data.append(item_value)
    return data


#添加、替换get请求ulr的字段中的值
#url: 请求url
#field: 需要修改的字段
#value: 需要修改成的值
#isSql: 默认为False,这种情况下会替换字段后的值。如果是True，会把值添加在原值的后边，不会改变原值。
def changeGetUrlFieldValue(url, field, value, isSql=False):
    partUrl = url.split('?')[1]
    fieldNum = str_all_index(partUrl, field)
    if len(fieldNum) != 1:
        for item in fieldNum:
            fieldLen = len(field)
            if partUrl[item + fieldLen] in '=':
                Num1 = partUrl.index('=', item)
                Num2 = partUrl.index('&', item)
                if isSql==True:
                    urlChange = url.split('?')[0] + '?' + str(partUrl[:Num2]) + ' ' + str(value) + str(partUrl[Num2:])
                else:
                    urlChange = url.split('?')[0] + '?' + str(partUrl[:Num1 + 1]) + str(value) + str(partUrl[Num2:])
    else:
        if '=' in partUrl and '&' in partUrl:
            Num1 = partUrl.index('=', fieldNum[0])
            if '&' in partUrl[fieldNum[0]:]:
                Num2 = partUrl.index('&', fieldNum[0])
                haveAnd = True
            else:
                Num2 = partUrl.index('&', fieldNum[0] - 1)
                haveAnd = False
            if isSql == True:
                urlChange = url.split('?')[0] + '?' + str(partUrl[:Num2]) + ' ' + str(value) + str(partUrl[Num2:])
            else:
                if haveAnd:
                    urlChange = url.split('?')[0] + '?' + str(partUrl[:Num1 + 1]) + str(value) + str(partUrl[Num2:])
                else:
                    urlChange = url.split('?')[0] + '?' + str(partUrl[:Num1 + 1]) + str(value)  # + partUrl[Num2:]
        if '=' in partUrl and '&' not in partUrl:
            Num1 = partUrl.index('=', fieldNum[0])
            if isSql == True:
                urlChange = url.split('?')[0] + '?' + str(partUrl[:]) + ' ' + str(value)
            else:
                urlChange = url.split('?')[0] + '?' + str(partUrl[:Num1 + 1]) + str(value)

    return  urlChange

#查询出入参数，在字符中位置，将位置存入list中返回
#str_ : 提供的字符串
#field: 在字符串中，寻找的值
def str_all_index(str_, field):
    index_list = []
    start = 0
    while True:
        x = str_.find(field, start)
        if x > -1:
            start = x + 1
            index_list.append(x)
        else:
            break
    return index_list

# 处理str，返回一个int或者float，用于进行加减计算
def strChangeIntFloat(*args):
    if '.' in args[0]:
        body = float(args[0])
    else:
        body = int(args[0])
    return body

# 输入两个数字，整形、浮点型都可以，将两个数相加，函数返回一个str类型
# num1: 输入数字，整形、浮点型都可以
# num2: 输入数字，整形、浮点型都可以
def strChangeIntFloatUpdate(str,num):
    if '.' in str:
        body = float(str)
        if isinstance(num, float):
            body = body + num
        if isinstance(num, int):
            body = body + float(num)
    else:
        body = int(str)
        if isinstance(num, float):
            body = body + int(num)
        if isinstance(num, int):
            body = body + num
    return body

def writeText(res,url,requestmethod,requestHeader,requestBody,path):
    requestHeader = json.dumps(requestHeader)
    with open(path, "a" ) as f:
        if requestmethod=='get':
            f.writelines(url+'\n')
            requestHeader = json.dumps(requestHeader)
            f.writelines(requestHeader)
            f.writelines('\n')
            f.writelines(res)
            f.writelines('\r\n')
        if requestmethod=='post':
            f.writelines(url+'\n')
            f.writelines(requestHeader)
            f.writelines('\n')
            requestBody = json.dumps(requestBody)
            f.writelines(requestBody)
            f.writelines('\n')
            f.writelines(res)
            f.writelines('\r\n')

# 通过模板生成yaml文件,yaml文件就是读取的接口文档
# templatePath ， 模板的地址
# filePath , 生成的的yaml文件地址
# num，对模板的内容，复制成多少个，存入到新yaml文件中
def templateWriteYaml(templatePath,filePath,num):
    num = int(num)
    yaml = YAML()
    if num<=1:
        with open(filePath, 'a', encoding='utf-8') as wf:
            data = read_yaml(templatePath)
            # yaml.dump(data, stream=wf, encoding='utf-8', Dumper=yaml.RoundTripDumper, allow_unicode=True)
            yaml.dump(data, wf)
            # yaml.dump(data, stream=wf, encoding='utf-8', Dumper=yaml.RoundTripDumper)
            # wf.write(yaml.dump(data, Dumper=yaml.RoundTripDumper, allow_unicode=True))
    elif num>1:
        for i in range(num):
            with open(filePath, 'a', encoding='utf-8') as wf:
                data = read_yaml(templatePath)
                # yaml.dump(data, stream=wf, encoding='utf-8', Dumper=yaml.RoundTripDumper, allow_unicode=True)
                yaml.dump(data, wf)
                # yaml.dump(data, stream=wf, encoding='utf-8', Dumper=yaml.RoundTripDumper)
                # wf.write(yaml.dump(data, Dumper=yaml.RoundTripDumper, allow_unicode=True))



# 输入任意参数.如果是json格式会转成字典，并返回。如果不是json格式，会返回false
# myjson：输入的类似json字符
def check_json_format(myjson):
    if isinstance(myjson, dict):
        return myjson
    else:
        try:
            json_dict = json.loads(myjson)
            if isinstance(json_dict, dict):
                return json_dict
            else:
                json_dict = json.loads(json.dumps(myjson, ensure_ascii=False))
                if isinstance(json_dict, dict):
                    return json_dict
                else:
                    return False
        except:
            try:
                json_dict = json.loads(json.dumps(myjson,ensure_ascii=False))
                if isinstance(json_dict,dict):
                    return json_dict
                else:
                    return False
            except:
                return False

# 对企业行政管理服务平台的报文，进行加密解密，通过python调用enAndDecrypt.js加解密，使用node命令，所以本地必须安装node
# 如果加密或者解密的字符串长度大于10000个字符，因为太大，会在本地自动生成decryptData.txt(自己配置路径，存储明文) 、
# encryptData(自己配置路径，存储密文)，作为临时文件，来进行加解密
# value : 需要加解密内容   encrptDecrypt：加密还是解密, True为加密，False为解密
# key: sm4密钥值   path : 为加解密的js路径
def sm4crypt_qiyexingzhengfuwuguanlipingtai(value,encrptDecrypt):
    key = '1234567896123450'
    path = "C:/Users/w08265/Desktop/enAndDecrypt.js"
    if len(value) > 10:
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


# 这个方法针对pytest脚本的前置、后置功能，编写的方法
# 判断burp插件存入到数据库中的请求、响应头中是否包含content-type，并通过application/json、application/x-www-form-urlencoded、
# text/html 判断出报文的格式
# headers：burp插件中存储的请求、响应头
def pytestHeaderType(headers):

    # headList = headers[1:len(headers)-1].split(',')
    # 新插件用这个分割
    headList = headers[1:len(headers)-1].split('\n')
    result = lineHeaderTypes(headList)
    return result

def dict2LineList(dic):
    lineList = []
    for item in dic.keys():
        lineList.append(item + ': '+dic.get(item))
    return lineList


def lineHeaderTypes(headList):
    result = 'post-json'
    for item_header in headList:
        item_header = item_header.lower()
        if 'content-type' in item_header and ':' in item_header and 'application/json' in item_header:
            result = 'post-json'
        elif 'content-type' in item_header and ':' in item_header and 'application/x-www-form-urlencoded' in item_header:
            result = 'post-form-urlencoded'
        elif 'content-type' in item_header and ':' in item_header and 'text/html' in item_header:
            result = 'text/html'
        elif 'content-type' in item_header and ':' in item_header and 'text/plain' in item_header:
            result = 'text/plain'
        elif 'content-type' in item_header and ':' in item_header and 'text/xml' in item_header:
            result = 'text/xml'
        elif 'content-type' in item_header and ':' in item_header and 'image/gif' in item_header:
            result = 'image/gif'
        elif 'content-type' in item_header and ':' in item_header and 'image/jpeg' in item_header:
            result = 'image/jpeg'
        elif 'content-type' in item_header and ':' in item_header and 'image/png' in item_header:
            result = 'image/png'
        elif 'content-type' in item_header and ':' in item_header and 'application/pdf' in item_header:
            result = 'application/pdf'
        elif 'content-type' in item_header and ':' in item_header and 'application/msword' in item_header:
            result = 'application/msword'
        elif 'content-type' in item_header and ':' in item_header and 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in item_header:
            result = 'application/msword'
        elif 'content-type' in item_header and ':' in item_header and 'application/vnd.ms-excel' in item_header:
            result = 'application/vnd.ms-excel'
        elif 'content-type' in item_header and ':' in item_header and 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in item_header:
            result = 'application/vnd.ms-excel'
        elif 'content-type' in item_header and ':' in item_header and 'application/zip' in item_header:
            result = 'application/zip'
        elif 'content-type' in item_header and ':' in item_header and 'application/x-gzip' in item_header:
            result = 'application/x-gzip'
        elif 'content-type' in item_header and ':' in item_header and 'application/x-rar-compressed' in item_header:
            result = 'application/x-rar-compressed'
        elif 'content-type' in item_header and ':' in item_header and 'application/vnd.ms-powerpoint' in item_header:
            result = 'application/vnd.ms-powerpoint'
        elif 'content-type' in item_header and ':' in item_header and 'application/vnd.openxmlformats-officedocument.presentationml.presentation' in item_header:
            result = 'application/vnd.ms-powerpoint'
        elif 'content-type' in item_header and ':' in item_header and 'application/octet-stream' in item_header:
            result = 'application/octet-stream'
        elif 'content-type' in item_header and ':' in item_header and 'multipart/form-data' in item_header and 'boundary=' in item_header:
            boundary = ''
            for item_header_inside in headList:
                if 'content-type' in item_header_inside.lower() and ':' in item_header_inside.lower() and 'boundary=' in item_header_inside.lower():
                    boundary = item_header_inside.split('boundary=')[1]
                    break
            result = 'multipart/form-data', boundary
        # elif 'accept-ranges' in item_header and ':' in item_header and 'bytes' in item_header:
        #     result = 'bytes'
    return result


# 解析multipart/form-data中请求体中的数据，包括filename、name、content-type 对应的值
# 返回值为str 或者 dict。如果是返回str,说明返回的是二进制文件，或者上传字段对应的值
# 如果返回的是dict，自定义字段'file-contentType'为上传文件类型，'fieldName'为上传字段的名
# 'uploadName'为文件组包上传使用的文件名, 'uploadFilename'文件本身的名字
# 方法中的参数 :  line, 表示报文中截取中的一行,为str
def parseMutipartFormData(line):
    parseResult = ''
    # line = line.lower()
    # 这个方法针对 multipart/form-data中请求体对内容的解析 , 处理文件上传部分 ,如果出现的文件部分响应结果
    # Content-Disposition: form-data; name="file"; filename="chrome.png" 针对报文中这种格式
    if 'Content-Disposition' in line and ':' in line and 'form-data' in line and \
            'name=' in line and 'filename=' in line :
        name = ''
        filename = ''
        element = line.split(';')
        # 通过 ; 截取成list
        for el in element:
            # 判断是否有name= 这个是上传文件的字段, filename= 是文件名
            if 'name=' in el.strip() and 'filename=' not in el.strip():
                el = el.strip()
                name = el.split('name=')[1]
                name = name[1:len(name) - 1]
            elif 'filename=' in el.strip():
                filename = el.split('filename=')[1]
                filename = filename[1:len(filename) - 1]
        parseResult = { 'file-fieldName': name, 'file-uploadFileName': filename}
    # Content-Disposition: form-data; name="id" 针对报文中这种格式
    elif 'Content-Disposition' in line and ':' in line and 'form-data' in line and \
            'name=' in line and 'filename=' not in line :
        name = ''
        element = line.split(';')
        # name= 代表字段, 下边紧跟着就是对应的value
        for el in element:
            if 'name=' in el.strip() :
                el = el.strip()
                name = el.split('name=')[1]
                name = name[1:len(name) - 1]
        parseResult = {'fieldName': name}
    # Content-Type: text/plain 针对报文中格式
    elif 'Content-Type' in line and ':' in line and 'Content-Disposition' not in line and \
            'form-data' not in line and 'name=' not in line and 'filename=' not in line :
        temp = []
        temp.append(line)
        result = lineHeaderTypes(temp)
        if isinstance(result, tuple):
            parseResult = {'file-contentType': result[0]}
        elif isinstance(result, str):
            parseResult = {'file-contentType': result}
    else:
        parseResult = line
    return parseResult



# 解析multipart/form-data的请求体, 将文件上传字段、文件名、文件类型、字段及对应的值
# 将解析出的值，放到dict中，返回dict。dict中'file-fieldName'为上传文件中的字段, 'file-contentType'为文件类型
# 'file-uploadFileName'为文件上传名
# body: multipart/form-data格式的上传文件的请求体
def getMultipartFormDataParams(body):
    # 因为是上传文件的流量，请求体中按照bytes存储，转成str
    # byte2Str = str(itemLog[6], encoding='gbk')
    # 切割str请求体，先通过 \r\n 按照每行切割出boudary, 再通过boudary切割出两个boudary之间的请求体信息
    splitBoundary = body.split(body.split('\r\n')[0])
    # all = []
    temp = {}
    # 把切割好的两个boudary之间的请求体，按照每组取出来
    for boundaryContent in splitBoundary:
        # 因为协议的原因，每组请求体中会有空行，空行不处理
        if boundaryContent == '': continue
        # 将这组里的请求体，按照\r\n切割，按照梅钢提取
        splitBoundaryList = boundaryContent.strip().split('\r\n')
        isFile = False
        isField = False
        fiedValue = ''
        fileStr = ''
        # temp = {}
        # 取出每个list中的元素，也就是每行请求体
        for num, lineContent in enumerate(splitBoundaryList):
            if lineContent == '': continue
            # 解析multipart/form-data中请求体中的数据，包括filename、name、content-type 对应的值
            # 返回值为str 或者 dict。如果是返回str,说明返回的是二进制文件，或者上传字段对应的值
            # 如果返回的是dict，自定义字段'file-content-type'为上传文件类型，'fieldName'为上传字段的名
            # 'uploadName'为文件组包上传使用的文件名, 'uploadFilename'文件本身的名字
            # 方法中的参数 :  line, 表示报文中截取中的一行,为str
            result = parseMutipartFormData(lineContent)
            if isinstance(result, dict) :
                uploadFieldName = result.get('file-fieldName')
                uploadFileName = result.get('file-uploadFileName')
                fileContentType = result.get('file-contentType')
                fieldName = result.get('fieldName')
                # Content-Disposition: form-data; name="fileName888" 针对类似这种格式
                if fieldName != None and uploadFieldName == None and uploadFileName == None and fileContentType == None :
                    temp[fieldName] = ''
                    isField = True
                # Content-Disposition: form-data; name="id" 针对报文中这种格式
                elif fieldName == None and uploadFieldName != None and uploadFileName != None and fileContentType == None :
                    temp['file-fieldName'] = uploadFieldName
                    temp['file-uploadFileName'] = uploadFileName
                    isFile = True
                # Content-Type: image/png 针对报文中这种格式
                elif fieldName == None and uploadFieldName == None and uploadFileName == None and fileContentType != None:
                    temp['file-contentType'] = fileContentType
                # else:
                #     fileType = temp.get('file-contentType')
                #     if fileType != None :
                #         if fileType in ['image/gif', 'image/jpeg', 'image/png', 'application/pdf','application/msword',
                #                         'application/vnd.ms-excel','application/octet-stream']:
                #             logging.info('是二进制文件')
                #             print('是二进制文件')
                #         else:
                #             if num == len(splitBoundaryList) + 1 :
                #                 for key in temp.keys():
                #                     if key not in ['file-fieldName', 'file-uploadFileName', 'file-contentType'] and \
                #                             temp.get(key) == '' :
                #                         temp[key] = fiedValue + str(result)
                #             else:
                #                 fiedValue += str(result)
                #     else:
                #         if num == len(splitBoundaryList) + 1:
                #             for key in temp.keys():
                #                 if key not in ['file-fieldName', 'file-uploadFileName', 'file-contentType'] and \
                #                         temp.get(key) == '':
                #                     temp[key] = fiedValue + str(result).strip()
                #         else:
                #             fiedValue += str(result).strip()
            elif isinstance(result, str) :
                if isField :
                    if num + 1 == len(splitBoundaryList):
                        for key in temp.keys():
                            if key not in ['file-fieldName', 'file-uploadFileName', 'file-contentType'] and \
                                    temp.get(key) == '':
                                temp[key] = result.strip()
                    # else:
                    #     fiedValue += str(result).strip()
                elif isFile :
                    fileType = temp.get('file-contentType')
                    if fileType != None:
                        if fileType in ['image/gif', 'image/jpeg', 'image/png', 'application/pdf', 'application/msword',
                                        'application/vnd.ms-excel', 'application/octet-stream']:
                            logging.info('是二进制文件')
                            if fileStr == '' :
                                fileStr = result + '\r\n'
                            else:
                                fileStr = fileStr + result + '\r\n'
                        else:
                            if num == len(splitBoundaryList) + 1:
                                for key in temp.keys():
                                    if key not in ['file-fieldName', 'file-uploadFileName', 'file-contentType'] and \
                                            temp.get(key) == '':
                                        temp[key] = fiedValue + str(result)
                            else:
                                fiedValue += str(result)
        if fileStr != '' :
            temp['file-fileStr'] = fileStr
    return temp


# 判断burp插件存入到数据库中的请求、响应头中是否包含content-type，并通过application/json、application/x-www-form-urlencoded、
# text/html 判断出报文的格式
# headers：burp插件中存储的请求、响应头
def headerType(headers):
    result = []
    headList = headers[1:len(headers)-1].split(',')
    # 新插件用这个分割
    # headList = headers[1:len(headers)-1].split('\n')
    for item_header in headList:
        item_header = item_header.lower()
        if 'content-type' in item_header and ':' in item_header and 'application/json' in item_header:
            result.append('json')
        elif 'content-type' in item_header and ':' in item_header and 'application/x-www-form-urlencoded' in item_header:
            result.append('x-www-form-urlencoded')
        elif 'content-type' in item_header and ':' in item_header and 'text/html' in item_header:
            result.append('text/html')
        elif 'content-type' in item_header and ':' in item_header and 'application/javascript' in item_header:
            result.append('application/javascript')
    return result


# 从请求体中获得json报文，按照字段和值的格式，存入到yaml文件中
# body : 请求体、响应体, json     content : 读取的收集成数据的Yaml表，是个字典
def readBodyIntoDict(body,content, isRes):
    # body_json = json.loads(body)
    for key in body.keys():
        listOrDict_writeYaml(key, body.get(key), content, isRes)
    return content


# list或者dict格式的数据，写入到content中
# field : 这层的字段   fieldValue： 这层的字段对应的value   content : 读取的收集成数据的Yaml表，dict格式
# isRes : 写true会对前的值进行标注，说明是响应报文拿到的数据。如果写false，说明是从请求报文中拿到的数字
def listOrDict_writeYaml(field, fieldValue, content, isRes):
    if isinstance(fieldValue, dict):
        for key in fieldValue.keys():
            # fieldValue.get(key)
            listOrDict_writeYaml(key, fieldValue.get(key), content, isRes)
    elif isinstance(fieldValue, list):
        for item in fieldValue:
            listOrDict_writeYaml(field, item, content, isRes)
    else:
        # 设置一个变量默认状态 fieldValue 不是list
        isList = False
        try:
            if '{' in str(fieldValue) and '}' in str(fieldValue):
                # 判断是不是dict
                isDict = check_json_format(fieldValue)
            else:
                isDict = False
        except:
            # print('str值不是dict')
            logging.info('str值不是dict')
        if isDict and isinstance(isDict, dict):
            # 如果是dict, 再去调用本方法
            for key in isDict.keys():
                listOrDict_writeYaml(key, isDict.get(key), content, isRes)
            isDict = True
        else:
            try:
                if '[' in str(fieldValue) and ']' in str(fieldValue):
                    # 如果不是dict, 判断下是否是list
                    isList = literal_eval(fieldValue)
                    if not isinstance(isList, list) and '[' not in str(isList) and ']' not in str(isList):
                        # if '[' not in str(isList) and ']' not in str(isList) :
                        isList = False
            except:
                # print('str值不是list')
                logging.info('str值不是list')
            # 是list，再调用本方法进行处理
            if isList and isinstance(isList, list):
                for item in isList:
                    listOrDict_writeYaml(field, item, content, isRes)
                isList = True
        # 既不是dict也不是list, 也就是str这时候再处理
        if not isDict and not isList:
            # 获得black_autosavefield中的字段黑名单, 这里边存储的字段如果和当前字段一样, 那不再会将值存储到dataConfig.yaml中
            black_autosavefield = content[0].get('black_autosavefield')
            # 默认都是存储的, 也就是true
            save = True
            # 遍历黑名单中的
            for item in black_autosavefield:
                # 如果当前field和存储黑名单中的字段相同, save=False也就是不再保存这个字段下的数据, 并且break退出循环
                if item == field:
                    save = False
                    break
            # 如果没有在存储黑名单中, 那进行字段对应值的存储处理
            if save:
                # yaml读取出dict，判断现在的字段是否存在与字典中。没有为None
                value = content[1].get(field)
                # reqBodyValue = value.get(fieldValue)
                # 传进来的key所对应的值
                bodyValue = fieldValue
                # 获得dataConfig.yaml中的autosavefield_limit, 这个值限制存储进字段对应的值的长度
                autosavefield_limit = content[0].get('autosavefield_limit')
                if autosavefield_limit != '':
                    try:
                        autosavefield_limit = int(autosavefield_limit)
                        # autosavefield_limit 如果为int, 进行比较大小必须小于等于autosavefield_limit
                        if len(value) < autosavefield_limit:
                            # 不存存储的字段, 为None
                            if value == None:
                                newField = content[0].get('newField')
                                if field not in newField:
                                    newField.append(field)
                                if bodyValue == '':
                                    content[1][field] = []
                                else:
                                    temp = []
                                    if isRes:
                                        temp.append('/**/下面的值是从响应报文提取数据/**/')
                                        temp.append(bodyValue)
                                    else:
                                        temp.append(bodyValue)
                                    content[1][field] = temp
                            else:
                                if bodyValue != '' and bodyValue != None and bodyValue not in value:
                                    if isRes:
                                        value.append('/**/下面的值是从响应报文提取数据/**/')
                                        value.append(bodyValue)
                                    else:
                                        value.append(bodyValue)
                                    content[1][field] = value
                    except:
                        # autosavefield_limit = ''
                        # print('autosavefield_limit输入有问题,无法转为int')
                        logging.info('autosavefield_limit输入有问题,无法转为int')
                else:
                    # autosavefield_limit 可能为 '' , 无需比较autosavefield_limit, 也是就是所有数据存储到dataConfig.yaml中
                    # if autosavefield_limit == '' :
                    # 不存存储的字段, 为None
                    if value == None:
                        newField = content[0].get('newField')
                        if field not in newField:
                            newField.append(field)
                        if bodyValue == '':
                            content[1][field] = []
                        else:
                            temp = []
                            if isRes:
                                temp.append('/**/下面的值是从响应报文提取数据/**/')
                                temp.append(bodyValue)
                            else:
                                temp.append(bodyValue)
                            content[1][field] = temp
                    else:
                        if bodyValue != '' and bodyValue != None and bodyValue not in value:
                            if isRes:
                                value.append('/**/下面的值是从响应报文提取数据/**/')
                                value.append(bodyValue)
                            else:
                                value.append(bodyValue)
                            content[1][field] = value


# 针对自动存储urlFieldValue到yaml的方法
# 从请求体中获得json报文，按照字段和值的格式，存入到yaml文件中
# body : 请求体、响应体, dict     content : 读取的收集成数据的Yaml表，是个字典
# isRes: 是否将写入到yaml的数据中, 标注数据来源于响应。False, 不写。True, 写
def readBodyIntoDict_auto(body, content, isRes):
    # 遍历获得dict中所有key, 也就是字段
    for key in body.keys():
        listOrDict_writeYaml_auto(key, body.get(key), content, isRes)
    return content


# 针对自动存储urlFieldValue到yaml的方法
# list或者dict格式的数据，写入到content中
# field : 这层的字段   fieldValue：这层的字段对应的value      content : 读取的收集成数据的Yaml表，dict格式
# isRes : 写true会对前的值进行标注，说明是响应报文拿到的数据。如果写false，说明是从请求报文中拿到的数字
def listOrDict_writeYaml_auto(field, fieldValue, content, isRes):
    if isinstance(fieldValue, dict):
        # 如果fieldValue是dict, 获得dict中的每个key和value, 再调用方法listOrDict_writeYaml_auto判断value值得类型
        for key in fieldValue.keys():
            listOrDict_writeYaml_auto(key, fieldValue.get(key), content, isRes)
    elif isinstance(fieldValue, list):
        for item in fieldValue:
            listOrDict_writeYaml_auto(field, item, content, isRes)
    else:
        # 设置一个变量默认状态 fieldValue 不是list
        isList = False
        try:
            # 转fieldValue为str, 去掉前后空格等, 判断第一个字符和最后一个字符, 是否是‘{’ , '}'
            fieldValue_strip = str(fieldValue).strip()
            if fieldValue_strip != '' and fieldValue_strip[0] == '{' and \
                    fieldValue_strip[len(fieldValue_strip)-1] == '}':
                # 判断是不是dict
                isDict = check_json_format(fieldValue)
            else:
                isDict = False
        except:
            # print('str值不是dict')
            logging.info('str值不是dict')

        # 如果是dict, 需要递归当前方法, 再处理dict, 直到为str为止
        if isDict and isinstance(isDict, dict):
            # 是dict, 获得dict中字段, 再去调用本方法
            for key in isDict.keys():
                listOrDict_writeYaml_auto(key, isDict.get(key), content, isRes)
            isDict = True
        else:
            # 不是dict, 判断下是否是list
            try:
                if fieldValue_strip[0] == '[' and fieldValue_strip[len(fieldValue_strip)-1] == ']':
                    # 如果不是dict, 判断下是否是list, 转换下是否是list
                    isList = literal_eval(fieldValue)
                    isList_str = str(isList)
                    # 如果符合条件, 那不是list
                    if not isinstance(isList, list) and \
                            not isList_str[0] == '[' and not isList_str[len(isList_str)-1] == ']':
                        isList = False
            except:
                # print('str值不是list')
                logging.info('str值不是list')
            ##############################********对list判断有些问题****###########################################
            # 是list，再调用本方法进行处理
            if isList and isinstance(isList, list):
                for item in isList:
                    listOrDict_writeYaml_auto(field, item, content, isRes)
                isList = True
            ##############################********对list判断有些问题****###########################################
        # 既不是dict也不是list, 也就是str这时候再处理
        if not isDict and not isList:
            # yaml读取出dict，判断现在的字段是否存在与字典中。没有为None
            value = content.get(field)
            # 不存存储的字段, 为None
            if value == None:
                if fieldValue == '':
                    content[field] = ['']
                else:
                    temp = []
                    if isRes:
                        temp.append('/**/下面的值是从响应报文提取数据/**/')
                        temp.append(fieldValue)
                    else:
                        temp.append(fieldValue)
                    content[field] = temp
            else:
                if fieldValue != '' and fieldValue != None :
                    if isRes:
                        value.append('/**/下面的值是从响应报文提取数据/**/')
                        value.append(fieldValue)
                    else:
                        value.append(fieldValue)
                    content[field] = value





# 将数据存储到excel中
def save_data_excel_singleSheet(title_data, target_list, output_file_name, sheet):
    if not output_file_name.endswith('.xlsx'):
        output_file_name += '.xlsx'
    if os.path.exists(output_file_name):
        wb = openpyxl.load_workbook(output_file_name)
        if sheet not in wb.sheetnames:
            wb.create_sheet(sheet)
        ws = wb[sheet]
    else:
        wb = openpyxl.Workbook()
        wb.create_sheet(sheet)
        ws = wb[sheet]
    target_list.insert(0, title_data)
    rows = len(target_list)
    lines = len(target_list[0])
    for i in range(rows):
        for j in range(lines):
            ws.cell(row= i + 1, column= j + 1).value = target_list[i][j]
    wb.save(filename=output_file_name)
    target_list.pop(0)





# 在于Yaml的url黑名单里，和方法里提供的参数url是否相同. 如果在黑名单中返回Flase，如果不存在返回True
# url: 为报文中原请求url
# urlBlock: 在yaml文件中漏洞被分类，这个是关于某个涉及url的黑名单名字 是一个list
def isInBlockUrl(url, urlBlock):
    block = True
    if len(urlBlock) != 0 and url != '':
        for item_urlBlock in urlBlock:
            if item_urlBlock == url :
                block = False
                break
    return block



# 判断提供的一条头信息，在于Yaml的header黑名单里，是否包含在这条头信息里. 如果在黑名单中返回Flase，如果不存在返回True
# url: 为报文中原请求url  header：一条头信息
# headerBlock: 在yaml文件中漏洞被分类，这个是关于某个涉及header的黑名单名字  是一个list
def isInBlockHeader(url, header, headerBlock):
    block = True
    # 两种黑名单写法,  使用{'url':['字段']} . 另一种['字段1','字段2']
    useUrlDict = False
    if len(headerBlock) != 0:
        for item_headerBlock in headerBlock:
            if item_headerBlock == '': continue
            data = check_json_format(item_headerBlock)
            if isinstance(data, dict):
                for key in data.keys():
                    if key == url:
                        useUrlDict = True
                        key_value_headerBlock = data.get(key)
                        for item_key_value_headerBlock in key_value_headerBlock:
                            if item_key_value_headerBlock in header:
                                block = False
                                break
                    if not block:
                        break
            if not block:
                break
        if not useUrlDict:
            for item_headerBlock in headerBlock:
                if isinstance(item_headerBlock, str) and item_headerBlock != '':
                    if item_headerBlock in header:
                        block = False
                        break
    return block


# 在于Yaml的field的黑名单里，和方法里提供的field是否相同. 如果在黑名单中返回Flase，如果不存在返回True
# url: 为报文中原请求url     field: 为原报文中的一个字段
# fieldBlock: 在yaml文件中漏洞被分类，这个是关于某个涉及field的黑名单名字  是个list
def isInBlockField(url, field, fieldBlock):
    block = True
    # 两种黑名单写法,  使用{'url':['字段']} . 另一种['字段1','字段2']
    useUrlDict = False
    # 黑名单不能为空, 需要判断的字段也不能为空, 为空block返回默认值True
    if len(fieldBlock) != 0 and block and field != '':
        # 遍历黑名单
        for item_fieldBlock in fieldBlock:
            if item_fieldBlock == '': continue
            # 校验是否是dict, 也就是判断哪种填写的模式
            data = check_json_format(item_fieldBlock)
            # 如果是dict, 说明是{'url':['字段']}
            if isinstance(data, dict):
                # 遍历所有的key, 也就是黑名单中的url
                for key in data.keys():
                    # 黑名单中的url等于和当前报文url相同
                    if key == url:
                        # 获得黑名单中的字段
                        key_value_fieldBlock = data.get(key)
                        # 存储字段的是list, 遍历list
                        for item_key_value_fieldBlock in key_value_fieldBlock:
                            item_key_value_fieldBlock = item_key_value_fieldBlock.strip()
                            # 如果黑名单中的字段和当前报文字段相同, 不再处理['字段1','字段2']这种模式
                            # 并且退出各种循环, 不需要再判断了
                            if item_key_value_fieldBlock == field:
                                useUrlDict = True
                                block = False
                                break
                    if not block:
                        break
            if not block:
                break
        # 当前报文url没有匹配到这种模式{'url':['字段']}
        if not useUrlDict:
            # 也就是当前黑名单是这样['字段1','字段2'], 遍历黑名单中的字段
            for item_fieldBlock in fieldBlock:
                # 判断输入是否是str, 黑名单配置都是用str
                if isinstance(item_fieldBlock, str) and item_fieldBlock != '':
                    item_fieldBlock = item_fieldBlock.strip()
                    # 如果相同block为False, 也就是包含在黑名单中, 同时退出循环
                    if item_fieldBlock == field:
                        block = False
                        break
                if not block:
                    break
    return block


# 在于Yaml的field的黑名单里，和方法里提供的field是否相同. 如果在黑名单中返回Flase，如果不存在返回True
# url: 为报文中原请求url     field: 为原报文中的一个字段   value: 需要处理的原字段field对应的值
# fieldBlock: 是dataConfig.yaml中关于某个涉及field的黑名单名字  是个list
# 黑名单, blackList_save_from_filter_sensitive, 格式如下:
# [ {'url1': {'字段1': [value1,value2] } }, {'url2': {'字段1': [value1,value2], '字段2': [value1,value2] } } ]
def isInBlockField_whiteBlackList(url, field, fieldBlock, value):
    block = True
    # 黑名单不能为空, 需要判断的字段也不能为空, 为空block返回默认值True
    if len(fieldBlock) != 0 and block and field != '':
        # 遍历黑名单
        for item_fieldBlock in fieldBlock:
            # 如果为false, 代笔在黑名单, 不需要再判断了直接跳出循环
            if not block:
                break
            # 为空跳过, 循环下一个
            if item_fieldBlock == '': continue
            # 校验是否是dict, 也就是判断哪种填写的模式
            data = check_json_format(item_fieldBlock)
            if isinstance(data, dict):
                # 遍历所有的key, 也就是黑名单中的url
                if url in list(data.keys()):
                    # 黑名单中的key也就是url存在和当前报文url相同的值, 通过url查询出当前黑名单Url下的字段和对应的值
                    fieldAndValue = data.get(url)
                    # 遍历所有的key, 也就是黑名单中当前url中的字段
                    if field in list(fieldAndValue.keys()):
                        # 通过字段获得, 对应字段的value值, 也就是字段对应值得黑名单
                        valueList = fieldAndValue.get(field)
                        # 判断原报文中字段对应得值是否, 包含在的黑名单单中, 在黑名单设置为block为False
                        if value in valueList:
                            block = False
            else:
                print('使用黑白名单测试敏感信息, 配置的黑名单 '+init_blackList_save_from_filter_sensitive+' 格式不对')
    return block



# 把sqlite中存储的headers，转为list存储, 并返回值
# headers：sqlite存储的headers
def formatLogHeaders(headers):
    headersList = []
    for num, item in enumerate(headers[1:len(headers) - 1].split('\n')):
        if num == 0:
            headersList.append(item)
        else:
            if item != '' and item != '\n':
                headersList.append(item[1:].strip())
    return headersList


# formatLogHeaders方法，将存储在sqlite中的头信息转成了list
# 本方法将生成的list，转成dict。例子: ['Server: nginx']  ----> {'Server':'nginx'}
def listHeaderChangDict(headerList):
    headerDict = {}
    # 第一个元素不是头消息，是请求行
    for num, item_header in enumerate(headerList):
        if num != 0:
            orginLen = len(item_header)
            changeLen = len(item_header.replace(':', ''))
            if orginLen - changeLen == 1:
                item =  item_header.split(':')
                headerDict[item[0]] = item[1].strip()
            else:
                firstLeft = item_header.index(':')
                headerDict[item_header[:firstLeft]] = item_header[firstLeft+1 :].strip()

    return headerDict




# 将java的时间戳，转换为时间
# timeStamp: 整型，java生成的时间戳。例如: 1695627901181
def javaTimeStampChangeTime(timeStamp):
    timeStamp = timeStamp / 1000
    timeArray = time.localtime(timeStamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)


def ms_to_hours(millis):
    sec = int(millis)
    if sec >= 1000:
        second = (sec / 1000) % 60
        seconds = int(second)
        minute = (sec/ (1000*60)) % 60
        minutes = int(minute)
        hours = (sec / (1000 * 60 * 60)) % 24
        formateTime = '%d 小时 %d 分钟 %d 秒' %(hours, minutes, seconds)
    else:
        formateTime = '%d 毫秒' %(sec)
    return formateTime



# python 默认都是unicode, 使用encode进行编码成gbk或者utf-8, 编码同时python3会将unicode变成bytes
# 使用decode将已经变成bytes转成unicode, 也就相当于str
# 获取编码格式, 类型有unicode、 gbk 、unf-8
def getCoding(strInput):
    if isinstance(strInput, str):
        return 'unicode'
    try:
        strInput.decode("utf8")
        return 'utf8'
    except:
        pass
    try:
        strInput.decode("gbk")
        return 'gbk'
    except:
        pass

# 通过__init__.py中的变量, 获得限制攻击负载的长度, 并将原有的攻击负载减少到限制的长度, 返回list
# type_limit: 限制哪种测试类型的攻击负载    yamlName: 在payload文件夹下的yaml攻击负载名
def limit_formatData(type_limit, yamlName):
    formateDataAll_global_dataConfigYaml = globalValue.get_value('global_dataConfigYaml')
    payload_limit = formateDataAll_global_dataConfigYaml[0].get(type_limit)
    if payload_limit == '':
        dataList = read_yaml(ROOT_DIR + '/payload/' + yamlName)
    else:
        try:
            payload_limit = int(payload_limit)
            if payload_limit >= 0:
                if payload_limit == 0:
                    payload_limit = 1
                dataList = read_yaml(ROOT_DIR + '/payload/' + yamlName)
                dataList = dataList[:payload_limit]
            else:
                dataList = read_yaml(ROOT_DIR + '/payload/' + yamlName)
        except Exception:
            dataList = read_yaml(ROOT_DIR + '/payload/' + yamlName)
    return dataList


# 通过__init__.py中的变量, 获得限制攻击负载的长度, 并将原有的攻击负载减少到限制的长度, 返回list
# type_limit: 限制哪种测试类型的攻击负载    listPayload: list格式的一串攻击负载
def limit_formatData_payload(type_limit, listPayload):
    formateDataAll_global_dataConfigYaml = globalValue.get_value('global_dataConfigYaml')
    payload_limit = formateDataAll_global_dataConfigYaml[0].get(type_limit)
    if payload_limit == '':
        dataList = listPayload
    else:
        try:
            payload_limit = int(payload_limit)
            if payload_limit >= 0:
                if payload_limit == 0:
                    payload_limit = 1
                dataList = listPayload
                dataList = dataList[:payload_limit]
            else:
                dataList = listPayload
        except Exception:
            dataList = listPayload
    return dataList


def valid_xml_char_ordinal(c):
    codepoint = ord(c)
    # conditions ordered by presumed frequency
    return (
        0x20 <= codepoint <= 0xD7FF or
        codepoint in (0x9, 0xA, 0xD) or
        0xE000 <= codepoint <= 0xFFFD or
        0x10000 <= codepoint <= 0x10FFFF
        )

# 查询全局变量或者对应系统的存储参数, 如: 存储数据库地址, 过滤的host地址, 存储的数据库加载方式
# 如果systemName为空, 查询的是当前测试系统的存储数据库地址, 过滤的host地址, 存储的数据库加载方式
# 如果systemName不为空, 查询的是systemName的存储数据库地址, 过滤的host地址, 存储的数据库加载方式
# systemName: 系统名称    field: 输入的查询字段
def readDataFieldValue_fromDataConfig(systemName, field):
    # 系统名为空, 说明需要查询保存环境信息
    if systemName != '' :
        dataConfig = read_yaml(ROOT_DIR + '/config/' + systemName + 'dataConfig.yaml')
        if isinstance(field, list):
            for item in field :
                fieldValue = dataConfig[0].get(item)
                if item == init_dataBasePath :
                    print('系统名<<' + systemName + '>>已存储的自动化测试使用数据库地址: ', fieldValue)
                elif item == init_filterUrl :
                    print('系统名<<' + systemName + '>>已存储的过滤host地址: ', fieldValue)
                elif item == init_loadDataBaseType :
                    print('系统名<<' + systemName + '>>已存储的数据库加载方式: ', fieldValue)
        # elif isinstance(field, str):
        #     fieldValue = dataConfig[0].get(field)
        #     if field == 'storeDataBasePath':
        #         print('系统名<<' + systemName + '>>保存的数据库地址: ', fieldValue)
        #     elif field == 'storeDataBasePath':
        #         print('系统名<<' + systemName + '>>已设置自动化测试使用数据库地址: ', fieldValue)
        #     elif field == 'filterUrl':
        #         print('系统名<<' + systemName + '>>设置的过滤host地址: ', fieldValue)
        #     elif field == 'loadDataBaseType':
        #         print('系统名<<' + systemName + '>>设置的数据库加载方式: ', fieldValue)
        #     elif field == 'loadDataBaseMany_id':
        #         print('系统名<<' + systemName + '>>设置的条件查询一条id数据: ', fieldValue)
        #     elif field == 'loadDataBaseMany_range':
        #         print('系统名<<' + systemName + '>>设置的条件查询id区间的数据: ', fieldValue)
        #     elif field == 'loadDataBaseMany_time':
        #         print('系统名<<' + systemName + '>>设置的条件查询时间区间的数据: ', fieldValue)
    else:
        # 系统名为空, 说明查询测试系统信息
        globalConfig = read_yaml(ROOT_DIR + '/config/' + 'globalConfig.yaml')
        if isinstance(field, list):
            for item in field:
                if item == 'global_testSystem':
                    # 获得全局变量存储的测试系统名
                    global_testSystem_value = globalConfig.get(item)
                    print('测试系统: ', global_testSystem_value)
                    # 获得存储的系统配置
                    dataConfig = read_yaml(ROOT_DIR + '/config/' + global_testSystem_value + 'dataConfig.yaml')
                    print('系统名<<' + global_testSystem_value + '>>测试使用数据库地址: ', dataConfig[0].get(init_dataBasePath))
                    print('系统名<<' + global_testSystem_value + '>>测试过滤host地址: ', dataConfig[0].get(init_filterUrl))
                    print('系统名<<' + global_testSystem_value + '>>测试数据库加载方式: ', dataConfig[0].get(init_loadDataBaseType))
                    print('自动化工具建立过的测试系统: ', globalConfig.get(init_global_allTestedSystem))
        # elif isinstance(field, str):
        #     fieldValue = globalConfig.get(field)
        #     if field == 'storeDataBasePath':
        #         print('测试系统保存的数据库地址: ', fieldValue)
        #     elif field == 'storeDataBasePath':
        #         print('测试系统已设置自动化测试使用数据库地址: ', fieldValue)
        #     elif field == 'filterUrl':
        #         print('测试系统设置的过滤host地址: ', fieldValue)
        #     elif field == 'loadDataBaseType':
        #         print('测试系统设置的数据库加载方式: ', fieldValue)
        #     elif field == 'loadDataBaseMany_id':
        #         print('测试系统设置的条件查询一条id数据: ', fieldValue)
        #     elif field == 'loadDataBaseMany_range':
        #         print('测试系统设置的条件查询id区间的数据: ', fieldValue)
        #     elif field == 'loadDataBaseMany_time':
        #         print('测试系统名设置的条件查询时间区间的数据: ', fieldValue)
    # return fieldValue


# 对dataConfig.yaml中的元素0中的字段赋值
# systemName: 系统名  field: 对应的字段   value:字段对应的值
def appendDataConfigValue(systemName, field, value):
    yaml = YAML()
    # 因为当前方法要获得用户输入的2个参数, 但是如果操作全局的测试环境, 只要一个参数即可, 多以value可能为空就是对globalConfig.yaml操作
    if value == '' :
        path = ROOT_DIR + '/config/' + 'globalConfig.yaml'
        globalConfig = read_yaml(path)
        # 原本是获得用户2个参数，现在是获得1个, 也就是sytemName实际就是value
        globalConfig[field] = systemName
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # f.write(yaml.dump(globalConfig, Dumper=yaml.RoundTripDumper, allow_unicode=True))
                yaml.dump(globalConfig, f)
            print('已将值存储到' + field + '字段中')
        except Exception:
            print('存储到dataConfig.yaml失败')
    else:
        if ',' in value:
            value = value.split(',')
        path = ROOT_DIR + '/config/' + systemName + 'dataConfig.yaml'
        dataConfig = read_yaml(path)
        # 添加判断,如果yaml中字段对应的值是list,那么按照append添加到list中, 如果对应值为str, 直接是替换
        if isinstance(dataConfig[0][field], list) :
            dataConfig[0][field].append(value)
        else:
            dataConfig[0][field] = value
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # f.write(yaml.dump(dataConfig, Dumper=yaml.RoundTripDumper, allow_unicode=True))
                yaml.dump(dataConfig, f)
                print('已将值存储到' + field + '字段中')
        except Exception:
            print('存储到dataConfig.yaml失败')

# # 专门针对测试使用数据库地址, 对dataBasePath赋值
# # systemName: 系统名    value: 写入的数据库地址,如果是int,那么实际上是取出storeDataBasePath中存储的对应位置值,如果是str，直接赋值
# def appendDataBasePath_fromDataConfig(systemName, value):
#     value = int(value)
#     if value =='' :
#         print('输入错误,添加的值为空')
#     else:
#         path = ROOT_DIR + '/config/' + systemName + 'dataConfig.yaml'
#         dataConfig = read_yaml(path)
#         if isinstance(value, int) :
#             storeDataBasePath_list = dataConfig[0].get('storeDataBasePath')
#             dataConfig[0]['dataBasePath'] = storeDataBasePath_list[value]
#         try:
#             with open(path, 'w', encoding='utf-8') as f:
#                 f.write(yaml.dump(dataConfig, Dumper=yaml.RoundTripDumper, allow_unicode=True))
#                 print('已将值存储到dataConfig.yaml的dataBasePath字段中')
#         except Exception:
#             print('存储到dataConfig.yaml失败')

# 对dataConfig.yaml中loadDataBaseMany_类型的输入值的写入
# systemName: 系统名  field: 对应的字段   value:字段对应的值  kind:类型
def appendDataConfigValue_loadDataBaseMany(systemName, field, value, kind):
    if value == '' :
        print('输入错误,添加的值为空')
    else:
        path = ROOT_DIR + '/config/' + systemName + 'dataConfig.yaml'
        dataConfig = read_yaml(path)
        # fieldValue = dataConfig[0].get(field)
        if kind == 'lmi' :
            dataConfig[0][field] = value
            dataConfig[0]['loadDataBaseType'] = 'lmi'
        elif kind == 'lmr' :
            if ',' in value:
                value = value.split(',')
                dataConfig[0][field] = value
                dataConfig[0]['loadDataBaseType'] = 'lmr'
            else:
                print('输入值为id区间范围,请使用英文逗号分割数字!!!')
        elif kind == 'lmt' :
            if ',' in value:
                value = value.split(',')
                dataConfig[0][field] = value
                dataConfig[0]['loadDataBaseType'] = 'lmt'
            else:
                print('输入值为时间区间范围,请使用英文逗号分割数字!!!')
    try:
        yaml = YAML()
        with open(path, 'w', encoding='utf-8') as f:
            # f.write(yaml.dump(dataConfig, Dumper=yaml.RoundTripDumper, allow_unicode=True))
            yaml.dump(dataConfig, f)
            print('已将值存储到dataConfig.yaml的 ' + field + ' dataBasePath字段中')
    except Exception:
        print('存储到dataConfig.yaml失败')


# 对dataConfig.yaml中的元素0中的字段赋值, 直接赋值str
# systemName: 系统名  field: 对应的字段   value:字段对应的值
def appendDataConfigValue_filterUrl(systemName, field, value):
    yaml = YAML()
    # 因为当前方法要获得用户输入的2个参数, 但是如果操作全局的测试环境, 只要一个参数即可, 多以value可能为空就是对globalConfig.yaml操作
    if value == '' :
        path = ROOT_DIR + '/config/' + 'globalConfig.yaml'
        globalConfig = read_yaml(path)
        # 原本是获得用户2个参数，现在是获得1个, 也就是sytemName实际就是value
        globalConfig[field] = systemName
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # f.write(yaml.dump(globalConfig, Dumper=yaml.RoundTripDumper, allow_unicode=True))
                yaml.dump(globalConfig, f)
            print('已将值存储到' + field + '字段中')
        except Exception:
            print('存储到dataConfig.yaml失败')
    else:
        path = ROOT_DIR + '/config/' + systemName + 'dataConfig.yaml'
        dataConfig = read_yaml(path)
        dataConfig[0][field] = value
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # f.write(yaml.dump(dataConfig, Dumper=yaml.RoundTripDumper, allow_unicode=True))
                yaml.dump(dataConfig, f)
                print('已将值存储到' + field + '字段中')
        except Exception:
            print('存储到dataConfig.yaml失败')



# 输入dict数据, 根据way来匹配白名单, 剔除不在白名单中的字段, 并将剔除后的dict数据返回
# dictBody: dict格式,请求、响应体     whiteFieldList: 白名单    way: 处理方式     url: 当前报文dict对应的url
# 返回值:  dict数据, 被剔除非白名单中字段
def onlyWhiteKey_inBody(dictBody, whiteFieldList, way, url, model):
    # 判断是否是dict, 并将处理后的值返回给dictBody
    dictBody,isList,isDict = formatDictList(dictBody)
    # dictBody非{}
    if dictBody != {} :
        # 获得dictBody中所有字段
        for dict_key in list(dictBody.keys()):
            # 判断当前字段是否在白名单中
            if not inWhite(dictBody , dict_key, whiteFieldList, way, url):
                # 获得当前字段对应的值
                dict_key_value = dictBody.get(dict_key)
                # 判断是否是dict或者list, 并将处理后的值返回给dict_key_value
                dict_key_value,isList,isDict = formatDictList(dict_key_value)
                # 调用方法, 处理当前的value值
                handle(dictBody, dict_key, dict_key_value, whiteFieldList, way, url, model)
            else:
                # 当前字段存在于白名单中
                # 查询当前测试类型下, 字段对应的value值的限制长度
                value_length_limited = model_createcaseLengthLimit(model)
                if haveFieldInDict(dictBody, dict_key) and \
                        len(str(dictBody.get(dict_key))) > int(value_length_limited):
                    # 字段不在对应白名单url对应的list中, 报文剔除这个字段
                    dictBody.pop(dict_key)
    return dictBody



# 处理dict_key_value, 按照list、dict、其他进行分类处理
# dictBody: onlyWhiteKey_inBody中的dictBody        dictBody_key: onlyWhiteKey_inBody中的传过来的字段, 例: dict_key
# dict_key_value: onlyWhiteKey_inBody中字段对应的值, 例: dict_key_value
# whiteFieldList: 白名单                way: 处理字段是否在白名单中的方式      model: 测试类型(数字)
def handle(dictBody, dictBody_key, dict_key_value, whiteFieldList, way, url, model):
    # 如果dict_key_value为dict
    if isinstance(dict_key_value, dict):
        # 如果dict_key_value的字段为0, 也就是没有字段, 没有任何值, 可能是{}
        if len(dict_key_value.keys()) == 0 :
            if inWhite(dictBody,dictBody_key,whiteFieldList, way, url) :
                # dictBody_key字段同一个dict下, 剔除掉这个字段
                dictBody.pop(dictBody_key)
        else:
            # dict_key_value有值, 有字段
            # 调用方法处理dict数据
            handleDict(dictBody, dictBody_key, dict_key_value, whiteFieldList, way, url, model)
            # 如果字段都没有符合要求, 都剔除, 导致dict变成{}, 没有字段 , 那需要剔除这个字段
            if len(dict_key_value) == 0 :
                dictBody.pop(dictBody_key)
    elif isinstance(dict_key_value, list):
        # 如果dict_key_value为list
        # 如果dict_key_value的字段为0, 也就是没有字段, 没有任何值, 可能是{}
        if len(dict_key_value) == 0 :
            # 不在白名单中, 剔除字段
            if not inWhite(dictBody, dictBody_key, whiteFieldList, way, url):
                dictBody.pop(dictBody_key)
        else:
            # 调用list处理方法
            handleList(dictBody, dictBody_key, dict_key_value, whiteFieldList, way, url, model)
            if dict_key_value == [] and haveFieldInDict(dictBody, dictBody_key):  # clearHandleDictBody == {} or
                dictBody.pop(dictBody_key)
    else:
        # 非list非dict, 直接调用本方法, 通过way来进行对应的处理
        listDictStr_makeUpNewBody(dictBody, dictBody_key, whiteFieldList, way, url, model)



# 按照way来分开处理uplayer_dictBody中的dict, 剔除不存在白名单中的字段
# value: field字段对应的值   whiteFieldList: 白名单list    way: 处理方式
# uplayer_dictBody: 上一层的dict    field: 如果value是list、str, 就是value对应的字段。如果是value是dict, 就是dict中对应字段
def listDictStr_makeUpNewBody(uplayer_dictBody, field, whiteFieldList, way, url, model):
    if way == 'auto':
        pass
    elif way == 'equal':
        # 用来按照位置来读取list, 默认值为0
        num = 0
        # 默认true, false代表针对url的白名单, true代表使用通用白名单
        # 先判断针对url的白名单中, 再判断通用白名单
        # 如果针对url的白名单中没有对应的url, 那么使用通用白名单
        isCommonWhiteList = True
        # 通用白名单list集合
        commonWhiteList = []
        # 针对url的dict白名单list集合
        urlWhiteList = []
        # 通过while循环把白名单中的dict(针对url)和其他元素(通用白名单字段)分开存入到不同List中
        while True:
            # 如果相等说明list元素遍历处理完成, 断开while
            if len(whiteFieldList) == num:
                break
            # 获得当前list元素的值
            item_whiteFieldList = whiteFieldList[num]
            # 针对url的dict存入到urlWhiteList
            if isinstance(item_whiteFieldList, dict):
                # 获得白名单中dict数据, dict针对url的白名单, 获得dict中的字段, 这个字段就是url
                urlWhiteList.append(item_whiteFieldList)
            else:
                # 白名单中非dict数据, 是通用白名单存入到commonWhiteList
                commonWhiteList.append(item_whiteFieldList)
            num += 1
        # 不能为空, 说明没有白名单
        if len(urlWhiteList) != 0 :
            num = 0
            while True:
                # 针对urlWhiteList进行处理
                # 如果相等说明list元素遍历处理完成, 断开whille
                if len(urlWhiteList) == num:
                    break
                # 获得当前list元素的值, 元素为一个dict
                item_urlWhiteList = urlWhiteList[num]
                # 针对url的白名单, 获得dict中的字段, 这个字段就是url
                urlWhiteList_url = item_urlWhiteList.keys()
                if url in urlWhiteList_url:
                    # 只要当前url和白名单中的dict的url相同, 那么不再会进入到通用字段是否在白名单的判断
                    isCommonWhiteList = False
                    # 判断uplayer_dictBody是否是dict
                    if isinstance(uplayer_dictBody, dict) :
                        # 获取白名单中url对应的白名单字段list, 判断field是否在里边 and uplayer_dictBody.get(field)
                        if field not in item_urlWhiteList.get(url) : # and haveFieldInDict(uplayer_dictBody, field)
                            # if uplayer_dictBody.get(field) == '' or uplayer_dictBody.get(field) :
                            if haveFieldInDict(uplayer_dictBody, field):
                                # 字段不在对应白名单url对应的list中, 报文剔除这个字段
                                uplayer_dictBody.pop(field)
                        else:
                            # 当前字段存在于白名单中
                            # 查询当前测试类型下, 字段对应的value值的限制长度
                            value_length_limited = model_createcaseLengthLimit(model)
                            if haveFieldInDict(uplayer_dictBody, field) and \
                                    len(uplayer_dictBody.get(field)) > int(value_length_limited):
                                # 字段不在对应白名单url对应的list中, 报文剔除这个字段
                                uplayer_dictBody.pop(field)
                        #     globalValue.get_value('')  model_createcaseLengthLimit(model)
                    else:
                        # 获取白名单中url对应的白名单字段list, 判断field是否在里边
                        if field not in item_urlWhiteList.get(url) :
                            # 字段不在对应白名单url对应的list中, 报文剔除这个字段
                            uplayer_dictBody.pop(field)
                        else:
                            # 当前字段存在于白名单中
                            # 查询当前测试类型下, 字段对应的value值的限制长度
                            value_length_limited = model_createcaseLengthLimit(model)
                            if haveFieldInDict(uplayer_dictBody, field) and \
                                    len(uplayer_dictBody.get(field)) > int(value_length_limited):
                                # 字段不在对应白名单url对应的list中, 报文剔除这个字段
                                uplayer_dictBody.pop(field)
                num += 1
        # 为空, 说明没有通用白名单
        if len(commonWhiteList) != 0 :
            # 如果url白名单判断没有当前url, 进入这个方法
            if isCommonWhiteList:
                # 判断uplayer_dictBody是否是字典
                if isinstance(uplayer_dictBody, dict) :
                    # 如果字段不在通用白名单集合里, 原报文剔除这个字段
                    if field not in commonWhiteList :
                        # if uplayer_dictBody.get(field) == '' or uplayer_dictBody.get(field) :
                        if haveFieldInDict(uplayer_dictBody, field) :
                            uplayer_dictBody.pop(field)
                    else:
                        # 当前字段存在于白名单中
                        # 查询当前测试类型下, 字段对应的value值的限制长度
                        value_length_limited = model_createcaseLengthLimit(model)
                        if haveFieldInDict(uplayer_dictBody, field) and \
                                len(uplayer_dictBody.get(field)) > int(value_length_limited):
                            # 字段不在对应白名单url对应的list中, 报文剔除这个字段
                            uplayer_dictBody.pop(field)
                else:
                    # 如果字段不在通用白名单集合里, 原报文剔除这个字段
                    if field not in commonWhiteList :
                        uplayer_dictBody.pop(field)
                    else:
                        # 当前字段存在于白名单中
                        # 查询当前测试类型下, 字段对应的value值的限制长度
                        value_length_limited = model_createcaseLengthLimit(model)
                        if haveFieldInDict(uplayer_dictBody, field) and \
                                len(uplayer_dictBody.get(field)) > int(value_length_limited):
                            # 字段不在对应白名单url对应的list中, 报文剔除这个字段
                            uplayer_dictBody.pop(field)
        else:
            # commonWhiteList为空, urlWhiteList不为空, 说明配置了白名单, 还是需要对原值进行处理
            # commonWhiteList、urlWhiteList都为空, 说明没有配置对应类型的白名单, 不做处理
            if len(urlWhiteList) !=0 and isCommonWhiteList :
                uplayer_dictBody.pop(field)




# 白名单处理方法, 处理dict类型, 按照way的方式, 处理对应类型的数据
# handleDictBody: 需要处理的dict类型数据     whiteFieldList: 白名单       way: 处理数据的方式
def handleDict(dictBody, dictBody_key, handleDictBody, whiteFieldList, way, url, model):
    # 获得dict所有字段, 每个字段存入list中
    all_field_0 = list(handleDictBody.keys())
    if len(all_field_0) == 0 :
        if not inWhite(dictBody, dictBody_key, whiteFieldList, way, url):
            dictBody.pop(dictBody_key)
    else:
        # 默认为0, while循环使用, 方便得知元素位置
        deleteNum_0 = 0
        while True:
            # 如果list长度等于deleteNum, 结束循环
            if len(all_field_0) == deleteNum_0:
                break
            # 整理下数据, 看看是否是list或者dict
            clearHandleDictBody,isList,isDict = formatDictList(handleDictBody.get(all_field_0[deleteNum_0]))
            # 当前字段all_field_0[deleteNum_0]没有在白名单中, 没有在白名单对对应的值进行处理
            # 在白名单中的字段不需要改变
            if not inWhite(handleDictBody, all_field_0[deleteNum_0], whiteFieldList, way, url) :
                # 如果不是dict也不是list, 可能是一个int、str, 删除掉当前元素
                if isinstance(clearHandleDictBody, dict):
                    if len(clearHandleDictBody.keys()) == 0 :
                        handleDictBody.pop(all_field_0[deleteNum_0])
                    else:
                        handleDict(handleDictBody, all_field_0[deleteNum_0], clearHandleDictBody, whiteFieldList, way, url, model)
                        if handleDictBody.get(all_field_0[deleteNum_0]) == {} : # or  handleDictBody.get(all_field_0[deleteNum_0]) == []
                            handleDictBody.pop(all_field_0[deleteNum_0])
                        else:
                            # 如果pop掉一个字段, 那么实际list长度不发生改变
                            deleteNum_0 += 1
                elif isinstance(clearHandleDictBody, list):
                    # 默认为[], 对应字段不在白名单, 去除字段
                    handleList(handleDictBody, all_field_0[deleteNum_0], clearHandleDictBody, whiteFieldList, way, url, model)
                    if clearHandleDictBody == [] and all_field_0[deleteNum_0] in handleDictBody :  # clearHandleDictBody == {} or
                        handleDictBody.pop(all_field_0[deleteNum_0])
                    else:
                        deleteNum_0 += 1
                else:
                    listDictStr_makeUpNewBody(handleDictBody, all_field_0[deleteNum_0], whiteFieldList, way, url, model)
                    deleteNum_0 += 1
            else:
                deleteNum_0 += 1


# 白名单处理方法, 处理list类型, 按照way的方式, 处理对应类型的数据
# upperDictBody: 查询到list, 对应的最上层dict, 例如 {'aaa': [ 1, 2, 3, [ 4, 5, 6 ] ] , 'bbb': '777'}
# upperDictBody_key: 查询到list, 最上层的字段, 例如 aaa
# handleDictBody: 需要处理的list类型数据, 可能是和dict同一层, 例如[ 1, 2, 3, [ 4, 5, 6 ] ], 也可能不是, 例如[ 4, 5, 6 ]
# whiteFieldList: 白名单       way: 处理数据的方式
def handleList(upperDictBody, upperDictBody_key, handleListBody, whiteFieldList, way, url, model):
    # handleListBody为空,也就是没有参数, 为[]
    if len(handleListBody) == 0 :
        # 不在白名单中, 除去对应字段
        if not inWhite(upperDictBody, upperDictBody_key, whiteFieldList, way, url):
            upperDictBody.pop(upperDictBody_key)
    else:
        #
        deleteNum_0 = 0
        while True:
            # 如果list长度大小等于deleteNum, 结束循环
            if len(handleListBody) == deleteNum_0:
                break
            # 整理下数据, 看看是否是list或者dict
            clearHandleDictBody, isList, isDict = formatDictList(handleListBody[deleteNum_0])
            # 如果不是dict也不是list, 可能是一个int、str, 删除掉当前元素
            if isinstance(clearHandleDictBody, dict):
                handleDict(upperDictBody, upperDictBody_key, clearHandleDictBody, whiteFieldList, way, url, model)
                if clearHandleDictBody == {} : #  or clearHandleDictBody == []
                    handleListBody.pop(deleteNum_0)
                else:
                    # 如果是list或者dict, deleteNum自加1
                    deleteNum_0 += 1
            elif isinstance(clearHandleDictBody, list):
                handleList(upperDictBody, upperDictBody_key, clearHandleDictBody, whiteFieldList, way, url, model)
                if clearHandleDictBody == []  : # clearHandleDictBody == {} or
                    if upperDictBody.get(upperDictBody_key) != clearHandleDictBody:
                        handleListBody.pop(deleteNum_0)
                    else:
                        upperDictBody.pop(upperDictBody_key)
                else:
                    # 如果是list或者dict, deleteNum自加1
                    deleteNum_0 += 1
            else:
                handleListBody.pop(deleteNum_0)



# 判断字段是否存在于白名单中, 在白名单中返回值为True, 不在白名单中False
# dictBody: dict数据     field: dict中的字段      whiteFieldList: 白名单集合     url: 报文中的请求地址
def inWhite(dictBody, field, whiteFieldList, way, url):
    have = False
    if way == 'auto':
        pass
    elif way == 'equal':
        # 用来按照位置来读取list, 默认值为0
        num = 0
        # 默认true, false代表针对url的白名单, true代表使用通用白名单
        # 先判断针对url的白名单中, 再判断通用白名单
        # 如果针对url的白名单中没有对应的url, 那么使用通用白名单
        commonWhiteList = True
        while True :
            # 如果相等说明list元素遍历处理完成, 断开whille
            if len(whiteFieldList) == num :
                break
            # 获得当前list元素的值
            item_whiteFieldList = whiteFieldList[num]
            # 白名单是一个List, 分为通用性和针对url的白名单, 针对url白名单使用dict, 例: [ '白名单字段1', { 'url': ['白名单字段2']}
            if isinstance(item_whiteFieldList, dict):
                # 针对url的白名单, 获得dict中的字段, 这个字段就是url
                whiteFieldList_url = item_whiteFieldList.keys()
                if url in whiteFieldList_url :
                    commonWhiteList = False
                    # 判断dictBody是否是dict
                    if isinstance(dictBody, dict):
                        # 获取白名单中url对应的白名单字段list, 判断field是否在里边
                        if field in item_whiteFieldList.get(url) and haveFieldInDict(dictBody, field):
                            # if dictBody.get(field) in [ '', [] ] or dictBody.get(field) :
                            have = True
                            break
                    else:
                        # 获取白名单中url对应的白名单字段list, 判断field是否在里边
                        if field in item_whiteFieldList.get(url) :
                            have = True
                            break
            num += 1
        if commonWhiteList :
            have = False
            num = 0
            while True:
                # 如果相等说明list元素遍历处理完成, 断开whille
                if len(whiteFieldList) == num:
                    break
                # 获得当前list元素的值
                item_whiteFieldList = whiteFieldList[num]
                # 白名单是一个List, 分为通用性和针对url的白名单, 针对url白名单使用dict, 例: [ '白名单字段1', { 'url': ['白名单字段2']}
                if not isinstance(item_whiteFieldList, dict):
                    # 判断dictBody是否是dict
                    if isinstance(dictBody,dict) :
                        # 当前字段field是否和通用白名单中字段相同
                        if field == item_whiteFieldList and haveFieldInDict(dictBody, field)  :
                            # if dictBody.get(field) in [ '', [] ] or dictBody.get(field):
                            have = True
                            break
                    else:
                        # 当前字段field是否和通用白名单中字段相同
                        if field == item_whiteFieldList :
                            have = True
                            break
                num += 1
    return have


# 判断是否是dict或者是eval, 如果是dict或者list, 会对应转换格式
# 输入参数  data : 输入数据
# 返回值一   data: 处理好的值, 如果原值data是list或者dict, 不会改变原值
# 返回值二   isList: 是list, 返回true, 不是, 返回false
# 返回值三   isDict: 是dict, 返回true, 不是, 返回false
def formatDictList(data):
    isList = False
    isDict = False
    if not isinstance(data,dict) and not isinstance(data,list) and len(str(data)) >= 2:
        if str(data).strip()[0] == '[' and str(data).strip()[1] == ']':
            data = eval(str(data))
            isList = True
        elif str(data).strip()[0] == '{' and str(data).strip()[1] == '}' and ':' in str(data):
            data = check_json_format(str(data))
            isDict = True
    else:
        if isinstance(data,list) :
            isList = True
        elif isinstance(data,dict) :
            isDict = True
    return data, isList, isDict

# 判断dict中是否包含字段
# 返回值为 True 表示字段field在dictBody中, 返回值False, 表示字段field不在dictBody中
# dictBody : dict集合      field: 是否包含在dictBody中的字段
def haveFieldInDict(dictBody, field):
    haveField = True
    try:
        result = dictBody.get(field)
        if result == None :
            haveField = False
    except Exception :
        haveField = False
    return haveField

# 根据生成用例类型, 查询全局变量钟对应的生成用例字段值的长度
# 返回值: 默认1个亿。如果查询出值为空, 使用默认值。如果查询出值, 返回查询值, 不使用默认值
# model: 测试类型
def model_createcaseLengthLimit(model):
    allDataConfig = globalValue.get_value('dataConfigYaml')[0]
    if model == 1:
        valueLength = allDataConfig.get(init_createPermissionCase_length_limit)
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 2:
        valueLength = int(allDataConfig.get(init_createSqlCase_length_limit))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 3:
        valueLength = int(allDataConfig.get(init_createXssCase_length_limit))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 4:
        valueLength = int(allDataConfig.get(init_createLengthCase_length_limit))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 5:
        valueLength = int(allDataConfig.get(init_createDownloadUrlCase_length_limit))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 5.1:
        valueLength = int(allDataConfig.get(init_creatDownloadFieldCase_length_limit))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 6:
        valueLength = int(allDataConfig.get(init_createUploadFileCase_length_limit))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 6.1:
        valueLength = int(allDataConfig.get(init_createUploadFieldCase_length_limit))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 41:
        valueLength = allDataConfig.get(init_createPermissionCase_length_limit_equal)
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 42:
        valueLength = int(allDataConfig.get(init_createSqlCase_length_limit_equal))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 43:
        valueLength = int(allDataConfig.get(init_createXssCase_length_limit_equal))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 44:
        valueLength = int(allDataConfig.get(init_createLengthCase_length_limit_equal))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 45:
        valueLength = int(allDataConfig.get(init_createDownloadUrlCase_length_limit_equal))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 45.1:
        valueLength = int(allDataConfig.get(init_creatDownloadFieldCase_length_limit_equal))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 46:
        valueLength = int(allDataConfig.get(init_createUploadFileCase_length_limit_equal))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)
    elif model == 46.1:
        valueLength = int(allDataConfig.get(init_createUploadFieldCase_length_limit_equal))
        # 如果没有对长度进行配置, 那么代表不需要进行限制, 那么让限制值无限大即可, 这里设置无限大为1个亿
        if valueLength == '':
            valueLength = 100000000
        else:
            valueLength = int(valueLength)

    else:
        valueLength = 100000000
    return valueLength




# 获得对应系统配置表里的字段对应的value , 字段写在fieldList, 返回的值会根据字段顺序把对应的值返回， 返回一个List
# systemName : 系统名称      fieldList: 配置表里的字段, 这是一个List, 会按照填写字段的顺序来查询对应字段的值
def getConfigSetting(systemName , fieldList):
    # # 读取全局的dataConfig.yaml, 获得测试系统名
    # globalConfig = read_yaml(ROOT_DIR + '/config/' + 'globalConfig.yaml')
    # global_testSystem = globalConfig.get('global_testSystem')
    # 通过系统名获得, 对应测试系统的dataConfig
    systemConfig = read_yaml(ROOT_DIR + '/config/' + systemName + 'dataConfig.yaml')[0]
    fieldValueList = []
    for item in fieldList :
        value = systemConfig.get(item)
        if value !=  None :
            fieldValueList.append(value)
        else:
            fieldValueList.append('')
            print('当前系统下dataConfig.yaml不存在提供字段的值, 请确定后重新输入!!!!')
    return fieldValueList



# 判断url和value, 是否包含存储在全局变量中, 提供得变量名中, 如果存在返回True, 如果不存在返回False
# 如果变量中不包含提供的变量名, 会在全局变量新建一个提供的变量名, 并且把url和对应的value写入到里边
# url: 当前的请求地址    value: 需要判断的值
# blackListUrlValue: 变量的值, 格式 [ {'url1': ['value1','value2'] } ]
# 或 [ {'url1': ['value1','value2'] ， 'url2': ['value1', 'value2' ] } ]
# 或  [ {'url1': ['value1','value2'] } , { 'url2': ['value1','value2'] }]
def urlValue_inVariableName(url, value, blackListUrlValue):
    # 变量, 是否在黑名单中
    have = False
    # 变量, 是否在黑名单中有相同的url, 默认没有, 为True
    noSameUrl = True
    # 循环黑名单, 查出每个dict
    for item in blackListUrlValue :
        # 检查格式是否为dict
        if check_json_format(item):
            # 获得key也就是url, 判断当前报文url是否在黑名单中
            if url in list(item.keys()) :
                # 有相同的url, noSameUrl设置为False
                noSameUrl = False
                # 获得黑名单中url对应的list
                valueList = item.get(url)
                # 判断当前value是否在list中, 包含在里边表示为True
                if value in valueList :
                    have = True
                else:
                    # 如果不在, 添加到当前url对应的list中
                    valueList.append(value)
        else:
            print('黑名单书写错误, 格式非dict!!!')
    # noSameUrl 为 True表示没有对应的黑名单url和当前的匹配
    if noSameUrl :
        # 添加一个进入黑名单中
        blackListUrlValue.append({ url: [value] })
    return have, blackListUrlValue


# 判断url和field, 是否包含存储在全局变量中, 提供得变量名中, 如果存在返回True, 如果不存在返回False
# 如果变量中不包含提供的变量名, 会在全局变量新建一个提供的变量名, 并且把url和对应的field写入到里边
# url: 当前的请求地址    field: 需要判断的字段
# blackListUrlField: 变量的值, 格式 [ {'url1': ['field1','field2'] } ]
# 或 [ {'url1': ['field1','field2'] ， 'url2': ['field1', 'field2' ] } ]
# 或  [ {'url1': ['field1','field2'] } , { 'url2': ['field1','field2'] }]
def urlField_inVariableName(url, field, blackListUrlField):
    # 变量, 是否在黑名单中
    have = False
    # 变量, 是否在黑名单中有相同的url, 默认没有, 为True
    noSameUrl = True
    # 循环黑名单, 查出每个dict
    for item in blackListUrlField :
        # 检查格式是否为dict
        if check_json_format(item):
            # 获得key也就是url, 判断当前报文url是否在黑名单中
            if url in list(item.keys()) :
                # 有相同的url, noSameUrl设置为False
                noSameUrl = False
                # 获得黑名单中url对应的list
                fieldList = item.get(url)
                # 判断当前field是否在list中, 包含在里边表示为True
                if field in fieldList :
                    have = True
                else:
                    # 如果不在, 添加到当前url对应的list中
                    fieldList.append(field)
        else:
            print('黑名单书写错误, 格式非dict!!!')
    # noSameUrl 为 True表示没有对应的黑名单url和当前的匹配
    if noSameUrl :
        # 添加一个进入黑名单中
        blackListUrlField.append({ url: [field] })
    return have



# 判断url、field、value, 是否包含存储在全局变量中, 提供得变量名中, 如果存在返回True, 如果不存在返回False
# 如果变量中不包含提供的变量名, 会在全局变量新建一个提供的变量名, 并且把url和对应的field写入到里边, field对应的value值写到里边
# url: 当前的请求地址    field: 需要判断的字段   value: 字段对应的值
# blackListUrlField: 变量的值, 格式 [ {'url1': { 'field1': ['value1','value2'] } } ]
# 或 [ {'url1': { 'field1': ['value1','value2'] } , 'url2': { 'field1': ['value1','value2'] } } ]
# 或  [ {'url1': { 'field1': ['value1','value2'] } } , {'url2': { 'field1': ['value1','value2'] } } ]
def urlFieldValue_inVariableName(url, field, value, blackListUrlField):
    # 变量, 是否在黑名单中
    have = False
    # 变量, 是否在黑名单中有相同的url, 默认没有, 为True
    noSameUrl = True
    # 循环黑名单, 查出每个dict
    for item in blackListUrlField :
        # 检查格式是否为dict
        if check_json_format(item):
            # 获得key也就是url, 判断当前报文url是否在黑名单中
            if url in list(item.keys()) :
                # 有相同的url, noSameUrl设置为False
                noSameUrl = False
                # 获得黑名单中url对应的list, 也就是字段集合, 是一个dict
                fieldDict = item.get(url)
                # 检查格式是否为dict
                if check_json_format(fieldDict):
                    # 判断当前field是否在field的list中, 包含在里边表示为True
                    if field in list(fieldDict.keys()) :
                        # 获得字段对应的value集合, 为list
                        valueList = fieldDict.get(field)
                        # 判断当前value是否在黑名单集合中, 在设置have为True, 不在添加到list中
                        if value in valueList:
                            have = True
                        else:
                            # 没有这个值添加到list里
                            valueList.append(value)

                    else:
                        # 如果不在, 添加到当前url对应的list中
                        fieldDict[field] = [value]
                else:
                    print('黑名单书写错误, 格式非dict!!!')
        else:
            print('黑名单书写错误, 格式非dict!!!')
    # noSameUrl 为 True表示没有对应的黑名单url和当前的匹配
    if noSameUrl :
        # 添加一个进入黑名单中
        blackListUrlField.append({ url: { field : [value] } })
    return have, blackListUrlField



# 判断url和value, 是否包含存储在全局变量中, 提供得变量名中, 如果存在返回True, 如果不存在返回False
# 如果变量中不包含提供的变量名, 会在全局变量新建一个提供的变量名, 并且把url和对应的value写入到里边
# url: 当前的请求地址    value: 需要判断的值
# writeIntoVariable: 如果不存在的url或者value值, 是否写入到黑名单的变量里, 如果写入相当于修改了原有的变量,
# 这里做一个控制。True写入,False不写入。
# blackListUrlValue: 变量的值, 格式 [ {'url1': ['value1','value2'] } ]
# 或 [ {'url1': ['value1','value2'] ， 'url2': ['value1', 'value2' ] } ]
# 或  [ {'url1': ['value1','value2'] } , { 'url2': ['value1','value2'] }]
def urlValue_inVariableName_canSave(url, value, blackListUrlValue, writeIntoVariable):
    # 变量, 是否在黑名单中
    have = False
    # 变量, 是否在黑名单中有相同的url, 默认没有, 为True
    noSameUrl = True
    # 循环黑名单, 查出每个dict
    for item in blackListUrlValue :
        # 检查格式是否为dict
        if check_json_format(item):
            # 获得key也就是url, 判断当前报文url是否在黑名单中
            if url in list(item.keys()) :
                # 有相同的url, noSameUrl设置为False
                noSameUrl = False
                # 获得黑名单中url对应的list
                valueList = item.get(url)
                # 判断当前value是否在list中, 包含在里边表示为True
                if value in valueList :
                    have = True
                else:
                    # 根据输入参数选择是否写入到变量里
                    if writeIntoVariable :
                        # 如果不在, 添加到当前url对应的list中
                        valueList.append(value)
        else:
            print('黑名单书写错误, 格式非dict!!!')
    # noSameUrl 为 True表示没有对应的黑名单url和当前的匹配
    # 根据输入参数选择是否写入到变量里
    if noSameUrl and writeIntoVariable:
        # 添加一个进入黑名单中
        blackListUrlValue.append({ url: [value] })
    return have


# 判断url和value, 是否包含存储在全局变量中, 提供得变量名中, 如果存在返回True, 如果不存在返回False
# 如果变量中不包含提供的变量名, 会在全局变量新建一个提供的变量名, 并且把url和对应的value写入到里边
# url: 当前的请求地址    value: 需要判断的值
# writeIntoVariable: 如果不存在的url或者value值, 是否写入到黑名单的变量里, 如果写入相当于修改了原有的变量,
# 这里做一个控制。True写入,False不写入。
# blackListUrlValue: 变量的值, 格式 [ {'url1': ['value1','value2'] } ]
# 或 [ {'url1': ['value1','value2'] ， 'url2': ['value1', 'value2' ] } ]
# 或  [ {'url1': ['value1','value2'] } , { 'url2': ['value1','value2'] }]
def urlValue_inVariableName_canSave_update(url, value, blackListUrlValue, writeIntoVariable):
    # 变量, 是否在黑名单中
    have = False
    # 变量, 是否在黑名单中有相同的url, 默认没有, 为True
    noSameUrl = True
    # 标志位, url在黑名单中, 默认为False, 如果在黑名单中为True
    urlInBlackList = False
    # 循环黑名单, 查出每个dict
    for item in blackListUrlValue :
        # 检查格式是否为dict
        if check_json_format(item):
            # 获得key也就是url, 判断当前报文url是否在黑名单中
            if url in list(item.keys()) :
                # 有相同的url, noSameUrl设置为False
                noSameUrl = False
                # 获得黑名单中url对应的list
                valueList = item.get(url)
                # 判断当前value是否在list中, 包含在里边表示为True
                if value in valueList :
                    have = True
                else:
                    # 根据输入参数选择是否写入到变量里
                    if writeIntoVariable :
                        # 如果不在, 添加到当前url对应的list中
                        valueList.append(value)
        else:
            print('黑名单书写错误, 格式非dict!!!')
    # noSameUrl 为 True表示没有对应的黑名单url和当前的匹配
    # 根据输入参数选择是否写入到变量里
    if noSameUrl and writeIntoVariable:
        # 添加一个进入黑名单中
        blackListUrlValue.append({ url: [value] })
    return have, urlInBlackList




# 判断url和field, 是否包含存储在全局变量中, 提供得变量名中, 如果存在返回True, 如果不存在返回False
# 如果变量中不包含提供的变量名, 会在全局变量新建一个提供的变量名, 并且把url和对应的field写入到里边
# url: 当前的请求地址    field: 需要判断的字段
# writeIntoVariable: 如果不存在的url或者value值, 是否写入到黑名单的变量里, 如果写入相当于修改了原有的变量,
# 这里做一个控制。True写入,False不写入。
# blackListUrlField: 变量的值, 格式 [ {'url1': ['field1','field2'] } ]
# 或 [ {'url1': ['field1','field2'] ， 'url2': ['field1', 'field2' ] } ]
# 或  [ {'url1': ['field1','field2'] } , { 'url2': ['field1','field2'] }]
def urlField_inVariableName_canSave(url, field, blackListUrlField, writeIntoVariable):
    # 变量, 是否在黑名单中
    have = False
    # 变量, 是否在黑名单中有相同的url, 默认没有, 为True
    noSameUrl = True
    # 循环黑名单, 查出每个dict
    for item in blackListUrlField :
        # 检查格式是否为dict
        if check_json_format(item):
            # 获得key也就是url, 判断当前报文url是否在黑名单中
            if url in list(item.keys()) :
                # 有相同的url, noSameUrl设置为False
                noSameUrl = False
                # 获得黑名单中url对应的list
                fieldList = item.get(url)
                # 判断当前field是否在list中, 包含在里边表示为True
                if field in fieldList :
                    have = True
                else:
                    # 根据输入参数选择是否写入到变量里
                    if writeIntoVariable:
                        # 如果不在, 添加到当前url对应的list中
                        fieldList.append(field)
        else:
            print('黑名单书写错误, 格式非dict!!!')
    # noSameUrl 为 True表示没有对应的黑名单url和当前的匹配
    # 根据输入参数writeIntoVariable选择是否写入到变量里
    if noSameUrl and writeIntoVariable:
        # 添加一个进入黑名单中
        blackListUrlField.append({ url: [field] })
    return have



# 判断url、field、value, 是否包含存储在全局变量中, 提供得变量名中, 如果存在返回True, 如果不存在返回False
# 如果变量中不包含提供的变量名, 会在全局变量新建一个提供的变量名, 并且把url和对应的field写入到里边, field对应的value值写到里边
# url: 当前的请求地址    field: 需要判断的字段   value: 字段对应的值
# writeIntoVariable: 如果不存在的url或者value值, 是否写入到黑名单的变量里, 如果写入相当于修改了原有的变量,
# 这里做一个控制。True写入,False不写入。
# blackListUrlField: 变量的值, 格式 [ {'url1': { 'field1': ['value1','value2'] } } ]
# 或 [ {'url1': { 'field1': ['value1','value2'] } , 'url2': { 'field1': ['value1','value2'] } } ]
# 或  [ {'url1': { 'field1': ['value1','value2'] } } , {'url2': { 'field1': ['value1','value2'] } } ]
def urlFieldValue_inVariableName_canSave(url, field, value, blackListUrlField, writeIntoVariable):
    # 变量, 是否在黑名单中
    have = False
    # 变量, 是否在黑名单中有相同的url, 默认没有, 为True
    noSameUrl = True
    # 循环黑名单, 查出每个dict
    for item in blackListUrlField :
        # 检查格式是否为dict
        if check_json_format(item):
            # 获得key也就是url, 判断当前报文url是否在黑名单中
            if url in list(item.keys()) :
                # 有相同的url, noSameUrl设置为False
                noSameUrl = False
                # 获得黑名单中url对应的list, 也就是字段集合, 是一个dict
                fieldDict = item.get(url)
                # 检查格式是否为dict
                if check_json_format(fieldDict):
                    # 判断当前field是否在field的list中, 包含在里边表示为True
                    if field in list(fieldDict.keys()) :
                        # 获得字段对应的value集合, 为list
                        valueList = fieldDict.get(field)
                        # 判断当前value是否在黑名单集合中, 在设置have为True, 不在添加到list中
                        if value in valueList:
                            have = True
                        else:
                            # 根据输入参数writeIntoVariable选择是否写入到变量里
                            if writeIntoVariable :
                                valueList.append(value)
                    else:
                        # 根据输入参数writeIntoVariable选择是否写入到变量里
                        if writeIntoVariable:
                            # 如果不在, 添加到当前url对应的list中
                            fieldDict[field] = [value]
                else:
                    print('黑名单书写错误, 格式非dict!!!')
        else:
            print('黑名单书写错误, 格式非dict!!!')
    # noSameUrl 为 True表示没有对应的黑名单url和当前的匹配
    # 根据输入参数writeIntoVariable选择是否写入到变量里
    if noSameUrl and writeIntoVariable :
        # 添加一个进入黑名单中
        blackListUrlField.append({ url: { field : [value] } })
    return have


# 判断url、field、value, 是否包含存储在全局变量中, 提供得变量名中, 如果存在返回True, 如果不存在返回False
# 如果变量中不包含提供的变量名, 会在全局变量新建一个提供的变量名, 并且把url和对应的field写入到里边, field对应的value值写到里边
# url: 当前的请求地址    field: 需要判断的字段   value: 字段对应的值
# writeIntoVariable: 如果不存在的url或者value值, 是否写入到黑名单的变量里, 如果写入相当于修改了原有的变量,
# 这里做一个控制。True写入,False不写入。
# blackListUrlField: 变量的值, 格式 [ {'url1': { 'field1': ['value1','value2'] } } ]
# 或 [ {'url1': { 'field1': ['value1','value2'] } , 'url2': { 'field1': ['value1','value2'] } } ]
# 或  [ {'url1': { 'field1': ['value1','value2'] } } , {'url2': { 'field1': ['value1','value2'] } } ]
def urlFieldValue_inVariableName_canSave_update(url, field, value, blackListUrlField, writeIntoVariable):
    # 变量, 是否在黑名单中
    have = False
    # 变量, 是否在黑名单中有相同的url, 默认没有, 为True
    noSameUrl = True
    # 标志位, url在黑名单中, 默认为False,如果在黑名单中为True
    urlInBlackList = False
    # 标志位, url和 Field在黑名单中, 默认为False,如果在黑名单中为True
    urlFieldInBlackList = False
    # 循环黑名单, 查出每个dict
    for item in blackListUrlField :
        # 检查格式是否为dict
        if check_json_format(item):
            # 获得key也就是url, 判断当前报文url是否在黑名单中
            if url in list(item.keys()) :
                # 当前url包含在黑名单中
                urlInBlackList = True
                # 有相同的url, noSameUrl设置为False
                noSameUrl = False
                # 获得黑名单中url对应的list, 也就是字段集合, 是一个dict
                fieldDict = item.get(url)
                # 检查格式是否为dict
                if check_json_format(fieldDict):
                    # 判断当前field是否在field的list中, 包含在里边表示为True
                    if field in list(fieldDict.keys()) :
                        # 获得字段对应的value集合, 为list
                        valueList = fieldDict.get(field)
                        # 判断当前value是否在黑名单集合中, 在设置have为True, 不在添加到list中
                        if value in valueList:
                            have = True
                        else:
                            # urlField包含在黑名单中, 但当前字段对应的值不再黑名单urlFieldValue中
                            # 如果在黑名单中urlFieldValue中, 还是不会修改, 让urlFieldInBlackList默认为False
                            urlFieldInBlackList = True
                            # 根据输入参数writeIntoVariable选择是否写入到变量里
                            if writeIntoVariable :
                                valueList.append(value)
                    else:
                        # 根据输入参数writeIntoVariable选择是否写入到变量里
                        if writeIntoVariable:
                            # 如果不在, 添加到当前url对应的list中
                            fieldDict[field] = [value]
                else:
                    print('黑名单书写错误, 格式非dict!!!')
        else:
            print('黑名单书写错误, 格式非dict!!!')
    # noSameUrl 为 True表示没有对应的黑名单url和当前的匹配
    # 根据输入参数writeIntoVariable选择是否写入到变量里
    if noSameUrl and writeIntoVariable :
        # 添加一个进入黑名单中
        blackListUrlField.append({ url: { field : [value] } })
    return have, urlInBlackList, urlFieldInBlackList


# 遍历获得路径下所有文件, 包括文件夹, 判断当前文件的后缀, 是否包含在过滤器中.如果包含在过滤器中, 会存储到list变量saveAllFilePath中
# 如果给的是一个文件, 那存入到saveAllFilePath只是一个文件. 如果是一个路径地址, 那存储所有满足要求文件的绝对路径.
# file_path: 可以是一个文件, 也可以是一个路径     saveAllFilePath: 存储到的list的变量名, 是个list
# suffixFilter: 满足要求的后缀集合, 是一个list
def traverse_folder(file_path, saveAllFilePath, suffixFilter):
    # 判断是否是文件
    if os.path.isfile(file_path):
        # 获得文件名后缀
        splitName = os.path.splitext(file_path)
        # 获得后缀方法是个list, 最后一个元素为文件后缀
        splitName_len = len(splitName) - 1
        # 判断后缀是否在过滤器中, 过滤器是后最的集合, 是一个list, 如果包含在过滤器中, 将当前的绝对路径添加到suffixFilter中
        if splitName[splitName_len] in suffixFilter:
            saveAllFilePath.append(file_path)
    else:
        # 不是文件, 是一个路径, 获得路径下的所有文件包括文件夹
        for file_name in os.listdir(file_path):
            # 获得文件名, 拼装这个文件的绝对路径
            compose_file_path = os.path.join(file_path, file_name)
            # 判断是否是文件
            if os.path.isfile(compose_file_path) :
                # 获得文件名后缀
                splitName = os.path.splitext(compose_file_path)
                # 获得后缀方法是个list, 最后一个元素为文件后缀
                splitName_len = len(splitName) - 1
                # 判断后缀是否在过滤器中, 过滤器是后最的集合, 是一个list, 如果包含在过滤器中, 将当前的绝对路径添加到suffixFilter中
                if splitName[splitName_len] in suffixFilter:
                    saveAllFilePath.append(compose_file_path)
            else:
                traverse_folder(compose_file_path, saveAllFilePath, suffixFilter)  # 递归遍历子文件夹

# 解析multipart/form-data的请求体, 返回一个dict。格式: { files:[ {field_name: form-data那行的name, field_name: 当前文件名
# content_type: 文件类型, file_content:二进制文件}], fields: { 报文中字段1: 字段1对应的值, 报文中字段2: 字段2对应的值}}
# body: multipart/form-data的请求体
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

# parse_multipart_form_data方法有一个返回值, 是对multipart/form-data的请求体的解析, 填写到方法参数里, 会将bytes恢复成文件
# 是files: 中的一个, files 存储一个List, 每个元素是一个dict, 代表一个文件
# file_info: parse_multipart_form_data对multipart/form-data的请求体的解析, 是一个dict
# output_dir: 输出文件路径         output_fileName: 输出文件名
def save_file(file_info, output_dir, output_fileName):
    # 创建输出目录（如果不存在）
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 确定文件的保存路径
    full_path = os.path.join(output_dir, output_fileName)

    # # 如果文件名重复，添加一个后缀来避免覆盖
    # base, ext = os.path.splitext(full_path)
    # counter = 1
    # while os.path.exists(full_path):
    #     full_path = f"{base}_{counter}{ext}"
    #     counter += 1

    # 将二进制文件内容保存到指定文件
    with open(full_path, 'wb') as f:
        f.write(file_info['file_content'])

    print(f"文件已保存为: {full_path}")
    return full_path



def extract_prefix(filename):
  """从符合 xxxxdataConfig.yaml 命名规范的文件名中提取 xxxx 部分。

  Args:
    filename: 文件名字符串。

  Returns:
    提取出的前缀字符串，如果文件名不符合规范则返回 None。
  """

  # 正则表达式匹配 xxxxdataConfig.yaml 格式
  pattern = r"^(.*)dataConfig\.yaml$"
  match = re.match(pattern, filename)

  if match:
    return match.group(1)
  else:
    return None

#
if __name__ == '__main__':
    params = sys.argv[1:]  # 获取命令行参数
    # systemName, field, value
    appendDataConfigValue(params[0], params[1], params[2])





