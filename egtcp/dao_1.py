#!/usr/bin/env python3
# coding=utf-8


from pymongo import MongoClient

DB_NAME = 'dadaoDb'
# COLLECTION_NAME = 'GlobalSourceSuppliers'
COLLECTION_NAME_A = 'TradeWow'
COLLECTION_NAME_B = 'TradeWow_copy'

# MONGO_CLIENT_DEV = MongoClient(host='192.168.2.203', port=27017, username="gt_rw", password="greattao5877",
#                                authSource=DB_NAME,
#                                authMechanism="SCRAM-SHA-1")

MONGO_CLIENT_LOCAL = MongoClient(host='localhost', port=27017,
                                 authSource=DB_NAME)

MONGO_CLIENT_DEV = MongoClient(host='localhost', port=27017,
                               authSource=DB_NAME)

# MONGO_CLIENT_DEV = MongoClient(host='localhost', port=27017,
#                             authSource=DB_NAME)
