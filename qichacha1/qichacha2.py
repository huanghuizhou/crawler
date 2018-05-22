#!/usr/bin/env python3
# coding=utf-8

import logging
import os
import random
import sys
import time
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from qichacha1.enterpriseEntity import Enterprise

sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/..'))


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


def main():
    localCookies = ['bn7vk7ldhtbiudelnkg7c5aps7', 'vd675udbu1voav057lto8avfd6', 'oqcght5edqgs8s027bvooloo86',
                    'bn7vk7ldhtbiudelnkg7c5aps7', 'n3ah97al5njvnjjrol18gkf595', 'gmpn0a4i1spi9ld96ahhf6f7s3',
                    'vti1kq84j7ponutk1k0lflobm6']
    companies = getCompanies()
    s = requests.Session()
    s.cookies['PHPSESSID'] = 'in25am0fs33u9c7ju0tt48h3t6'
    # s.cookies['Hm_lpvt_3456bee468c83cc63fb5147f119f1075']=str(int(time.time()))
    # s.cookies['Hm_lvt_3456bee468c83cc63fb5147f119f1075']='1526518687,1526550657,1526629076'
    # s.cookies['hasShow']='1'
    # zg = '%7B%22sid%22%3A%201526619320530%2C%22updated%22%3A%20' + str(int(time.time())) + '123' + '%2C%22info%22%3A%201526550657092%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22%22%2C%22cuid%22%3A%20%22ea7692aaf104ff11046743151615b0b6%22%7D'
    #
    # s.cookies['zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f'] = zg
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'})
    port = 1235
    proxy_server = '192.168.150.98:' + str(port)
    proxy = {
        'http': proxy_server,
        'https': proxy_server
    }

    startUrl = "https://www.qichacha.com"
    out = open('E:/outInfo.txt', 'a')
    errorout = open('E:/errorOut.txt', 'a')
    r1 = s.get(startUrl, proxies=proxy)
    for index, company in enumerate(companies):

        try:
            url = 'https://www.qichacha.com/search?key=' + quote(company)
            r = s.get(url, proxies=proxy)
            if r.status_code != 200:
                print('code error')
                errorout.write(company + '\n')
                errorout.flush()
                break
            html = r.text
            soup = BeautifulSoup(html, "lxml")

            trs = soup.find("div", {"id": "ajaxlist"}).find("section").find("table").find("tbody").findAll("tr")
            tds = trs[0].findAll("td")
            ps = tds[1].findAll("p")
            legal = ps[0].find("a").string.replace("\n", "").strip()
            # enterpriseName = tds[1].find("a").getText().replace("\n", "").strip()
            enterpriseName = company
            registerCapital = ps[0].findAll("span")[0].string.replace("注册资本：", "").replace("\n", "").strip()
            buildTime = ps[0].findAll("span")[1].string.replace("成立时间：", "").replace("\n", "").strip()
            emailAndPhone = ps[1].getText().replace("\n", "").strip()
            email = emailAndPhone[emailAndPhone.find("邮箱："):emailAndPhone.find("电话：")].replace("邮箱：", "").strip()
            phone = ps[1].find("span").string.replace("电话：", "").replace("\n", "").strip()
            address = ps[2].getText().replace("地址：", "").replace("\n", "").strip()
            enterprise = Enterprise(enterpriseName, legal, registerCapital, buildTime, email, phone, address)
            out.write(getCvs(enterprise) + '\n')
            time.sleep(0.4 + random.randint(0, 20) * 0.01)
            out.flush()
        except Exception as e:
            logger.error("line", index)
            logger.error("{} can not get info", company)
            print(company + " can not get info")
            print(" line", index)
            # 写出失败企业
            errorout.write(company + '\n')
            errorout.flush()
            # newcookie=localCookies[random.randint(0,2)]
            # s.cookies['PHPSESSID']=newcookie
            # s.cookies['Hm_lpvt_3456bee468c83cc63fb5147f119f1075'] = str(int(time.time()))
            # zg = '%7B%22sid%22%3A%201526619320530%2C%22updated%22%3A%20' + str(int(time.time())) + '123' + '%2C%22info%22%3A%201526550657092%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22%22%2C%22cuid%22%3A%20%22ea7692aaf104ff11046743151615b0b6%22%7D'
            #
            # s.cookies['zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f'] = zg
            # s.cookies['hasShow'] = '1'
            # port+=1
            print("port:", port)
            proxy_server = '192.168.150.98:' + str(port)
            proxy = {
                'http': proxy_server,
                'https': proxy_server
            }
            s.get(startUrl, proxies=proxy)
    out.close()
    errorout.close()


def getCompanies():
    companies = [];
    f = open("E:\enterprise.txt", encoding='utf-8')
    # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    while line:
        # print(line, end = '')　　　# 在 Python 3中使用
        companies.append(line.replace("\n", ""))
        line = f.readline()
    f.close()
    return companies


# 导出
def getCvs(enterprise):
    outCvs = '"' + enterprise.name + '","' + enterprise.legal + '","' + enterprise.registerCapital + '","' + enterprise.buildTime + '","' + enterprise.email + '","' + enterprise.phone + '","' + enterprise.address + '"'
    print(outCvs)
    return outCvs


if __name__ == '__main__':
    main()
