#!/usr/bin/env python3
# coding=utf-8

import datetime

from pymongo import MongoClient

# a = {
#     1: 1,
#     2: 2,
#     3: {
#         4: 4,
#         5: {
#             6: 6
#         }
#     }
# }
#
# b = {
#     3: {
#         4: 40,
#         5: {
#             6: 60,
#             7: 7
#         }
#     }
# }
#
# deep_merge_dict(b, a)
# pprint.pprint(a, indent=4)

client = MongoClient(host='192.168.2.203', port=27017, username="gt_rw", password="greattao5877", authSource="dadaoDb",
                     authMechanism="SCRAM-SHA-1")
db = client['dadaoDb']
collection = db['test1']
post = {
    "_id": "1233",
    "author": "Mike",
    "text": "My first blog post!",
    "tags": ["mongodb", "python", "pymongo", "123"],
    "date": datetime.datetime.utcnow()
}

# doc = collection.replace_one({'_id': '1233'}, post, upsert=True)
doc = collection.find_one({'_id': '6008847958405'})
print(doc)
