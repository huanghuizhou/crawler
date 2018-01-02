#!/usr/bin/env python3
# coding=utf-8

import io
import json
import re
import time

import requests
from scrapy.selector import Selector

import captcha
from exception import BizException

TIME_INTERVAL = 0.5


def handle_result(func):
    def wrapper(self, *args, **kwargs):
        tried = 0
        while True:
            try:
                response = func(self, *args, **kwargs)
            except BizException:
                continue
            ret = response.json()
            code = ret['code']
            self.token = ret['token']
            if code == 423:
                captcha_text = self.get_captcha()
                self.unlock(captcha_text)
                tried += 1
                time.sleep(TIME_INTERVAL)
                continue
            text = json.dumps(ret)
            text = re.sub('<.*?>', '', text)
            ret = json.loads(text)
            if tried > 0:
                print("Captcha succeed in", tried, "times")
            return ret

    return wrapper


class TradeStudy(object):
    def __init__(self):
        self.username = '18658283306'
        self.password = 'vxPMcWfaMzf4t3LW'
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36 OPR/49.0.2725.64'
        }
        self.token = ''
        self.login()

    def _handle_response(self, response):
        if response.status_code != 200:
            raise BizException('<' + response.url + '> code ' + str(response.status_code))

    def login(self):
        login_url = 'http://sso.tradestudy.cn/login?service=http%3A%2F%2Fmy.tradestudy.cn%2Flogin'

        self.session = requests.Session()

        # login post request
        login_page = self.session.get(login_url).text
        login_html = Selector(text=login_page)
        form = login_html.xpath('//form')
        lt = form.xpath('//input[@name="lt"]/@value').extract_first()
        execution = form.xpath('//input[@name="execution"]/@value').extract_first()
        response = self.session.post(login_url, data={
            'm': 'ajax',
            'username': self.username,
            'password': self.password,
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit',
            'rememberMe': 'true'
        }, headers=self.headers)

        self._handle_response(response)
        # print(response)

        # ticket request
        ticket_url = response.json()['to']
        response = self.session.get(ticket_url, headers=self.headers, allow_redirects=False)
        if response.status_code != 302:
            raise RuntimeError('Failed to exchange ticket ' + response.status_code)
        # print(response)

    @handle_result
    def search(self, **kwargs):
        """
        根据条件搜索
        :param kwargs: country, blno, buyers, suppliers,
        :return:
        """
        if not self.token:
            self.get_init_token()
        url = 'http://my.tradestudy.cn/customs/query/'
        kwargs['token'] = self.token
        kwargs['order'] = 'desc'
        if 'country' not in kwargs:
            kwargs['country'] = 'america'
        response = self.session.get(url, params=kwargs)
        self._handle_response(response)
        return response

    def get_init_token(self):
        url = 'http://my.tradestudy.cn/customs/'
        response = self.session.get(url, headers=self.headers)
        self._handle_response(response)
        html = Selector(text=response.text)
        self.token = html.xpath('//input[@id="token"]/@value').extract_first()
        return self.token

    def get_captcha(self):
        url = 'http://my.tradestudy.cn/customs/captcha'
        response = self.session.get(url, headers=self.headers)
        self._handle_response(response)
        file = io.BytesIO(response.content)
        return captcha.parse_captcha(file)

    def unlock(self, captcha_code):
        url = 'http://my.tradestudy.cn/customs/unlock'
        response = self.session.post(url, data={
            'captcha': captcha_code
        }, headers=self.headers)
        self._handle_response(response)
        if response.status_code == 200:
            return len(response.json()) == 0
        else:
            return False


if __name__ == '__main__':
    t = TradeStudy()

    # print(t.get_captcha())

    # search test
    suppliers = 'Ningbo Heyuan Textile Product Co. Ltd'
    buyers = 'DOLLAR GENERAL CORPORATION'
    # print('Searching supplier: ' + suppliers)
    # print('Result:')
    for i in range(1000):
        result = t.search(suppliers=suppliers, buyers=buyers)
        time.sleep(TIME_INTERVAL)
        if len(result) == 0:
            print('result error')
        print(json.dumps(result))
