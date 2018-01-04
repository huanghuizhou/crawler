# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from egtcp.dao import MONGO_CLIENT
from egtcp.utils import to_dict


class GlobalSourcePipeline(object):
    def __init__(self):
        self.client = MONGO_CLIENT
        self.collection = self.client['dadaoDb']['test1']

    def process_item(self, item, spider):
        supplier_id = item['id']
        data = to_dict(dict(item))
        data['_id'] = data.pop('id')
        data['done'] = False
        del data['todo_page_set']

        supplier = self.collection.find_one({'_id': supplier_id})
        if not supplier:
            self.collection.insert_one(data)
        else:
            # deep_merge_dict(data, supplier)
            if len(item['todo_page_set']) == 0:
                data['done'] = True
            self.collection.replace_one({'_id': supplier_id}, data, upsert=True)

        return item
