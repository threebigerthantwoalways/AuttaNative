import os,sys

# 获取当前执行文件所在目录（适用于 .exe 和 Python 脚本）
def get_executable_dir():
    if getattr(sys, 'frozen', False):  # 判断是否为 PyInstaller 打包后的文件
        return os.path.dirname(sys.executable)  # 获取 .exe 所在目录
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # 获取 .py 文件所在目录

# 获取主目录路径
# ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ROOT_DIR = get_executable_dir()

# 测试类型, 方法autoSave调用
init_testcaseStoryName_permission = '权限测试'
init_testcaseStoryName_sql = 'SQL注入测试'
init_testcaseStoryName_xss = '反射型xss测试'
init_testcaseStoryName_length = '边界值测试'
init_testcaseStoryName_download_url = '任意下载测试针对url目录测试'
init_testcaseStoryName_download_field= '任意下载测试针对字段测试'
init_testcaseStoryName_upload_multiFile = '任意上传测试不同文件'
init_testcaseStoryName_upload_field = '任意上传测试字段'

init_testcaseStoryName_permission_auto = '权限测试auto'
init_testcaseStoryName_sql_auto = 'SQL注入测试auto'
init_testcaseStoryName_xss_auto = '反射型xss测试auto'
init_testcaseStoryName_length_auto = '边界值测试auto'
init_testcaseStoryName_download_field_auto = '任意下载测试针对字段测试auto'
init_testcaseStoryName_upload_field_auto = '任意上传测试字段auto'

init_testcaseStoryName_permission_equal = '权限测试equal'
init_testcaseStoryName_sql_equal = 'SQL注入测试equal'
init_testcaseStoryName_xss_equal = '反射型xss测试equal'
init_testcaseStoryName_length_equal = '边界值测试equal'
init_testcaseStoryName_download_field_equal = '任意下载测试针对字段测试equal'
init_testcaseStoryName_upload_field_equal = '任意上传测试字段equal'

# shellCommand.py 调用的命令类型, 通过cmd输入的命令类型, 执行不同的方法
init_type_firstTestSystemInitial = 'ftsi'   # 首次测试系统初始化,生成各个配置表
init_type_queryInitSetting = 'qis'          # 查询当前系统初始化相关设置
# init_type_addDataBasePath = 'adp'           # 保存系统对应的数据库地址
init_type_setDataBasePath = 'sdp'           # 设置自动化测试系统对应的数据库地址
init_type_setFilterUrl = 'sfu'              # 设置自动化测试多虑数据库中的host
init_type_loadDataBaseType = 'ldt'          # 设置加载数据库方式
init_type_setTestSystem = 'sts'             # 设置当前系统配置为测试系统
# init_type_loadDataBaseManyId = 'lmi'        # 设置按照id加载一条数据库数据
# init_type_loadDataBaseManyRange = 'lmr'     # 设置按照id区间加载数据库中数据
# init_type_loadDataBaseManyTime = 'lmt'      # 设置按照时间区间加载数据库中的数据

init_type_saveDataConfig = 'sdc'             # 生成 dataconfig.yaml 文件
init_type_createPermissionCase = 'cp'        # 生成权限测试用例
init_type_createSqlCase = 'cs'               # 生成sql测试用例
init_type_createXssCase = 'cx'               # 生成xss测试用例
init_type_createLengthCase = 'cl'            # 生成边界值测试用例
init_type_createDownloadUrl = 'cdu'          # 生成下载测试针对url测试用例
init_type_createDownloadField = 'cdf'        # 生成下载测试针对字段测试用例
init_type_createUploadMultiFile = 'cumf'     # 生成上传测试针对上传不同文件测试用例
init_type_createUploadField = 'cuf'          # 生成上传测试针对字段测试用例
init_type_testAll = 'tall'                   # 测试单个系统, 从dataConfig.yaml文件生成到生成报告, 整个过程
init_type_testSensitive = 'tsen'             # 测试敏感信息
init_type_testStoryCase = 'tstory'           # 测试某个类型下的所有测试用例
init_type_testManyCase = 'tmany'             # 测试某个类型下指定的测试用例
# dataConfig.yaml配置中代表字段
init_autosavefield_limit = 'autosavefield_limit'
init_black_autosavefield = 'black_autosavefield'

init_permission_payload_limit = 'permission_payload_limit'
init_sql_payload_limit = 'sql_payload_limit'
init_xss_payload_limit = 'xss_payload_limit'
init_length_payload_limit = 'length_payload_limit'
init_download_testUrl_payload_limit = 'download_testUrl_payload_limit'
init_download_testfield_payload_limit = 'download_testfield_payload_limit'
init_upload_multifile_payload_limit = 'upload_multifile_payload_limit'
init_upload_field_payload_limit = 'upload_field_payload_limit'

init_permission_payload_limit_auto = 'permission_payload_limit_auto'
init_sql_payload_limit_auto = 'sql_payload_limit_auto'
init_xss_payload_limit_auto = 'xss_payload_limit_auto'
init_length_payload_limit_auto = 'length_payload_limit_auto'
init_download_testUrl_payload_limit_auto = 'download_testUrl_payload_limit_auto'
init_download_testfield_payload_limit_auto = 'download_testfield_payload_limit_auto'
init_upload_multifile_payload_limit_auto = 'upload_multifile_payload_limit_auto'
init_upload_field_payload_limit_auto = 'upload_field_payload_limit_auto'

init_permission_payload_limit_equal = 'permission_payload_limit_equal'
init_sql_payload_limit_equal = 'sql_payload_limit_equal'
init_xss_payload_limit_equal = 'xss_payload_limit_equal'
init_length_payload_limit_equal = 'length_payload_limit_equal'
init_download_testUrl_payload_limit_equal = 'download_testUrl_payload_limit_equal'
init_download_testfield_payload_limit_equal = 'download_testfield_payload_limit_equal'
init_upload_multifile_payload_limit_equal = 'upload_multifile_payload_limit_equal'
init_upload_field_payload_limit_equal = 'upload_field_payload_limit_equal'


# 全局设置的url的白名单
init_white_testUrl = 'white_testUrl'
# 黑名单全局的url，使用名, 方法jsonFieldValueSensitive、调用
init_black_testUrl = 'black_testUrl'
#
init_assert_all = 'assert_all'
# 敏感信息黑名单的url，使用名, 方法jsonFieldValueSensitive、调用
init_black_sensitive_testUrl = 'black_sensitive_testUrl'
# 敏感信息黑名单header，使用名, 方法jsonFieldValueSensitive、调用
init_black_sensitive_testHeader = 'black_sensitive_testHeader'
# 敏感信息黑名单field，使用名, 方法jsonFieldValueSensitive、调用
init_black_sensitive_testField = 'black_sensitive_testField'

# 使用这种模式测试敏感信息, 需要把敏感信息写入到这个字段中, 执行命令代码会自动化的执行敏感信息测试同时把非填写的敏感信息写入到黑名单中
init_filter_sensitive_unsave_into_blackList = 'filter_sensitive_unsave_into_blackList'
# 黑名单, 剔除了填写在init_filter_sensitive_unsave_into_blackList 中的信息
init_blackList_save_from_filter_sensitive = 'blackList_save_from_filter_sensitive'
# 过滤器, 在dataConfig.yaml中一个配置字段, 使用在敏感信息过滤重复的敏感信息测试, 这里存储了处理过的url,存储方式为dict, url为字段, 对应的值
# 为数字, 这个数字是filter_sensitive_urlNum_field_value(值为list)中的元素位置, 里边存储了过滤的header字段和对应值, 存储了
# 过滤字段和对应值
init_filter_sensitive_url = 'filter_sensitive_url'
# 看上个变量注释, filter_sensitive_urlNum_field_value 就是它
init_filter_sensitive_urlNum_field_value = 'filter_sensitive_urlNum_field_value'
# 自动化测试使用正则规则
init_regList_test = 'regList_test'
# 自动化测试存储的正则规则
init_regDict_store = 'regDict_store'
# 自动化测试使用包含内容
init_conList_test = 'conList_test'
# 自动化测试存储使用包含内容
init_conDict_store = 'conDict_store'

init_createPermissionCase_length_limit = 'createPermissionCase_length_limit'
init_createSqlCase_length_limit = 'createSqlCase_length_limit'
init_createXssCase_length_limit = 'createXssCase_length_limit'
init_createLengthCase_length_limit = 'createLengthCase_length_limit'
init_createDownloadUrlCase_length_limit = 'createDownloadUrlCase_length_limit'
init_creatDownloadFieldCase_length_limit = 'creatDownloadFieldCase_length_limit'
init_createUploadFileCase_length_limit = 'createUploadFileCase_length_limit'
init_createUploadFieldCase_length_limit = 'createUploadFieldCase_length_limit'

init_createPermissionCase_length_limit_auto = 'createPermissionCase_length_limit_auto'
init_createSqlCase_length_limit_auto = 'createSqlCase_length_limit_auto'
init_createXssCase_length_limit_auto = 'createXssCase_length_limit_auto'
init_createLengthCase_length_limit_auto = 'createLengthCase_length_limit_auto'
init_createDownloadUrlCase_length_limit_auto = 'createDownloadUrlCase_length_limit_auto'
init_creatDownloadFieldCase_length_limit_auto = 'creatDownloadFieldCase_length_limit_auto'
init_createUploadFileCase_length_limit_auto = 'createUploadFileCase_length_limit_auto'
init_createUploadFieldCase_length_limit_auto = 'createUploadFieldCase_length_limit_auto'

init_createPermissionCase_length_limit_equal = 'createPermissionCase_length_limit_equal'
init_createSqlCase_length_limit_equal = 'createSqlCase_length_limit_equal'
init_createXssCase_length_limit_equal = 'createXssCase_length_limit_equal'
init_createLengthCase_length_limit_equal = 'createLengthCase_length_limit_equal'
init_createDownloadUrlCase_length_limit_equal = 'createDownloadUrlCase_length_limit_equal'
init_creatDownloadFieldCase_length_limit_equal = 'creatDownloadFieldCase_length_limit_equal'
init_createUploadFileCase_length_limit_equal = 'createUploadFileCase_length_limit_equal'
init_createUploadFieldCase_length_limit_equal = 'createUploadFieldCase_length_limit_equal'


# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_permission_testUrl = 'black_permission_testUrl'
# # 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black__permission_testHeader = 'black_permission_testHeader'
# # 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_permission_testField = 'black_permission_testField'
# sql注入url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_sql_testUrl = 'black_sql_testUrl'
# # sql注入header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_sql_testHeader = 'black_sql_testHeader'
# # sql注入字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_sql_testField = 'black_sql_testField'
# xss测试url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_xss_testUrl = 'black_xss_testUrl'
# # xss测试header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_xss_testHeader = 'black_xss_testHeader'
# # xss测试字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_xss_testField = 'black_xss_testField'
# 边界值测试url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_length_testUrl = 'black_length_testUrl'
# # 边界值测试header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_length_testHeader = 'black_length_testHeader'
# # 边界值测试字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_length_testField = 'black_length_testField'
# 下载测试针对url的url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testUrl_multiUrl = 'black_download_testUrl_multiUrl'
# # 下载测试针对url的header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testHeader_multiUrl = 'black_download_testHeader_multiUrl'
# # 下载测试针对url的字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testField_multiUrl = 'black_download_testField_multiUrl'
# 下载测试针对字段, 请求体中url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testUrl_field = 'black_download_testUrl_field'
# # 下载测试针对字段, 请求体中header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testHeader_field = 'black_download_testHeader_field'
# # 下载测试针对字段, 请求体中字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testField_field = 'black_download_testField_field'
# 上传测试针对不同文件修改content-type, url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_upload_testUrl_multiFile = 'black_upload_testUrl_multiFile'
# # 上传测试针对不同文件修改content-type, header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_upload_testHeader_multiFile = 'black_upload_testHeader_multiFile'
# # 上传测试针对不同文件修改content-type, 字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_upload_testField_multiFile = 'black_upload_testField_multiFile'
# 本功能要修改为针对字段, 对字段添加攻击负载. url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_upload_testUrl_field = 'black_upload_testUrl_field'
# # 本功能要修改为针对字段,  对字段添加攻击负载. 请求头黑名单变量名.  方法jsonHeaderFieldTest调用
# init_black_upload_testHeader_field = 'black_upload_testHeader_field'
# # 本功能要修改为针对字段, 对字段添加攻击负载. 请求字段黑名单变量名.. 方法jsonHeaderFieldTest调用
# init_black_upload_testField_field = 'black_upload_testField_field'




# 权限用例生成方式
# init_create_testcase_model_permission = 'create_testcase_model_permission'
# 权限url相等白名单变量名. 方法调用
init_white_permission_testUrl = 'white_permission_testUrl'
# 权限header相等白名单变量名. 方法调用
init_white_permission_testHeader = 'white_permission_testHeader'
# 权限字段相等白名单变量名. 方法调用
init_white_permission_testField = 'white_permission_testField'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_permission_testUrl = 'black_permission_testUrl'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_permission_testHeader = 'black_permission_testHeader'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_permission_testField = 'black_permission_testField'
# 全量权限测试断言
init_assert_permission = 'assert_permission'
# 权限url相等白名单变量名. 方法调用
init_white_permission_testUrl_auto = 'white_permission_testUrl_auto'
# 权限header相等白名单变量名. 方法调用
init_white_permission_testHeader_auto = 'white_permission_testHeader_auto'
# 权限字段相等白名单变量名. 方法调用
init_white_permission_testField_auto = 'white_permission_testField_auto'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_permission_testUrl_auto = 'black_permission_testUrl_auto'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_permission_testHeader_auto = 'black_permission_testHeader_auto'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_permission_testField_auto = 'black_permission_testField_auto'
# auto权限测试断言
init_assert_permission_auto = 'assert_permission_auto'
# 权限url相等白名单变量名. 方法调用
init_white_permission_testUrl_equal = 'white_permission_testUrl_equal'
# 权限header相等白名单变量名. 方法调用
init_white_permission_testHeader_equal = 'white_permission_testHeader_equal'
# 权限字段相等白名单变量名. 方法调用
init_white_permission_testField_equal = 'white_permission_testField_equal'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_permission_testUrl_equal = 'black_permission_testUrl_equal'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_permission_testHeader_equal = 'black_permission_testHeader_equal'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_permission_testField_equal = 'black_permission_testField_equal'
# equal权限测试断言
init_assert_permission_equal = 'assert_permission_equal'

# 权限用例生成方式
# init_create_testcase_model_sql = 'create_testcase_model_sql'
# 权限url相等白名单变量名. 方法调用
init_white_sql_testUrl = 'white_sql_testUrl'
# 权限header相等白名单变量名. 方法调用
init_white_sql_testHeader = 'white_sql_testHeader'
# 权限字段相等白名单变量名. 方法调用
init_white_sql_testField = 'white_sql_testField'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_sql_testUrl = 'black_sql_testUrl'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_sql_testHeader = 'black_sql_testHeader'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_sql_testField = 'black_sql_testField'
# 全量sql断言
init_assert_sql = 'assert_sql'
# 权限url相等白名单变量名. 方法调用
init_white_sql_testUrl_auto = 'white_sql_testUrl_auto'
# 权限header相等白名单变量名. 方法调用
init_white_sql_testHeader_auto = 'white_sql_testHeader_auto'
# 权限字段相等白名单变量名. 方法调用
init_white_sql_testField_auto = 'white_sql_testField_auto'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_sql_testUrl_auto = 'black_sql_testUrl_auto'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_sql_testHeader_auto = 'black_sql_testHeader_auto'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_sql_testField_auto = 'black_sql_testField_auto'
# auto的sql断言
init_assert_sql_auto = 'assert_sql_auto'
# 权限url相等白名单变量名. 方法调用
init_white_sql_testUrl_equal = 'white_sql_testUrl_equal'
# 权限header相等白名单变量名. 方法调用
init_white_sql_testHeader_equal = 'white_sql_testHeader_equal'
# 权限字段相等白名单变量名. 方法调用
init_white_sql_testField_equal = 'white_sql_testField_equal'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_sql_testUrl_equal = 'black_sql_testUrl_equal'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_sql_testHeader_equal = 'black_sql_testHeader_equal'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_sql_testField_equal = 'black_sql_testField_equal'
# equal的sql断言
init_assert_sql_equal = 'assert_sql_equal'

# 权限用例生成方式
# init_create_testcase_model_xss = 'create_testcase_model_xss'
# 权限url相等白名单变量名. 方法调用
init_white_xss_testUrl = 'white_xss_testUrl'
# 权限header相等白名单变量名. 方法调用
init_white_xss_testHeader = 'white_xss_testHeader'
# 权限字段相等白名单变量名. 方法调用
init_white_xss_testField = 'white_xss_testField'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_xss_testUrl = 'black_xss_testUrl'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_xss_testHeader = 'black_xss_testHeader'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_xss_testField = 'black_xss_testField'
# 全量xss断言
init_assert_xss = 'assert_xss'
# 权限url相等白名单变量名. 方法调用
init_white_xss_testUrl_auto = 'white_xss_testUrl_auto'
# 权限header相等白名单变量名. 方法调用
init_white_xss_testHeader_auto = 'white_xss_testHeader_auto'
# 权限字段相等白名单变量名. 方法调用
init_white_xss_testField_auto = 'white_xss_testField_auto'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_xss_testUrl_auto = 'black_xss_testUrl_auto'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_xss_testHeader_auto = 'black_xss_testHeader_auto'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_xss_testField_auto = 'black_xss_testField_auto'
# auto的xss断言
init_assert_xss_auto = 'assert_xss_auto'
# 权限url相等白名单变量名. 方法调用
init_white_xss_testUrl_equal = 'white_xss_testUrl_equal'
# 权限header相等白名单变量名. 方法调用
init_white_xss_testHeader_equal = 'white_xss_testHeader_equal'
# 权限字段相等白名单变量名. 方法调用
init_white_xss_testField_equal = 'white_xss_testField_equal'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_xss_testUrl_equal = 'black_xss_testUrl_equal'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_xss_testHeader_equal = 'black_xss_testHeader_equal'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_xss_testField_equal = 'black_xss_testField_equal'
# equal的xss断言
init_assert_xss_equal = 'assert_xss_equal'

#
# init_create_testcase_model_length = 'create_testcase_model_length'
# 权限url相等白名单变量名. 方法调用
init_white_length_testUrl = 'white_length_testUrl'
# 权限header相等白名单变量名. 方法调用
init_white_length_testHeader = 'white_length_testHeader'
# 权限字段相等白名单变量名. 方法调用
init_white_length_testField = 'white_length_testField'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_length_testUrl = 'black_length_testUrl'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_length_testHeader = 'black_length_testHeader'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_length_testField = 'black_length_testField'
# 全量边界值断言
init_assert_length = 'assert_length'
# 权限url相等白名单变量名. 方法调用
init_white_length_testUrl_auto = 'white_length_testUrl_auto'
# 权限header相等白名单变量名. 方法调用
init_white_length_testHeader_auto = 'white_length_testHeader_auto'
# 权限字段相等白名单变量名. 方法调用
init_white_length_testField_auto = 'white_length_testField_auto'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_length_testUrl_auto = 'black_length_testUrl_auto'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_length_testHeader_auto = 'black_length_testHeader_auto'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_length_testField_auto = 'black_length_testField_auto'
# auto的边界值断言
init_assert_length_auto = 'assert_length_auto'
# 权限url相等白名单变量名. 方法调用
init_white_length_testUrl_equal = 'white_length_testUrl_equal'
# 权限header相等白名单变量名. 方法调用
init_white_length_testHeader_equal = 'white_length_testHeader_equal'
# 权限字段相等白名单变量名. 方法调用
init_white_length_testField_equal = 'white_length_testField_equal'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_length_testUrl_equal = 'black_length_testUrl_equal'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_length_testHeader_equal = 'black_length_testHeader_equal'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_length_testField_equal = 'black_length_testField_equal'
# equal的边界值断言
init_assert_length_equal = 'assert_length_equal'

#
# init_create_testcase_model_download_multiUrl = 'create_testcase_model_download_multiUrl'
# 权限url相等白名单变量名. 方法调用
init_white_download_testUrl_multiUrl = 'white_download_testUrl_multiUrl'
# 权限header相等白名单变量名. 方法调用
init_white_download_testHeader_multiUrl = 'white_download_testHeader_multiUrl'
# 权限字段相等白名单变量名. 方法调用
init_white_download_testField_multiUrl = 'white_download_testField_multiUrl'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testUrl_multiUrl = 'black_download_testUrl_multiUrl'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testHeader_multiUrl = 'black_download_testHeader_multiUrl'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testField_multiUrl = 'black_download_testField_multiUrl'
# 全量下载测试,针对url
init_assert_download_multiUrl = 'assert_download_multiUrl'
# 权限url相等白名单变量名. 方法调用  1
init_white_download_testUrl_multiUrl_equal = 'white_download_testUrl_multiUrl_equal'
# 权限header相等白名单变量名. 方法调用
init_white_download_testHeader_multiUrl_equal = 'white_download_testHeader_multiUrl_equal'
# 权限字段相等白名单变量名. 方法调用
init_white_download_testField_multiUrl_equal = 'white_download_testField_multiUrl_equal'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testUrl_multiUrl_equal = 'black_download_testUrl_multiUrl_equal'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testHeader_multiUrl_equal = 'black_download_testHeader_multiUrl_equal'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testField_multiUrl_equal = 'black_download_testField_multiUrl_equal'
# equal下载测试,针对url
init_assert_download_multiUrl_equal = 'assert_download_multiUrl_equal'

#
# init_create_testcase_model_download_field = 'create_testcase_model_download_field'
# 权限url相等白名单变量名. 方法调用
init_white_download_testUrl_field = 'white_download_testUrl_field'
# 权限header相等白名单变量名. 方法调用
init_white_download_testHeader_field = 'white_download_testHeader_field'
# 权限字段相等白名单变量名. 方法调用
init_white_download_testField_field = 'white_download_testField_field'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testUrl_field = 'black_download_testUrl_field'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testHeader_field = 'black_download_testHeader_field'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testField_field = 'black_download_testField_field'
# 全量下载测试针对字段
init_assert_download_field = 'assert_download_field'
# 权限url相等白名单变量名. 方法调用
init_white_download_testUrl_field_auto = 'white_download_testUrl_field_auto'
# 权限header相等白名单变量名. 方法调用
init_white_download_testHeader_field_auto = 'white_download_testHeader_field_auto'
# 权限字段相等白名单变量名. 方法调用
init_white_download_testField_field_auto = 'white_download_testField_field_auto'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testUrl_field_auto = 'black_download_testUrl_field_auto'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testHeader_field_auto = 'black_download_testHeader_field_auto'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testField_field_auto = 'black_download_testField_field_auto'
# auto下载测试,针对字段
init_assert_download_field_auto = 'assert_download_field_auto'
# 权限url相等白名单变量名. 方法调用  1
init_white_download_testUrl_field_equal = 'white_download_testUrl_field_equal'
# 权限header相等白名单变量名. 方法调用
init_white_download_testHeader_field_equal = 'white_download_testHeader_field_equal'
# 权限字段相等白名单变量名. 方法调用
init_white_download_testField_field_equal = 'white_download_testField_field_equal'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testUrl_field_equal = 'black_download_testUrl_field_equal'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testHeader_field_equal = 'black_download_testHeader_field_equal'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_download_testField_field_equal = 'black_download_testField_field_equal'
# equal下载测试,针对字段
init_assert_download_field_equal = 'assert_download_field_equal'

#
# init_create_testcase_model_upload_multiFile = 'create_testcase_model_upload_multiFile'
# 权限url相等白名单变量名. 方法调用
init_white_upload_testUrl_multiFile = 'white_upload_testUrl_multiFile'
# 权限header相等白名单变量名. 方法调用
init_white_upload_testHeader_multiFile = 'white_upload_testHeader_multiFile'
# 权限字段相等白名单变量名. 方法调用
init_white_upload_testField_multiFile = 'white_upload_testField_multiFile'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testUrl_multiFile = 'black_upload_testUrl_multiFile'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testHeader_multiFile = 'black_upload_testHeader_multiFile'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testField_multiFile = 'black_upload_testField_multiFile'
# 全量测试上传针对不同文件
init_assert_upload_multiFile = 'assert_upload_multiFile'
# 权限url相等白名单变量名. 方法调用
init_white_upload_testUrl_multiFile_equal = 'white_upload_testUrl_multiFile_equal'
# 权限header相等白名单变量名. 方法调用
init_white_upload_testHeader_multiFile_equal = 'white_upload_testHeader_multiFile_equal'
# 权限字段相等白名单变量名. 方法调用
init_white_upload_testField_multiFile_equal = 'white_upload_testField_multiFile_equal'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testUrl_multiFile_equal = 'black_upload_testUrl_multiFile_equal'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testHeader_multiFile_equal = 'black_upload_testHeader_multiFile_equal'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testField_multiFile_equal = 'black_upload_testField_multiFile_equal'
# equal上传测试针对不同文件
init_assert_upload_multiFile_equal = 'assert_upload_multiFile_equal'

#
# init_create_testcase_model_upload_field = 'create_testcase_model_upload_field'
# 权限url相等白名单变量名. 方法调用
init_white_upload_testUrl_field = 'white_upload_testUrl_field'
# 权限header相等白名单变量名. 方法调用
init_white_upload_testHeader_field = 'white_upload_testHeader_field'
# 权限字段相等白名单变量名. 方法调用
init_white_upload_testField_field = 'white_upload_testField_field'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testUrl_field = 'black_upload_testUrl_field'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testHeader_field = 'black_upload_testHeader_field'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testField_field = 'black_upload_testField_field'
# 全量测试上传, 针对字段
init_assert_upload_field = 'assert_upload_field'
# 权限url相等白名单变量名. 方法调用
init_white_upload_testUrl_field_auto = 'white_upload_testUrl_field_auto'
# 权限header相等白名单变量名. 方法调用
init_white_upload_testHeader_field_auto = 'white_upload_testHeader_field_auto'
# 权限字段相等白名单变量名. 方法调用
init_white_upload_testField_field_auto = 'white_upload_testField_field_auto'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testUrl_field_auto = 'black_upload_testUrl_field_auto'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testHeader_field_auto = 'black_upload_testHeader_field_auto'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testField_field_auto = 'black_upload_testField_field_auto'
# auto测试上传, 针对字段
init_assert_upload_field_auto = 'assert_upload_field_auto'
# 权限url相等白名单变量名. 方法调用
init_white_upload_testUrl_field_equal = 'white_upload_testUrl_field_equal'
# 权限header相等白名单变量名. 方法调用
init_white_upload_testHeader_field_equal = 'white_upload_testHeader_field_equal'
# 权限字段相等白名单变量名. 方法调用
init_white_upload_testField_field_equal = 'white_upload_testField_field_equal'
# 权限url黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testUrl_field_equal = 'black_upload_testUrl_field_equal'
# 权限header黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testHeader_field_equal = 'black_upload_testHeader_field_equal'
# 针对生成用例auto, 权限字段黑名单变量名. 方法jsonHeaderFieldTest调用
init_black_upload_testField_field_equal = 'black_upload_testField_field_equal'
# equal测试上传, 针对字段
init_assert_upload_field_equal = 'assert_upload_field_equal'

# 读取数据库的后缀类型, 先执行'urlHeader':{},'header':{}, 后执行'urlScript':{},'script':{}
init_filter_dataBaseName_suffix = 'filter_dataBaseName_suffix'

# init_modifyReqHeader_urlHeader = 'modifyReqHeader_urlHeader'
# 修改请求头, 通过字段修改
# init_modifyReqHeader_header = 'modifyReqHeader_header'

# init_modifyReqHeader_urlHeaderScript = 'modifyReqHeader_urlHeaderScript'

# init_modifyReqHeader_headerScript = 'modifyReqHeader_headerScript'

# 修改请求头
init_need_modifyReqHeader = 'need_modifyReqHeader'
# 修改请体中字段对应的值
# init_need_modifyReqBodyFieldValue = 'need_modifyReqBodyFieldValue'
# 修改请求体中的文字
# init_need_modifyReqBodyText = 'need_modifyReqBodyText'
# 修改响应头
# init_need_modifyResHeader = 'need_modifyResHeader'
# 修改响应体中字段对应的值
# init_need_modifyResBodyFeildValue = 'need_modifyResBodyFeildValue'
# 修改响应体中的文字
# init_need_modifyResBodyText = 'need_modifyResBodyText'
# 请求体中包含某些字符, 脚本应该实现什么功能
# init_need_reqBodyContain_scriptDoSomething = 'need_reqBodyContain_scriptDoSomething'
# 请求体中包含某些字段, 脚本应该实现什么功能
# init_need_reqBodyEqualField_scriptDoSomething = 'need_reqBodyEqualField_scriptDoSomething'
# 请求体中包含某些字段对应的值, 脚本应该实现什么功能
# init_need_reqBodyEqualFieldValue_scriptDoSomething = 'need_reqBodyEqualFieldValue_scriptDoSomething'
# 响应体中包含某些字符, 脚本应该实现什么功能
# init_need_resBodyContain_scriptDoSomething = 'need_resBodyContain_scriptDoSomething'
# 响应体中包含某些字段, 脚本应该实现什么功能
# init_need_resBodyEqualField_scriptDoSomething = 'need_resBodyEqualField_scriptDoSomething'
# 响应体中包含某些字段对应的值, 脚本应该实现什么功能
# init_need_resBodyEqualFieldValue_scriptDoSomething = 'need_resBodyEqualFieldValue_scriptDoSomething'


init_global_testSystem = 'global_testSystem'
init_global_proxy = 'global_proxy'
init_global_proxy_port = 'global_proxy_port'
init_global_allTestedSystem = 'allTestedSystem'
init_global_allTestedSetting = 'allTestedSetting'
init_global_allCreateTestcase = 'allCreateTestcase'
init_global_allTest = 'allTest'
init_global_allArrangeAnalysis = 'allArrangeAnalysis'
init_global_imageType = 'allImageType'
init_global_imageType_value = {'原图': 'image','绘制图片': 'draw'}
init_global_db_field = 'allDbField'
init_global_db_field_value = ["ID", "LOCAL_SOURCE_IP", "TARGET_URL", "HTTP_METHOD","BURP_TOOL", "REQ_HEADERS",
"REQ_BODY", "RES_HEADERS","RES_BODY", "WORK_NUM", "SAME_DIRECTORY","ENCRYPT_DECRYPT_KEY", "SEND_DATETIME"]
init_global_allTestedSetting_value = {'数据库名':'dataBasePath','读取数据库过滤的Host':'filterUrl','加载数据库方式':'loadDataBaseType',
'请求头配置': init_need_modifyReqHeader, '敏感信息规则包含': init_conList_test, '敏感信息规则正则': init_regList_test,
'敏感信息规则包含存储': init_conDict_store, '敏感信息规则正则存储': init_regDict_store,
'权限测试白名单URL': 'white_permission_testUrl', '权限测试白名单URL字段': 'white_permission_testField', '权限测试白名单字段': 'white_permission_testField',
'权限测试黑名单URL': 'black_permission_testUrl', '权限测试黑名单URL字段': 'black_permission_testField', '权限测试黑名单字段': 'black_permission_testField',
'权限测试白名单URL(equal)': 'white_permission_testUrl_equal', '权限测试白名单URL字段(equal)': 'white_permission_testField_equal', '权限测试白名单字段(equal)': 'white_permission_testField_equal',
'权限测试黑名单URL(equal)': 'black_permission_testUrl_equal', '权限测试黑名单URL字段(equal)': 'black_permission_testField_equal', '权限测试黑名单字段(equal)': 'black_permission_testField_equal',

'sql测试白名单URL': 'white_sql_testUrl', 'sql测试白名单URL字段': 'white_sql_testField', 'sql测试白名单字段': 'white_sql_testField',
'sql测试黑名单URL': 'black_sql_testUrl', 'sql测试黑名单URL字段': 'black_sql_testField', 'sql测试黑名单字段': 'black_sql_testField',
'sql测试白名单URL(equal)': 'white_sql_testUrl_equal', 'sql测试白名单URL字段(equal)': 'white_sql_testField_equal', 'sql测试白名单字段(equal)': 'white_sql_testField_equal',
'sql测试黑名单URL(equal)': 'black_sql_testUrl_equal', 'sql测试黑名单URL字段(equal)': 'black_sql_testField_equal', 'sql测试黑名单字段(equal)': 'black_sql_testField_equal',

'xss测试白名单URL': 'white_xss_testUrl', 'xss测试白名单URL字段': 'white_xss_testField', 'xss测试白名单字段': 'white_xss_testField',
'xss测试黑名单URL': 'black_xss_testUrl', 'xss测试黑名单URL字段': 'black_xss_testField', 'xss测试黑名单字段': 'black_xss_testField',
'xss测试白名单URL(equal)': 'white_xss_testUrl_equal', 'xss测试白名单URL字段(equal)': 'white_xss_testField_equal', 'xss测试白名单字段(equal)': 'white_xss_testField_equal',
'xss测试黑名单URL(equal)': 'black_xss_testUrl_equal', 'xss测试黑名单URL字段(equal)': 'black_xss_testField_equal', 'xss测试黑名单字段(equal)': 'black_xss_testField_equal',

'边界值测试白名单URL': 'white_length_testUrl', '边界值测试白名单URL字段': 'white_length_testField', '边界值测试白名单字段': 'white_length_testField',
'边界值测试黑名单URL': 'black_length_testUrl', '边界值测试黑名单URL字段': 'black_length_testField', '边界值测试黑名单字段': 'black_length_testField',
'边界值测试白名单URL(equal)': 'white_length_testUrl_equal', '边界值测试白名单URL字段(equal)': 'white_length_testField_equal', '边界值测试白名单字段(equal)': 'white_length_testField_equal',
'边界值测试黑名单URL(equal)': 'black_length_testUrl_equal', '边界值测试黑名单URL字段(equal)': 'black_length_testField_equal', '边界值测试黑名单字段(equal)': 'black_length_testField_equal',

'下载地址测试白名单URL': 'white_download_testUrl_multiUrl',
'下载地址测试黑名单URL': 'black_download_testUrl_multiUrl',
'下载地址测试白名单URL(equal)': 'white_download_testUrl_multiUrl_equal',
'下载地址测试黑名单URL(equal)': 'black_download_testUrl_multiUrl_equal',

'下载字段测试白名单URL': 'white_download_testUrl_field', '下载字段测试白名单URL字段': 'white_download_testField_field', '下载字段测试白名单字段': 'white_download_testField_field',
'下载字段测试黑名单URL': 'black_download_testUrl_field', '下载字段测试黑名单URL字段': 'black_download_testField_field', '下载字段测试黑名单字段': 'black_download_testField_field',
'下载字段测试白名单URL(equal)': 'white_download_testUrl_field_equal', '下载字段测试白名单URL字段(equal)': 'white_download_testField_field_equal', '下载字段测试白名单字段(equal)': 'white_download_testField_field_equal',
'下载字段测试黑名单URL(equal)': 'black_download_testUrl_field_equal', '下载字段测试黑名单URL字段(equal)': 'black_download_testField_field_equal', '下载字段测试黑名单字段(equal)': 'black_download_testField_field_equal',

'上传多文件测试白名单URL': 'white_upload_testUrl_multiFile',
'上传多文件测试黑名单URL': 'black_upload_testUrl_multiFile',
'上传多文件测试白名单URL(equal)': 'white_upload_testUrl_multiFile_equal',
'上传多文件测试黑名单URL(equal)': 'black_upload_testUrl_multiFile_equal',

'上传字段测试白名单URL': 'white_upload_testUrl_field', '上传字段测试白名单URL字段': 'white_upload_testField_field', '上传字段测试白名单字段': 'white_upload_testField_field',
'上传字段测试黑名单URL': 'black_upload_testUrl_field', '上传字段测试黑名单URL字段': 'black_upload_testField_field', '上传字段测试黑名单字段': 'black_upload_testField_field',
'上传字段测试白名单URL(equal)': 'white_upload_testUrl_field_equal', '上传字段测试白名单URL字段(equal)': 'white_upload_testField_field_equal', '上传字段测试白名单字段(equal)': 'white_upload_testField_field_equal',
'上传字段测试黑名单URL(equal)': 'black_upload_testUrl_field_equal', '上传字段测试黑名单URL字段(equal)': 'black_upload_testField_field_equal', '上传字段测试黑名单字段(equal)': 'black_upload_testField_field_equal',

'权限测试用例生成value长度限制':'createPermissionCase_length_limit','sql测试用例生成value长度限制':'createSqlCase_length_limit',
'xss测试用例生成value长度限制':'createXssCase_length_limit','边界值测试用例生成value长度限制':'createLengthCase_length_limit',
'下载针对字段测试用例生成value长度限制':'creatDownloadFieldCase_length_limit','上传针对字段测试用例生成value长度限制':'createUploadFieldCase_length_limit',
'权限测试用例生成value长度限制(equal)':'createPermissionCase_length_limit_equal','sql测试用例生成value长度限制(equal)':'createSqlCase_length_limit_equal',
'xss测试用例生成value长度限制(equal)':'createXssCase_length_limit_equal','边界值测试用例生成value长度限制(equal)':'createLengthCase_length_limit_equal',
'下载针对字段测试用例生成value长度限制(equal)':'creatDownloadFieldCase_length_limit_equal','上传针对字段测试用例生成value长度限制(equal)':'createUploadFieldCase_length_limit_equal',
'权限测试攻击负载限制':'permission_payload_limit','sql测试攻击负载限制':'sql_payload_limit','xss测试攻击负载限制':'xss_payload_limit',
'边界值测试攻击负载限制':'length_payload_limit','下载针对URL测试攻击负载限制':'download_testUrl_payload_limit',
'下载针对字段测试攻击负载限制':'download_testfield_payload_limit','上传针对多文件测试攻击负载限制':'upload_multifile_payload_limit',
'上传针对字段测试攻击负载限制':'upload_field_payload_limit',
'权限测试攻击负载限制(equal)':'permission_payload_limit_equal','sql测试攻击负载限制(equal)':'sql_payload_limit_equal','xss测试攻击负载限制(equal)':'xss_payload_limit_equal',
'边界值测试攻击负载限制(equal)':'length_payload_limit_equal','下载针对URL测试攻击负载限制(equal)':'download_testUrl_payload_limit_equal',
'下载针对字段测试攻击负载限制(equal)':'download_testfield_payload_limit_equal','上传针对多文件测试攻击负载限制(equal)':'upload_multifile_payload_limit_equal',
'上传针对字段测试攻击负载限制(equal)':'upload_field_payload_limit_equal',
'权限测试断言':'assert_permission','sql测试断言':'assert_sql','xss测试断言':'assert_xss','边界值测试断言':'assert_length',
'下载针对url测试断言':'assert_download_multiUrl','下载针对字段测试断言':'assert_download_field','上传多文件测试断言':'assert_upload_multiFile',
'上传针对字段测试断言':'assert_upload_field',
'权限测试断言(equal)':'assert_permission_equal','sql测试断言(equal)':'assert_sql_equal','xss测试断言(equal)':'assert_xss_equal','边界值测试断言(equal)':'assert_length_equal',
'下载针对url测试断言(equal)':'assert_download_multiUrl_equal','下载针对字段测试断言(equal)':'assert_download_field_equal','上传多文件测试断言(equal)':'assert_upload_multiFile_equal',
'上传针对字段测试断言(equal)':'assert_upload_field_equal'
}
init_global_allCreateTestcase_value = {'生成yaml格式接口':'2'}
init_global_allTest_value = { '生成yaml格式接口': '2' }
init_global_allArrangeAnalysis_value = {'绘制图片(标注位置)': 'drawArrow'}

init_global_config = {init_global_testSystem:'', init_global_proxy:'', init_global_proxy_port:'',
init_global_allTestedSystem: [], init_global_imageType : init_global_imageType_value,
init_global_db_field : init_global_db_field_value ,
init_global_allTestedSetting: init_global_allTestedSetting_value,
init_global_allCreateTestcase: init_global_allCreateTestcase_value, init_global_allTest: init_global_allTest_value,
init_global_allArrangeAnalysis: init_global_allArrangeAnalysis_value }

# 系统下拉框第一行的选项名
init_system_first_dropdown_option = '全部测试系统'
# 设置参数下拉框第一行的选项名
init_setting_first_dropdown_option = '设置参数'

init_dataBasePath = 'dataBasePath'
init_filterUrl = 'filterUrl'
init_loadDataBaseType = 'loadDataBaseType'

init_filterHeader = 'filterHeader'
init_filterUrlValue = 'filterUrlValue'
init_filterUrlField = 'filterUrlField'
init_filterUrlFieldValue = 'filterUrlFieldValue'
init_blackHeader = 'blackHeader'
init_blackUrlValue = 'blackUrlValue'
init_blackUrlField = 'blackUrlField'
init_blackUrlFieldValue = 'blackUrlFieldValue'



# wsdl接口
init_con_wsdl = 'wsdl'
# jvm启动参数
init_con_jvm = 'jvm启动参数'
# 百度可能导致key泄露的url
init_con_api_baidu1 = 'api.map.baidu.com/api'
# 百度可能导致key泄露的url
init_con_api_baidu2 = 'api.map.baidu.com/getscript'
# 腾讯可能导致key泄露的url
init_con_api_tecent1 = 'map.qq.com/api'
# 腾讯可能导致key泄露的url
init_con_api_tecent2 = 'apis.map.qq.com'
# 可能导致key泄露的url
init_con_api_map = 'webapi.amap.com/maps'

# 包含apache错误信息提示
init_con_apache = 'apache'
# 包含tomcat错误信息提示
init_con_tomcat = 'tomcat'
# 包含mysql错误信息提示
init_con_mysql = 'mysql'
# 包含ibatis错误信息提示
init_con_ibatis = 'ibatis'
# 包含mybatis错误信息提示
init_con_mybatis = 'mybatis'
# 包含exception错误信息提示
init_con_exception = 'exception'


# 姓名的正则表达式
init_reg_name = r"([赵|钱|孙|李|周|吴|郑|王|冯|陈|褚|卫|蒋|沈|韩|杨|朱|秦|尤|许|何|吕|施|张|孔|曹|严|华|金|魏|陶|姜|戚|谢|邹|喻|柏|水|窦|章|云|苏|潘|葛|奚|范|彭|郎|鲁|韦|昌|马|苗|凤|花|方|俞|任|袁|柳|酆|鲍|史|唐|费|廉|岑|薛|雷|贺|倪|汤|滕|殷|罗|毕|郝|邬|安|常|乐|于|时|傅|皮|卞|齐|康|伍|余|元|卜|顾|孟|平|黄|和|穆|萧|尹|姚|邵|湛|汪|祁|毛|禹|狄|米|贝|明|臧|计|伏|成|戴|谈|宋|茅|庞|熊|纪|舒|屈|项|祝|董|梁|杜|阮|蓝|闵|席|季|麻|强|贾|路|娄|危|江|童|颜|郭|梅|盛|林|刁|锺|徐|邱|骆|高|夏|蔡|田|樊|胡|凌|霍|虞|万|支|柯|昝|管|卢|莫|经|房|裘|缪|干|解|应|宗|丁|宣|贲|邓|郁|单|杭|洪|包|诸|左|石|崔|吉|钮|龚|程|嵇|邢|滑|裴|陆|荣|翁|荀|羊|於|惠|甄|麴|家|封|芮|羿|储|靳|汲|邴|糜|松|井|段|富|巫|乌|焦|巴|弓|牧|隗|山|谷|车|侯|宓|蓬|全|郗|班|仰|秋|仲|伊|宫|宁|仇|栾|暴|甘|钭|历|戎|祖|武|符|刘|景|詹|束|龙|叶|幸|司|韶|郜|黎|溥|印|宿|白|怀|蒲|邰|从|鄂|索|咸|籍|卓|蔺|屠|蒙|池|乔|阳|郁|胥|能|苍|双|闻|莘|党|翟|谭|贡|劳|逄|姬|申|扶|堵|冉|宰|郦|雍|却|桑|桂|濮|牛|寿|通|边|扈|燕|冀|浦|尚|农|温|别|庄|晏|柴|瞿|充|慕|连|茹|习|宦|艾|鱼|容|向|古|易|慎|戈|廖|庾|终|暨|居|衡|步|都|耿|满|弘|匡|国|文|寇|广|禄|阙|东|欧|沃|利|蔚|越|夔|隆|师|巩|厍|聂|晁|勾|敖|融|冷|訾|辛|阚|那|简|饶|空|曾|毋|沙|乜|养|鞠|须|丰|巢|关|蒯|相|荆|红|游|竺|权|司马|上官|欧阳|夏侯|诸葛|闻人|东方|赫连|皇甫|尉迟|公羊|澹台|公冶宗政|濮阳|淳于|单于|太叔|申屠|公孙|仲孙|轩辕|令狐|钟离|宇文|长孙|慕容|司徒|司空|召|有|舜|岳|黄辰|寸|贰|皇|侨|彤|竭|端|赫|实|甫|集|象|翠|狂|辟|典|良|函|芒|苦|其|京|中|夕|乌孙|完颜|富察|费莫|蹇|称|诺|来|多|繁|戊|朴|回|毓|鉏|税|荤|靖|绪|愈|硕|牢|买|但|巧|枚|撒|泰|秘|亥|绍|以|壬|森|斋|释|奕|姒|朋|求|羽|用|占|真|穰|翦|闾|漆|贵|代|贯|旁|崇|栋|告|休|褒|谏|锐|皋|闳|在|歧|禾|示|是|委|钊|频|嬴|呼|大|威|昂|律|冒|保|系|抄|定|化|莱|校|么|抗|祢|綦|悟|宏|功|庚|务|敏|捷|拱|兆|丑|丙|畅|苟|随|类|卯|俟|友|答|乙|允|甲|留|尾|佼|玄|乘|裔|延|植|环|矫|赛|昔|侍|度|旷|遇|偶|前|由|咎|塞|敛|受|泷|袭|衅|叔|圣|御|夫|仆|镇|藩|邸|府|掌|首|员|焉|戏|可|智|尔|凭|悉|进|笃|厚|仁|业|肇|资|合|仍|九|衷|哀|刑|俎|仵|圭|夷|徭|蛮|汗|孛|乾|帖|罕|洛|淦|洋|邶|郸|郯|邗|邛|剑|虢|隋|蒿|茆|菅|苌|树|桐|锁|钟|机|盘|铎|斛|玉|线|针|箕|庹|绳|磨|蒉|瓮|弭|刀|疏|牵|浑|恽|势|世|仝|同|蚁|止|戢|睢|冼|种|涂|肖|己|泣|潜|卷|脱|谬|蹉|赧|浮|顿|说|次|错|念|夙|斯|完|丹|表|聊|源|姓|吾|寻|展|出|不|户|闭|才|无|书|学|愚|本|性|雪|霜|烟|寒|少|字|桥|板|斐|独|千|诗|嘉|扬|善|揭|祈|析|赤|紫|青|柔|刚|奇|拜|佛|陀|弥|阿|素|长|僧|隐|仙|隽|宇|祭|酒|淡|塔|琦|闪|始|星|南|天|接|波|碧|速|禚|腾|潮|镜|似|澄|潭|謇|纵|渠|奈|风|春|濯|沐|茂|英|兰|檀|藤|枝|检|生|折|登|驹|骑|貊|虎|肥|鹿|雀|野|禽|飞|节|宜|鲜|粟|栗|豆|帛|官|布|衣|藏|宝|钞|银|门|盈|庆|喜|及|普|建|营|巨|望|希|道|载|声|漫|犁|力|贸|勤|革|改|兴|亓|睦|修|信|闽|北|守|坚|勇|汉|练|尉|士|旅|五|令|将|旗|军|行|奉|敬|恭|仪|母|堂|丘|义|礼|慈|孝|理|伦|卿|问|永|辉|位|让|尧|依|犹|介|承|市|所|苑|杞|剧|第|零|谌|招|续|达|忻|六|鄞|战|迟|候|宛|励|粘|萨|邝|覃|辜|初|楼|城|区|局|台|原|考|妫|纳|泉|老|清|德|卑|过|麦|曲|竹|百|福|言|第五|佟|爱|年|笪|谯|哈|墨|连|南宫|赏|伯|佴|佘|牟|商|西门|东门|左丘|梁丘|琴|后|况|亢|缑|帅|微生|羊舌|海|归|呼延|南门|东郭|百里|钦|鄢|汝|法|闫|楚|晋|谷梁|宰父|夹谷|拓跋|壤驷|乐正|漆雕|公西|巫马|端木|颛孙|子车|督|仉|司寇|亓官|三小|鲜于|锺离|盖|逯|库|郏|逢|阴|薄|厉|稽|闾丘|公良|段干|开|光|操|瑞|眭|泥|运|摩|伟|铁|迮][\u4e00-\u9fa5]{1,3}$)"
# 18位身份证正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_18_idcard = r"(([1-9]\d{5}(19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]))"  # 18位身份证
# 港澳身份证正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_hongkong_macao_idcard = r"(^([A-Z]\d{6,10}(\(w{1}\))?)$)"  # 港澳身份证
# 台湾居民来往大陆通行证正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_taiwan_idcard = r"(^\d{8}|^[a-zA-Z0-9]{10}|^\d{18}$)"  # 台湾居民来往大陆通行证
# 军官证正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_military_idcard = r"(^[\u4E00-\u9FA5](字第)([0-9a-zA-Z]{4,8})(号?)$)"  # 军官证
# 护照正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_passport = r"(^([a-zA-Z]|[0-9]){5,17}$)"  # 护照
# 手机号码正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_mobilephone = r"([1](([3][0-9])|([4][5-9])|([5][0-3,5-9])|([6][5,6])|([7][0-8])|([8][0-9])|([9][1,5,8,9]))[0-9]{8})"  # 手机号码正则校验
# 座机号区号本地号码没有使用'-'连接正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_no_telephone = r"(^0\d{2,3}\d{7,8}$)"  # 座机号  区号本地号码没有使用'-'连接
# 15位身份证正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_15_idcard = r"(([1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}))"  # 15位身份证
# 座机号区号与当地电话号，用 '-' 连接正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_have_telephone = r"(^0\d{2,3}-\d{7,8}$)"  # 座机号  区号与当地电话号，用 '-' 连接
# 出生年月日或年月日(2022-10-01)正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_birthday = r"(^(19|20)\d{2}\-((0?[1-9])|(1[0-2]))\-((0?[1-9])|([1-2]\d)|3[01])$)"  # 出生年月日或年月日(2022-10-01)
# 邮箱正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_mailbox = r"(^([a-zA-Z]|[0-9])(\w)+@[a-zA-Z0-9]+\.([a-zA-Z]{2,4})$)"  # 邮箱
# 6214卡号正则表达式, 方法isOrNotSensitive_html、isOrNotSensitive调用
init_reg_bankcard = r"(^(6214)\d{12}|^(6214)\s+\d{4}\s+\d{4}\s+\d{4}$)"  # 卡号

# 6228开头卡号,16位
init_reg_bankcard_6228 = r"((6228)\d{12}|(6228)\s+\d{4}\s+\d{4}\s+\d{4})"
# 6226开头卡号,16位
init_reg_bankcard_6226 = r"((6226)\d{12}|(6226)\s+\d{4}\s+\d{4}\s+\d{4})"
# 6217开头卡号,16位
init_reg_bankcard_6217 = r"((6217)\d{12}|(6217)\s+\d{4}\s+\d{4}\s+\d{4})"
# 9003开头卡号,16位
init_reg_bankcard_9003 = r"((9003)\d{12}|(9003)\s+\d{4}\s+\d{4}\s+\d{4})"
# 8112开头卡号,19位
init_reg_bankcard_8112 = r"((8112)\d{15}|(8112)\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{3})"
# 4115开头卡号,18位
init_reg_bankcard_4115 = r"((4115)\d{14}|(4115)\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{2})"
# 3550开头卡号,17位
init_reg_bankcard_3550 = r"((3550)\d{13}|(3550)\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{1})"

# 身份证2
init_reg_18_idcard2 = r"[^0-9]((\d{8}(0\d|10|11|12)([0-2]\d|30|31)\d{3}$)|(\d{6}(18|19|20)\d{2}(0[1-9]|10|11|12)([0-2]\d|30|31)\d{3}(\d|X|x)))[^0-9]"
# 邮箱2
init_reg_mailbox2 = r"(([a-z0-9][_|\.])*[a-z0-9]+@([a-z0-9][-|_|\.])*[a-z0-9]+\.((?!js|css|jpg|jpeg|png|ico)[a-z]{2,}))"
# 手机号2
# init_reg_mobilephone2 = r"[^\w]((?:(?:\+|00)86)?1(?:(?:3[\d])|(?:4[5-79])|(?:5[0-35-9])|(?:6[5-7])|(?:7[0-8])|(?:8[\d])|(?:9[189]))\d{8})[^\w]"
init_reg_mobilephone2 = r"((?:(?:\+|00)86)?1(?:(?:3[\d])|(?:4[5-79])|(?:5[0-35-9])|(?:6[5-7])|(?:7[0-8])|(?:8[\d])|(?:9[189]))\d{8})"


# 初始化生成配置表,方法autoSave调用
init_dataConfig = [{'system':'', 'newUrl': [], 'scenario_create_case': [], init_dataBasePath:'', init_filterUrl:[],
init_loadDataBaseType: 'loadAll', init_filter_dataBaseName_suffix: ['.db','.log','.json'],
# init_modifyReqHeader_urlHeader: {},init_modifyReqHeader_header: {},init_modifyReqHeader_urlHeaderScript: {},
# init_modifyReqHeader_headerScript: {},
init_need_modifyReqHeader:[{'modify_header':'','value':''}, {'modify_url':'','modify_header':'','value':''}],
# init_need_modifyReqBodyFieldValue:{'urlFieldValue':{},'fieldValue':{},'urlFieldValueScript':{},'fieldValueScript':{}}, init_need_modifyReqBodyText: {'urlText':{},'text':{},'urlTextScript':{},'textScript':{}},
# init_need_modifyResHeader:{'urlHeader':{},'header':{},'urlHeaderScript':{},'headerScript':{}},
# init_need_modifyResBodyFeildValue:{'urlFieldValue':{},'fieldValue':{},'urlFieldValueScript':{},'fieldValueScript':{}}, init_need_modifyResBodyText: {'urlText':{},'text':{},'urlTextScript':{},'textScript':{}},
# init_need_reqBodyContain_scriptDoSomething : {'urlContainScript':{},'containScript':{}}, init_need_reqBodyEqualField_scriptDoSomething: {'urlEqualFieldScript':{},'equalFieldScript':{}},
# init_need_reqBodyEqualFieldValue_scriptDoSomething: {'urlEqualFieldValueScript':[],'equalFieldValueScript':[]},
# init_need_resBodyContain_scriptDoSomething: {'urlContainScript':{},'containScript':{}},  init_need_resBodyEqualField_scriptDoSomething: {'urlEqualFieldScript':{},'equalFieldScript':{}},
# init_need_resBodyEqualFieldValue_scriptDoSomething: {'urlEqualFieldValueScript':[],'equalFieldValueScript':[]},
init_autosavefield_limit: '',init_black_autosavefield: [],
init_createPermissionCase_length_limit : '200' , init_createSqlCase_length_limit : '200' , init_createXssCase_length_limit : '200' ,
init_createLengthCase_length_limit : '200' , init_createDownloadUrlCase_length_limit : '200' , init_creatDownloadFieldCase_length_limit : '200' ,
init_createUploadFileCase_length_limit : '200' , init_createUploadFieldCase_length_limit : '200' ,

init_createPermissionCase_length_limit_equal : '200' , init_createSqlCase_length_limit_equal : '200' , init_createXssCase_length_limit_equal : '200' ,
init_createLengthCase_length_limit_equal : '200' , init_createDownloadUrlCase_length_limit_equal : '200' , init_creatDownloadFieldCase_length_limit_equal : '200' ,
init_createUploadFileCase_length_limit_equal : '200' , init_createUploadFieldCase_length_limit_equal : '200' ,

init_permission_payload_limit: '10', init_sql_payload_limit: '10', init_xss_payload_limit: '10', init_length_payload_limit: '10',
init_download_testUrl_payload_limit: '10', init_download_testfield_payload_limit: '10', init_upload_multifile_payload_limit: '10',
init_upload_field_payload_limit: '10',

init_permission_payload_limit_equal: '10', init_sql_payload_limit_equal: '10', init_xss_payload_limit_equal: '10',
init_length_payload_limit_equal: '10', init_download_testUrl_payload_limit_equal: '10', init_download_testfield_payload_limit_equal: '10',
init_upload_multifile_payload_limit_equal: '10', init_upload_field_payload_limit_equal: '10',

init_filter_sensitive_unsave_into_blackList: { init_filterHeader: [], init_filterUrlValue: [] , init_filterUrlField: [], init_filterUrlFieldValue:[] },
init_blackList_save_from_filter_sensitive: { init_blackHeader: [], init_blackUrlValue: [] , init_blackUrlField: [], init_blackUrlFieldValue:[] },
init_filter_sensitive_url: {}, init_filter_sensitive_urlNum_field_value : [{'@*#filterUrl': ''}],

init_conList_test: ['wsdl接口', 'jvm启动参数', '百度可能1导致key泄露的url', '百度可能2导致key泄露的url', '腾讯1可能导致key泄露的url',
'腾讯2可能导致key泄露的url', '可能导致key泄露的url', '包含apache错误信息提示', '包含tomcat错误信息提示', '包含mysql错误信息提示',
'包含ibatis错误信息提示', '包含mybati错误信息提示', '包含exception错误信息提示'],
init_regList_test: ['18位身份证号1', '手机号码1', '座机号区号本地号码未用-连接', '15位身份证号', '座机号码区号与本地号码使用-连接',
'邮箱1', '6214开头卡号', '18位身份证号2', '邮箱2', '手机号码2', '6228开头卡号16位', '6226开头卡号16位', '6217开头卡号16位',
'9003开头卡号16位', '8112开头卡号19位', '4115开头卡号18位', '3550开头卡号17位'],
init_conDict_store: {'wsdl接口': init_con_wsdl, 'jvm启动参数': init_con_jvm, '百度可能1导致key泄露的url': init_con_api_baidu1,
'百度可能2导致key泄露的url': init_con_api_baidu2, '腾讯1可能导致key泄露的url': init_con_api_tecent1,
'腾讯2可能导致key泄露的url': init_con_api_tecent2, '可能导致key泄露的url': init_con_api_map,
'包含apache错误信息提示':init_con_apache, '包含tomcat错误信息提示': init_con_tomcat, '包含mysql错误信息提示': init_con_mysql,
'包含ibatis错误信息提示':init_con_ibatis, '包含mybati错误信息提示': init_con_mybatis,
'包含exception错误信息提示': init_con_exception},

init_regDict_store: {'姓名': init_reg_name, '18位身份证号1': init_reg_18_idcard,
'港澳身份证': init_reg_hongkong_macao_idcard,'台湾居民来往大陆通行证': init_reg_taiwan_idcard,
'军官证': init_reg_military_idcard, '护照': init_reg_passport, '手机号码1': init_reg_mobilephone,
'座机号区号本地号码未用-连接': init_reg_no_telephone,
'15位身份证号': init_reg_15_idcard, '座机号码区号与本地号码使用-连接': init_reg_have_telephone,
'出生年月日或者年月日': init_reg_birthday,'邮箱1': init_reg_mailbox, '6214开头卡号': init_reg_bankcard,
'18位身份证号2': init_reg_18_idcard2, '邮箱2': init_reg_mailbox2, '手机号码2': init_reg_mobilephone2,
'6228开头卡号16位': init_reg_bankcard_6228, '6226开头卡号16位': init_reg_bankcard_6226,
'6217开头卡号16位': init_reg_bankcard_6217, '9003开头卡号16位': init_reg_bankcard_9003,
'8112开头卡号19位': init_reg_bankcard_8112, '4115开头卡号18位': init_reg_bankcard_4115,
'3550开头卡号17位': init_reg_bankcard_3550},

init_white_testUrl: [] , init_black_testUrl: [],init_assert_all: [],
init_black_sensitive_testUrl: [], init_black_sensitive_testHeader: [], init_black_sensitive_testField: [],'assert_sensitive': [],
# init_create_testcase_model_permission: 'equal',
init_white_permission_testUrl: [], init_white_permission_testHeader: [],init_white_permission_testField: [],
init_black_permission_testUrl: [], init_black_permission_testHeader: [],init_black_permission_testField: [],
init_assert_permission: [],
init_white_permission_testUrl_auto: [], init_white_permission_testHeader_auto: [],init_white_permission_testField_auto: [],
init_black_permission_testUrl_auto: [], init_black_permission_testHeader_auto: [],init_black_permission_testField_auto: [],
init_assert_permission_auto: [],
init_white_permission_testUrl_equal: [], init_white_permission_testHeader_equal: [],init_white_permission_testField_equal: [],
init_black_permission_testUrl_equal: [], init_black_permission_testHeader_equal: [],init_black_permission_testField_equal: [],
init_assert_permission_equal: [],
# init_create_testcase_model_sql: 'equal',
init_white_sql_testUrl: [], init_white_sql_testHeader: [],init_white_sql_testField: [],
init_black_sql_testUrl: [], init_black_sql_testHeader: [],init_black_sql_testField: [],
init_assert_sql: [],
init_white_sql_testUrl_auto: [], init_white_sql_testHeader_auto: [],init_white_sql_testField_auto: [],
init_black_sql_testUrl_auto: [], init_black_sql_testHeader_auto: [],init_black_sql_testField_auto: [],
init_assert_sql_auto: [],
init_white_sql_testUrl_equal: [], init_white_sql_testHeader_equal: [],init_white_sql_testField_equal: [],
init_black_sql_testUrl_equal: [], init_black_sql_testHeader_equal: [],init_black_sql_testField_equal: [],
init_assert_sql_equal: [],
# init_create_testcase_model_xss: 'equal',
init_white_xss_testUrl: [], init_white_xss_testHeader: [],init_white_xss_testField: [],
init_black_xss_testUrl: [], init_black_xss_testHeader: [],init_black_xss_testField: [],
init_assert_xss: [],
init_white_xss_testUrl_auto: [], init_white_xss_testHeader_auto: [],init_white_xss_testField_auto: [],
init_black_xss_testUrl_auto: [],init_black_xss_testHeader_auto: [],init_black_xss_testField_auto: [],
init_assert_xss_auto: [],
init_white_xss_testUrl_equal: [], init_white_xss_testHeader_equal: [],init_white_xss_testField_equal: [],
init_black_xss_testUrl_equal: [],init_black_xss_testHeader_equal: [],init_black_xss_testField_equal: [],
init_assert_xss_equal: [],
# init_create_testcase_model_length: 'equal',
init_white_length_testUrl: [], init_white_length_testHeader: [],init_white_length_testField: [],
init_black_length_testUrl: [], init_black_length_testHeader: [],init_black_length_testField: [],
init_assert_length: [],
init_white_length_testUrl_auto: [], init_white_length_testHeader_auto: [],init_white_length_testField_auto: [],
init_black_length_testUrl_auto: [], init_black_length_testHeader_auto: [],init_black_length_testField_auto: [],
init_assert_length_auto: [],
init_white_length_testUrl_equal: [], init_white_length_testHeader_equal: [],init_white_length_testField_equal: [],
init_black_length_testUrl_equal: [], init_black_length_testHeader_equal: [],init_black_length_testField_equal: [],
init_assert_length_equal: [],
# init_create_testcase_model_download_multiUrl: 'equal',
init_white_download_testUrl_multiUrl: [], init_white_download_testHeader_multiUrl: [],init_white_download_testField_multiUrl: [],
init_black_download_testUrl_multiUrl: [], init_black_download_testHeader_multiUrl: [],init_black_download_testField_multiUrl: [],
init_assert_download_multiUrl: [],
init_white_download_testUrl_multiUrl_equal: [], init_white_download_testHeader_multiUrl_equal: [],init_white_download_testField_multiUrl_equal: [],
init_black_download_testUrl_multiUrl_equal: [], init_black_download_testHeader_multiUrl_equal: [],init_black_download_testField_multiUrl_equal: [],
init_assert_download_multiUrl_equal: [],
# init_create_testcase_model_download_field: 'equal',
init_white_download_testUrl_field: [], init_white_download_testHeader_field: [],init_white_download_testField_field: [],
init_black_download_testUrl_field: [], init_black_download_testHeader_field: [],init_black_download_testField_field: [],
init_assert_download_field: [],
init_white_download_testUrl_field_auto: [], init_white_download_testHeader_field_auto: [],init_white_download_testField_field_auto: [],
init_black_download_testUrl_field_auto: [], init_black_download_testHeader_field_auto: [],init_black_download_testField_field_auto: [],
init_assert_download_field_auto: [],
init_white_download_testUrl_field_equal: [], init_white_download_testHeader_field_equal: [],init_white_download_testField_field_equal: [],
init_black_download_testUrl_field_equal: [], init_black_download_testHeader_field_equal: [],init_black_download_testField_field_equal: [],
init_assert_download_field_equal: [],
# init_create_testcase_model_upload_multiFile: 'equal',
init_white_upload_testUrl_multiFile: [], init_white_upload_testHeader_multiFile: [],init_white_upload_testField_multiFile: [],
init_black_upload_testUrl_multiFile: [], init_black_upload_testHeader_multiFile: [],init_black_upload_testField_multiFile: [],
init_assert_upload_multiFile: [],
init_white_upload_testUrl_multiFile_equal: [], init_white_upload_testHeader_multiFile_equal: [],init_white_upload_testField_multiFile_equal: [],
init_black_upload_testUrl_multiFile_equal: [], init_black_upload_testHeader_multiFile_equal: [],init_black_upload_testField_multiFile_equal: [],
init_assert_upload_multiFile_equal: [],
# init_create_testcase_model_upload_field: 'equal',
init_white_upload_testUrl_field: [], init_white_upload_testHeader_field: [],init_white_upload_testField_field: [],
init_black_upload_testUrl_field: [], init_black_upload_testHeader_field: [],init_black_upload_testField_field: [],
init_assert_upload_field: [],
init_white_upload_testUrl_field_auto: [], init_white_upload_testHeader_field_auto: [],init_white_upload_testField_field_auto: [],
init_black_upload_testUrl_field_auto: [], init_black_upload_testHeader_field_auto: [],init_black_upload_testField_field_auto: [],
init_assert_upload_field_auto: [],
init_white_upload_testUrl_field_equal: [], init_white_upload_testHeader_field_equal: [],init_white_upload_testField_field_equal: [],
init_black_upload_testUrl_field_equal: [], init_black_upload_testHeader_field_equal: [],init_black_upload_testField_field_equal: [],
init_assert_upload_field_equal: [],

#'black_sql_testUrl': [], 'black_sql_testHeader': [], 'black_sql_testField': [],'assert_sql': [],
# 'black_xss_testUrl': [], 'black_xss_testHeader': [], 'black_xss_testField': [],'assert_xss': [],
# 'black_length_testUrl': [], 'black_length_testHeader': [], 'black_length_testField': [] ,'assert_length': [],
# 'black_download_testUrl_multiUrl': [], 'black_download_testHeader_multiUrl': [], 'black_download_testField_multiUrl': [] ,'assert_download_multiUrl': [],
# 'black_download_testUrl_field': [], 'black_download_testHeader_field': [], 'black_download_testField_field': [] ,'assert_download_field': [],
# 'black_upload_testUrl_multiFile': [], 'black_upload_testHeader_multiFile': [], 'black_upload_testField_multiFile': [] ,'assert_upload_multiFile': [],
# 'black_upload_testUrl_field': [], 'black_upload_testHeader_field': [], 'black_upload_testField_field': [] ,'assert_upload_field': [],
'newCreateTestCase': [], 'newField': []
},
{},{}]
# 初始化生成testCaseYamlPath.yaml表, 方法autoSave调用
init_testCaseYamlPath = [{'system': '',
'config': {'enviroment': 'https://10.200.98.11:17442', 'duli-envi': '11111',
        'dev-envi': '4444',
        'test-envi': '3333', 'tong-envi': '11223344',
        'explain-payload-limit': '攻击负载个数限制. 参数值: limitless ,不限制共计负载. 参数值: 必须填写数字 , 发送等于数字攻击负载个数',
        'permissiontest-payload-limit': '',
        'sqltest-payload-limit': '',
        'xsstest-payload-limit': '',
        'lengthtest-payload-limit': '',
        'download_urltest-payload-limit': '',
        'download_fieldtest-payload-limit': '',
        'upload_multifiletest-payload-limit': '',
        'upload_fieldtest-payload-limit': '',
        'need_modifyHeader': ['Cookie'], 'need_modifyBody': [],'need_restart': [],
        'Cookie': 'Bearer 094c6e552a1e47b2a3b2ab1c9d5904a01692172446679',
        'Authorization': 'Bearer fed8d8d462fa4d0d8145839ddcacfb5c1692177883218'},
        'path': [
                {'caseName': None,
                'testPath': 'D:\\PythonProject\\TestInterface\\testcase\\test-xinjiagou\\test_01_api.yaml',
                'collectDataPath': 'D:\\PythonProject\\TestInterface\\testcase\\test-xinjiagou\\\\test_01_fixture.yaml'},
                {'caseName': '',
                'testPath': 'D:\\PythonProject\\TestInterface\\testcase\\test-xinjiagou\\test_2_api.yaml',
                'collectDataPath': 'D:\\PythonProject\\TestInterface\\testcase\\test-xinjiagou\\test_2_fixture.yaml'}]}]
# 将敏感信息写入excel中的第一行信息，方法autoSensitive、autoSensitive_single调用
init_excelTitile_http = ['数据库中ID', '请求地址', '请求方式', '请求头', '请求体', '响应头','响应体', '响应头敏感信息', '响应体敏感信息']
# 将敏感信息测试的统计结果, 写入excel中的第一行信息，方法autoSensitive调用
init_excelTitile_statistic = ['数据库中总接口数量', '完成测试系统接口数量', '完成测试系统接口', '异常接口数量', '异常接口id']
# 将总的统计结果, 写入excel中的第一行信息，方法totalTest调用
init_excelTitile_total_statistic =  ['测试用例共计', '本次自动化测试自动化断言通过用例共计', '本次自动化测试疑似缺陷用例共计', '本次自动化测试时间共计', '', '', '']
# testcase的绝对路径, 方法autoSensitive_single、autoSensitive_single调用
init_testcase_path = ROOT_DIR + '/testcase/'
# config的绝对路径, 方法autoSensitive、autoSensitive_single调用
init_config_path = ROOT_DIR + '/config/'
# 生成测试报告名，存入的全局变量中的名字, 方法autoSensitive调用
init_global_reportName = 'global_reportName'
# 打印日志需要写入中文提示信息, 提示完成提取id, 方法autoSensitive、autoSensitive_single调用
init_tips_id = '完成提取id: '
# 打印日志需要写入中文提示信息, 提示处理接口id异常的一部分, 方法autoSensitive、autoSensitive_single调用
init_tips_wrongid1 = '处理接口 id：'
init_tips_wrongid2 = ' 出现异常'
# 打印日志需要写入中文提示信息, 提示敏感信息, 方法autoSensitive、autoSensitive_single调用
init_tips_sensitive = '敏感信息'
# 打印日志需要写入中文提示信息, 提示敏感信息统计, 方法autoSensitive、autoSensitive_single调用
init_tips_sensitive_statistic = '敏感信息测试统计'
# 测试完成以后将统计数据写入到excel中的sheet, 名字就是这个, 方法totalTest调用
init_tips_total_statistic_summary = '测试用例统计汇总'
# 打印日志需要写入中文提示信息, 提示敏感信息, 方法autoSensitive、autoSensitive_single调用
init_tips_html_sensitive = 'html响应体敏感信息'
# 打印日志需要写入中文提示信息, 提示数据库中总接口数, 方法autoSensitive、autoSensitive_single调用
init_tips_sum_interface = '数据库中总接口数量: '
# 打印日志需要写入中文提示信息, 数据库需要过滤url来进行对应处理, 所以实际的处理接口数小于等于总接口数, 提示下这个数量,
# 方法autoSensitive、autoSensitive_single调用
init_tips_sum_related_interface = '完成测试系统接口数量: '
# 打印日志需要写入中文提示信息, 提示数据库中可以正常处理的都有哪些接口id, 方法autoSensitive、autoSensitive_single调用
init_tips_process_interface_id = '完成测试系统接口: '
# 打印日志需要写入中文提示信息, 提示过滤ip后的数据，无法处理多少接口数量, 方法autoSensitive、autoSensitive_single调用
init_tips_sum_abnormal_interface = '异常接口数量: '
# 打印日志需要写入中文提示信息, 提示过滤ip后的数据，无法处理多少接口id, 方法autoSensitive、autoSensitive_single调用
init_tips_process_abnormal_interface_id = '异常接口id： '
# dataConfig.yaml抽取数据以后会写入到yaml，如果写不进去会报这个错误, 方法autoCreate、autoCreate_single调用
init_tips_write_dataConfig_abnormal = 'dataConfigYaml配置表出现问题，未存入新值进入文件中'
# 敏感信息存入到excel中的名的后半部分, 方法autoSensitive_single、autoSensitive_single调用
init_tips_sensitive_statistic_excel = '_敏感信息_自动化测试结果统计.xlsx'
# 报文中如果出现敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法findSensitiveFromBody调用
init_tips_header_sensitive = '/**/头消息敏感信息-疑似/**/'
# 报文中如果header出现ip敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法headerSensitive调用
init_tips_header_ip_sensitive = '/**/头消息敏感信息-疑似/**/IP地址'
# 报文中如果header出现中间件敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法headerSensitive调用
init_tips_header_midware_sensitive = '/**/头消息敏感信息-疑似/**/中间件版本'
# 报文中如果出现姓名敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_name_sensitive = '/**/敏感信息-疑似/**/姓名'
# 报文中如果出现18位身份证敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_18_idcard_sensitive = '/**/敏感信息-疑似/**/18位身份证'
# 报文中如果出现港澳通行证敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_hongkong_macao_idcard_sensitive = '/**/敏感信息-疑似/**/港澳身份证'
# 报文中如果出现台湾通行证敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_hongkong_macao_idcard_sensitive = '/**/敏感信息-疑似/**/台湾居民来往大陆通行证'
# 报文中如果出现台湾通行证敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_military_idcard_sensitive = '/**/敏感信息-疑似/**/军官证'
# 报文中如果出现护照敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_passport_sensitive = '/**/敏感信息-疑似/**/护照'
# 报文中如果出现手机号敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_mobilephone_sensitive = '/**/敏感信息-疑似/**/手机号码'
# 报文中如果出现座机没有'-'敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_no_telephone_sensitive = '/**/敏感信息-疑似/**/座机号区号本地号码没有使用\'-\'连接'
# 报文中如果出现座机没有'-'敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_15_idcard_sensitive = '/**/敏感信息-疑似/**/15位身份证号'
# 报文中如果出现座机有'-'敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_have_telephone_sensitive = '/**/敏感信息-疑似/**/座机号码区号与本地号码使用\'-\'连接'
# 报文中如果出现生日敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_birthday_sensitive = '/**/敏感信息-疑似/**/出生年月日或者年月日'
# 报文中如果出现邮箱敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_mailbox_sensitive = '/**/敏感信息-疑似/**/邮箱'
# 报文中如果出现6214开头卡号敏感信息，会写入到excel中，为了标注头为敏感信息会写入到里边，方法isOrNotSensitive_html、isOrNotSensitive调用
init_tips_bankcard_sensitive = '/**/敏感信息-疑似/**/6214开头卡号'



# # 全局设置的header的白名单
# init_white_testHeader = 'white_testHeader'
# # 全局设置的字段的白名单, 生成模式为生成所有用例
# init_white_testField = 'white_testField'
# 全局设置的字段的白名单, 生成模式为自动生成
# init_white_testField_auto = 'white_testField_auto'
# # 全局设置的字段的白名单, 生成模式为字段相同测试
# init_white_testField_equal = 'white_testField_equal'


# # sql注入url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_sql_testUrl = 'black_sql_testUrl'
# # sql注入header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_sql_testHeader = 'black_sql_testHeader'
# # sql注入字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_sql_testField = 'black_sql_testField'


# xss测试url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_xss_testUrl = 'black_xss_testUrl'
# # xss测试header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_xss_testHeader = 'black_xss_testHeader'
# # xss测试字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_xss_testField = 'black_xss_testField'


# # 边界值测试url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_length_testUrl = 'black_length_testUrl'
# # 边界值测试header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_length_testHeader = 'black_length_testHeader'
# # 边界值测试字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_length_testField = 'black_length_testField'


# # 下载测试针对url的url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testUrl_multiUrl = 'black_download_testUrl_multiUrl'
# # 下载测试针对url的header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testHeader_multiUrl = 'black_download_testHeader_multiUrl'
# # 下载测试针对url的字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testField_multiUrl = 'black_download_testField_multiUrl'


# # 下载测试针对字段, 请求体中url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testUrl_field = 'black_download_testUrl_field'
# # 下载测试针对字段, 请求体中header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testHeader_field = 'black_download_testHeader_field'
# # 下载测试针对字段, 请求体中字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_download_testField_field = 'black_download_testField_field'


# # 上传测试针对不同文件修改content-type, url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_upload_testUrl_multiFile = 'black_upload_testUrl_multiFile'
# # 上传测试针对不同文件修改content-type, header黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_upload_testHeader_multiFile = 'black_upload_testHeader_multiFile'
# # 上传测试针对不同文件修改content-type, 字段黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_upload_testField_multiFile = 'black_upload_testField_multiFile'

# # 本功能要修改为针对字段, 对字段添加攻击负载. url黑名单变量名. 方法jsonHeaderFieldTest调用
# init_black_upload_testUrl_field = 'black_upload_testUrl_field'
# # 本功能要修改为针对字段,  对字段添加攻击负载. 请求头黑名单变量名.  方法jsonHeaderFieldTest调用
# init_black_upload_testHeader_field = 'black_upload_testHeader_field'
# # 本功能要修改为针对字段, 对字段添加攻击负载. 请求字段黑名单变量名.. 方法jsonHeaderFieldTest调用
# init_black_upload_testField_field = 'black_upload_testField_field'
#########################################




# 敏感信息测试响应头，判断头中存在哪些中间件, 变量存储中间件名, 方法headerSensitive调用
init_middleWare = ['tomcat', 'nginx', 'weblogic', 'jboss', 'jetty', 'webshere', 'glassfish']
# 头消息中的content-type中的不同类型，表示下载接口标识. 方法creteTestCase_downLoadMutiUrl、createTestCase_downLoadField、creatTestCaseYaml_upLoadFile调用
init_content_type_download_header = ['image/gif', 'image/jpeg', 'image/png', 'application/pdf','application/msword', 'application/vnd.ms-excel','application/zip','application/octet-stream']
# 头消息中的content-type中的不同类型，表示上传接口标识. 方法creteTestCaseFrom_multiPartFormData调用
init_content_type_upload_header = ['image/gif','image/jpeg','image/png','application/pdf','application/msword','application/vnd.ms-excel','application/zip','application/octet-stream','multipart/form-data']

# 生成yaml的接口文件模板, 方法createDictData调用
init_yamlData = [{'api_name': {'name': '112211'},'api_request': {'url': {'url': ''},'method': {'requestMethod': ''},'headers': {},'params': {}},'api_validate': [],'api_config': {'preRequest': [], 'afterResponse': [], 'formatData': []}}]
# 生成python脚本模板, autoCreateTestcase中的变量pyTemplate_upLoadMutiFile调用
init_pyTemplate_upLoadMutiFile = '''# -*- coding:utf-8 -*-
import allure
import pytest
from util.yaml_util import read_yaml_update
from parsehttp.requestMethod import requestCase
from util import globalValue
from parsehttp.paramsMethod import fixture_requestCollectTestData

@pytest.fixture(scope="function", params=fixture_requestCollectTestData('$system','collect_date', '$testName', '$story'))
def $fixtureName(request):  # my_fixture(request) request为固定写法
    yield request.param

class TestApi:

    @allure.story('$story')
    @allure.severity(allure.severity_level.CRITICAL)
    # @allure.step('修改通过GET请求提交的非当前用户账号')
    @pytest.mark.parametrize('args', read_yaml_update('$system','test', '$testName', '$story'))
    def $function(self, args, $fixtureName):
        requestCase(args, $fixtureName,'$system')
    '''
# 生成python脚本模板, autoCreateTestcase中的变量pyTemplate调用
init_pyTemplate = '''# -*- coding:utf-8 -*-
import allure
import pytest
from util.yaml_util import read_yaml_update
from parsehttp.requestMethod import requestCase
from util import globalValue
from parsehttp.paramsMethod import fixture_requestCollectTestData

@pytest.fixture(scope="function", params=fixture_requestCollectTestData('$system','collect_date', '$testName', '$story'))
def $fixtureName(request):  # my_fixture(request) request为固定写法
    yield request.param

class TestApi:

    @allure.story('$story')
    @allure.severity(allure.severity_level.CRITICAL)
    # @allure.step('修改通过GET请求提交的非当前用户账号')
    @pytest.mark.parametrize('args', read_yaml_update('$system','test', '$testName', '$story'))
    def $function(self, args, $fixtureName):
        requestCase(args, $fixtureName,'$system')
    '''
# 生成python脚本模板, autoCreateTestcase中的变量pyTemplate调用, 针对权限测试, 保持数据库中报文不变, 只是替换权限, 再发送请求
init_pyTemplate_orignalBody_permission = '''# -*- coding:utf-8 -*-
import allure
import pytest
from util.yaml_util import read_yaml_update
from parsehttp.requestMethod import requestCase
from util import globalValue
from parsehttp.paramsMethod import fixture_requestCollectTestData

@pytest.fixture(scope="function", params=['1'])
def $fixtureName(request):  # my_fixture(request) request为固定写法
    yield request.param

class TestApi:

    @allure.story('$story')
    @allure.severity(allure.severity_level.CRITICAL)
    # @allure.step('修改通过GET请求提交的非当前用户账号')
    @pytest.mark.parametrize('args', read_yaml_update('$system','test', '$testName', '$story'))
    def $function(self, args, $fixtureName):
        requestCase(args, $fixtureName,'$system')
    '''
# 生成python脚本模板, autoCreateTestcase中的变量pyTemplate_downLoadUrl调用
init_pyTemplate_downLoadUrl = '''# -*- coding:utf-8 -*-
import allure
import pytest
from util.yaml_util import read_yaml_update
from parsehttp.requestMethod import requestCase
from util import globalValue
from fuction_script.formatDataAll import justFormat

@pytest.fixture(scope="function", params=justFormat('downLoadUrl', '$system', '$testName', '$story'))
def $fixtureName(request):  # my_fixture(request) request为固定写法
    yield request.param

class TestApi:

    @allure.story('$story')
    @allure.severity(allure.severity_level.CRITICAL)
    # @allure.step('修改通过GET请求提交的非当前用户账号')
    @pytest.mark.parametrize('args', read_yaml_update('$system','test', '$testName', '$story'))
    def $function(self, args, $fixtureName):
        requestCase(args, $fixtureName,'$system')
    '''
# 生成python脚本模板, autoCreateTestcase中的变量pyTemplate_downLoadField调用
init_pyTemplate_downLoadField = '''# -*- coding:utf-8 -*-
import allure
import pytest
from util.yaml_util import read_yaml_update
from parsehttp.requestMethod import requestCase
from util import globalValue
from fuction_script.formatDataAll import justFormat

@pytest.fixture(scope="function", params=justFormat('downLoadField', '$system', '$testName', '$story'))
def $fixtureName(request):  # my_fixture(request) request为固定写法
    yield request.param

class TestApi:

    @allure.story('$story')
    @allure.severity(allure.severity_level.CRITICAL)
    # @allure.step('修改通过GET请求提交的非当前用户账号')
    @pytest.mark.parametrize('args', read_yaml_update('$system','test', '$testName', '$story'))
    def $function(self, args, $fixtureName):
        requestCase(args, $fixtureName,'$system')
    '''
# 生成python脚本模板, autoCreateTestcase中的变量pyTemplate_sqlDiffParams_url调用
init_pyTemplate_sqlDiffParams_url = '''# -*- coding:utf-8 -*-
import allure
import pytest
from util.yaml_util import read_yaml_update
from parsehttp.requestMethod import requestCase
from util import globalValue
from fuction_script.formatDataAll import justFormat

@pytest.fixture(scope="function", params=justFormat('sqlDiffParams_url', '$system', '$testName', '$story'))
def $fixtureName(request):  # my_fixture(request) request为固定写法
    yield request.param

class TestApi:

    @allure.story('$story')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize('args', read_yaml_update('$system','test', '$testName', '$story'))
    def $function(self, args, $fixtureName):
        requestCase(args, $fixtureName,'$system')
    '''
# 生成python脚本模板, autoCreateTestcase中的变量pyTemplate_sqlDiffParams_body调用
init_pyTemplate_sqlDiffParams_body = '''# -*- coding:utf-8 -*-
import allure
import pytest
from util.yaml_util import read_yaml_update
from parsehttp.requestMethod import requestCase
from util import globalValue
from fuction_script.formatDataAll import justFormat

@pytest.fixture(scope="function", params=justFormat('sqlDiffParams_body', '$system', '$testName', '$story'))
def $fixtureName(request):  # my_fixture(request) request为固定写法
    yield request.param

class TestApi:

    @allure.story('$story')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize('args', read_yaml_update('$system','test', '$testName', '$story'))
    def $function(self, args, $fixtureName):
        requestCase(args, $fixtureName,'$system')
    '''
# 生成python脚本模板, autoCreateTestcase中的变量pyTemplate_sqlDiffParams_body调用
init_pyTemplate_sqlDiffParams_body_multipart_form_data = '''# -*- coding:utf-8 -*-
import allure
import pytest
from util.yaml_util import read_yaml_update
from parsehttp.requestMethod import requestCase
from util import globalValue
from fuction_script.formatDataAll import justFormat

@pytest.fixture(scope="function", params=justFormat('sqlDiffParams_body_multipart_form_data', '$system', '$testName', '$story'))
def $fixtureName(request):  # my_fixture(request) request为固定写法
    yield request.param

class TestApi:

    @allure.story('$story')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize('args', read_yaml_update('$system','test', '$testName', '$story'))
    def $function(self, args, $fixtureName):
        requestCase(args, $fixtureName,'$system')
    '''
















