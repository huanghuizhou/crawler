#!/usr/bin/env python3
# coding=utf-8

import logging

import requests

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


def get_trade_list(supplier_name):
    """
    https://www.tradewow.com/#/search
    :param supplier_name:
    :return: resp(see trade_wow_example.txt)
    """
    query = {
        "needHighlighting": False,
        "query":            {
            "country":  "America",
            "field":    "shipperName",
            "keywords": supplier_name,
            "years":    [
                "2016"
            ],
            "pageNum":  0,
            "pageSize": 100
        },
        "aggregation":      {
            "consigneeName": {
                "pageNum":  0,
                "pageSize": 100
            },
            "shipperName":   {
                "pageNum":  0,
                "pageSize": 100
            }
        }
    }
    resp = requests.post(TRADE_WOW_API, json=query)
    if resp.status_code != 200:
        raise ValueError('Code %d, message %s' % (resp.status_code, resp.text))
    resp_json = resp.json()
    return resp_json


def save_trade_wow(data):
    collection = MONGO_CLIENT[DB_NAME][TRADE_WOW_COLLECTION]
    for trade in data:
        trade['_id'] = trade.pop('id')
        collection.replace_one({'_id': trade['_id']}, trade, upsert=True)


def save_trade_info(supplier_name, aggregations):
    try:
        items = aggregations['consigneeName']['items']
    except KeyError:
        logger.error('aggregations items not found for %s' % supplier_name)
        return
    collection = MONGO_CLIENT[DB_NAME][TRADE_INFO_COLLECTION]
    collection.delete_many({'supplier': supplier_name})
    for item in items:
        if 'key' not in item:
            logger.error('key not found in item %s' % str(item))
            continue
        collection.insert_one({
            'supplier': supplier_name,
            'buyer':    item['key']
        })


def main():
    collection = MONGO_CLIENT[DB_NAME][COLLECTION_NAME]
    ids = [x['_id'] for x in collection.find({'done': True}, {'_id': 1})]
    for supplier_id in ids:
        supplier = collection.find_one({'_id': supplier_id})
        if not supplier:
            logger.error('supplier id %s can not be found' % supplier_id)
            continue
        try:
            name = supplier['basic_info_en']['name']
        except KeyError:
            logger.error('unknown supplier name of %s' % supplier_id)
            continue
        trade = get_trade_list(name)
        save_trade_wow(trade['data'])
        save_trade_info(name, trade['aggregations'])


if __name__ == '__main__':
    main()
