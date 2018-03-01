#!/usr/bin/env python3
# coding=utf-8


import random

import requests

PROXY = {
    'http':  'http://127.0.0.1:1235',
    'https': 'http://127.0.0.1:1235',
}
REQUEST_TIMEOUT = 5  # seconds
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 OPR/50.0.2762.67',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
]


def get(url, params=None, **kwargs):
    ua = USER_AGENTS[random.randint(0, len(USER_AGENTS) - 1)]
    return requests.get(url, params=params, proxies=PROXY, timeout=REQUEST_TIMEOUT, headers={'User-Agent': ua},
                        **kwargs)
