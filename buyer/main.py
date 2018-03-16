#!/usr/bin/env python3
# coding=utf-8

import logging
import multiprocessing
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import quote, urlparse

import requests
from pymongo import MongoClient
from scrapy import Selector
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

import network
from exception import MaxRetryExceeded

sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/..'))
from egtcp.dao import MONGO_CLIENT, DB_NAME

BUYER_COLLECTION = 'Buyers'
GOOGLE_MAP_SEARCH = 'https://www.google.com/maps/place/%s/@39.0163683,-86.1636772,4z'
GOOGLE_SEARCH = 'https://www.google.com/search?ie=UTF-8&oe=UTF-8&q='
SELENIUM_SERVER = 'http://192.168.20.240:4444/wd/hub'
TMP_DIR = '/tmp'
UPLOAD_API = 'https://basic.egtcp.com/upload'
PROXY = {
    'http':  'http://127.0.0.1:1235',
    'https': 'http://127.0.0.1:1235',
}
REQUEST_TIMEOUT = 5  # seconds

IMAGE_PATTERN = re.compile('url\("(.*?)"\)')
GOOGLE_RESULT_PATTERN = re.compile('q=(.*?)&')
EMAIL_PATTERN = re.compile('([a-zA-Z0-9\-.]+@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9_\-]+)+)')


def get_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    # Standard output handler
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s:%(lineno)s: %(message)s'))
    log.addHandler(sh)

    return log


logger = get_logger(__file__)
collection = MONGO_CLIENT[DB_NAME][BUYER_COLLECTION]
driver = None


def init_network():
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:1235'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:1235'


def init_selenium():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--lang=en_US,en')
    return webdriver.Remote(SELENIUM_SERVER, webdriver.DesiredCapabilities.CHROME,
                            options=chrome_options)


def init_mongo():
    return MongoClient(host='192.168.2.203', port=27017, username="gt_rw", password="greattao5877",
                       authSource=DB_NAME,
                       authMechanism="SCRAM-SHA-1")


def do_with_retry(func, arg=None, wait_time=1, max_retry=5):
    tried = 0
    while True:
        tried += 1
        if tried > max_retry:
            raise MaxRetryExceeded

        try:
            return func(arg)
        except Exception as e:
            time.sleep(wait_time)


def _extract_info(response, field):
    xpath = '//span[@class="section-info-icon maps-sprite-pane-info-%s"]/following-sibling::span[2]/span[@class="widget-pane-link"]/text()' % field
    return response.xpath(xpath).extract_first()


def _extract_image_url(style):
    m = IMAGE_PATTERN.search(style)
    if not m:
        return None
    url = m.group(1)
    if not url.startswith('http'):
        url = 'http:' + url
    if 'googleusercontent.com' in url:
        url = url.split('=')[0]
    return url


def _file_ext(url):
    o = urlparse(url)
    path = o.path
    if '.' not in path:
        return 'jpeg'
    return path.split('.')[-1]


def _upload_cdn(url):
    raw_image_resp = network.get(url)
    if raw_image_resp.status_code != 200:
        raise IOError('Failed to download image ' + url)

    ext = _file_ext(url)
    cdn_image_resp = requests.post(UPLOAD_API, files={'file': ('image.' + ext, raw_image_resp.content)})
    ret = cdn_image_resp.json()
    if cdn_image_resp.status_code != 200:
        logger.error('Failed to upload cdn ' + str(ret))
        return None
    return ret['url']


def find_images():
    # 点图片按钮
    driver.find_element_by_css_selector('.section-image-pack-button').click()
    img_css = 'div.gallery-image-high-res.loaded'
    do_with_retry(lambda x: driver.find_element_by_css_selector(img_css), wait_time=3, max_retry=10)
    elements = driver.find_elements_by_css_selector(img_css)
    images = []
    for element in elements:
        raw_image_url = _extract_image_url(element.get_attribute('style'))
        try:
            cdn_image_url = _upload_cdn(raw_image_url)
        except Exception as e:
            logger.error(e)
            cdn_image_url = None
        images.append({
            'raw_url': raw_image_url,
            'cdn_url': cdn_image_url
        })
    return images


def check_loading(css):
    try:
        if driver.find_element_by_css_selector(css):
            raise RuntimeError
    except NoSuchElementException:
        pass


def find_place(place_name):
    url = GOOGLE_MAP_SEARCH % quote(place_name)
    driver.get(url)
    # 点搜索按钮
    do_with_retry(lambda x: driver.find_element_by_css_selector('#searchbox-searchbutton').click())
    # 等搜索结果dom加载
    do_with_retry(lambda x: check_loading('div.loading'), wait_time=3)

    if 'search' in driver.current_url:
        if len(driver.find_elements_by_css_selector('div.section-bad-query')) > 0:
            # 无结果
            return None
        # 如果是搜索页，点第一个结果
        do_with_retry(lambda x: driver.find_element_by_xpath('(//div[@class="section-result"])').click(),
                      wait_time=3)
    # 尝试获取title
    do_with_retry(lambda x: driver.find_element_by_xpath('//h1[@class="section-hero-header-title"]'), wait_time=3)
    # 解析字段
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    response = Selector(text=html)
    place = {
        'full_name': response.xpath('//h1[@class="section-hero-header-title"]/text()').extract_first(),
        'address':   _extract_info(response, 'address'),
        'website':   _extract_info(response, 'website'),
        'phone':     _extract_info(response, 'phone'),
        'images':    find_images()
    }
    # print(place)
    return place


def find_emails(website):
    keyword = 'mail ' + website
    url = GOOGLE_SEARCH + quote(keyword)
    resp = network.get(url)
    if resp.status_code != 200:
        logger.error('Response from "%s" error, code %s', url, resp.status_code)
        logger.debug('Response: %s', resp.text)
        raise IOError('Failed to search mail from ' + url)
    response = Selector(text=resp.text)

    target_url = response.xpath('//div[@class="g"]/h3/a/@href').extract_first()
    if target_url.startswith('/url'):
        m = GOOGLE_RESULT_PATTERN.search(target_url)
        if not m:
            raise ValueError('Failed to parse google search result %s', target_url)
        target_url = m.group(1)
    target_response = network.get(target_url)
    if target_response.status_code != 200:
        logger.warning('Target site "%s" may be down, code %s', target_url, target_response.status_code)
        logger.debug('Target site response\n %s', target_response.text)
    matches = EMAIL_PATTERN.findall(target_response.text)
    return [m[0] for m in matches]


def work(query, page_begin, page_end):
    global driver, collection
    # init_network()
    driver = init_selenium()
    client = init_mongo()
    collection = client[DB_NAME][BUYER_COLLECTION]
    logger.info(
        'Initialized successfully, start working from %d to %d' % (page_begin, page_end))
    cursor = collection.find(query, {'_id': 1}).skip(page_begin).limit(page_end - page_begin + 1)
    ids = [x['_id'] for x in cursor]
    for doc_id in ids:
        doc = collection.find_one(doc_id)
        if 'name' not in doc:
            logger.error('name not found in doc %s', doc)
            continue
        try:
            place = find_place(doc['name'])
        except Exception as e:
            logger.error('Failed to find place %s', str(e))
            continue
        if not place:
            logger.warning('No place info found for "%s"', doc['name'])
            place = {'miss': True}
        if 'website' in place and place['website']:
            try:
                emails = find_emails(place['website'])
                place['emails'] = emails
            except Exception as e:
                logger.error('Failed to find emails %s', str(e))
        doc.update(place)
        doc['update_time'] = datetime.now()
        if '_id' in doc:
            del doc['_id']
        collection.replace_one({'name': doc['name']}, doc)
        logger.info('Place info "%s" updated', doc['name'])


def main():
    query = {
        'full_name': {'$exists': False},
        '$or':       [
            {'miss': False},
            {'miss': {'$exists': False}}
        ]
    }
    count = collection.count(query)
    page_num = 4
    page_size = count // page_num
    processes = []
    for i in range(page_num):
        page_begin = page_size * i
        if i == page_num - 1:
            page_end = count
        else:
            page_end = page_begin + page_size - 1
        process_name = 'query-%d-%d' % (page_begin, page_end)
        p = multiprocessing.Process(target=work, args=(query, page_begin, page_end), name=process_name)
        p.start()
        logger.info('Sub process %s started', process_name)
        processes.append(p)

    for p in processes:
        p.join()
        logger.info('Sub process %s finished', p.name)


if __name__ == '__main__':
    main()
