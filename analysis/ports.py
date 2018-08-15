#!/usr/bin/env python3
# coding=utf-8

import json
from collections import defaultdict

s = """GBFEL1	USLOB	MXVER	JPOSK	KWKUW	UAYAL	PAMAN	BERNE																																																																																																																																																																																			
1	2	1	2	1	1	2	1																																																																																																																																																																																			
"""

data = json.load(open('./port.json',encoding='UTF-8'))
code_mapping = {x['portCode']: x for x in data}
name_mapping = {x['portEnName']: x for x in data}

s0, s1 = s.strip('\n').split('\n')
ports = s0.split('\t')
amounts = s1.split('\t')

country_mapping = defaultdict(float)
for idx, name in enumerate(ports):
    if name in code_mapping:
        port = code_mapping[name]
    elif name in name_mapping:
        port = name_mapping[name]
    else:
        continue

    country_mapping[port['countryCode']] += float(amounts[idx])

# print(json.dumps(country_mapping, indent=4, ensure_ascii=False))
sorted_list = [(k, country_mapping[k]) for k in sorted(country_mapping, key=country_mapping.get, reverse=True)]
print(sorted_list)
print()
print('\t'.join((x[0] for x in sorted_list)))
print('\t'.join((str(x[1]) for x in sorted_list)))
