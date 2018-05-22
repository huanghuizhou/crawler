# coding=utf-8
import datetime
import logging
import os
import traceback

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 日志
from qichacha1.enterpriseEntity import Enterprise


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


# 测试用例执行函数
def work(browser):
    global company
    url = 'https://www.qichacha.com/search?key='
    # 读取全部企业
    companies = getCompanies()
    browser.get('https://www.qichacha.com')

    cookie = browser.get_cookie("PHPSESSID")
    del cookie['value']
    cookie['value'] = "oqcght5edqgs8s027bvooloo86"
    browser.add_cookie(cookie)

    out = open('E:/outInfo.txt', 'a')
    try:
        for company in companies:
            infoUrl = url + company
            browser.get(infoUrl)
            html1 = browser.execute_script("return document.documentElement.outerHTML")
            soup = BeautifulSoup(html1, "lxml")
            trs = soup.find("div", {"id": "ajaxlist"}).find("section").find("table").find("tbody").findAll("tr")
            tds = trs[0].findAll("td")
            ps = tds[1].findAll("p")
            legal = ps[0].find("a").string.replace("\n", "").strip()
            enterpriseName = tds[1].find("a").getText().replace("\n", "").strip()
            registerCapital = ps[0].findAll("span")[0].string.replace("注册资本：", "").replace("\n", "").strip()
            buildTime = ps[0].findAll("span")[1].string.replace("成立时间：", "").replace("\n", "").strip()
            emailAndPhone = ps[1].getText().replace("\n", "").strip()
            email = emailAndPhone[emailAndPhone.find("邮箱："):emailAndPhone.find("电话：")].replace("邮箱：", "").strip()
            phone = ps[1].find("span").string.replace("电话：", "").replace("\n", "").strip()
            address = ps[2].getText().replace("地址：", "").replace("\n", "").strip()
            enterprise = Enterprise(enterpriseName, legal, registerCapital, buildTime, email, phone, address)
            out.write(getCvs(enterprise) + '\n')
            # sleep(1)
            out.flush()
    except Exception as e:
        logger.error("{} can not get info", company)
        print(company + " can not get info")
    finally:
        out.close()


def writeLog():
    # 组合日志文件名（当前文件名+当前时间）.比如：case_login_success_20150817192533
    basename = os.path.splitext(os.path.basename(__file__))[0]
    logFile = basename + "-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".log"
    logging.basicConfig(filename=logFile)
    s = traceback.format_exc()
    logging.error(s)
    browser.get_screenshot_as_file("./" + logFile + "-screenshot_error.png")


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


if __name__ == "__main__":
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    browser = webdriver.Chrome(chrome_options=chrome_options)  # Chrome界面
    # browser = webdriver.PhantomJS()  # 无界面
    work(browser)
    browser.quit()
