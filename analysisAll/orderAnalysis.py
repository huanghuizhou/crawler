import json
import pymssql

import pymysql
import logging

# DB_HOST = '192.168.2.203'
# DB_USER = 'greatTao'
# DB_PASSWD = 'greatTao.1314'
# DB_PORT = 3306

DB_HOST = '192.168.2.203'
DB_USER = 'greattao'
DB_PASSWD = 'greatTao.5877'
DB_PORT = 3308

# MS_DB_HOST = 'DEVDB.great-tao.com\\GTTOWN_DEV'
MS_DB_USER = 'sa'
MS_DB_PASSWD = 'P@ssw0rd'
MS_DB_DATABASE = 'GtTown'
MS_DB_HOST = 'DEVDB.great-tao.com\\GTTOWN_STAGE'
gttown_crowdsourcing_db = pymysql.connect(host=DB_HOST,  # 192.168.100.254
                                          user=DB_USER,
                                          passwd=DB_PASSWD,
                                          db="gttown_crowdsourcing",
                                          port=DB_PORT,  # 3306
                                          use_unicode=True,
                                          charset="utf8")
enterprise_db = pymssql.connect(host=MS_DB_HOST,
                                user=MS_DB_USER,
                                password=MS_DB_PASSWD,
                                database=MS_DB_DATABASE,
                                charset="utf8")

def get_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    # Standard output handler
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(logging.Formatter('%(levelname)s - %(name)s:%(lineno)s: %(message)s'))
    log.addHandler(sh)
    return log


logger = get_logger(__file__)


# 供应商省分布
areaKey = {'110000': '北京市',
           '120000': '天津市',
           '130000': '河北省',
           '140000': '山西省',
           '150000': '内蒙古自治区',
           '210000': '辽宁省',
           '220000': '吉林省',
           '230000': '黑龙江省',
           '310000': '上海市',
           '320000': '江苏省',
           '330000': '浙江省',
           '340000': '安徽省',
           '350000': '福建省',
           '360000': '江西省',
           '370000': '山东省',
           '410000': '河南省',
           '420000': '湖北省',
           '430000': '湖南省',
           '440000': '广东省',
           '450000': '广西壮族自治区',
           '460000': '海南省',
           '500000': '重庆市',
           '510000': '四川省',
           '520000': '贵州省',
           '530000': '云南省',
           '540000': '西藏自治区',
           '610000': '陕西省',
           '620000': '甘肃省',
           '630000': '青海省',
           '640000': '宁夏回族自治区',
           '650000': '新疆维吾尔自治区',
           '710000': '台湾省',
           '820000': '澳门特别行政区',
           '810000': '香港特别行政区',
           '110000': '北京市',
           '120000': '天津市',
           '130000': '河北省',
           '140000': '山西省',
           '150000': '内蒙古自治区',
           '210000': '辽宁省',
           '220000': '吉林省',
           '230000': '黑龙江省',
           '310000': '上海市',
           '320000': '江苏省',
           '330000': '浙江省',
           '340000': '安徽省',
           '350000': '福建省',
           '360000': '江西省',
           '370000': '山东省',
           '410000': '河南省',
           '420000': '湖北省',
           '430000': '湖南省',
           '440000': '广东省',
           '450000': '广西壮族自治区',
           '460000': '海南省',
           '500000': '重庆市',
           '510000': '四川省',
           '520000': '贵州省',
           '530000': '云南省',
           '540000': '西藏自治区',
           '610000': '陕西省',
           '620000': '甘肃省',
           '630000': '青海省',
           '640000': '宁夏回族自治区',
           '650000': '新疆维吾尔自治区',
           '710000': '台湾省',
           '820000': '澳门特别行政区',
           '810000': '香港特别行政区'}



def tradeInfo_1(year, type):
    buyerInfo = {}
    buyerInfoNum = {}
    supplierInfo = {}
    supplierInfoNum = {}

    cursor = gttown_crowdsourcing_db.cursor()
    sql = "select orderId,finalDestinarion,clientId,declarationAmount  from `" + (
                type + 'order') + "` where createDate>'" + str(
        year) + "' and createDate<'" + str(year + 1) + "'"
    cursor.execute(sql)
    results = cursor.fetchall()
    for orderInfo in results:
        orderId = orderInfo[0]
        # 目的地
        finalDestinarion = orderInfo[1]
        if finalDestinarion is None:
            finalDestinarion = '未知'
            logger.debug("orderId：%s 未找到对应目的地信息" % orderId)
        clientId = orderInfo[2]
        # 金额
        declarationAmount = orderInfo[3]
        if declarationAmount is None:
            declarationAmount = 0
            logger.debug("orderId：%s 报关金额为空" % orderId)
        # 供应商信息
        supplierSql = "select District  from EnterpriseProfileLocale where LocaleId='zh-CN' and  EnterpriseId='" + str(
            clientId) + "'"
        csr = enterprise_db.cursor()
        csr.execute(supplierSql)
        supplierResults = csr.fetchone()
        if supplierResults is not None:
            # 省
            district = supplierResults[0]
            if district is None:
                supplierSql1 = "select District  from EnterpriseProfileLocale where LocaleId='en' and  EnterpriseId='" + str(
                    clientId) + "'"
                csr.execute(supplierSql1)
                district = csr.fetchone()[0]

            if district is None:
                district = "未知"
            else:
                if (len(str(district)) >= 2):
                    district = str(district)[0: 2] + "0000"

            if district in supplierInfo:
                supplierInfo[district] = supplierInfo[district] + declarationAmount
            else:
                supplierInfo[district] = declarationAmount

            if district in supplierInfoNum:
                supplierInfoNum[district] = supplierInfoNum[district] + 1
            else:
                supplierInfoNum[district] = 1
        else:
            logger.debug("orderId：%s ,clientId: %s 未找到对应供应商信息" % (orderId, clientId))

        # 目的地信息
        if finalDestinarion in buyerInfo:
            buyerInfo[finalDestinarion] = buyerInfo[finalDestinarion] + declarationAmount
        else:
            buyerInfo[finalDestinarion] = declarationAmount

        if finalDestinarion in buyerInfoNum:
            buyerInfoNum[finalDestinarion] = buyerInfoNum[finalDestinarion] + 1
        else:
            buyerInfoNum[finalDestinarion] = 1
    resultsDict = {}
    resultsDict['buyerInfo'] = buyerInfo
    resultsDict['buyerInfoNum'] = buyerInfoNum
    resultsDict['supplierInfo'] = supplierInfo
    resultsDict['supplierInfoNum'] = supplierInfoNum
    return resultsDict


def tradeInfo_2(year, type):
    buyerInfo = {}
    buyerInfoNum = {}
    supplierInfo = {}
    supplierInfoNum = {}

    cursor = gttown_crowdsourcing_db.cursor()
    sql = "select orderId,finalDestinarion,clientId  from `" + (type + 'order') + "` where createDate>'" + str(
        year) + "' and createDate<'" + str(year + 1) + "'"
    cursor.execute(sql)
    results = cursor.fetchall()
    for orderInfo in results:
        orderId = orderInfo[0]
        # 目的地
        finalDestinarion = orderInfo[1]
        if finalDestinarion is None:
            finalDestinarion = '未知'
            logger.debug("orderId：%s 未找到对应目的地信息" % orderId)
        clientId = orderInfo[2]
        # 金额
        buyerSql = "select price  from `" + (type + 'logistics_cost') + "`  where priceNameType=2 and  orderId='" + str(
            orderId) + "'"
        cursor.execute(buyerSql)
        buyerresults = cursor.fetchone()
        if buyerresults is None:
            declarationAmount = 0
        else:
            declarationAmount = buyerresults[0]
            if declarationAmount is None:
                declarationAmount = 0
                logger.debug("orderId：%s 报关金额为空" % orderId)

        # 供应商信息
        supplierSql = "select District  from EnterpriseProfileLocale where LocaleId='zh-CN' and  EnterpriseId='" + str(
            clientId) + "'"
        csr = enterprise_db.cursor()
        csr.execute(supplierSql)
        supplierResults = csr.fetchone()
        if supplierResults is not None:
            # 省
            district = supplierResults[0]
            if district is None:
                supplierSql1 = "select District  from EnterpriseProfileLocale where LocaleId='en' and  EnterpriseId='" + str(
                    clientId) + "'"
                csr.execute(supplierSql1)
                district = csr.fetchone()[0]

            if district is None:
                district = "未知"
            else:
                if (len(str(district)) >= 2):
                    district = str(district)[0: 2] + "0000"

            if district in supplierInfo:
                supplierInfo[district] = supplierInfo[district] + declarationAmount
            else:
                supplierInfo[district] = declarationAmount

            if district in supplierInfoNum:
                supplierInfoNum[district] = supplierInfoNum[district] + 1
            else:
                supplierInfoNum[district] = 1
        else:
            logger.debug("orderId：%s ,clientId: %s 未找到对应供应商信息" % (orderId, clientId))

        # 目的地信息
        if finalDestinarion in buyerInfo:
            buyerInfo[finalDestinarion] = buyerInfo[finalDestinarion] + declarationAmount
        else:
            buyerInfo[finalDestinarion] = declarationAmount

        if finalDestinarion in buyerInfoNum:
            buyerInfoNum[finalDestinarion] = buyerInfoNum[finalDestinarion] + 1
        else:
            buyerInfoNum[finalDestinarion] = 1
    resultsDict = {}
    resultsDict['buyerInfo'] = buyerInfo
    resultsDict['buyerInfoNum'] = buyerInfoNum
    resultsDict['supplierInfo'] = supplierInfo
    resultsDict['supplierInfoNum'] = supplierInfoNum
    return resultsDict



def dataProcessor(dict, year):
    buyerInfo = dict['buyerInfo']
    buyerInfoNum = dict['buyerInfoNum']
    supplierInfo = dict['supplierInfo']
    supplierInfoNum = dict['supplierInfoNum']
    buyerData = {}
    buyerNumData = {}
    supplierData = {}
    supplierNumData = {}
    for key in areaKey:
        if key in supplierInfo:
            supplierData[areaKey[key]] = supplierInfo[key]

    for key in supplierInfo:
        if key not in areaKey:
            supplierData[key]=supplierInfo[key]


    for key in areaKey:
        if key in supplierInfoNum:
            supplierNumData[areaKey[key]] = supplierInfoNum[key]

    for key in supplierInfoNum:
        if key not in areaKey:
            supplierData[key]=supplierInfo[key]


    print(buyerInfo)
    buyerData =gangkouToCountry(buyerInfo)
    print(buyerData)

    print(buyerInfoNum)
    buyerNumData =gangkouToCountry(buyerInfoNum)
    print(buyerNumData)

    print(str(year) + "采购商各国贸易额")
    print(buyerData)
    print(str(year) + "采购商各国订单数")
    print(buyerNumData)
    print(str(year) + "供应商各省贸易额")
    print(supplierData)
    print(str(year) + "供应商各省订单数")
    print(supplierNumData)

    dataDict={}
    dataDict[str(year) + "采购商各国贸易额"]=buyerData
    dataDict[str(year) + "采购商各国订单数"]=buyerNumData
    dataDict[str(year) + "供应商各省贸易额"]=supplierData
    dataDict[str(year) + "供应商各省订单数"]=supplierNumData
    return dataDict
    # out.write(str(year) + "采购商各国贸易额" + '\n')
    # writeDict(buyerData)
    # # out.write(str(buyerData) + '\n')
    # out.write(str(year) + "采购商各国订单数" + '\n')
    # writeDict(buyerNumData)
    # # out.write(str(buyerNumData) + '\n')
    # out.write(str(year) + "供应商各省贸易额" + '\n')
    # writeDict(supplierData)
    # # out.write(str(supplierData) + '\n')
    # out.write(str(year) + "供应商各省订单数" + '\n')
    # writeDict(supplierNumData)
    # # out.write(str(supplierNumData) + '\n')
    # out.flush()

def gangkouToCountry(buyerDict):
    buyerCountryDict={}
    data = json.load(open('./port.json', encoding='UTF-8'))
    code_mapping = {x['portCode']: x for x in data}
    name_mapping = {x['portEnName']: x for x in data}

    for key in buyerDict:
        if key in code_mapping:
            port = code_mapping[key]
            country = port['countryCode']
        elif key in name_mapping:
            port = name_mapping[key]
            country = port['countryCode']
        else:
            country='未知'

        if country in buyerCountryDict:
            buyerCountryDict[country]=buyerCountryDict[country]+buyerDict[key]
        else:
            buyerCountryDict[country]=buyerDict[key]

    return buyerCountryDict





def doOrder():
    orderDict={}
    dict2016= dataProcessor(tradeInfo_1(2016, ''),2016)
    dict2017 = dataProcessor(tradeInfo_1(2017, ''),2017)
    dict2018 = dataProcessor(tradeInfo_1(2018, ''),2018)
    orderDict['历史物流信息Order']=dict(dict(dict2016,**dict2017),**dict2018)
    return orderDict
def doLooOrder():
    looDict={}
    dict2016 =dataProcessor(tradeInfo_1(2016, 'loo_'),2016)
    dict2017 =dataProcessor(tradeInfo_1(2017, 'loo_'),2017)
    dict2018 =dataProcessor(tradeInfo_1(2018, 'loo_'),2018)
    looDict['物流在线信息LooOrder']=dict(dict(dict2016,**dict2017),**dict2018)
    return looDict

def doAhoOrder():
    ahoDict = {}
    dict2016=dataProcessor(tradeInfo_2(2016, 'aho_'),2016)
    dict2017=dataProcessor(tradeInfo_2(2017, 'aho_'),2017)
    dict2018=dataProcessor(tradeInfo_2(2018, 'aho_'),2018)
    ahoDict['代理历史信息AhoOrder']=dict(dict(dict2016,**dict2017),**dict2018)
    return ahoDict

def doAooOrder():
    aooDict = {}
    dict2016=dataProcessor(tradeInfo_2(2016, 'aoo_'),2016)
    dict2017=dataProcessor(tradeInfo_2(2017, 'aoo_'),2017)
    dict2018=dataProcessor(tradeInfo_2(2018, 'aoo_'),2018)
    aooDict['代理在线信息AooOrder']=dict(dict(dict2016,**dict2017),**dict2018)
    return aooDict




def main():
    dict1=doOrder()
    dict2 =doLooOrder()
    dict3 =doAhoOrder()
    dict4 =doAooOrder()
    print(111)

def getOrder():
    return dict(dict(dict(doOrder(), **doLooOrder()), **doAhoOrder()),**doAooOrder())

if __name__ == '__main__':
    main()
