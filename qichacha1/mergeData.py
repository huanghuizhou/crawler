#!/usr/bin/env python3
# coding=utf-8

import logging
import os
import sys

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
    oldDate = getOldData()
    newDate = getNewData()

    out = open('G:/merge/merge.txt', 'a')
    outNotExist = open('G:/merge/ccc.txt', 'a')
    for index, name in enumerate(oldDate):
        if (newDate.get(name)):
            newDateInfo = newDate.get(name)
            oldDateInfo = oldDate.get(name)
            out.write(oldDateInfo[0:-2] + "," + newDateInfo)
        else:
            outNotExist.write(name + "\n")
            out.write(oldDate.get(name))
            print(name, "not exist")

    out.close()


def getOldData():
    oldData = {}
    f = open("G:\merge\\aaaaa.csv")
    # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    while line:
        name = line.split(",")[0]
        oldData[name] = line
        line = f.readline()
    f.close()
    return oldData


def getNewData():
    newData = {}
    f = open("G:\merge\outInfo.csv")
    # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    while line:
        name = line.split(",")[0]
        newData[name] = line
        line = f.readline()
    f.close()
    return newData


if __name__ == '__main__':
    main()
