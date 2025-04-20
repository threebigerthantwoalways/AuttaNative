# -*- coding:utf-8 -*-
import os,time,PIL
from PIL import Image, ImageDraw, ImageFont
import sqlite3,shutil,math,sys
from ruamel import yaml


def createDirectory(createAllDir):
    # 遍历目录, 生成对应目录
    for item_dir in createAllDir:
        if not os.path.isdir(item_dir):
            os.makedirs(item_dir)
    print('Test system,create directory finish!!!')

# 数据库查询所有
def loadDataBase_ALL(dataBasePath):
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
        # 查询表明
        cursor.execute(sql_search)
        data = cursor.fetchall()
        cursor.close()
        db.close()
        return  data


# 按照条件查询数据库
def loadDataBase_Many(dataBasePath, num, beginEndId, dataTime):
    splitName = os.path.splitext(dataBasePath)
    splitName_len = len(splitName) - 1
    if splitName[splitName_len] == '.db':
        # 读取sqlite数据
        db = sqlite3.connect(dataBasePath)
        db.text_factory = lambda  x: str(x,'gbk','ignore')
        # db.text_factory = str
        # 创建游标curson来执行execute SQL语句
        cursor = db.cursor()
        if num != '':
            sql_search = 'select * from activity where id={}'.format(num)
        elif beginEndId !='' and beginEndId != []:
            sql_search = 'select * from activity where id between {} and {}'.format(beginEndId[0], beginEndId[1])
        elif dataTime !='' or dataTime != []:
            sql_search = 'select * from activity where SEND_DATETIME >={}  and SEND_DATETIME <={} '.format(dataTime[0],
                                                                                                    dataTime[1])
        # 查询表明  SEND_DATETIME
        cursor.execute(sql_search)
        data = cursor.fetchall()
        cursor.close()
        db.close()
        return  data


# 根据输入的字段, 和存储在对应字段下的值是否包含value, 来进行查询数据库
# dataBasePath: 数据库地址       field: sqlite的表activity中的字段      value: 包含的值, 包含的值会查询出来
def loadDataBase_fieldValue_ALL(dataBasePath, field, value):
    splitName = os.path.splitext(dataBasePath)
    splitName_len = len(splitName) - 1
    if splitName[splitName_len] == '.db':
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
        return  data


# 给定图片地址, 标签地址, 画出点击位置
# imagePath: 需要画图的图片地址    labelPath: 和需要画图的图片地址对应的标签地址    drawImagePath: 画出的新图生成地址
def drawText_onPicture(imagePath, labelPath, drawImagePath):
    directory = [imagePath, labelPath, drawImagePath]
    createDirectory(directory)
    for itemFileName in os.listdir(imagePath):
        itemFileName = itemFileName.replace('.png', '')
        XYPosition = ''
        with open(labelPath + '/' + itemFileName + '.txt', 'r') as f:
            XYPosition = f.read()
        XYPosition = XYPosition.split(' ')
        if XYPosition != '' :
            # 设置字体
            font = ImageFont.truetype('simsun.ttc', size=25)

            img = Image.open(imagePath + '/' + itemFileName + '.png')
            draw = ImageDraw.Draw(img)
            # font.set_variation_by_name('bold')
            if XYPosition[0] == 'Key.enter' :
                # 添加文本
                draw.text((100, 100), 'Enter', font=font, fill='red')
                img.save(drawImagePath + '/' + itemFileName + '.png')
            else:
                # # 添加文本
                # draw.text((int(XYPosition[0]), int(XYPosition[1])), 'W', font=font, fill='red')
                # img.save(drawImagePath + '/' + itemFileName + '.png' )
                # draw_arrow_on_image(image_path, output_path, target_coord
                draw_arrow_on_image(imagePath + '/' + itemFileName + '.png',
                                    drawImagePath + '/' + itemFileName + '.png',
                                    (int(XYPosition[0]), int(XYPosition[1])))
        print('picture、label: ' + itemFileName + '  finish！！！')



# 通过burp写入数据库中的时间(毫秒), 来获得image文件夹下所对应的图片, 返回一个List
# logTime: burp插件写入到数据库中的时间(毫秒), 是一个List, 例: ['2024-07-06 21:21:02.198451']
# imagePath: 存放通过脚本生成的png截图
# interval: 间隔, 填写数字代表秒, 给定的时间戳在这个间隔范围内都是会被查询出来, 差0.5秒也是可以的。 这个值也可以为0, 也就是完全相同
def getSameTimeImage(logTime, imagePath, interval):
    result = []
    if int(interval) ==  0 :
        # 初始化元素位置为 0
        iterator_num = 0
        # 遍历文件名list中的所有元素
        while True:
            # iteratorDP_num会在后边自加1, 当长度和iteratorDP_num相同, 代表遍历结束
            if len(logTime) == iterator_num:
                break
            # 获得文件的绝对路径, 调用主方法
            one_logTime = logTime[iterator_num]
            for itemFileName in os.listdir(imagePath):
                itemFileName = itemFileName.replace('.png', '')
                itemFileName = itemFileName.replace('+', ':')
                if itemFileName == one_logTime :
                    result.append(itemFileName.replace(':', '+') + '.png')
            # 代表元素值得变量, 自加一
            iterator_num += 1
    else:
        from datetime import datetime
        # 初始化元素位置为 0
        iterator_num = 0
        # 遍历文件名list中的所有元素
        while True:
            # iteratorDP_num会在后边自加1, 当长度和iteratorDP_num相同, 代表遍历结束
            if len(logTime) == iterator_num:
                break
            # 获得文件的绝对路径, 调用主方法
            one_logTime = logTime[iterator_num]
            one_logTime_datetime = datetime.strptime(one_logTime, '%Y-%m-%d %H:%M:%S.%f')
            for itemFileName in os.listdir(imagePath):
                # itemFileName_ = itemFileName.replace(itemFileName.replace('.png', ''), ':')
                itemFileName = itemFileName.replace('.png', '')
                itemFileName = itemFileName.replace('+', ':')
                itemFileName_datetime = datetime.strptime(itemFileName, '%Y-%m-%d %H:%M:%S.%f')
                second_1 = one_logTime_datetime - itemFileName_datetime
                second_2 = itemFileName_datetime - one_logTime_datetime
                if second_1.seconds <= interval or second_2.seconds <= interval:
                    result.append(itemFileName.replace(':', '+')+'.png')
            # 代表元素值得变量, 自加一
            iterator_num += 1
    return result


# 通过图片截图上的名字(去掉.png或者包含也可以), 查询数据库中相同, 或者在一个时间间隔上的数据库的数据
# logTime: 图片中的名字, 例: [ '2024-07-06 21+21+02.198451.png', '2024-07-06 21+21+18.067656.png' ]
# 或者 [ '2024-07-06 21+21+02.198451', '2024-07-06 21+21+18.067656' ]
# 或者 [ '2024-07-06 21:21:02.198451.png', '2024-07-06 21:21:18.067656.png' ]
# 或者 [ '2024-07-06 21:21:02.198451', '2024-07-06 21:21:18.067656' ], 以上是单个时间查询
# 以下是区间查询, 也可以混合的写到一块, 元素1开始时间, 元素2结束时间, 开始时间必须早于结束时间
# [[ '2024-07-06 21+31+09.572667.png', '2024-07-06 21+34+05.718834.png' ]]
# 或者 [[ '2024-07-06 21+31+09.572667', '2024-07-06 21+34+05.718834' ]]
# 或者 [[ '2024-07-06 21:31:09.572667.png', '2024-07-06 21:34:05.718834.png' ]]
# 或者 [[ '2024-07-06 21:31:09.572667', '2024-07-06 21:34:05.718834' ]]
# dataBasePath: 数据库地址, 可以是一个路径, 会找到里边所有的数据库, 来寻找
# interval: 时间间隔, 1000是一秒, 可以是0, 就是需要完全相同时间。如果是非0, 查询单独时间, 会增加减少interval, 获得这个区间里的接口
# 如果是非0, 查询区间, 会将开始时间减少interval, 结束时间增加interval
def getSameTimeSqliteLog(logTime, dataBasePath, interval):
    result = {}
    saveAllFilePath = []
    traverse_folder(dataBasePath, saveAllFilePath, ['.db'])
    # 如果不为空, 说明list中存有正确的路径
    if len(saveAllFilePath) != 0:
        # 调用获取所有文件方法, 返回的是一个List, 设置一个代表list元素位置的全局变量数字为0
        iterator_num = 0
        # 遍历文件名list中的所有元素
        while True:
            # iterator_num会在后边自加1, 当长度和iterator_num相同, 代表遍历结束
            if len(saveAllFilePath) == iterator_num:
                break
            # 获得文件的绝对路径, 调用主方法
            one_dataBasePath = saveAllFilePath[iterator_num]
            getTimeFromDataBase(logTime, one_dataBasePath, result, interval)
            # 代表元素值得变量, 自加一
            iterator_num += 1
    else:
        print('database path wrong,please check out!!!!')
    for key in list(result.keys()) :
        # print('time interval: ',interval,'毫秒, 输入查询时间: ' + key)
        for item in result.get(key) :
            print(item[12],item[2])
    return result


# 通过时间集合list, 获得数据库中对应的报文数据, 并写入到allLogData(dict)集合中
# timeList: 时间list集合, 有单独时间, 也有区间时间                 allLogData: 一个dict集合, 存储查询出的对应报文日志
# interval: 时间间隔
def getTimeFromDataBase(timeList, dataBasePath,  allLogData, interval):
    # 初始化元素位置为 0
    iterator_num = 0
    # 遍历文件名list中的所有元素
    while True:
        # iteratorDP_num会在后边自加1, 当长度和iteratorDP_num相同, 代表遍历结束
        if len(timeList) == iterator_num:
            break
        # 获得文件的绝对路径, 调用主方法
        one_timeList = timeList[iterator_num]
        if isinstance(one_timeList, str):
            if interval == 0 :
                data = loadDataBase_fieldValue_ALL(dataBasePath, 'send_datetime', one_timeList.replace('.png', '').replace('+', ':'))
                allLogData[dataBasePath+'_'+one_timeList] = data
            else:
                from datetime import datetime
                # 去掉.png, 替换+为:, 将替换后的时间字符串, 转化为时间数组
                timeArray = datetime.strptime(one_timeList.replace('.png', '').replace('+', ':'), '%Y-%m-%d %H:%M:%S.%f')
                # 转化为时间戳
                ret_stamp = time.mktime(timeArray.timetuple()) * 1000.0 + timeArray.microsecond / 1000.0
                beginTime = (ret_stamp - interval) / 1000
                endTime = (ret_stamp + interval) / 1000
                import datetime
                # 转为str
                beginTime_str = '\'' + datetime.datetime.fromtimestamp(beginTime).strftime('%Y-%m-%d %H:%M:%S.%f') + '\''
                # 转为str
                endTime_str = '\'' + datetime.datetime.fromtimestamp(endTime).strftime('%Y-%m-%d %H:%M:%S.%f') + '\''
                allLogData[dataBasePath+'_'+one_timeList] = loadDataBase_Many(dataBasePath, '', '', [beginTime_str, endTime_str])
        else:
            if interval == 0 :
                # 拼接开始结束时间
                beginTime_str = '\'' + str(one_timeList[0].replace('.png', '').replace('+', ':')) + '\''
                endTime_str = '\'' + str(one_timeList[1].replace('.png', '').replace('+', ':')) + '\''
                allLogData[dataBasePath + '_' + str(one_timeList[0])+ '<->'+ str(one_timeList[1])] = \
                    loadDataBase_Many(dataBasePath, '', '', [beginTime_str, endTime_str])
            else:
                from datetime import datetime
                # 去掉.png, 替换+为:, 将替换后的时间字符串, 转化为时间数组
                timeArray_0 = datetime.strptime(one_timeList[0].replace('.png', '').replace('+', ':'),
                                                '%Y-%m-%d %H:%M:%S.%f')
                # 去掉.png, 替换+为:, 将替换后的时间字符串, 转化为时间数组
                timeArray_1 = datetime.strptime(one_timeList[1].replace('.png', '').replace('+', ':'),
                                                '%Y-%m-%d %H:%M:%S.%f')
                # 转化为时间戳
                ret_stamp_0 = time.mktime(timeArray_0.timetuple()) * 1000.0 + timeArray_0.microsecond / 1000.0
                # 转化为时间戳
                ret_stamp_1 = time.mktime(timeArray_1.timetuple()) * 1000.0 + timeArray_1.microsecond / 1000.0
                beginTime = (ret_stamp_0 - interval) / 1000
                endTime = (ret_stamp_1 + interval) / 1000
                import datetime
                # 转为str
                beginTime_str = '\'' + datetime.datetime.fromtimestamp(beginTime).strftime('%Y-%m-%d %H:%M:%S.%f') + '\''
                # 转为str
                endTime_str = '\'' + datetime.datetime.fromtimestamp(endTime).strftime('%Y-%m-%d %H:%M:%S.%f') + '\''
                # 调用方法loadDataBase_Many查询时间范围中的数据, 将数据库以及擦汗寻时间范围作为key, 写入到dict中
                allLogData[dataBasePath + '_' + str(one_timeList[0])+ '<->'+ str(one_timeList[1])] = \
                    loadDataBase_Many(dataBasePath, '', '', [beginTime_str, endTime_str])
        # 代表元素值得变量, 自加一
        iterator_num += 1



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



# 通过给定的url, 根据数据库的查询方式, 给出数据库中相对应的报文信息, 还会显示对应的时间戳
# url: 查询的请求地址          dataBasePath: 数据库地址       picturePath: 自动化脚本截图存放地址
def getPictureSameFromUrl(url, dataBasePath, picturePath):
    # 存储所有文件下下的.db文件
    allDataPath = []
    traverse_folder(dataBasePath, allDataPath, ['.db'])
    # 获得图片文件下下所有图片名
    allPictureName = os.listdir(picturePath)
    # 遍历路径下所有数据库
    for item_path in allDataPath:
        # 通过url, 查询当前数据库下字段target_url, 是否包含相同url
        allSearchData = loadDataBase_fieldValue_ALL(item_path, 'target_url', url)
        # 如果有, 遍历查询结果
        for item_log in allSearchData:
            # 将每条时间戳, 改成文件夹下的时间戳格式
            changeTimeStampToFileName = item_log[12].replace(':', '+') + '.png'
            # 判断当前时间戳, 是否包含在图片文件夹下
            if changeTimeStampToFileName in allPictureName:
                print('database path: ' + item_path, '  database id: ' + str(item_log[0]), '  picture same timestamp: ' + changeTimeStampToFileName)


# 查询数据库中的时间戳, 与截图相匹配, 如果与给定文件夹下的图片名相同, 那么将这张图片复制到新文件夹下
# dataBasePath: 数据库地址          searchType: 查询数据库方式, True为全量查询, False为条件查询, 条件如下
# num: 数据库id查询, 参数int格式        beginEndId: 数据库id区间查询, 参数list格式
# beginEndId: 数据库时间区间查询, 参数list格式, 例: ['\'2024-07-06 21:20:52.563086\'', '\'2024-07-06 21:22:25.289479\'']
# picturePath: 截图路径      copyPicturePath: 复制新图片路径
def copySameTimeStampPictureFromDataBase(dataBasePath, searchType, num, beginEndId, dataTime, picturePath, copyPicturePath):
    allTimeStampYaml = {}
    if searchType :
        allData = loadDataBase_ALL(dataBasePath)
        allPictureName = os.listdir(picturePath)
        for item_log in allData :
            # 将每条时间戳, 改成文件夹下的时间戳格式
            changeTimeStampToFileName = item_log[12].replace(':', '+') + '.png'
            if changeTimeStampToFileName in allPictureName :
                shutil.copy(picturePath + '/' +changeTimeStampToFileName,
                            copyPicturePath + '/' +changeTimeStampToFileName)
                allTimeStampYaml[changeTimeStampToFileName] = ''
    else:
        allData = loadDataBase_Many(dataBasePath, num, beginEndId, dataTime)
        allPictureName = os.listdir(picturePath)
        for item_log in allData :
            # 将每条时间戳, 改成文件夹下的时间戳格式
            changeTimeStampToFileName = item_log[12].replace(':', '+') + '.png'
            if changeTimeStampToFileName in allPictureName :
                shutil.copy(picturePath + '/' +changeTimeStampToFileName,
                            copyPicturePath + '/' +changeTimeStampToFileName)
                allTimeStampYaml[changeTimeStampToFileName] = ''
    # 备份dataConfig.yaml
    with open(copyPicturePath + '/timeStamp.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml.dump(allTimeStampYaml, Dumper=yaml.RoundTripDumper, allow_unicode=True))


def adjust_start_point_and_direction(image_size, target_coord, start_offset):
    """
    调整箭头的起点和方向，使其不会超出图片边界，并根据边界改变箭头方向。

    :param image_size: 图片的尺寸 (宽度, 高度)
    :param target_coord: 箭头指向的目标坐标 (x, y)
    :param start_offset: 箭头起点相对于目标点的偏移量
    :return: 调整后的起点坐标 (x, y) 和新的偏移量方向
    """
    img_width, img_height = image_size
    end_x, end_y = target_coord
    start_x = end_x - start_offset[0]
    start_y = end_y - start_offset[1]

    # 如果箭头起点接触图片顶部，则从下向上画箭头
    if start_y < 0:
        start_y = img_height  # 从底部向上画
        start_offset = (start_offset[0], -start_offset[1])  # 改变箭头方向

    # 如果箭头起点接触图片底部，则从上向下画箭头
    elif start_y > img_height:
        start_y = 0  # 从顶部向下画
        start_offset = (start_offset[0], -start_offset[1])

    # 如果箭头起点接触图片左侧，则从右侧向左画箭头
    if start_x < 0:
        start_x = img_width  # 从右侧向左画
        start_offset = (-start_offset[0], start_offset[1])  # 改变箭头方向

    # 如果箭头起点接触图片右侧，则从左向右画箭头
    elif start_x > img_width:
        start_x = 0  # 从左侧向右画
        start_offset = (-start_offset[0], start_offset[1])

    return (start_x, start_y), start_offset



def draw_arrow_on_image(image_path, output_path, target_coord, start_offset=(100, 100), arrow_length=30, arrow_angle=30,
                        color=(255, 0, 0), width=8):
    """
    在已有图片上绘制指向指定坐标的箭头，箭头自动调整起点方向避免超出边界并根据需要改变方向。

    :param image_path: 原始图片路径
    :param target_coord: 箭头指向的目标坐标 (x, y)
    :param start_offset: 箭头的起点相对于目标点的偏移量
    :param arrow_length: 箭头两侧的长度
    :param arrow_angle: 箭头两侧与主线的夹角，单位为度
    :param color: 箭头的颜色
    :param width: 箭头主线的宽度
    :param output_path: 输出文件夹
    """
    # 打开原始图片
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # 获取图片尺寸
    image_size = image.size

    # 调整箭头的起点和方向，避免超出图片边界，并选择合适的方向
    start, adjusted_offset = adjust_start_point_and_direction(image_size, target_coord, start_offset)

    # 确定箭头的终点
    end = target_coord  # 箭头指向的坐标

    # 绘制主线
    draw.line([start, end], fill=color, width=width)

    # 计算箭头头部两条边
    angle = math.atan2(end[1] - start[1], end[0] - start[0])  # 箭头主线的角度
    angle1 = angle + math.radians(arrow_angle)  # 箭头左边的角度
    angle2 = angle - math.radians(arrow_angle)  # 箭头右边的角度

    # 计算箭头两侧的顶点
    arrow_point1 = (end[0] - arrow_length * math.cos(angle1), end[1] - arrow_length * math.sin(angle1))
    arrow_point2 = (end[0] - arrow_length * math.cos(angle2), end[1] - arrow_length * math.sin(angle2))

    # 绘制箭头的两条边
    draw.line([end, arrow_point1], fill=color, width=width)
    draw.line([end, arrow_point2], fill=color, width=width)

    # 显示和保存结果图片
    # image.show()  # 显示图片
    image.save(output_path)  # 保存带箭头的图片



if __name__ == '__main__':


    params = sys.argv[1:]  # 获取命令行参数
    # 第一个参数: 原始图片据对路径   第二个参数: 原图片标签路径    第三个参数: 绘制图片生成路径
    drawText_onPicture(params[0], params[1], params[2])
    # drawText_onPicture(r'C:\数据库\截图\image', r'C:\数据库\截图\label', r'C:\数据库\截图\draw')
    print('draw picture finish！！！')









