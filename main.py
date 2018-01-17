#!/usr/bin/env python3
# coding=utf-8

from scrapy import cmdline

cmdline.execute("scrapy crawl global_source -s JOBDIR=jobs/global-source-1".split())
