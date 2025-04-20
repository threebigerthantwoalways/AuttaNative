import sys,copy,time,logging,random,os
sys.stdout.reconfigure(encoding='utf-8')
# 当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上级目录
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
from config import *
from database.dataBaseSqlite import loadDataBase_ALL, loadDataBase_Many, generate_sql_query_safe, loadDataBase_ids
from util.yaml_util import read_yaml
from util import globalValue
from ruamel.yaml import YAML
from urllib import  parse
import urllib.parse
from util.utils import getConfigSetting

pyTemplate_upLoadMutiFile = init_pyTemplate_upLoadMutiFile
pyTemplate = init_pyTemplate
pyTemplate_downLoadUrl = init_pyTemplate_downLoadUrl
pyTemplate_downLoadField = init_pyTemplate_downLoadField









if __name__ == '__main__':
    params = sys.argv[1:]  # 获取命令行参数
    if '--scenario' in params :
        # params[0]: 生成用例类型, str类型, 后边代码会转数字    params[2]: 业务场景, 是一段文字, str类型
        globalConfig = read_yaml(ROOT_DIR + '/config/' + 'globalConfig.yaml')
        systemName = globalConfig[init_global_testSystem]
        # 读取当前系统的dataConfig.yaml
        dataBasePath, filterUrl, loadDataBaseType = getConfigSetting(systemName,
                                                                     ['dataBasePath', 'filterUrl', 'loadDataBaseType'])
        pic_flow = read_yaml(f'{ROOT_DIR}/testcase/{systemName}/pic_flow.yaml')
        pic_name_flow_num = pic_flow.get(params[2])
        # 从yaml存储的数据中，包含业务名、图片名、数据库中的ID值, 从对应的业务找出数据库中存储的ID值
        # 通过ID值, 这个值是list, 拼接sql语句, 进行数据库查询, 得到结果
        ids = []
        for key in pic_name_flow_num.keys():
            ids = pic_name_flow_num.get(key)
        sqlParams = generate_sql_query_safe(ids)
        all = loadDataBase_ids(dataBasePath, sqlParams[0], sqlParams[1])
        import json
        temp = []
        for num, itemLog in enumerate(all) :
            yamlData = {'api_name':{'name':''}, 'api_request':{'url': {'url': ''},'method':{'requestMethod':''},'headers':'','params':''}}
            # 将name值存储到yamlData的name中
            yamlData['api_name']['name'] = f'功能测试, 数据库中ID {itemLog[0]} ,业务 {params[2]} , 业务中第 {num} 接口'
            # 将url值存储到yamlData的url中
            yamlData['api_request']['url']['url'] = itemLog[2]
            yamlData['api_request']['method']['requestMethod'] = itemLog[3]
            # 请求头存入headers中
            yamlData['api_request']['headers'] = json.loads(itemLog[5])  # 先格式化头变成list，再转为dict
            try:
                if itemLog[6] != None and itemLog[6].stripe() != '':
                    yamlData[0]['api_request']['params'] = json.loads(itemLog[6])
            except Exception as  e:
                print(f'非dict,报错 -> {e}')
            temp.append(yamlData)
        yaml = YAML()
        with open(f'{ROOT_DIR}/{params[2]}.yaml', 'w', encoding='utf-8') as f:
            # f.write(yaml.dump(read_yaml(dataConfigYamlPath), Dumper=yaml.RoundTripDumper, allow_unicode=True))
            yaml.dump(temp, f)






