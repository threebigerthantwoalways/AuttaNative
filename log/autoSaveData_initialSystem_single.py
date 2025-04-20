import os,logging,sys,time
sys.stdout.reconfigure(encoding='utf-8')
# 当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上级目录
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
from database.dataBaseSqlite import loadDataBase_ALL,loadDataBase_Many
from config import *
from util.yaml_util import read_yaml
from ruamel.yaml import YAML
from urllib import  parse
from util.utils import readBodyIntoDict, check_json_format, headerType, getConfigSetting, traverse_folder, \
    save_data_excel_singleSheet, readBodyIntoDict_auto
from util import globalValue


# burp插件将测试流量导入到sqlite数据库，本方法自动化将字段与对应的值提取到yaml中。提取的数据会当作安全测试的数据进行使用
# 同时会生成黑名单到yaml文件中，黑名单中的url、头、字段，不会产生对应的测试用例
# dataBasePath: sqlite数据库地址  filterUrl：sqlite包含大量报文日志，过滤出需要的url地址报文
# systemName: 系统名，生成的配置文件会已系统名作为文件名的一部分
# def autoSave(dataBasePath, filterUrl, systemName, loadDataBaseType):
def autoSave(systemName):
    yaml = YAML()
    # 读取当前系统的dataConfig.yaml
    dataBasePath,filterUrl,loadDataBaseType = getConfigSetting(systemName, ['dataBasePath','filterUrl','loadDataBaseType'])
    # 获得对应系统的dataConfig.yaml
    dataConfigYamlPath = ROOT_DIR + '/config/' + systemName + 'dataConfig.yaml'
    dataConfigYaml = read_yaml(dataConfigYamlPath)
    # 过滤器, 当前只过滤 .db
    # filterFile = ['.db']
    filterFile = dataConfigYaml[0][init_filter_dataBaseName_suffix]
    # 存储文件路径的变量
    allFileNamePath = []
    # 迭代遍历路径下文件, 过滤出符合过滤器要求的文件。如果是一个文件路径, 返回list, 只有一个元素, 就是这个文件绝对路径
    traverse_folder(dataBasePath, allFileNamePath, filterFile)
    # 如果不为空, 说明list中存有正确的路径
    if len(allFileNamePath) != 0 :
        # 备份dataConfig.yaml
        with open(init_config_path + systemName + 'dataConfig_autoSave_backup.yaml', 'w', encoding='utf-8') as f:
            # f.write(yaml.dump(dataConfigYaml, Dumper=yaml.RoundTripDumper, allow_unicode=True))
            yaml.dump(dataConfigYaml, f)
        # 调用获取所有文件方法, 返回的是一个List, 设置一个代表list元素位置的全局变量数字为0
        iteratorDP_num = 0
        # 遍历文件名list中的所有元素
        while True:
            # iteratorDP_num会在后边自加1, 当长度和iteratorDP_num相同, 代表遍历结束
            if len(allFileNamePath) == iteratorDP_num:
                break
            # 获得文件的绝对路径, 调用主方法
            one_dataBasePath = allFileNamePath[iteratorDP_num]
            autoSave_main(systemName, one_dataBasePath, filterUrl, loadDataBaseType, dataConfigYaml)
            # 代表元素值得变量, 自加一
            iteratorDP_num += 1
        # 判断dataConfigYaml元素1, 不为空, 元素1中的key不为0
        if dataConfigYaml[0] and len(dataConfigYaml[0].keys()) != 0:
            # 提取数据后, dataConfigYaml内容可能已经改变, 覆盖写入到原文件中
            with open(dataConfigYamlPath, 'w', encoding='utf-8') as f:
                # f.write(yaml.dump(dataConfigYaml, Dumper=yaml.RoundTripDumper, allow_unicode=True))
                yaml.dump(dataConfigYaml, f)
        else:
            logging.info('dataConfigYaml配置表出现问题，未存入新值进入文件中')
            print('dataConfigYaml配置表出现问题，未存入新值进入文件中')
    else:
        print('数据库文件路径填写错误,请检查!!!!')




def autoSave_main(systemName, dataBasePath, filterUrl, loadDataBaseType, dataConfigYaml):
    # 初始化各个文件、文件夹
    initialSystem(systemName)
    # 有逗号, 说明加载数据库方式可能为id区间, 也可能是时间区间
    if isinstance(loadDataBaseType, list):
        # 标志位, 判断是时间区间加载数据库, 还是id区间加载数据库, 默认为False
        timeLoadDatabase = False
        for item in loadDataBaseType :
            # 判断如果有 : , 说明是时间加载
            if ':' in item :
                timeLoadDatabase = True
        if timeLoadDatabase :
            all = loadDataBase_Many(dataBasePath, '', '', loadDataBaseType)
        else:
            # 没有 : , 说明是id区间加载数据库
            all = loadDataBase_Many(dataBasePath, '', loadDataBaseType, '')
    else:
        # 没有逗号, 要不就是加载数据库所有数据
        if loadDataBaseType == 'loadAll' :
            all = loadDataBase_ALL(dataBasePath)
        else:
            # 要不就是单独的一个数字, 一个id
            all = loadDataBase_Many(dataBasePath, int(loadDataBaseType), '', '')
    # 查询数据库结果为None
    if all == None:
        now = time.localtime(time.time())
        nowNum = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_' + str(now.tm_hour) + '_' + str(
            now.tm_min) + '_' + str(now.tm_sec)
        reportPathName = init_testcase_path + systemName + '/report/' + nowNum + '_' + systemName + '_' + os.path.basename(
            dataBasePath) + '_加载出现错误_查询数据库返回为None.xlsx'
        excelTitile = init_excelTitile_statistic
        allSummaryData = [[0, 0, str(0), 0, str(0)]]
        save_data_excel_singleSheet(excelTitile, allSummaryData, reportPathName, '敏感信息测试统计')
        print('\n')
    # 查询数据库返回值为list, 并且list中没有元素
    elif isinstance(all, list) and len(all) == 0:
        now = time.localtime(time.time())
        nowNum = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_' + str(now.tm_hour) + '_' + str(
            now.tm_min) + '_' + str(now.tm_sec)
        reportPathName = init_testcase_path + systemName + '/report/' + nowNum + '_' + systemName + '_' + os.path.basename(
            dataBasePath) + '_加载返回数据为0_没有匹配数据被查询出来.xlsx'
        excelTitile = init_excelTitile_statistic
        allSummaryData = [[0, 0, str(0), 0, str(0)]]
        save_data_excel_singleSheet(excelTitile, allSummaryData, reportPathName, '敏感信息测试统计')
        print('\n')
    else:
        num = 0
        allnum = len(all)
        normalInterface = []
        badInterface = []
        for item in all:
            params = parse.urlparse(item[2])
            urlIpPort = params.netloc
            if urlIpPort in filterUrl :
                try:
                    saveFieldValueIntoYmal(item, dataConfigYaml)
                    num += 1
                    normalInterface.append(item[0])
                    logging.info('完成提取id: ' + str(item[0]))
                    print('完成提取id: ' + str(item[0]))
                except Exception:
                    badInterface.append(item[0])
                    logging.info('处理接口 id：' + str(item[0]) + ' 出现异常')
                    print('处理接口 id：' + str(item[0]) + ' 出现异常')
        logging.info('异常接口id： ' + str(badInterface))
        logging.info('完成测试系统接口: ' + str(normalInterface))
        logging.info('异常接口数量' + str(len(badInterface)))
        logging.info('完成测试系统接口数量: ' + str(num))
        logging.info('总接口数量: ' + str(allnum))
        logging.info('数据库: ' + dataBasePath + ' 处理完成')
        print('异常接口id： ' + str(badInterface))
        print('完成测试系统接口: ' + str(normalInterface))
        print('异常接口数量' + str(len(badInterface)))
        print('完成测试系统接口数量: ' + str(num))
        print('总接口数量: ' + str(allnum))
        print('数据库: ' + dataBasePath + ' 处理完成')
        print('\n')


# item[0]:ID             item[1]:本地ip地址        item[2]:url          item[3]:请求方式      item[4]:BURP_TOOL
# item[5]:请求头         item[6]:请求体            item[7]:响应头        item[8]:响应体        item[9]:发送请求时间
# 将一条burp插件的日志中的字段和字段对应的值,提取到一个yaml文件中
# item_logData : burp插件中的一条报文日志      dataConfigYaml: 读取的对应系统的dataConfig.yaml表
def saveFieldValueIntoYmal(item_logData, dataConfigYaml):
    url = item_logData[2]
    reqHeaders = item_logData[5]
    reqBody = item_logData[6]
    resHeaders = item_logData[7]
    resBody = item_logData[8]
    params = parse.urlparse(url).query
    changeDict = parse.parse_qs(params)
    if changeDict != {}:
        result = {}
        # params = params.split('&')
        # for itm_split_first in params:
        #     item_split_second = itm_split_first.split('=')
        #     temp = []
        #     temp.append(item_split_second[1])
        #     result[item_split_second[0]] = temp
        for key in changeDict.keys():
            result[key] = changeDict.get(key)[0]
        if result != {}:
            readBodyIntoDict(result, dataConfigYaml, False)
    if reqBody not in ['', '{}', '[]', '{'':''}']:
        bodyType = headerType(reqHeaders)
        if 'json' in bodyType:
            reqBody_json = check_json_format(reqBody)
            if reqBody_json:
                readBodyIntoDict(reqBody_json, dataConfigYaml, False)
            #     bodySensitive = jsonFieldValueSensitive(url, resHeadersList, resBody_json, read_yamlPath)
        elif 'x-www-form-urlencoded' in bodyType:
            bodyParams = parse.urlparse('http://www.fakeUrl.com/fake.do?'+reqBody).query
            changeDict = parse.parse_qs(bodyParams)
            if changeDict != {}:
                result = {}
                # bodyParams = bodyParams.split('&')
                # for itm_split_first in bodyParams:
                #     item_split_second = itm_split_first.split('=')
                #     temp = []
                #     temp.append(item_split_second[1])
                #     result[item_split_second[0]] = temp
                for key in changeDict.keys():
                    result[key] = changeDict.get(key)[0]
                if result != {}:
                    readBodyIntoDict(result, dataConfigYaml, False)
    if resBody not in ['', '{}', '[]', '{'':''}']:
        bodyType = headerType(resHeaders)
        if 'json' in bodyType:
            resBody_json = check_json_format(resBody)
            if resBody_json:
                readBodyIntoDict(resBody_json, dataConfigYaml, False)
        elif 'x-www-form-urlencoded' in bodyType:
            bodyParams = parse.urlparse('http://www.fakeUrl.com/fake.do?' + resBody).query
            changeDict = parse.parse_qs(bodyParams)
            if changeDict != {}:
                result = {}
                bodyParams = bodyParams.split('&')
                for itm_split_first in bodyParams:
                    item_split_second = itm_split_first.split('=')
                    temp = []
                    temp.append(item_split_second[1])
                    result[item_split_second[0]] = temp
                if result != {}:
                    readBodyIntoDict(result, dataConfigYaml, False)


###########################################分析同一个url下的字段, 对应的值是否相同
# list分开, 元素1， {'url': 个数} , 元素2, {'url': [{'和url相同的url1字段1': '值', '和url相同的url1字段2': '值'}
# , {'和url相同的url2字段1': '值', '和url相同的url2字段2': '值'}]}
# 1. 数据库中总的url数量, 可以进行比较判断 , 应对 4
# 2. 多少相同的url, 可以进行比较判断, 应对 5 ,  实际上是url下可比对的字段对应的值有多少个
# 4. 通过比较每个接口相同的字段, 来过滤掉设备标记、版本信息等
# 5. 同一个接口下, 相同字段对应的值, 变化情况, 提取出用户上传的参数, 这也是服务端需要的值, 也是测试点
# 6. 让字段为空, 和有值两种情况, 发送请求, 通过响应结果比对判断是否需要测试当前字段

# 5 中比对url或者字段下值的总数, 去重, 得到的个数, 与原有数据比对, 写入字段中的总数据个数100个,
# 如果达到要求生成用例, 直接写入黑名单, 后续的数据也不再写入到data.yaml中。 如果比值没有达到要求, 会继续可以写入数据。

# 将多个或1个数据库, 逐个按照url->字段->值的格式, 存入到data.yaml中
# systemName: 系统名字
def autoSave_sameUrlFildValueIntoYaml(systemName):
    # 设置一个全局变量, 将读取的dataConfigYaml_content, 存入到全局变量的一个key中, 方便调用
    globalValue._init()
    # 初始化环境, 文件夹什么的
    initialSystem(systemName)
    # # 设置一个临时全局变量tempBlackListSensitiveUrlHeaderFieldValue, 用来判断在敏感信息测试过程中, 是否有重复的敏感信息
    # # 如果是重复的敏感信息, 会剔除掉, 不写入excel中, 就是通过这个来进行存储和比较。不是持久化存储, 代码结束就消失了。
    # tempBlackListSensitiveUrlHeaderFieldValue = { 'blackHeader': [], 'blackUrlValue': [] ,'blackUrlField': [], 'blackUrlFieldValue':[] }
    # globalValue.set_value('tempBlackListSensitiveUrlHeaderFieldValue', tempBlackListSensitiveUrlHeaderFieldValue)
    # 读取当前系统的dataConfig.yaml
    dataBasePath, filterUrl, loadDataBaseType = getConfigSetting(systemName,
                                                                 ['dataBasePath', 'filterUrl', 'loadDataBaseType'])
    # 读取配置表, 将配置表中的值存入到全局变量dataConfigYaml中
    dataConfigYamlPath = init_config_path + systemName + 'dataConfig.yaml'
    dataConfigYaml_content = read_yaml(dataConfigYamlPath)
    globalValue.set_value('dataConfigYaml', dataConfigYaml_content)
    # 读取当前系统下的data.yaml文件, 数据会按照 { '请求地址' : {'字段': ['值1', '值2'] } } 格式存储到里边
    # 读取数据存储表, 将配置表中的值存入到全局变量dataConfigYaml中
    dataYamlPath = ROOT_DIR + '/testcase/' + systemName + '/data.yaml'
    dataYaml_content = read_yaml(dataYamlPath)
    globalValue.set_value('dataYaml', dataYaml_content)
    # 过滤器, 当前只过滤 .db
    filterFile = dataConfigYaml_content[0][init_filter_dataBaseName_suffix]
    # 存储文件路径的变量
    allFileNamePath = []
    # 迭代遍历路径下文件, 过滤出符合过滤器要求的文件。如果是一个文件路径, 返回list, 只有一个元素, 就是这个文件绝对路径
    traverse_folder(dataBasePath, allFileNamePath, filterFile)
    # 如果不为空, 说明list中存有正确的路径
    if len(allFileNamePath) != 0:
        yaml = YAML()
        # 备份data.yaml
        with open(ROOT_DIR + '/testcase/' + systemName + '/data_backup.yaml', 'w',
                  encoding='utf-8') as f:
            # f.write(yaml.dump(dataYaml_content, Dumper=yaml.RoundTripDumper, allow_unicode=True))
            yaml.dump(dataYaml_content, f)
        # 统计无重复接口数量, 希望显示在前边, 提前在这里设置一个空置
        dataYaml_content[0]['totalUrl_noDouble'] = 0
        # 调用获取所有文件方法, 返回的是一个List, 设置一个代表list元素位置的全局变量数字为0
        iteratorDP_num = 0
        # 遍历文件名list中的所有元素
        while True:
            # iteratorDP_num会在后边自加1, 当长度和iteratorDP_num相同, 代表遍历结束
            if len(allFileNamePath) == iteratorDP_num:
                break
            # 获得文件的绝对路径, 调用主方法
            one_dataBasePath = allFileNamePath[iteratorDP_num]
            autoSave_sameUrlFildValueIntoYaml_main(systemName, one_dataBasePath, filterUrl, loadDataBaseType, dataYaml_content)
            # 代表元素值得变量, 自加一
            iteratorDP_num += 1
        if dataYaml_content[1] and len(dataYaml_content[1].keys()) != 0 :
            totalUrl_noDouble = dataYaml_content[1].keys()
            # 统计无重复接口数量
            dataYaml_content[0]['totalUrl_noDouble'] = len(totalUrl_noDouble)
            # 遍历所有key, 也就是没有参数的url
            for item_url in totalUrl_noDouble :
                # 调用获取所有文件方法, 返回的是一个List, 设置一个代表list元素位置的全局变量数字为0
                iterator_num = 0
                # 获得当前url下的所有字段, 实际上也就是报文中所有的字段
                urlField_list = list(dataYaml_content[1].get(item_url).keys())
                # 遍历文件名list中的所有元素
                while True:
                    # iterator_num会在后边自加1, 当长度和iteratorDP_num相同, 代表遍历结束
                    if len(urlField_list) == iterator_num:
                        break
                    # 获得每个元素
                    one_urlField = urlField_list[iterator_num]
                    # 查询是否有过字段个数的记载
                    fieldNum = dataYaml_content[0].get(one_urlField)
                    # 会加1
                    if fieldNum == None:
                        dataYaml_content[0][one_urlField] = 1
                    else:
                        dataYaml_content[0][one_urlField] = fieldNum + 1
                    # 代表元素值得变量, 自加一
                    iterator_num += 1
            with open(dataYamlPath, 'w', encoding='utf-8') as f:
                # f.write(yaml.dump(dataYaml_content, Dumper=yaml.RoundTripDumper, allow_unicode=True))
                yaml.dump(dataYaml_content, f)
    else:
        print('数据库文件路径填写错误,请检查!!!!')



# 处理单个数据库中的方法, 按照url->字段->值的格式, 存入到data.yaml中
# systemName: 测试系统名     dataBasePath: 数据库地址      filterUrl: url过滤的关键字    loadDataBaseType: 加载数据库方式
# dataYaml_content: data.yaml的内容
def autoSave_sameUrlFildValueIntoYaml_main(systemName, dataBasePath, filterUrl, loadDataBaseType, dataYaml_content):
    # 有逗号, 说明加载数据库方式可能为id区间, 也可能是时间区间
    if isinstance(loadDataBaseType, list):
        # 标志位, 判断是时间区间加载数据库, 还是id区间加载数据库, 默认为False
        timeLoadDatabase = False
        for item in loadDataBaseType:
            # 判断如果有 : , 说明是时间加载
            if ':' in item:
                timeLoadDatabase = True
        if timeLoadDatabase:
            all = loadDataBase_Many(dataBasePath, '', '', loadDataBaseType)
        else:
            # 没有 : , 说明是id区间加载数据库
            all = loadDataBase_Many(dataBasePath, '', loadDataBaseType, '')
    else:
        # 没有逗号, 要不就是加载数据库所有数据
        if loadDataBaseType == 'loadAll':
            all = loadDataBase_ALL(dataBasePath)
        else:
            # 要不就是单独的一个数字, 一个id
            all = loadDataBase_Many(dataBasePath, int(loadDataBaseType), '', '')
    # 查询数据库结果为None
    if all == None:
        # 设置敏感信息文档生成路径
        now = time.localtime(time.time())
        nowNum = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_' + str(
            now.tm_hour) + '_' + str(now.tm_min) + '_' + str(now.tm_sec)
        reportPathName = init_testcase_path + systemName + '/report/' + nowNum + '_' + systemName + '_将请求URL字段及值写入到data.yaml功能_' + os.path.basename(
            dataBasePath) + '_加载出现错误_查询数据库返回为None.xlsx'
        excelTitile = ['数据库中总接口数量', '完成测试系统接口数量', '完成测试系统接口', '异常接口数量', '异常接口id']
        allSummaryData = [[0, 0, str(0), 0, str(0)]]
        save_data_excel_singleSheet(excelTitile, allSummaryData, reportPathName, '敏感信息测试统计')
        print('\n')
    # 查询数据库返回值为list, 并且list中没有元素
    elif isinstance(all, list) and len(all) == 0:
        # 设置敏感信息文档生成路径
        now = time.localtime(time.time())
        nowNum = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_' + str(
            now.tm_hour) + '_' + str(now.tm_min) + '_' + str(now.tm_sec)
        reportPathName = init_testcase_path + systemName + '/report/' + nowNum + '_' + systemName + '_将请求URL字段及值写入到data.yaml功能_' + os.path.basename(
            dataBasePath) + '_加载返回数据为0_没有匹配数据被查询出来.xlsx'
        excelTitile = ['数据库中总接口数量', '完成测试系统接口数量', '完成测试系统接口', '异常接口数量', '异常接口id']
        allSummaryData = [[0, 0, str(0), 0, str(0)]]
        save_data_excel_singleSheet(excelTitile, allSummaryData, reportPathName, '敏感信息测试统计')
        print('\n')
    else:
        # 完成测试系统接口数量
        num = 0
        # 数据库中总接口数量
        allnum = len(all)
        # 完成测试系统接口
        normalInterface = []
        # 异常接口id
        badInterface = []
        # 遍历逐条读取通过从数据库中查询的报文
        for item in all:
            # 获得url的host, 如果和预设在dataConfig.yaml中的值相同, 才会进行敏感信息的测试
            params = parse.urlparse(item[2])
            urlIpPort = params.netloc
            if urlIpPort in filterUrl :
                try:
                    # 调用方法进行敏感信息测试
                    saveUrlFieldValue_intoYmal_item(item, dataYaml_content)
                    num += 1
                    normalInterface.append(item[0])
                    print('完成提取id: ' + str(item[0]))
                    logging.info('完成提取id: ' + str(item[0]))
                except Exception:
                    badInterface.append(item[0])
                    print('处理接口 id：' + str(item[0]) + ' 出现异常')
                    logging.info('处理接口 id：' + str(item[0]) + ' 出现异常')
        logging.info('异常接口id： ' + str(badInterface))
        logging.info('完成处理接口: ' + str(normalInterface))
        logging.info('异常处理接口数量: ' + str(len(badInterface)))
        logging.info('完成处理接口数量: ' + str(num))
        logging.info('数据库中总接口数量: ' + str(allnum))
        logging.info('数据库: ' + dataBasePath + ' 处理完成')
        print('异常接口id： ' + str(badInterface))
        print('完成处理接口: ' + str(normalInterface))
        print('异常处理接口数量: ' + str(len(badInterface)))
        print('完成处理接口数量: ' + str(num))
        print('数据库中总接口数量: ' + str(allnum))
        print('数据库: ' + dataBasePath + ' 处理完成')
        print('\n')


# 按照数据数据类型, 调用方法, 处理报文日志, 类型包括: json、get参数、x-www-form-urlencoded、请求参数是否为空
# item[0]:ID             item[1]:本地ip地址        item[2]:url          item[3]:请求方式      item[4]:BURP_TOOL
# item[5]:请求头         item[6]:请求体            item[7]:响应头        item[8]:响应体        item[12]:发送请求时间
# 将一条burp插件的日志中的字段和字段对应的值,提取到一个yaml文件中
# item_logData : burp插件中的一条报文日志      dataYaml: 读取的对应系统的data.yaml表
def saveUrlFieldValue_intoYmal_item(item_logData, dataYaml):
    url = item_logData[2]
    reqHeaders = item_logData[5]
    reqBody = item_logData[6]
    params = parse.urlparse(url).query
    changeDict = parse.parse_qs(params)
    if changeDict != {}:
        result = {}
        for key in changeDict.keys():
            result[key] = changeDict.get(key)[0]
        if result != {}:
            # readBodyIntoDict(result, dataYaml, False)
            write_urlFieldValue_intoDictYaml(dataYaml, url, result)
    if reqBody not in ['', '{}', '[]', '{'':''}']:
        bodyType = headerType(reqHeaders)
        if 'json' in bodyType:
            reqBody_json = check_json_format(reqBody)
            if reqBody_json:
                # readBodyIntoDict(reqBody_json, dataYaml, False)
                write_urlFieldValue_intoDictYaml(dataYaml, url, reqBody_json)
        elif 'x-www-form-urlencoded' in bodyType:
            bodyParams = parse.urlparse('http://www.fakeUrl.com/fake.do?'+reqBody).query
            changeDict = parse.parse_qs(bodyParams)
            if changeDict != {}:
                result = {}
                for key in changeDict.keys():
                    result[key] = changeDict.get(key)[0]
                if result != {}:
                    # readBodyIntoDict(result, dataYaml, False)
                    write_urlFieldValue_intoDictYaml(dataYaml, url, result)


# 按照dataYaml是否有当前url, 来分类处理, url、field、value
# dataYaml: dataYaml.yaml表中的内容         url: 当前报文请求地址       body: 请求体dict类型
def write_urlFieldValue_intoDictYaml(dataYaml, url, body):
    # 第一个元素用来对总接口数(去重)、单个url、字段出现次数, 进行统计
    urlField_statiitic = dataYaml[0]
    # dataYaml是一个list, 0元素, 就是使用urlFieldValue写入的报文数据
    urlFieldValue = dataYaml[1]
    # 解析url, 拼接出一个没有?以及后边参数的url
    params = parse.urlparse(url)
    noQuestionUrl = params.scheme + '://' + params.netloc + params.path
    # 判断当前url, 没有?的url, 是否包含在urlFieldValue中, 这个集合格式
    # { 'url1': {'字段1': ['值1', '值2'] }, 'url2': {'字段1': ['值1',值2], '字段2': ['值1','值2'] }}
    # 所以urlFieldValue.keys(), 实际就是url集合
    if noQuestionUrl in list(urlFieldValue.keys()) :
        # 如果noQuestionUrl在集合中, 说明集合处理过对应url, 直接从url中取值, 作为参数调用方法即可
        body_handle = readBodyIntoDict_auto(body, urlFieldValue.get(url), False)
        urlFieldValue[noQuestionUrl] = body_handle
    else:
        # noQuestionUrl没有在集合中, 说明没有处理过当前url, 设置一个{}
        fieldValue = {}
        # 调用方法, 获得一个fieldValue的dict集合,
        body_handle = readBodyIntoDict_auto(body, fieldValue, False)
        # urlFieldValue是一个dict, 按照上边格式赋值
        urlFieldValue[noQuestionUrl] = body_handle
    # 统计总接口数量
    totalNum = urlField_statiitic.get('total')
    # 统计接口总量, 加1
    if totalNum == None:
        urlField_statiitic['total'] = 1
    else:
        urlField_statiitic['total'] = totalNum + 1
    # 统计当前url的个数
    urlNum = urlField_statiitic.get(noQuestionUrl)
    if urlNum == None:
        urlField_statiitic[noQuestionUrl] = 1
    else:
        urlField_statiitic[noQuestionUrl] = urlNum + 1



# 初始化测试系统, 生成各种配置表文件夹
# systemName : 测试系统名
def initialSystem(systemName):
    yaml = YAML()
    # 获得对应系统的dataConfig.yaml
    dataConfigYamlPath = ROOT_DIR + '/config/' + systemName + 'dataConfig.yaml'
    dataYamlPath = ROOT_DIR + '/testcase/' + systemName + '/data.yaml'
    createAllDir = [
                    ROOT_DIR + '/testcase/' + systemName + '/report/download'
                    ]
    # 遍历目录, 生成对应目录
    for item_dir in createAllDir:
        if not os.path.isdir(item_dir):
            os.makedirs(item_dir)
    print('当前测试系统,各测试类型文件夹生成完成!!!')
    logging.info('当前测试系统,各测试类型文件夹生成完成!!!')
    # 测试用全局配置表globalConfig.yaml
    if not os.path.exists(ROOT_DIR + '/config/' + 'globalConfig.yaml'):
        # yaml表是list，这样为了防止，字段中的值和系统中特殊标记的值重复，[1]中的才是存储字段和对应值的dict
        # init_dataConfig 存储在config/__init__.py中
        with open(ROOT_DIR + '/config/' + 'globalConfig.yaml', 'w', encoding='utf-8') as f:
            # f.write(yaml.dump(init_global_config, Dumper=yaml.RoundTripDumper, allow_unicode=True))
            yaml.dump(init_global_config, f)
        print('当前测试系统,dataConfig.yaml生成完成!!!')
        logging.info('当前测试系统,dataConfig.yaml生成完成!!!')
    else:
        globalConfig = read_yaml(ROOT_DIR + '/config/' + 'globalConfig.yaml')
        if systemName not in globalConfig['allTestedSystem'] :
            globalConfig['allTestedSystem'].append(systemName)
            with open(ROOT_DIR + '/config/' + 'globalConfig.yaml', 'w', encoding='utf-8') as f:
                # f.write(yaml.dump(init_global_config, Dumper=yaml.RoundTripDumper, allow_unicode=True))
                yaml.dump(globalConfig, f)
        else:
            print('当前新建系统名已经存在, 如果相关配置文件丢失, 脚本会恢复到初始状态。如果相关配置文件存在, 不做任何处理')
            logging.info('当前新建系统名已经存在, 如果相关配置文件丢失, 脚本会恢复到初始状态。如果相关配置文件存在, 不做任何处理')
    # 如果这个路径下没有对应系统名的dataConfig.yaml,生成一个
    if not os.path.exists(dataConfigYamlPath):
        init_dataConfig[0]['system'] = systemName
        # yaml表是list，这样为了防止，字段中的值和系统中特殊标记的值重复，[1]中的才是存储字段和对应值的dict
        # init_dataConfig 存储在config/__init__.py中

        with open(dataConfigYamlPath, 'w', encoding='utf-8') as f:
            # f.write(yaml.dump(init_dataConfig, Dumper=yaml.RoundTripDumper, allow_unicode=True))
            yaml.dump(init_dataConfig, f)
        print('当前测试系统,dataConfig.yaml生成完成!!!')
        logging.info('当前测试系统,dataConfig.yaml生成完成!!!')

    # auto自动化分析生成测试用例, 准备使用这个表, 计划权限测试的攻击负载也配置在这里
    if not os.path.exists(dataYamlPath):
        # 生成data.yaml, 内容就是一个空dict
        with open(dataYamlPath, 'w', encoding='utf-8') as f:
            # f.write(yaml.dump( [ {}, {} ], Dumper=yaml.RoundTripDumper, allow_unicode=True))
            yaml.dump([ {}, {} ], f)
        logging.info('当前测试系统,data.yaml生成完成!!!')
        print('当前测试系统,data.yaml生成完成!!!')
    # 使用pytest进行接口自动化测试，在运行之前需要配置表。当前判断这个配置表是否存在，不存在，生成pytest配置表
    if not os.path.exists(init_testcase_path + systemName + '/testCaseYamlPath.yaml'):
        # init_testCaseYamlPath 存储在config/__init__.py中，修改其中的system的值为系统名称
        init_testCaseYamlPath[0]['system'] = systemName
        with open(init_testcase_path + systemName + '/testCaseYamlPath.yaml', 'w', encoding='utf-8') as f:
            # f.write(yaml.dump(init_testCaseYamlPath, Dumper=yaml.RoundTripDumper, allow_unicode=True))
            yaml.dump(init_testCaseYamlPath, f)
        print('当前测试系统,testCaseYamlPath.yaml生成完成!!!')
        logging.info('当前测试系统,testCaseYamlPath.yaml生成完成!!!')


if __name__ == '__main__':
    params = sys.argv[1:]  # 获取命令行参数
    initialSystem(params[0])











