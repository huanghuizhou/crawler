#!/usr/bin/env python3
# coding=utf-8

import sys

from scrapy import cmdline

if 'debug' in sys.argv:
    cmdline.execute("scrapy crawl global_source".split())
    quit()

cmdline.execute("scrapy crawl global_source -s JOBDIR=jobs/global-source-1".split())
