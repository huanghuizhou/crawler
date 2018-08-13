#!/usr/bin/env python3
# coding=utf-8

import logging
import os
import sys

import pymysql
import pymssql

sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/..'))

# DB_HOST = '192.168.2.203'
# DB_USER = 'greatTao'
# DB_PASSWD = 'greatTao.1314'
# DB_PORT = 3306

DB_HOST = '192.168.2.203'
DB_USER = 'greattao'
DB_PASSWD = 'greatTao.5877'
DB_PORT = 3308
OUT_FILE = './result.csv'

# 打开mysql数据库链接

channel_crm_db = pymysql.connect(host=DB_HOST,  # 192.168.100.254
                                 user=DB_USER,
                                 passwd=DB_PASSWD,
                                 db="channel_crm",
                                 port=DB_PORT,  # 3306
                                 use_unicode=True,
                                 charset="utf8")

gttown_crm_db = pymysql.connect(host=DB_HOST,  # 192.168.100.254
                                user=DB_USER,
                                passwd=DB_PASSWD,
                                db="gttown_crm",
                                port=DB_PORT,  # 3306
                                use_unicode=True,
                                charset="utf8")

gttown_crowdsourcing_db = pymysql.connect(host=DB_HOST,  # 192.168.100.254
                                          user=DB_USER,
                                          passwd=DB_PASSWD,
                                          db="gttown_crowdsourcing",
                                          port=DB_PORT,  # 3306
                                          use_unicode=True,
                                          charset="utf8")


enterprise_db = pymssql.connect(host='DEVDB.great-tao.com\\GTTOWN_DEV',
                                user='sa',
                                password='P@ssw0rd',
                                database='GtTown',
                                charset="utf8")

# 行业字段
industryKey = {0: '其他',
               1: '机械',
               2: '硬件',
               3: '工业零件&amp;制造服务',
               4: '环境',
               5: '电子元件',
               6: '测量&amp;分析仪器',
               7: '电气设备&amp;零件',
               8: '电信设备',
               9: '安全&amp;保护',
               10: '灯光&amp;照明',
               11: '交通工具',
               12: '汽车&amp;摩托车',
               13: '化学品',
               14: '矿物&amp;冶金',
               15: '服装',
               16: '纺织品&amp;皮革产品',
               17: '建筑&amp;地产',
               18: '家具',
               19: '计算机硬件&amp;软件',
               20: '电子产品',
               21: '运动&amp;娱乐',
               22: '玩具&amp;爱好',
               23: '美容&amp;个人护理',
               24: '礼品&amp;工艺',
               25: '行李箱&amp;箱包',
               26: '鞋&amp;配件',
               27: '食品&amp;饮料',
               28: '家居用品&amp;户外',
               29: '办公&amp;文具用品',
               30: '健康&amp;医疗',
               31: '家用电器',
               32: '包装&amp;印刷',
               33: '橡胶&amp;塑料',
               34: '服务设备',
               35: '钟表、珠宝、眼镜',
               36: '工具',
               37: '能源',
               38: '农业'}
# 采购商国家分布
countryKey = {}
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

out = open(OUT_FILE, 'w')


def doChannelCustomer():
    cursor = gttown_crm_db.cursor()
    sql = """select id,role from channel_customer"""
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        id = row[0]
        role = row[1]
        analysis(role, id)
    # 处理数据并导出
    industrydataProcessor()


# 采购商行业统计
buyerIndustryDict = {}
# 供应商行业统计
supplierIndustryDict = {}
# 总行业统计
industryDict = {}
# 采购商国家分布
countryDict = {}
# 供应商省分布
areaDict = {}


# 根绝角色类型分别统计
def analysis(role, id):
    cursor = gttown_crm_db.cursor()

    # 1采购商
    if role == 1:
        sql = """select id,role,country,industry from channel_customer where id=%s"""
        cursor.execute(sql, (id))
        buyer = cursor.fetchone()
        id = buyer[0]
        country = buyer[2]
        country = str.upper(country)
        industry = buyer[3]
        if industry in buyerIndustryDict:
            buyerIndustryDict[industry] = buyerIndustryDict[industry] + 1
        else:
            buyerIndustryDict[industry] = 1

        if country in countryDict:
            countryDict[country] = countryDict[country] + 1
        else:
            countryDict[country] = 1
    else:
        # 2供应商
        if role == 2:
            sql = """select id,role,district,industry from channel_customer where id=%s"""
            cursor.execute(sql, (id))
            supplier = cursor.fetchone()
            id = supplier[0]
            district = supplier[2]
            if (len(str(district)) > 1):
                district = str(district)[0: 2] + "0000"
            industry = supplier[3]
            if industry in supplierIndustryDict:
                supplierIndustryDict[industry] = supplierIndustryDict[industry] + 1
            else:
                supplierIndustryDict[industry] = 1

            if district in areaDict:
                areaDict[district] = areaDict[district] + 1
            else:
                areaDict[district] = 1


# 处理数据并保存
def industrydataProcessor():
    # 采购商行业统计
    buyerIndustryDate = {}
    for key in sorted(buyerIndustryDict):
        if key in industryKey:
            buyerIndustryDate[industryKey[key]] = buyerIndustryDict[key]
    # 供应商行业统计
    supplierIndustryDate = {}
    for key in sorted(supplierIndustryDict):
        if key in industryKey:
            supplierIndustryDate[industryKey[key]] = supplierIndustryDict[key]

    # 行业总计
    industryDate = {}
    industryDate = dict(buyerIndustryDate)
    for key in supplierIndustryDate:
        if key in buyerIndustryDate:
            industryDate[key] = supplierIndustryDate[key] + industryDate[key]
        else:
            industryDate[key] = supplierIndustryDate[key]

    # 采购商国家分布
    countryDate = dict(countryDict)
    for key in sorted(supplierIndustryDict):
        if key in industryKey:
            supplierIndustryDate[industryKey[key]] = supplierIndustryDict[key]
    # 供应商省市区分布
    areaDate = {}
    for key in areaKey:
        if key in areaDict:
            areaDate[areaKey[key]] = areaDict[key]
    print(buyerIndustryDate)
    print(supplierIndustryDate)
    print(industryDate)
    print(areaDate)
    print(countryDate)

    out.write('国外采购商行业统计' + '\n')
    writeDict(buyerIndustryDate)
    # out.write(str(buyerIndustryDate) + '\n')
    out.write('国内供应商行业统计' + '\n')
    writeDict(supplierIndustryDate)
    # out.write(str(supplierIndustryDate) + '\n')
    out.write('行业合计' + '\n')
    writeDict(industryDate)
    # out.write(str(industryDate) + '\n')
    out.write('国内供应商地区统计' + '\n')
    writeDict(areaDate)
    # out.write(str(areaDate) + '\n')
    out.write('国外采购商国家统计' + '\n')
    writeDict(countryDate)
    # out.write(str(countryDate) + '\n')
    out.flush()


def tradeInfo(year):
    buyerTrade = {}
    buyerTradeNum = {}
    supplierTrade = {}
    supplierTradeNum = {}

    cursor = gttown_crm_db.cursor()
    sql = "select id,buyer_id,seller_id from trade_order where create_time >'" + str(
        year) + "' and create_time<'" + str(year + 1) + "'"
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        id = row[0]
        buyereId = row[1]
        sellerId = row[2]

        # 订单信息
        tradeSql = "select quantity,price  from trade_order_commodity where trade_order_id='" + str(id) + "'"
        cursor.execute(tradeSql)
        tradeResults = cursor.fetchone()
        if tradeResults is not None:
            quantity = tradeResults[0]
            price = tradeResults[1]
            # 单笔贸易额
            tradeMoney = quantity * price

        else:
            logger.debug("trade_order_id: %s 未找到对应订单信息" % id)
            tradeMoney = 0
        # 供应商信息
        supplierSql = "select province,id  from customer where id='" + str(sellerId) + "'"
        cursor.execute(supplierSql)
        supplierResults = cursor.fetchone()
        if supplierResults is not None:
            # 省
            province = supplierResults[0]
            if province is None:
                province = "未知"
            if province in supplierTrade:
                supplierTrade[province] = supplierTrade[province] + tradeMoney
            else:
                supplierTrade[province] = tradeMoney

            if province in supplierTradeNum:
                supplierTradeNum[province] = supplierTradeNum[province] + 1
            else:
                supplierTradeNum[province] = 1
        else:
            logger.debug("orderId：%s ,sellerId: %s 未找到对应供应商信息" % (id, sellerId))

        # 采购商信息
        corChannel = channel_crm_db.cursor()
        buyerSql = "select country,id  from customer where id='" + str(buyereId) + "'"
        corChannel.execute(buyerSql)
        buyerResults = corChannel.fetchone()
        if buyerResults is not None:
            # 国家
            country = buyerResults[0]
            if country is None:
                country = "未知"
            if country in buyerTrade:
                buyerTrade[country] = buyerTrade[country] + tradeMoney
            else:
                buyerTrade[country] = tradeMoney

            if country in buyerTradeNum:
                buyerTradeNum[country] = buyerTradeNum[country] + 1
            else:
                buyerTradeNum[country] = 1

        else:
            logger.debug("orderId：%s ,buyereId: %s 未找到对应采购商信息" % (id, buyereId))

    resultsDict = {}
    resultsDict['buyerTrade'] = buyerTrade
    resultsDict['buyerTradeNum'] = buyerTradeNum
    resultsDict['supplierTrade'] = supplierTrade
    resultsDict['supplierTradeNum'] = supplierTradeNum
    return resultsDict


def tradeDataProcessor(dict, year):
    buyerTrade = dict['buyerTrade']
    buyerTradeNum = dict['buyerTradeNum']
    supplierTrade = dict['supplierTrade']
    supplierTradeNum = dict['supplierTradeNum']
    buyerData = {}
    buyerNumData = {}
    supplierData = {}
    supplierNumData = {}
    for key in areaKey:
        if key in supplierTrade:
            supplierData[areaKey[key]] = supplierTrade[key]

    for key in areaKey:
        if key in supplierTradeNum:
            supplierNumData[areaKey[key]] = supplierTradeNum[key]
    buyerData = buyerTrade.copy()
    buyerNumData = buyerTradeNum.copy()
    print(str(year) + "采购商各国贸易额")
    print(buyerData)
    print(str(year) + "采购商各国订单数")
    print(buyerNumData)
    print(str(year) + "供应商各省贸易额")
    print(supplierData)
    print(str(year) + "供应商各省订单数")
    print(supplierNumData)

    out.write(str(year) + "采购商各国贸易额" + '\n')
    writeDict(buyerData)
    # out.write(str(buyerData) + '\n')
    out.write(str(year) + "采购商各国订单数" + '\n')
    writeDict(buyerNumData)
    # out.write(str(buyerNumData) + '\n')
    out.write(str(year) + "供应商各省贸易额" + '\n')
    writeDict(supplierData)
    # out.write(str(supplierData) + '\n')
    out.write(str(year) + "供应商各省订单数" + '\n')
    writeDict(supplierNumData)
    # out.write(str(supplierNumData) + '\n')
    out.flush()


# 贸易总额
def tradeTotal():
    cursor = gttown_crowdsourcing_db.cursor()
    sql = """select SUM(declarationAmount) from `order`"""
    cursor.execute(sql)
    results = cursor.fetchall()
    tradeTotal = results[0][0]
    out.write("贸易额总额" + '\n')
    out.write(str(tradeTotal) + '\n')
    out.flush()


def writeDict(dict):
    for key in dict:
        out.write(key + ",")

    out.write('\n')
    for value in dict.values():
        out.write(str(value) + ",")
    out.write('\n')
    out.write('\n')


def doTrage():
    # 2016年
    tradeDataProcessor(tradeInfo(2016), 2016)
    # 2017年
    tradeDataProcessor(tradeInfo(2017), 2017)
    # 2018年
    tradeDataProcessor(tradeInfo(2018), 2018)
    # 贸易总金额
    tradeTotal()


def main():
    # 行业信息处理
    doChannelCustomer()
    # 贸易额处理
    doTrage()

    channel_crm_db.close()
    gttown_crm_db.close()
    gttown_crowdsourcing_db.close()
    out.close()


if __name__ == '__main__':
    main()
