#!/usr/bin/env python3
# coding=utf-8
import decimal
import json

import channelCustomer
import orderAnalysis

OUT_FILE = './resultAll.txt'
out = open(OUT_FILE, 'w', encoding='utf-8')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def mergeBuyerByYear(year, tradeAll, orderAll):
    tradeStr = str(year) + '采购商各国贸易额'
    tradeNumStr = str(year) + '采购商各国订单数'
    tradeDict = tradeAll[tradeStr]
    tradeNumDict = tradeAll[tradeNumStr]
    for x in orderAll:
        orderTradeDict = orderAll[x][tradeStr]
        orderTradeNumDict = orderAll[x][tradeNumStr]
        for trade in orderTradeDict:
            if trade in tradeDict:
                tradeDict[trade] = tradeDict[trade] + orderTradeDict[trade]
            else:
                tradeDict[trade] = orderTradeDict[trade]

        for tradeNum in orderTradeNumDict:
            if tradeNum in tradeNumDict:
                tradeNumDict[tradeNum] = tradeNumDict[tradeNum] + orderTradeNumDict[tradeNum]
            else:
                tradeNumDict[tradeNum] = orderTradeNumDict[tradeNum]

    tradeAll[tradeStr] = tradeDict
    tradeAll[tradeNumStr] = tradeNumDict


def mergeSupplierByYear(year, tradeAll, orderAll):
    tradeStr = str(year) + '供应商各省贸易额'
    tradeNumStr = str(year) + '供应商各省订单数'
    tradeDict = tradeAll[tradeStr]
    tradeNumDict = tradeAll[tradeNumStr]
    for x in orderAll:
        orderTradeDict = orderAll[x][tradeStr]
        orderTradeNumDict = orderAll[x][tradeNumStr]
        for trade in orderTradeDict:
            if trade in tradeDict:
                tradeDict[trade] = tradeDict[trade] + orderTradeDict[trade]
            else:
                tradeDict[trade] = orderTradeDict[trade]

        for tradeNum in orderTradeNumDict:
            if tradeNum in tradeNumDict:
                tradeNumDict[tradeNum] = tradeNumDict[tradeNum] + orderTradeNumDict[tradeNum]
            else:
                tradeNumDict[tradeNum] = orderTradeNumDict[tradeNum]

    tradeAll[tradeStr] = tradeDict
    tradeAll[tradeNumStr] = tradeNumDict


def sortTrade(tradeAll):
    for key in tradeAll:
        tradeAll[key] = dict(sorted(tradeAll[key].items(), key=lambda d: d[1], reverse=True))


def main():
    tradeAll = channelCustomer.getTradeAll()
    orderAll = orderAnalysis.getOrder()

    # 合并
    mergeBuyerByYear(2016, tradeAll, orderAll)
    mergeSupplierByYear(2016, tradeAll, orderAll)
    mergeBuyerByYear(2017, tradeAll, orderAll)
    mergeSupplierByYear(2017, tradeAll, orderAll)
    mergeBuyerByYear(2018, tradeAll, orderAll)
    mergeSupplierByYear(2018, tradeAll, orderAll)
    # 倒序排序
    sortTrade(tradeAll)
    out.write(json.dumps(tradeAll, ensure_ascii=False, indent=4,cls=DecimalEncoder))
    out.flush()
    out.close()


if __name__ == "__main__":
    main()
    print('ok')



