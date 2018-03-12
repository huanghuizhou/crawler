#!/usr/bin/env python3
# coding=utf-8

import logging
import os
import sys
import time

import requests

sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/..'))

from egtcp.dao import MONGO_CLIENT, DB_NAME, COLLECTION_NAME

# https://www.tradewow.com/#/search 原始数据
TRADE_WOW_COLLECTION = 'TradeWow'
# 供应商和采购商贸易往来映射
TRADE_INFO_COLLECTION = 'TradeInfo'

TRADE_WOW_API = 'https://www.tradewow.com/api/v1/warehouse/search'


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


def get_trade_list(buyer_name):
    """
    https://www.tradewow.com/#/search
    :param buyer_name:
    :return: resp(see trade_wow_example.txt)
    """
    query = {
        "needHighlighting": False,
        "query": {
            "country": "America",
            "field": "consigneeName",
            "keywords": buyer_name,
            "years": [
                "2016"
            ],
            "pageNum": 0,
            "pageSize": 100
        },
        "aggregation": {
            "consigneeName": {
                "pageNum": 0,
                "pageSize": 100
            },
            "shipperName": {
                "pageNum": 0,
                "pageSize": 100
            }
        }
    }
    resp = requests.post(TRADE_WOW_API, json=query)
    if resp.status_code != 200:
        raise ValueError('Code %d, message %s' % (resp.status_code, resp.text))
    resp_json = resp.json()
    return resp_json


def save_trade_wow(buyer, data):
    collection = MONGO_CLIENT[DB_NAME][TRADE_WOW_COLLECTION]
    for trade in data:
        trade['_id'] = trade.pop('id')
        trade['buyer_id'] = buyer['_id']
        collection.replace_one({'_id': trade['_id']}, trade, upsert=True)


def save_trade_info(supplier, aggregations):
    name = supplier['name']
    try:
        name_cn = supplier['name']
    except KeyError:
        name_cn = ''

    try:
        items = aggregations['consigneeName']['items']
    except KeyError:
        logger.error('aggregations items not found for %s' % name)
        return
    collection = MONGO_CLIENT[DB_NAME][TRADE_INFO_COLLECTION]
    collection.delete_many({'supplier': name})
    for item in items:
        if 'key' not in item:
            logger.error('key not found in item %s' % str(item))
            continue
        collection.insert_one({
            'supplier': name,
            'supplierCn': name_cn,
            'buyer': item['key']
        })


def main():
    collection = MONGO_CLIENT[DB_NAME][COLLECTION_NAME]
    tradewow_collection = MONGO_CLIENT[DB_NAME][TRADE_WOW_COLLECTION]
    ids = [x['_id'] for x in collection.find()]
    for buyer_id in ids:
        buyer = collection.find_one({'_id': buyer_id})
        if not buyer:
            logger.error('buyer id %s can not be found' % buyer_id)
            continue
        trade = tradewow_collection.find_one({'buyer_id': buyer_id})
        if trade:
            logger.debug('buyer %s info found, skip' % buyer_id)
            continue

        try:
            name = buyer['name']
        except KeyError:
            logger.error('unknown buyer name of %s' % buyer_id)
            continue
        while True:
            try:
                trade = get_trade_list(name)
            except Exception as e:
                logger.warning('Failed to retrieve %s, wait for 1 min' % buyer_id, e)
                time.sleep(60)
            else:
                break

        save_trade_wow(buyer, trade['data'])
        # save_trade_info(buyer, trade['aggregations'])
        if len(trade['data']) > 0:
            logger.info('buyer %s(%s) trade info saved' % (buyer_id, name))


if __name__ == '__main__':
    main()
