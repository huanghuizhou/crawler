#!/usr/bin/env python3
# coding=utf-8


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
