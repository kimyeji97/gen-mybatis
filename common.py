#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import config as config

def replace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def bool_str(boo):
    if boo:
        return 'true'
    else:
        return 'false'

def to_lower(s):
    return s.lower()

def to_field_name(value):
    value = value.replace("tb_", "", 1)
    value = value.replace("TB_", "", 1)

    def camelcase():
        yield str.lower
        while True:
            yield str.capitalize

    c = camelcase()
    if config.__IS_VERSION_3__:
        return "".join(c.__next__()(x) if x else '_' for x in re.split('[-_ ]', value))
    else:
        return "".join(c.next()(x) if x else '_' for x in re.split('[-_ ]', value))


def to_class_name(value):
    tmpval = to_field_name(value)
    return tmpval[0].upper() + tmpval[1:]


def make_import_code(package):
    return "import {};".format(package)


def make_package_code(package):
    return "package {};".format(package)


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def startswith_ignore_case(str1, *str2):
    for prefix in str2:
        if str1.lower().startswith(prefix.lower()):
            return True
    return False

def endswith_ignore_case(str1, *str2):
    for postfix in str2:
        if str1.lower().endswith(postfix.lower()):
            return True

    return False