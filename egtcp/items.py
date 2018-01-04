# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class CompanyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = Field()
    url = Field()
    basic_info_en = Field()
    basic_info_cn = Field()
    contact_info = Field()
    certificate_info = Field()
    trade_info = Field()
    detailed_info = Field()
    todo_page_set = Field()  # 需要parse的页面set(common.PageType)
