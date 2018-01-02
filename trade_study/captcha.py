#!/usr/bin/env python3
# coding=utf-8


import string
from PIL import Image
from pytesseract import image_to_string


def init_table(threshold=140):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    return table


def parse_captcha(file):
    im = Image.open(file)
    im = im.convert('L')
    im = im.point(init_table(100), '1')
    # im.show()
    return image_to_string(im, config='-psm 6 -c tessedit_char_whitelist=' + string.ascii_uppercase + string.digits)
