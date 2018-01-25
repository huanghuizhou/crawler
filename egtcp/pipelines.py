# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import logging
from datetime import datetime

from egtcp.dao import MONGO_CLIENT, COLLECTION_NAME, DB_NAME
from egtcp.utils import to_dict


class GlobalSourcePipeline(object):
    def __init__(self):
        self.client = MONGO_CLIENT
        self.collection = self.client[DB_NAME][COLLECTION_NAME]
        self.logger = logging.getLogger(__name__)

    def process_item(self, item, spider):
        current_ts = datetime.now()
        supplier_id = item['id']
        data = to_dict(dict(item))
        data['_id'] = data.pop('id')
        self.logger.debug("%s todo_page_set id == %s", item['id'], id(item['todo_page_set']))
        data['done'] = len(item['todo_page_set']) == 0
        data['update_time'] = current_ts
        del data['todo_page_set']

        data = self._clean_data(data)
        if not self.collection.find_one({'_id': supplier_id}):
            data['create_time'] = current_ts
        self.collection.replace_one({'_id': supplier_id}, data, upsert=True)
        return item

    def _clean_data(self, data):
        if isinstance(data, dict):
            for key in data.keys():
                value = self._clean_data(data[key])
                data[key] = value
            return data
        if isinstance(data, str):
            return self._clean_string(data)
        if isinstance(data, list):
            replaced_data = []
            for value in data:
                v = self._clean_data(value)
                if v:
                    replaced_data.append(v)
            return replaced_data
        return data

    def _clean_string(self, s):
        return s.strip('\r\n\t ')
