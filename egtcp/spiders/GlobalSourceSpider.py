#!/usr/bin/env python3
# coding=utf-8

import re
from enum import Enum

import scrapy
from scrapy.http import Request

from egtcp import models
from egtcp.items import CompanyItem


class PageType(Enum):
    CATEGORY_LIST = 0
    SUB_CATEGORY_LIST = 1
    SUPPLIER_LIST = 2
    SUPPLIER_MAIN_PAGE = 3
    SUPPLIER_COMPANY_PROFILE = 4
    SUPPLIER_CREDIT_PROFILE = 5
    SUPPLIER_SERVICE = 6
    SUPPLIER_CERTIFICATE = 7
    SUPPLIER_FACTORY = 8
    SUPPLIER_R_D = 9
    SUPPLIER_OEM = 10
    SUPPLIER_QC = 11
    SUPPLIER_TRADE_SHOW = 12


REGEX_PATTERN_ID = re.compile('.*/si/(\d*)/Home.*')


class GlobalSourceSpider(scrapy.Spider):
    name = 'global_source'
    allowed_domains = ['globalsources.com']
    start_urls = [
        'http://www.chinasuppliers.globalsources.com/SITE/top-china-suppliers.html'
    ]
    login_url = 'https://login.globalsources.com/sso/GeneralManager?action=Login'
    login_user = 'gamespy1991@gmail.com'
    login_password = 'mAL-UwW-H3L-ch4'

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.parse_handler_mapping = {
            PageType.CATEGORY_LIST:            self.parse_category_list,
            PageType.SUB_CATEGORY_LIST:        self.parse_sub_category_list,
            PageType.SUPPLIER_LIST:            self.parse_supplier_list,
            PageType.SUPPLIER_MAIN_PAGE:       self.parse_supplier_main_page,
            PageType.SUPPLIER_COMPANY_PROFILE: self.parse_supplier_company_profile,
            PageType.SUPPLIER_CREDIT_PROFILE:  self.parse_supplier_credit_profile,
            PageType.SUPPLIER_SERVICE:         self.parse_supplier_service,
            PageType.SUPPLIER_CERTIFICATE:     self.parse_supplier_certificate,
            PageType.SUPPLIER_FACTORY:         self.parse_supplier_factory,
            PageType.SUPPLIER_R_D:             self.parse_supplier_r_d,
            PageType.SUPPLIER_OEM:             self.parse_supplier_oem,
            PageType.SUPPLIER_QC:              self.parse_supplier_qc,
            PageType.SUPPLIER_TRADE_SHOW:      self.parse_supplier_trade_show
        }

    def start_requests(self):
        # let's start by sending a first request to login page
        yield scrapy.Request(self.login_url, self.parse_login)

    def parse_login(self, response):
        # got the login page, let's fill the login form...
        data, url, method = self.fill_login_form(response, self.login_user, self.login_password)

        # ... and send a request with our login data
        return scrapy.FormRequest(url, formdata=dict(data),
                                  method=method, callback=self.start_crawl)

    def fill_login_form(self, response, username, password):
        data = {
            'FORM_ID_KEY':      response.xpath('//form/input[@name="FORM_ID_KEY"]/@value').extract_first(),
            'execute':          'Login',
            'application':      'GSOL',
            'appURL':           'http://www.globalsources.com/GeneralManager?action=ReMap&where=GoHome',
            'fromWhere':        'GSOL',
            'language':         'en',
            'fld_UserID':       username,
            'fld_UserPassword': password,
            'Remember':         'true',
            'fld_RememberMe':   'true'
        }
        url = 'https://login.globalsources.com/sso/GeneralManager?action=Login'
        method = 'POST'
        return data, url, method

    def start_crawl(self, response):
        # OK, we're in, let's start crawling the protected pages
        for url in self.start_urls:
            yield scrapy.Request(url, meta={'type': PageType.CATEGORY_LIST})

    def parse(self, response):
        # do stuff with the logged in response
        page_type = response.meta['type']
        if page_type not in self.parse_handler_mapping:
            self.logger.error('%s handler not found')
            return

        handler = self.parse_handler_mapping[page_type]
        try:
            for result in handler(response):
                yield result
        except Exception as e:
            self.logger.error("Exception occurred %s", e)

    def parse_category_list(self, response):
        """
        e.g. http://www.chinasuppliers.globalsources.com/SITE/top-china-suppliers.html
        :param response:
        :return:
        """
        for url in response.xpath('//a[@class="parentpt"]/@href').extract():
            yield Request(url, meta={'type': PageType.SUB_CATEGORY_LIST})

    def parse_sub_category_list(self, response):
        """
        e.g. http://www.chinasuppliers.globalsources.com/china-manufacturers/Auto-Part/3000000151248.htm
        http://www.chinasuppliers.globalsources.com/china-manufacturers/Auto-Part/3000000151248/2.htm
        :param response:
        :return:
        """
        for supplier_url in response.xpath('//a[@class="darkblue"]/@href').extract():
            yield Request(supplier_url, meta={'type': PageType.SUPPLIER_LIST})
        page_name = response.url.rsplit('/', 1)[-1]
        name, _ = page_name.split('.')
        if len(name) > 4:
            # Page 1
            for page_url in response.xpath('//div[contains(@id, "pgSet")]/a/@href').extract():
                yield Request(page_url, meta={'type': PageType.SUB_CATEGORY_LIST})

    def parse_supplier_list(self, response):
        """
        e.g. http://www.chinasuppliers.globalsources.com/china-suppliers/07-Strut-Bar.htm
        :param response:
        :return:
        """

        def extract_id(url):
            m = REGEX_PATTERN_ID.match(url)
            if m is None:
                raise RuntimeError("Cannot extract id from homepage url " + url)
            return m.group(1)

        for supplier_selector in response.xpath('//div[@class="tcs_supplierInfo"]'):
            item = CompanyItem()
            homepage_url = supplier_selector.xpath('h3[@class="title"]/a/@href').extract_first()
            item['id'] = extract_id(homepage_url)

            basic_info_en = models.BasicInfo()
            basic_info_en.name = supplier_selector.xpath('h3[@class="title"]/a/@title').extract_first()
            basic_info_en.registration_location = supplier_selector.xpath('p[@class="mt15"]/text()').extract()[
                -1].strip()
            basic_info_en.type = supplier_selector.xpath(
                'p[@class="mt5"]/span[text()[contains(.,"Business Type:")]]/parent::node()/text()').extract()[
                -1].strip()
            basic_info_en.business_scope = ','.join(supplier_selector.xpath(
                'p[@class="mt5"]/span[text()[contains(.,"Main Products:")]]/parent::node()/a/text()').extract())
            item['basic_info_en'] = basic_info_en

            certificate_info = models.CertificateInfo()
            certificate_info.certificate = ''.join(supplier_selector.xpath(
                'p[@class="mt5"]/span[text()[contains(.,"Company Cert:")]]/parent::node()/text()').extract()).strip()
            item['certificate_info'] = certificate_info

            item['contact_info'] = models.ContactInfo()
            item['trade_info'] = models.TradeInfo()
            item['detailed_info'] = models.EnterpriseDetailInfo()
            yield Request(homepage_url, meta={'type': PageType.SUPPLIER_MAIN_PAGE, 'item': item})

    def parse_supplier_main_page(self, response):
        """
        e.g. http://hkaa.manufacturer.globalsources.com/si/6008839515551/Homepage.htm
        :param response:
        :return:
        """
        item = response.meta['item']

        contact_info = item['contact_info']
        contact_persons = response.xpath('//div[@class="csSec "]/p/text()').extract()
        for i in range(0, len(contact_persons), 2):
            name = contact_persons[i]
            position = contact_persons[i + 1]
            if len(name.strip()) == 0:
                continue
            person = models.ContactInfo.ContactPerson()
            person.name = name
            person.position = position
            contact_info.persons.append(person)

        yield item

    def parse_supplier_company_profile(self, response):
        return []

    def parse_supplier_credit_profile(self, response):
        return []

    def parse_supplier_service(self, response):
        return []

    def parse_supplier_certificate(self, response):
        return []

    def parse_supplier_factory(self, response):
        return []

    def parse_supplier_r_d(self, response):
        return []

    def parse_supplier_oem(self, response):
        return []

    def parse_supplier_qc(self, response):
        return []

    def parse_supplier_trade_show(self, response):
        return []
