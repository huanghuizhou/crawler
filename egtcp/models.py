#!/usr/bin/env python3
# coding=utf-8


class BasicInfo(object):
    def __init__(self):
        self.name = ''
        self.registration_number = ''
        self.registration_location = ''
        self.address = ''
        self.year_established = ''
        self.date_established = ''
        self.legal_form = ''
        self.type = ''
        self.status = ''
        self.registration_agency = ''
        self.authorized_capital = ''
        self.paid_up_capital = ''
        self.legal_representatives = ''
        self.business_scope = ''
        self.business_permit_expiry = ''
        self.shareholders = []
        self.import_export_license_obtained = ''


class ContactInfo(object):
    def __init__(self):
        self.persons = []
        self.tel = ''
        self.fax = ''
        self.mobile = ''
        self.email = []
        self.website = ''

    class ContactPerson(object):
        def __init__(self):
            self.name = ''
            self.position = ''


class CertificateInfo(object):
    def __init__(self):
        self.certificate = []
        self.standard = ''
        self.issue_date = ''
        self.issue_by = ''
        self.number = ''
        self.expiry_date = ''
        self.scope = ''
        self.image_url = ''


class TradeInfo(object):
    def __init__(self):
        self.type = ''
        self.export_countries = []
        self.major_customers = []
        self.export_percentage = ''
        self.payment_method = ''
        self.total_annual_sales = ''
        self.oem_support = False
        self.sample_policy = ''
        self.warranty = ''
        self.export_import_processing_support = ''
        self.after_sales_service = ''
        self.oem_capability = ''
        self.oem_experience = ''
        self.design_service_offered = False
        self.design_service_detail = ''
        self.buyer_label_offered = False
        self.buyer_label_detail = ''
        self.material_component = ''
        self.minimum_order = ''
        self.major_market_served = ''
        self.main_oem_customers = ''


class EnterpriseDetailInfo(object):
    def __init__(self):
        self.main_product = ''
        self.description = ''
        self.total_capitalization = ''
        self.brand_name = ''
        self.bank_detail = []
        self.factory_ownership = []
        self.primary_competitive_advantage = []
        self.factory_size_in_square_meters = ''
        self.factory_size_in_square_feet = ''
        self.total_area = ''
        self.built_in_size = ''
        self.investment_on_manufacturing_equipment = ''
        self.staff_detail = []
        self.total_staff_amount = ''
        self.engineer_staff_amount = ''
        self.production_staff_amount = ''
        self.capacity = EnterpriseDetailInfo.Capacity()
        self.research_and_develop = EnterpriseDetailInfo.ResearchAndDevelop()
        self.qc = EnterpriseDetailInfo.QualityControl()
        self.trade_show = []  # models.EnterpriseDetailInfo.TradeShow

    class Capacity(object):
        def __init__(self):
            self.monthly_capacity = ''
            self.monthly_output = ''
            self.production_lines_amount = ''

    class ResearchAndDevelop(object):
        def __init__(self):
            self.rd_staff_amount = ''
            self.location = ''
            self.profile = ''
            self.equipment = ''
            self.patent = ''
            self.award = ''

    class QualityControl(object):
        def __init__(self):
            self.responsibility = []
            self.technical_support = ''
            self.staff_amount = ''
            self.equipment = ''
            self.testing_detail = ''
            self.other_info = ''

    class TradeShow(object):
        def __init__(self):
            self.name = ''
            self.location = ''
            self.date = ''
