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
        # for url in self.start_urls:
        #     yield scrapy.Request(url, meta={'type': PageType.CATEGORY_LIST})
        # todo 移除调试代码，调试从某个固定供应商主页进去，不过列表
        item = CompanyItem()
        url = 'http://hebeileader.manufacturer.globalsources.com/si/6008841464350/Homepage.htm'
        item['id'] = '6008841464350'
        item['url'] = url
        item['basic_info_en'] = models.BasicInfo()
        item['basic_info_cn'] = models.BasicInfo()
        item['contact_info'] = models.ContactInfo()
        item['certificate_info'] = models.CertificateInfo()
        item['trade_info'] = models.TradeInfo()
        item['detailed_info'] = models.EnterpriseDetailInfo()
        yield scrapy.Request(url,
                             meta={'type': PageType.SUPPLIER_MAIN_PAGE, 'item': item})

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
            self.logger.error("Exception occurred in %s %s", handler.__name__, e)

    def parse_category_list(self, response):
        """
        总分类列表
        e.g. http://www.chinasuppliers.globalsources.com/SITE/top-china-suppliers.html
        :param response:
        :return:
        """
        for url in response.xpath('//a[@class="parentpt"]/@href').extract():
            yield Request(url, meta={'type': PageType.SUB_CATEGORY_LIST})

    def parse_sub_category_list(self, response):
        """
        子分类列表
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
        供应商列表
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
            basic_info_en.registration_location = supplier_selector.xpath('p[@class="mt15"]/text()').extract()
            basic_info_en.type = supplier_selector.xpath(
                'p[@class="mt5"]/span[text()[contains(.,"Business Type:")]]/parent::node()/text()').extract()
            basic_info_en.business_scope = ','.join(supplier_selector.xpath(
                'p[@class="mt5"]/span[text()[contains(.,"Main Products:")]]/parent::node()/a/text()').extract())
            item['basic_info_en'] = basic_info_en

            certificate_info = models.CertificateInfo()
            certificate_info.certificate = ''.join(supplier_selector.xpath(
                'p[@class="mt5"]/span[text()[contains(.,"Company Cert:")]]/parent::node()/text()').extract())
            item['certificate_info'] = certificate_info

            item['basic_info_cn'] = models.BasicInfo()
            item['contact_info'] = models.ContactInfo()
            item['trade_info'] = models.TradeInfo()
            item['detailed_info'] = models.EnterpriseDetailInfo()
            yield Request(homepage_url, meta={'type': PageType.SUPPLIER_MAIN_PAGE, 'item': item})

    def parse_supplier_main_page(self, response):
        """
        供应商主页
        e.g. http://hkaa.manufacturer.globalsources.com/si/6008839515551/Homepage.htm
        :param response:
        :return:
        """
        item = response.meta['item']
        item['url'] = response.url

        contact_info = item['contact_info']
        contact_persons = response.xpath('//div[@class="csSec "]/p/text()').extract()
        contact_persons = [x.strip() for x in contact_persons if len(x.strip()) > 0]
        for i in range(0, len(contact_persons), 2):
            name = contact_persons[i]
            position = contact_persons[i + 1] if i + 1 < len(contact_persons) else ''
            if len(name.strip()) == 0:
                continue
            person = models.ContactInfo.ContactPerson()
            person.name = name
            person.position = position
            contact_info.persons.append(person)
        contact_info.tel = response.xpath(
            '//div[@class="spCompanyInfo fl"]/p/em[text()[contains(.,"Tel: ")]]/parent::node()/text()') \
            .extract_first()
        contact_info.fax = response.xpath(
            '//div[@class="spCompanyInfo fl"]/p/em[text()[contains(.,"Fax: ")]]/parent::node()/text()') \
            .extract_first()
        contact_info.mobile = response.xpath(
            '//div[@class="spCompanyInfo fl"]/p/em[text()[contains(.,"Mobile: ")]]/parent::node()/text()') \
            .extract_first()
        contact_info.website = response.xpath(
            '//div[@class="spCompanyInfo fl"]/p/em[text()[contains(.,"Other Homepage Address: ")]]/parent::node()/text()') \
            .extract_first()
        contact_info.email = response.xpath('//div[@class="clearfix contDetEmail"]/ul/li/img/@src').extract()

        detailed_info = item['detailed_info']
        detailed_info.description = ''.join(response.xpath('//div[@id="allContent"]/child::node()').extract())

        basic_info_cn = item['basic_info_cn']
        basic_info_cn.name = response.xpath('//div[@class="spSnaSection"]/p/a/text()').extract_first()
        basic_info_cn.registration_number = response.xpath(
            '//div[@class="spSnaSection"]/p/em[text()[contains(.,"Registration Number: ")]]/parent::node()/text()') \
            .extract_first()
        basic_info_cn.registration_location = response.xpath(
            '//div[@class="spSnaSection"]/p/em[text()[contains(.,"Company Registration Address: ")]]/parent::node()/text()') \
            .extract_first()

        basic_info_en = item['basic_info_en']
        basic_info_en.name = response.xpath('//div[@class="spCompanyInfo fl"]/p[1]/text()').extract_first()
        basic_info_en.registration_location = response.xpath(
            '//div[@class="spCompanyInfo fl"]/address/span/text()').extract_first()
        basic_info_en.registration_number = basic_info_cn.registration_number

        # other sub page link
        company_profile_url = self._extract_sub_page_url_from_nav(response, 'Company Information')
        if company_profile_url:
            yield Request(company_profile_url, meta={'type': PageType.SUPPLIER_COMPANY_PROFILE, 'item': item})
        trade_show_url = self._extract_sub_page_url_from_nav(response, 'Trade Show')
        if trade_show_url:
            yield Request(trade_show_url, meta={'type': PageType.SUPPLIER_TRADE_SHOW, 'item': item})
        credit_profile_url = self._extract_sub_page_url(response, 'Business Registration Profile')
        if credit_profile_url:
            yield Request(credit_profile_url, meta={'type': PageType.SUPPLIER_CREDIT_PROFILE, 'item': item})
        service_url = self._extract_sub_page_url(response, 'Services and Support')
        if service_url:
            yield Request(service_url, meta={'type': PageType.SUPPLIER_SERVICE, 'item': item})
        certification_url = self._extract_sub_page_url(response, 'Certifications')
        if certification_url:
            yield Request(certification_url, meta={'type': PageType.SUPPLIER_CERTIFICATE, 'item': item})
        factory_tour_url = self._extract_sub_page_url(response, 'Factory Tour')
        if factory_tour_url:
            yield Request(factory_tour_url, meta={'type': PageType.SUPPLIER_FACTORY, 'item': item})
        rnd_url = self._extract_sub_page_url(response, 'Research and Development')
        if rnd_url:
            yield Request(rnd_url, meta={'type': PageType.SUPPLIER_R_D, 'item': item})
        oem_url = self._extract_sub_page_url(response, 'OEM/ODM')
        if oem_url:
            yield Request(oem_url, meta={'type': PageType.SUPPLIER_OEM, 'item': item})
        qc_url = self._extract_sub_page_url(response, 'Quality Control')
        if qc_url:
            yield Request(qc_url, meta={'type': PageType.SUPPLIER_QC, 'item': item})
        yield item

    def parse_supplier_company_profile(self, response):
        """
        e.g. http://cmac.manufacturer.globalsources.com/si/6008839396424/CompanyProfile.htm
        :param response:
        :return:
        """

        item = response.meta['item']

        trade_info = item['trade_info']
        trade_info.export_countries = self._extract_info_list_ul_li(response, 'Past Export Markets/Countries:')
        trade_info.major_customers = self._extract_info_list_p(response, 'Major Customers:')
        trade_info.oem_support = self._extract_info(response, 'OEM Services:')
        trade_info.total_annual_sales = self._extract_info(response, 'Total Annual Sales:')
        trade_info.payment_method = self._extract_info(response, 'Payment Method:')
        trade_info.export_percentage = self._extract_info(response, 'Export Percentage:')

        basic_info_cn = item['basic_info_cn']
        basic_info_cn.year_established = self._extract_info(response, 'Year Established:')

        basic_info_en = item['basic_info_en']
        basic_info_en.year_established = basic_info_cn.year_established

        detailed_info = item['detailed_info']
        detailed_info.total_staff_amount = self._extract_info(response, 'No. of Total Staff:')
        detailed_info.engineer_staff_amount = self._extract_info(response, 'No. of Engineers:')
        detailed_info.total_capitalization = self._extract_info(response, 'Total Capitalization:')
        detailed_info.brand_name = self._extract_info(response, 'Brand Names:')
        detailed_info.factory_ownership = self._extract_info(response, 'Factory Ownership:')
        detailed_info.capacity.production_lines_amount = self._extract_info(response, 'No. of Production Lines:')
        detailed_info.capacity.monthly_capacity = self._extract_info(response, 'Monthly capacity:')
        detailed_info.researchAndDevelop.rd_staff_amount = self._extract_info(response, 'No. of R&D Staff:')
        detailed_info.primary_competitive_advantage = self._extract_info_list_p(response,
                                                                                'Primary Competitive Advantages:')
        detailed_info.factory_size_in_square_meters = self._extract_info(response, 'Factory Size in Square Meters:')
        detailed_info.investment_on_manufacturing_equipment = self._extract_info(response,
                                                                                 'Investment on Manufacturing Equipment:')
        detailed_info.qc.responsibility = self._extract_info(response, 'QC Responsibility:')

        certificate_info = item['certificate_info']
        certificate_info.export_countries = response.xpath(
            '//p[@class="fl c6 proDetTit" and text()="Certifications:"]/following-sibling::div/ul/li/text()[1]').extract()
        yield item

    def parse_supplier_credit_profile(self, response):
        """
        e.g. http://cmac.manufacturer.globalsources.com/si/6008839396424/CreditProfile.htm
        :param response:
        :return:
        """

        return []

    def parse_supplier_service(self, response):
        """
        http://xmzhxi.manufacturer.globalsources.com/si/6008800522305/Services.htm
        :param response:
        :return:
        """
        return []

    def parse_supplier_certificate(self, response):
        """
        http://cmac.manufacturer.globalsources.com/si/6008839396424/Certifications.htm
        :param response:
        :return:
        """
        return []

    def parse_supplier_factory(self, response):
        """
        http://jingjintech.manufacturer.globalsources.com/si/6008852333064/FactoryTour.htm
        :param response:
        :return:
        """
        return []

    def parse_supplier_r_d(self, response):
        """
        http://xmzhxi.manufacturer.globalsources.com/si/6008800522305/RnD.htm
        :param response:
        :return:
        """
        return []

    def parse_supplier_oem(self, response):
        """
        http://xmzhxi.manufacturer.globalsources.com/si/6008800522305/OEM.htm
        :param response:
        :return:
        """
        return []

    def parse_supplier_qc(self, response):
        """
        http://xmzhxi.manufacturer.globalsources.com/si/6008800522305/QC.htm
        :param response:
        :return:
        """
        return []

    def parse_supplier_trade_show(self, response):
        """
        http://xmzhxi.manufacturer.globalsources.com/si/6008800522305/TradeShow.htm
        :param response:
        :return:
        """
        return []

    def _extract_info(self, response, text):
        """
        详情页，单行普通文本
        :param response:
        :param text:
        :return:
        """
        xpath = '//p[@class="fl c6 proDetTit" and text()="%s"]/following-sibling::div/text()' % text
        return response.xpath(xpath).extract_first()

    def _extract_info_list_p(self, response, text):
        """
        详情页，多行普通文本
        :param response:
        :param text:
        :return:
        """
        xpath = '//p[@class="fl c6 proDetTit" and text()="%s"]/following-sibling::div/p/text()' % text
        return response.xpath(xpath).extract()

    def _extract_info_list_ul_li(self, response, text):
        """
        详情页，包裹在UL/LI里的文本
        :param response:
        :param text:
        :return:
        """
        xpath = '//p[@class="fl c6 proDetTit" and text()="%s"]/following-sibling::div/ul/li/text()' % text
        return response.xpath(xpath).extract()

    def _extract_sub_page_url(self, response, text):
        """
        导航栏悬停菜单
        :param response:
        :param text:
        :return:
        """
        xpath = '//ul[@class="navL2 navInfoList dotList"]/li/a[text()[contains(.,"%s")]]/@href' % text
        return response.xpath(xpath).extract_first()

    def _extract_sub_page_url_from_nav(self, response, text):
        """
        导航栏本身
        :param response:
        :param text:
        :return:
        """
        xpath = '//li/a[@class="spNavA" and text()[contains(.,"%s")]]/@href' % text
        return response.xpath(xpath).extract_first()
