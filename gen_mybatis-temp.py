#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, io, re
import datetime

from dataclasses import dataclass
from gen_config import __IS_VERSION_3__


# @dataclass
class PackagePathInfo:
    json_property = 'com.fasterxml.jackson.annotation.JsonProperty'
    date_time_format = 'org.springframework.format.annotation.DateTimeFormat'
    json_format = 'com.fasterxml.jackson.annotation.JsonFormat'

    def __init__(self, xml_path, mapper_path, model_path, gen_domain_package, base_domain_path, column_path, enum_path):
        self.xml_path = xml_path
        self.mapper_path = mapper_path
        self.model_path = model_path
        self.gen_domain_package = gen_domain_package
        self.base_domain_path = base_domain_path
        self.column_path = column_path
        self.enum_path = enum_path


# @dataclass
class ColumnInfo:
    date_format_pattern = 'yyyy-MM-dd'
    date_time_format_pattern = 'yyyy-MM-dd HH:mm:ss'
    date_time3_format_pattern = 'yyyy-MM-dd HH:mm:ss.SSS'
    time_format_pattern = 'HH:mm:ss'

    def __init__(self):
        pass

    def __int__(self, is_remove_cd, is_remove_yn, is_use_date_format, is_use_time_format, base_domain_colums):
        self.is_remove_cd = is_remove_cd
        self.is_remove_yn = is_remove_yn
        self.is_use_date_format = is_use_date_format
        self.is_use_time_format = is_use_time_format
        self.base_domain_colums = base_domain_colums

    def set_date_format_pattern(self, pattern):
        self.date_format_pattern = pattern

    def set_date_time_format_pattern(self, pattern):
        self.date_time_format_pattern = pattern
        self.date_time3_format_pattern = pattern + '.SSS'

    def set_time_format_pattern(self, pattern):
        self.time_format_pattern = pattern


SP4 = ' ' * 4
SP8 = ' ' * 8
SP12 = ' ' * 12

_package_path_info: PackagePathInfo = None
_column_info: ColumnInfo = None


def set_base_info(p_info: PackagePathInfo, c_info: ColumnInfo):
    _package_path_info = p_info
    _column_info = c_info


def replace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def to_field_name(value):
    value = value.replace("tb_", "", 1)
    value = value.replace("TB_", "", 1)

    def camelcase():
        yield str.lower
        while True:
            yield str.capitalize

    c = camelcase()
    if __IS_VERSION_3__:
        return "".join(c.__next__()(x) if x else '_' for x in re.split('[-_ ]', value))
    else:
        return "".join(c.next()(x) if x else '_' for x in re.split('[-_ ]', value))


def bool_str(boo):
    if boo:
        return 'true'
    else:
        return 'false'


def to_class_name(value):
    tmpval = to_field_name(value)
    return tmpval[0].upper() + tmpval[1:]


def make_import_code(package):
    return "import {};".format(package)


def make_package_code(package):
    return "package {};".format(package), ""


# model 코드 생성
def get_model_code(table, fields, mapper_package, model_gen_package):
    table_class_name = to_class_name(table.table_name) + 'Core'

    # 중복 제어해야함
    source_prefix = [
        make_package_code(model_gen_package)
        , make_import_code(_package_path_info.column_path)
        , make_import_code(_package_path_info.base_domain_path)
        , make_import_code("lombok.ToString")
    ]

    source = [
        "@ToString"
        , "public class {} extends BaseDomain".format(table_class_name)
        , "{"
    ]

    # 매개변수 추가
    for field in fields:

        # BaseDomain에 존재하는 컬럼이면 -> skip
        if field.name in _column_info.base_domain_colums:
            continue

        # Class Type import문 추가
        if field.java_type_package is not None:
            source_prefix.append(make_import_code(field.java_type_package))

        # JsonProperty 추가
        if field.jackson_prop is not None:
            source_prefix.append(make_import_code(_package_path_info.json_property))

            prop_str_list = []
            # value 옵션 추가
            if 'value' in field.jackson_prop:
                prop_str_list.append('value = "{}"'.format(field.jackson_prop['value']))
            # access 옵션 추가
            if 'access' in field.jackson_prop:
                prop_str_list.append('access = {}'.format(field.jackson_prop['access']))

            if len(prop_str_list) > 0:
                source.append('    @JsonProperty({})'.format(','.join(prop_str_list)))

        # 날짜 Type 인 경우
        if (_column_info.is_use_date_format is True):
            if field.type.startswith("date") or field.type.startswith("timestamp"):
                source_prefix.append(make_import_code(_package_path_info.date_time_format))
                source_prefix.append(make_import_code(_package_path_info.json_format))
                source.append('    @DateTimeFormat(pattern="' + _column_info.date_format_pattern + '")')
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.date_format_pattern + '")')
        # 날짜 시간 Type 인 경우
        elif (_column_info.is_use_time_format is True):
            source_prefix.append(make_import_code(_package_path_info.date_time_format))
            source_prefix.append(make_import_code(_package_path_info.json_format))
            if field.type.startswith("datetime(3") or field.type.startswith("timestamp(3"):
                source.append('    @DateTimeFormat(pattern="' + _column_info.date_time3_format_pattern + '")')
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.date_time3_format_pattern + '")')
            elif field.type == 'datetime' or field.type == 'timestamp':
                source.append('    @DateTimeFormat(pattern="' + _column_info.date_time_format_pattern + '")')
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.date_time_format_pattern + '")')
            elif field.type == 'time':
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.time_format_pattern + '")')

        # Field 추가
        source.append('    @Column(columnName = "{}", type = "{}", nullable = {}, primary = {})'
                      .format(field.name, field.type, bool_str(field.nullable), bool_str(field.is_pk)))
        source.append("    private {} {};".format(field.java_type, field.java_field_name))

    source.append("}")
    source_prefix.append("")
    source_prefix.append("")

    return "\n".join(source_prefix + source)

# TODO [Lilly 20240703] 여기부터 작업하면 됨
def get_ex_model_code(table,fields , mapper_package, model_package):
    tname = table.table_name
    core_table_class_name = to_class_name(tname) + 'Core'
    table_class_name = to_class_name(tname)
    # table_field_name = to_field_name(tname)
    source_prefix = []
    source_prefix.append("package {};".format(model_package))
    source_prefix.append("")
    # source_prefix.append("import org.apache.commons.lang3.builder.ToStringBuilder;")
    source_prefix.append("import com.innerwave.core.gen.domain." + core_table_class_name  + ";")
    source_prefix.append("import lombok.Data;")
    source_prefix.append("import lombok.EqualsAndHashCode;")

    source = []
    source.append("@Data")
    source.append("@EqualsAndHashCode(callSuper=false)")
    source.append("public class {} extends {}".format(table_class_name, core_table_class_name))
    source.append("{")
    source.append("}")

    source_prefix.append("")
    source_prefix.append("")
    return "\n".join(source_prefix + source)