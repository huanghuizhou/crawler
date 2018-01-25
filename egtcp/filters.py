#!/usr/bin/env python3
# coding=utf-8

import logging

from scrapy.dupefilters import BaseDupeFilter

from egtcp.dao import MONGO_CLIENT, DB_NAME, DUPL_COLLECTION_NAME


class DupFilterInMongo(BaseDupeFilter):

    def __init__(self, debug=False):
        self.client = MONGO_CLIENT
        self.collection = MONGO_CLIENT[DB_NAME][DUPL_COLLECTION_NAME]
        self.logdupes = True
        self.debug = debug
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_settings(cls, settings):
        debug = settings.getbool('DUPEFILTER_DEBUG')
        return cls(debug)

    def request_seen(self, request):
        """
        duplicate structure:
        {
            'url': duplicated url,
            'referrers': [referrer1, referrer2, ...]
        }
        :param request:
        :return:
        """
        if 'china' not in request.url:
            return False

        duplicate = self.collection.find_one({'url': request.url})
        referer = request.headers.get('Referer')
        if referer:
            referer = referer.decode('utf-8')
        if not duplicate:
            duplicate = {
                'url':      request.url,
                'referers': [referer],
            }
            self.collection.insert_one(duplicate)
            return False
        duplicate['referers'].append(referer)
        self.collection.replace_one({'url': request.url}, duplicate)
        return True

    def log(self, request, spider):
        if self.debug:
            msg = "Filtered duplicate request: %(request)s"
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
        elif self.logdupes:
            msg = ("Filtered duplicate request: %(request)s"
                   " - no more duplicates will be shown"
                   " (see DUPEFILTER_DEBUG to show all duplicates)")
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
            self.logdupes = False

        spider.crawler.stats.inc_value('dupefilter/filtered', spider=spider)
