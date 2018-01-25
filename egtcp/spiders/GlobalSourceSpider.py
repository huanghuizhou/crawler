#!/usr/bin/env python3
# coding=utf-8

import re

import scrapy
from scrapy.http import Request

from egtcp import models
from egtcp.common import PageType
from egtcp.items import CompanyItem
from egtcp.utils import complete_url

REGEX_PATTERN_ID = re.compile('.*/(\d*)/Homepage.htm*')


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
        # todo 移除调试代码，调试从某个固定供应商主页进去，不过列表
        # item = CompanyItem()
        # url = 'http://epoch.manufacturer.globalsources.com/si/6008851852171/Homepage.htm'
        # item['id'] = '6008851852171'
        # item['todo_page_set'] = set()
        # item['url'] = url
        # item['basic_info_en'] = models.BasicInfo()
        # item['basic_info_cn'] = models.BasicInfo()
        # item['contact_info'] = models.ContactInfo()
        # item['certificate_info'] = models.CertificateInfo()
        # item['trade_info'] = models.TradeInfo()
        # item['detailed_info'] = models.EnterpriseDetailInfo()
        # yield scrapy.Request(url,
        #                      meta={'type': PageType.SUPPLIER_MAIN_PAGE, 'item': item})

    def parse(self, response):
        # do stuff with the logged in response
        page_type = response.meta['type']
        if page_type not in self.parse_handler_mapping:
            self.logger.error('%s handler not found', page_type)
            return

        handler = self.parse_handler_mapping[page_type]
        try:
            for result in handler(response):
                yield result
        except Exception as e:
            self.logger.error("Exception occurred in (%s): %s %s", response.url, handler.__name__, e)

    def parse_category_list(self, response):
        """
        总分类列表
        e.g. http://www.chinasuppliers.globalsources.com/SITE/top-china-suppliers.html
        :param response:
        :return:
        """
        for url in response.xpath('//a[@class="parentpt"]/@href').extract():
            yield Request(complete_url(response.url, url), meta={'type': PageType.SUB_CATEGORY_LIST})

    def parse_sub_category_list(self, response):
        """
        子分类列表
        e.g. http://www.chinasuppliers.globalsources.com/china-manufacturers/Auto-Part/3000000151248.htm
        http://www.chinasuppliers.globalsources.com/china-manufacturers/Auto-Part/3000000151248/2.htm
        :param response:
        :return:
        """
        for supplier_url in response.xpath('//a[@class="darkblue"]/@href').extract():
            yield Request(complete_url(response.url, supplier_url), meta={'type': PageType.SUPPLIER_LIST})
        page_name = response.url.rsplit('/', 1)[-1]
        name, _ = page_name.split('.')
        if len(name) > 4:
            # Page 1
            for page_url in response.xpath('//div[contains(@id, "pgSet")]/a/@href').extract():
                yield Request(complete_url(response.url, page_url), meta={'type': PageType.SUB_CATEGORY_LIST})

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

        def init_item(supplier_id):
            item = CompanyItem()
            item['id'] = supplier_id
            item['todo_page_set'] = set()
            item['basic_info_en'] = models.BasicInfo()
            item['certificate_info'] = models.CertificateInfo()
            item['basic_info_cn'] = models.BasicInfo()
            item['contact_info'] = models.ContactInfo()
            item['trade_info'] = models.TradeInfo()
            item['detailed_info'] = models.EnterpriseDetailInfo()
            return item

        # 供应商详情
        top_suppliers = response.xpath('//div[@class="tcs_supplierInfo"]/h3/a/@href').extract()
        other_suppliers = response.xpath('//div[@class="unverified_detail"]/p[1]/a/@href').extract()
        for homepage_url in top_suppliers + other_suppliers:
            item = init_item(extract_id(homepage_url))
            yield Request(complete_url(response.url, homepage_url),
                          meta={'type': PageType.SUPPLIER_MAIN_PAGE, 'item': item})

        next_page_url = response.xpath(
            '//p[@class="pagination pagination_mar"]/a[@class="nextPage"]/@href').extract_first()
        if next_page_url:
            yield Request(complete_url(response.url, next_page_url),
                          meta={'type': PageType.SUPPLIER_LIST})

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
        basic_info_cn.name = response.xpath(
            '//div[@class="spSnaSection"]/p/em[text()[contains(.,"Registered Company:")]]/parent::node()/a/text()').extract_first()
        basic_info_cn.registration_number = response.xpath(
            '//div[@class="spSnaSection"]/p/em[text()[contains(.,"Registration Number: ")]]/parent::node()/text()') \
            .extract_first()
        basic_info_cn.registration_location = response.xpath(
            '//div[@class="spSnaSection"]/p/em[text()[contains(.,"Company Registration Address: ")]]/parent::node()/text()') \
            .extract_first()

        basic_info_en = item['basic_info_en']
        basic_info_en.name = response.xpath('//div[@class="spCompanyInfo fl"]/p[1]/text()').extract_first()
        basic_info_en.address = response.xpath(
            '//div[@class="spCompanyInfo fl"]/address/span/text()').extract_first()
        basic_info_en.registration_number = basic_info_cn.registration_number

        # other sub page link
        todo_page_set = item['todo_page_set']
        request_list = []
        company_profile_url = self._extract_sub_page_url_from_nav(response, 'Company Information')
        if company_profile_url:
            todo_page_set.add(PageType.SUPPLIER_COMPANY_PROFILE)
            request_list.append(Request(complete_url(response.url, company_profile_url),
                                        meta={'type': PageType.SUPPLIER_COMPANY_PROFILE, 'item': item}))
        trade_show_url = self._extract_sub_page_url_from_nav(response, 'Trade Show')
        if trade_show_url:
            todo_page_set.add(PageType.SUPPLIER_TRADE_SHOW)
            request_list.append(Request(complete_url(response.url, trade_show_url),
                                        meta={'type': PageType.SUPPLIER_TRADE_SHOW, 'item': item}))
        credit_profile_url = self._extract_sub_page_url(response, 'Business Registration Profile')
        if credit_profile_url:
            todo_page_set.add(PageType.SUPPLIER_CREDIT_PROFILE)
            request_list.append(Request(complete_url(response.url, credit_profile_url),
                                        meta={'type': PageType.SUPPLIER_CREDIT_PROFILE, 'item': item}))
        service_url = self._extract_sub_page_url(response, 'Services and Support')
        if service_url:
            todo_page_set.add(PageType.SUPPLIER_SERVICE)
            request_list.append(Request(complete_url(response.url, service_url),
                                        meta={'type': PageType.SUPPLIER_SERVICE, 'item': item}))
        certification_url = self._extract_sub_page_url(response, 'Certifications')
        if certification_url:
            todo_page_set.add(PageType.SUPPLIER_CERTIFICATE)
            request_list.append(Request(complete_url(response.url, certification_url),
                                        meta={'type': PageType.SUPPLIER_CERTIFICATE, 'item': item}))
        factory_tour_url = self._extract_sub_page_url(response, 'Factory Tour')
        if factory_tour_url:
            todo_page_set.add(PageType.SUPPLIER_FACTORY)
            request_list.append(Request(complete_url(response.url, factory_tour_url),
                                        meta={'type': PageType.SUPPLIER_FACTORY, 'item': item}))
        rnd_url = self._extract_sub_page_url(response, 'Research and Development')
        if rnd_url:
            todo_page_set.add(PageType.SUPPLIER_R_D)
            request_list.append(
                Request(complete_url(response.url, rnd_url), meta={'type': PageType.SUPPLIER_R_D, 'item': item}))
        oem_url = self._extract_sub_page_url(response, 'OEM/ODM')
        if oem_url:
            todo_page_set.add(PageType.SUPPLIER_OEM)
            request_list.append(
                Request(complete_url(response.url, oem_url), meta={'type': PageType.SUPPLIER_OEM, 'item': item}))
        qc_url = self._extract_sub_page_url(response, 'Quality Control')
        if qc_url:
            todo_page_set.add(PageType.SUPPLIER_QC)
            request_list.append(
                Request(complete_url(response.url, qc_url), meta={'type': PageType.SUPPLIER_QC, 'item': item}))

        for req in request_list:
            yield req
        self.logger.debug("%s todo_page_set id == %s", item['id'], id(item['todo_page_set']))
        yield item

    def parse_supplier_company_profile(self, response):
        """
        e.g. http://cmac.manufacturer.globalsources.com/si/6008839396424/CompanyProfile.htm
        :param response:
        :return:
        """

        item = response.meta['item']

        trade_info = item['trade_info']
        trade_info.export_countries = self._extract_info_list(response, 'Past Export Markets/Countries:')
        trade_info.major_customers = self._extract_info_list(response, 'Major Customers:')
        trade_info.oem_support = self._extract_info(response, 'OEM Services:')
        trade_info.total_annual_sales = self._extract_info(response, 'Total Annual Sales:')
        trade_info.payment_method = self._extract_info(response, 'Payment Method:')
        trade_info.export_percentage = self._extract_info(response, 'Export Percentage:')

        basic_info_cn = item['basic_info_cn']
        basic_info_cn.year_established = self._extract_info(response, 'Year Established:')

        basic_info_en = item['basic_info_en']
        basic_info_en.year_established = basic_info_cn.year_established
        basic_info_en.type = self._extract_info_list(response, 'Business Type:')

        detailed_info = item['detailed_info']
        detailed_info.total_staff_amount = self._extract_info(response, 'No. of Total Staff:')
        detailed_info.engineer_staff_amount = self._extract_info(response, 'No. of Engineers:')
        detailed_info.total_capitalization = self._extract_info(response, 'Total Capitalization:')
        detailed_info.brand_name = self._extract_info(response, 'Brand Names:')
        detailed_info.bank_detail = self._extract_info_list(response, 'Bank Details:')
        detailed_info.factory_ownership = self._extract_info_list(response, 'Factory Ownership:')
        detailed_info.capacity.production_lines_amount = self._extract_info(response, 'No. of Production Lines:')
        detailed_info.capacity.monthly_capacity = self._extract_info(response, 'Monthly capacity:')
        detailed_info.research_and_develop.rd_staff_amount = self._extract_info(response, 'No. of R&D Staff:')
        detailed_info.primary_competitive_advantage = self._extract_info_list(response,
                                                                              'Primary Competitive Advantages:')
        detailed_info.factory_size_in_square_meters = self._extract_info(response, 'Factory Size in Square Meters:')
        detailed_info.investment_on_manufacturing_equipment = self._extract_info(response,
                                                                                 'Investment on Manufacturing Equipment:')
        detailed_info.qc.responsibility = self._extract_info_list(response, 'QC Responsibility:')

        certificate_info = item['certificate_info']
        certificate_info.certificate = response.xpath(
            '//p[@class="fl c6 proDetTit" and text()="Certifications:"]/following-sibling::div/ul/li/text()[1]').extract()
        self.logger.debug("%s todo_page_set id == %s", item['id'], id(item['todo_page_set']))
        item['todo_page_set'].remove(PageType.SUPPLIER_COMPANY_PROFILE)
        yield item

    def parse_supplier_credit_profile(self, response):
        """
        e.g. http://cmac.manufacturer.globalsources.com/si/6008839396424/CreditProfile.htm
        :param response:
        :return:
        """
        item = response.meta['item']
        basic_info_en = item['basic_info_en']
        basic_info_en.registration_location = self._extract_info(response, 'Registered Address:')
        basic_info_en.date_established = self._extract_info(response, 'Incorporation Date:')
        basic_info_en.legal_form = self._extract_info(response, 'Legal Form:')
        basic_info_en.status = self._extract_info(response, 'Company Status:')
        basic_info_en.registration_agency = self._extract_info(response, 'Registration Agency:')
        basic_info_en.registration_number = self._extract_info(response, 'Registration Number:')
        basic_info_en.authorized_capital = self._extract_info(response, 'Authorized Capital:')
        basic_info_en.paid_up_capital = self._extract_info(response, 'Paid-Up Capital:')
        basic_info_en.legal_representatives = self._extract_info(response, 'Legal Representatives:')
        basic_info_en.import_export_license_obtained = self._extract_info(response,
                                                                          'Import & Export Licences Obtained:')
        basic_info_en.business_permit_expiry = self._extract_info(response, 'Business Permit Expiry:')
        basic_info_en.shareholders = self._extract_info_list(response, 'Shareholders:')
        basic_info_en.business_scope = self._extract_info(response, 'Business Scope:')

        self.logger.debug("%s todo_page_set id == %s", item['id'], id(item['todo_page_set']))
        item['todo_page_set'].remove(PageType.SUPPLIER_CREDIT_PROFILE)
        yield item

    def parse_supplier_service(self, response):
        """
        http://xmzhxi.manufacturer.globalsources.com/si/6008800522305/Services.htm
        :param response:
        :return:
        """
        item = response.meta['item']

        trade_info = item['trade_info']
        trade_info.sample_policy = self._extract_info(response, 'Sample Availability & Policy:')
        trade_info.warranty = self._extract_info(response, 'Guarantees/Warranties/Terms and Conditions:')
        trade_info.export_import_processing_support = self._extract_info(response, 'Export/Import Processing Support:')
        trade_info.after_sales_service = self._extract_info(response, 'After Sales Service:')
        self.logger.debug("%s todo_page_set id == %s", item['id'], id(item['todo_page_set']))
        item['todo_page_set'].remove(PageType.SUPPLIER_SERVICE)
        yield item

    def parse_supplier_certificate(self, response):
        """
        http://cmac.manufacturer.globalsources.com/si/6008839396424/Certifications.htm
        :param response:
        :return:
        """

        def extract_info(text):
            xpath = '//span[@class="proCatVerfied_sub" and text()="%s"]/following-sibling::span/text()' % text
            return response.xpath(xpath).extract_first()

        item = response.meta['item']

        certificate_info = item['certificate_info']
        certificate_info.standard = extract_info('Certificate Standard:')
        certificate_info.issue_date = extract_info('Issue Date:')
        certificate_info.issue_by = extract_info('Issued By:')
        certificate_info.number = extract_info('Number:')
        certificate_info.expiry_date = extract_info('Expiry Date:')
        certificate_info.scope = extract_info('Scope/Range:')
        certificate_info.image_url = response.xpath(
            '//i[@class="picBigIcon"]/preceding-sibling::img/@src').extract_first()
        self.logger.debug("%s todo_page_set id == %s", item['id'], id(item['todo_page_set']))
        item['todo_page_set'].remove(PageType.SUPPLIER_CERTIFICATE)
        yield item

    def parse_supplier_factory(self, response):
        """
        http://jingjintech.manufacturer.globalsources.com/si/6008852333064/FactoryTour.htm
        :param response:
        :return:
        """
        item = response.meta['item']

        detailed_info = item['detailed_info']
        detailed_info.total_area = self._extract_info(response, 'Total area of:')
        detailed_info.built_in_size = self._extract_info(response, 'Built in:')
        detailed_info.production_staff_amount = self._extract_info(response, 'Production Staff:')
        detailed_info.qc.staff_amount = self._extract_info(response, 'QC Staff:')
        detailed_info.research_and_develop.rd_staff_amount = self._extract_info(response, 'R&D Staff:')
        self.logger.debug("%s todo_page_set id == %s", item['id'], id(item['todo_page_set']))
        item['todo_page_set'].remove(PageType.SUPPLIER_FACTORY)
        yield item

    def parse_supplier_r_d(self, response):
        """
        http://xmzhxi.manufacturer.globalsources.com/si/6008800522305/RnD.htm
        :param response:
        :return:
        """
        item = response.meta['item']

        detailed_info = item['detailed_info']
        detailed_info.research_and_develop.location = self._extract_info(response, 'Locations:')
        detailed_info.research_and_develop.profile = self._extract_info(response, 'Profile:')
        detailed_info.research_and_develop.equipment = self._extract_info(response, 'Machinery/Equipment for R&D:')
        detailed_info.research_and_develop.patent = self._extract_info(response, 'Patents & Copyrights:')
        detailed_info.research_and_develop.award = self._extract_info(response, 'Awards & Other Recognitions:')
        self.logger.debug("%s todo_page_set id == %s", item['id'], id(item['todo_page_set']))
        item['todo_page_set'].remove(PageType.SUPPLIER_R_D)
        yield item

    def parse_supplier_oem(self, response):
        """
        http://xmzhxi.manufacturer.globalsources.com/si/6008800522305/OEM.htm
        :param response:
        :return:
        """
        item = response.meta['item']

        trade_info = item['trade_info']
        trade_info.oem_capability = self._extract_info(response, 'OEM/ODM Capability:')
        trade_info.oem_experience = self._extract_info(response, 'Years of OEM/ODM Experience:')
        trade_info.design_service_offered = self._extract_info(response, 'Design Services Offered:')
        trade_info.design_service_detail = self._extract_info(response, 'Details of Design Services Offered:')
        trade_info.buyer_label_offered = self._extract_info(response, 'Buyer Label Offered:')
        trade_info.buyer_label_detail = self._extract_info(response, 'Details of Buyer Label Offered:')
        trade_info.material_component = self._extract_info(response, 'Materials/Components:')
        trade_info.minimum_order = self._extract_info(response, 'Minimum Order')
        trade_info.major_market_served = self._extract_info_list(response, 'Major Markets Served:')
        trade_info.main_oem_customers = self._extract_info(response, 'Main OEM/ODM Customers:')

        detailed_info = item['detailed_info']
        detailed_info.factory_size_in_square_meters = self._extract_info(response, 'Size of Factory in Square Meters:')
        detailed_info.factory_size_in_square_feet = self._extract_info(response, 'Factory Size in Square Feet:')
        detailed_info.staff_detail = self._extract_info_list(response, 'Staff Details:')
        detailed_info.capacity.monthly_capacity = self._extract_info(response, 'Monthly Capacity:')
        detailed_info.capacity.monthly_output = self._extract_info(response, 'Monthly Output:')
        self.logger.debug("%s todo_page_set id == %s", item['id'], id(item['todo_page_set']))
        item['todo_page_set'].remove(PageType.SUPPLIER_OEM)
        yield item

    def parse_supplier_qc(self, response):
        """
        http://xmzhxi.manufacturer.globalsources.com/si/6008800522305/QC.htm
        :param response:
        :return:
        """
        item = response.meta['item']

        detailed_info = item['detailed_info']
        detailed_info.qc.technical_support = self._extract_info(response, 'QC/Technical Support:')
        detailed_info.qc.staff_amount = self._extract_info(response, 'QC Staff:')
        detailed_info.qc.equipment = self._extract_info(response, 'Materials/Components:')
        detailed_info.qc.testing_detail = self._extract_info(response, 'Procedures/testing Details:')
        detailed_info.qc.other_info = self._extract_info(response, 'Other Information:')
        self.logger.debug("%s todo_page_set id == %s", item['id'], id(item['todo_page_set']))
        item['todo_page_set'].remove(PageType.SUPPLIER_QC)
        yield item

    def parse_supplier_trade_show(self, response):
        """
        http://xmzhxi.manufacturer.globalsources.com/si/6008800522305/trade_show.htm
        :param response:
        :return:
        """

        def extract_info(text):
            xpath = 'div/div/p[text()[contains(.,"%s")]]/following-sibling::p/text()' % text
            return selector.xpath(xpath).extract_first()

        item = response.meta['item']

        detailed_info = item['detailed_info']
        for selector in response.xpath('//div[@class[contains(.,"proDetCont mt10")]]'):
            trade_show = models.EnterpriseDetailInfo.TradeShow()
            trade_show.name = extract_info('Trade Show')
            trade_show.location = extract_info('Location/Venue')
            trade_show.date = extract_info('Show Date')
            detailed_info.trade_show.append(trade_show)
        self.logger.debug("%s todo_page_set id == %s", item['id'], id(item['todo_page_set']))
        item['todo_page_set'].remove(PageType.SUPPLIER_TRADE_SHOW)
        yield item

    def _extract_info(self, response, text):
        """
        详情页，单行普通文本
        :param response:
        :param text:
        :return:
        """
        xpath = '//p[@class="fl c6 proDetTit" and text()="%s"]/following-sibling::*//text()' % text
        return response.xpath(xpath).extract_first()

    def _extract_info_list(self, response, text):
        """
        详情页，多行普通文本
        :param response:
        :param text:
        :return:
        """
        xpath = '//p[@class="fl c6 proDetTit" and text()="%s"]/following-sibling::*//text()' % text
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
