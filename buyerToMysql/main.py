#!/usr/bin/env python3
# coding=utf-8

import datetime
import logging
import os
import sys
import time

import pymysql

sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/..'))

from dao import MONGO_CLIENT_DEV, DB_NAME, COLLECTION_NAME

# 打开mysql数据库链接
# db = pymysql.connect(host="121.201.69.46",  # 192.168.100.254
#                      user="gtdata",
#                      passwd="Admin@123",
#                      db="gttown_crm",
#                      port=23306,  # 3306
#                      use_unicode=True,
#                      charset="utf8")

db = pymysql.connect(host="192.168.2.203",  # 192.168.100.254
                     user="greatTao",
                     passwd="greatTao.1314",
                     db="channel_crm",
                     port=3306,  # 3306
                     use_unicode=True,
                     charset="utf8")


# db = pymysql.connect(host="localhost",  # 192.168.100.254
#                      user="root",
#                      passwd="12345678",
#                      db="test",
#                      port=3306,  # 3306
#                      use_unicode=True,
#                      charset="utf8")


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



def insert_Mysql(buyerInfo, no):
    # list格式
    email = ""
    image = ""

    # emails 为list
    if ("emails" in buyerInfo.keys()):
        emails = buyerInfo['emails']
        if emails is None:
            emails = ""
        if (len(emails) > 0):
            for e in emails:
                email = email + e + ","
            email = email[0:-1]

    # images为list +dict
    if ("images" in buyerInfo.keys()):
        images = buyerInfo['images']
        if images is None:
            images = ""
        if (len(images) > 0):
            for i in images:
                imageInfo = ""
                for name, value in i.items():
                    if value is None:
                        value = ""
                    imageInfo = imageInfo + name + ":" + value + ","
                imageInfo = "{" + imageInfo[0:-1] + "}"
                image = image + imageInfo + ","
            image = image[0:-1]

    fullName = ""
    if ("full_name" in buyerInfo.keys()):
        fullName = buyerInfo['full_name']
        if fullName is None:
            fullName = ""

    else:
        if ("name" in buyerInfo.keys()):
            fullName = buyerInfo['name']
            if fullName is None:
                fullName = ""

    address = ""
    if ("address" in buyerInfo.keys()):
        address = buyerInfo['address']
        if address is None:
            address = ""

    phone = ""
    if ("phone" in buyerInfo.keys()):
        phone = buyerInfo['phone']
        if phone is None:
            phone = ""

    website = ""
    if ("website" in buyerInfo.keys()):
        website = buyerInfo['website']
        if website is None:
            website = ""

    remark = "{phone:" + phone + "};{emails:" + email + "};{images:" + image + "}"
    if (len(remark) > 2000):
        remark = remark[0:2000]

    customerNo = "GTCUST" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + no
    sql = """INSERT INTO customer (isPrivate,origin,customerSourceType,customerSourceInfo,createrUserName,createrUserRealName,customerNo,address,webSite,enterpriseName,remark,customerType) \
value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    try:
        cursor = db.cursor()
        cursor.execute(sql,
                       ("0", "4", "0", "互联网", "crawler", "BOSS系统", customerNo, address, website, fullName, remark, "1"))
        db.commit()
        print(customerNo + buyerInfo['name'])
    except Exception as e:
        logger.warning('Failed to insert into customer sql is %s' % sql, e)
        print('Failed to insert into customer sql is %s' % sql, e)
        time.sleep(5)


def main():
    collection_dev = MONGO_CLIENT_DEV[DB_NAME][COLLECTION_NAME]

    no = 1
    # mongodb中获取数据
    for x in collection_dev.find():
        if ("miss" in x.keys()):
            if (x['miss'] == True):
                continue

        # 插入到mysql
        StrNo = str(no).zfill(5)
        insert_Mysql(x, StrNo)
        no += 1


if __name__ == '__main__':
    main()
