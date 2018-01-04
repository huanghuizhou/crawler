#!/usr/bin/env python3
# coding=utf-8

from urllib.parse import urlparse


def to_dict(obj, class_prefix=None):
    clazz = obj.__class__.__name__
    if isinstance(obj, dict):
        ret = {}
        for key, value in obj.items():
            if isinstance(value, list):
                ret[key] = [to_dict(x) for x in value]
            else:
                ret[key] = to_dict(value)
    elif ((class_prefix is None) or (class_prefix and clazz.startswith(class_prefix))) and hasattr(obj, '__dict__'):
        ret = {}
        for key, value in getattr(obj, '__dict__').items():
            if isinstance(value, list):
                ret[key] = [to_dict(x) for x in value]
            else:
                ret[key] = to_dict(value)
    else:
        ret = obj
    return ret


def deep_merge_dict(src, dest):
    """
    从src复制到dest
    对于src中到value，如果dest中不存在，直接添加；如果dest中存在，再次执行deep_merge_dict
    :param src:
    :param dest:
    :return:
    """
    if not isinstance(src, dict) or not isinstance(dest, dict):
        raise ValueError("src and dest must be dict")

    for key, value in src.items():
        if key not in dest:
            dest[key] = value
            continue
        dest_value = dest[key]
        if dest_value.__class__ != value.__class__:
            raise ValueError("field '%s' in src and dest must be of the same type", key)

        if isinstance(value, dict):
            deep_merge_dict(value, dest_value)
        else:
            dest[key] = value


def complete_url(page, target_url):
    """
    拼接完整URL（如果缺scheme和host）
    :param page: 所在页面URL
    :param target_url: 目标URL
    :return:
    """
    if not target_url:
        return None
    if target_url.startswith('http://') or target_url.startswith('https://'):
        return target_url
    o = urlparse(page)
    host = '%s://%s:%d' % (o.scheme, o.hostname, o.port if o.port else 80)
    if target_url.startswith('/'):
        return host + target_url
    else:
        return host + '/' + target_url
