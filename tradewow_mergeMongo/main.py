#!/usr/bin/env python3
# coding=utf-8

import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/..'))

from egtcp.dao_1 import MONGO_CLIENT_DEV, MONGO_CLIENT_LOCAL, DB_NAME, COLLECTION_NAME_A, COLLECTION_NAME_B


# https://www.tradewow.com/#/search 原始数据

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


def insert_trade_wow(trade):
    collection_dev = MONGO_CLIENT_DEV[DB_NAME][COLLECTION_NAME_B]
    collection_dev.replace_one({'_id': trade['_id']}, trade, upsert=True)


def replace_trade_wow(oldTrade, buyerId):
    collection_dev = MONGO_CLIENT_DEV[DB_NAME][COLLECTION_NAME_B]
    oldTrade['buyerId'] = buyerId
    collection_dev.replace_one({'_id': oldTrade['_id']}, oldTrade, upsert=True)


def main():
    collection_local = MONGO_CLIENT_LOCAL[DB_NAME][COLLECTION_NAME_A]
    collection_dev = MONGO_CLIENT_DEV[DB_NAME][COLLECTION_NAME_B]
    ids = [x['_id'] for x in collection_local.find().skip(161000)]
    for tradeWow_id in ids:
        tradeWow = collection_local.find_one({'_id': tradeWow_id})
        if not tradeWow:
            logger.error('tradeWow id %s can not be found' % tradeWow_id)
            continue
        oldTrade = collection_dev.find_one(
            {'productDesc': tradeWow['productDesc'], 'shipperName': tradeWow['shipperName'],
             'consigneeName': tradeWow['consigneeName'], 'actArrivalDate': tradeWow['actArrivalDate']})
        if oldTrade:
            replace_trade_wow(oldTrade, tradeWow['buyerId'])
            logger.info('replace tradeWow %s ' % tradeWow_id)
        else:
            insert_trade_wow(tradeWow)
            logger.info('insert tradeWow %s ' % tradeWow_id)


if __name__ == '__main__':
    main()
