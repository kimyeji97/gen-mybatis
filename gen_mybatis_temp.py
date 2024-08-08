#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, io, re
import datetime

from dataclasses import dataclass
from gen_config_temp import __IS_VERSION_3__


# @dataclass
class PackagePathInfo:
    json_property = 'com.fasterxml.jackson.annotation.JsonProperty'
    date_time_format = 'org.springframework.format.annotation.DateTimeFormat'
    json_format = 'com.fasterxml.jackson.annotation.JsonFormat'
    lombok_data = 'lombok.Data'
    lombok_extend_hashcode = 'lombok.EqualsAndHashCode'
    lombok_toString = 'lombok.ToString'


    def __init__(self, xml_path, mapper_path, model_path, base_domain_path, column_path, enum_path, core_domain_package, core_mapper_package):
        self.xml_path = xml_path
        self.mapper_path = mapper_path
        self.model_path = model_path
        self.base_domain_path = base_domain_path
        self.column_path = column_path
        self.enum_path = enum_path
        self.core_domain_package = core_domain_package
        self.core_mapper_package = core_mapper_package


# @dataclass
class ColumnInfo:
    date_format_pattern = 'yyyy-MM-dd'
    date_time_format_pattern = 'yyyy-MM-dd HH:mm:ss'
    date_time3_format_pattern = 'yyyy-MM-dd HH:mm:ss.SSS'
    time_format_pattern = 'HH:mm:ss'
    insert_dt_columns = []
    update_dt_columns = []

    def __init__(self):
        pass

    def __int__(self, is_remove_cd, is_remove_yn, is_use_date_format, is_use_time_format, base_domain_columns, insert_dt_columns, update_dt_columns):
        self.is_remove_cd = is_remove_cd
        self.is_remove_yn = is_remove_yn
        self.is_use_date_format = is_use_date_format
        self.is_use_time_format = is_use_time_format
        self.base_domain_columns = base_domain_columns
        self.insert_dt_columns = insert_dt_columns
        self.update_dt_columns = update_dt_columns

    def set_date_format_pattern(self, pattern):
        self.date_format_pattern = pattern

    def set_date_time_format_pattern(self, pattern):
        self.date_time_format_pattern = pattern
        self.date_time3_format_pattern = pattern + '.SSS'

    def set_time_format_pattern(self, pattern):
        self.time_format_pattern = pattern

    def include_insert_dt_columns(self, column):
        if len(self.insert_dt_columns) < 1:
            return False
        return column in self.insert_dt_columns
    def include_update_dt_columns(self, column):
        if len(self.update_dt_columns) < 1:
            return False
        return column in self.update_dt_columns


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


# Model Core 생성
def get_model_code(table, fields, mapper_package, model_gen_package):
    table_class_name = to_class_name(table.table_name) + 'Core'

    # 중복 제어해야함
    source_prefix = [
        make_package_code(model_gen_package)
        , make_import_code(_package_path_info.column_path)
        , make_import_code(_package_path_info.base_domain_path)
        , make_import_code(_package_path_info.lombok_toString)
    ]

    source = [
        "@ToString"
        , "public class {} extends BaseDomain".format(table_class_name)
        , "{"
    ]

    # 매개변수 추가
    for field in fields:

        # BaseDomain에 존재하는 컬럼이면 -> skip
        if field.name in _column_info.base_domain_columns:
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

# Model 생성
def get_ex_model_code(table,fields , mapper_package, model_package):
    tname = table.table_name
    core_table_class_name = to_class_name(tname) + 'Core'
    table_class_name = to_class_name(tname)

    source_prefix = [
        make_package_code(model_package)
        , ""
        , make_import_code(_package_path_info.core_domain_package + "."+core_table_class_name)
        , make_import_code(_package_path_info.lombok_data)
        , make_import_code(_package_path_info.lombok_extend_hashcode)
        , ""
        , ""
    ]

    source = [
        "@Data"
        , "@EqualsAndHashCode(callSuper = false)"
        , "public class {} extends {}".format(table_class_name, core_table_class_name)
        , "{"
        , "}"
    ]
    return "\n".join(source_prefix + source)


# TODO [Lilly 20240806] 여기부터
def get_mapper_code(table, fields, mapper_package, model_package):
    tname = table.table_name
    table_class_name = to_class_name(tname)
    corePackage = _package_path_info.core_mapper_package

    mapper = """package %(mapper_package)s;

import %(gen_package)s.%(table_class_name)sMapperCore;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface %(table_class_name)sMapper extends %(table_class_name)sMapperCore
{
    
}
"""
    return mapper % {
        'table_class_name' : table_class_name
        ,'mapper_package':mapper_package
        ,'model_package':model_package, 'gen_package':corePackage}

def gen_mapper_gen_code(table,fields , mapper_package, model_package):
    tname = table.table_name
    table_class_name = to_class_name(tname)
    table_field_name = to_field_name(tname)
    key_params = make_mapper_key_params(fields)

    corePackage = _package_path_info.core_mapper_package

    sequence_mapper_src = ''
    if table.sequence is not None:
        seq_cls_name = to_class_name(table.sequence)
        sequence_mapper_src = """
    Long getNext{seq_cls_name}();

    Long getLast{seq_cls_name}();

    Long setLast{seq_cls_name}(Long lastValue);
""".format(seq_cls_name = seq_cls_name
           ,sequence_name = table.sequence)

    mapper =  """package %(mapper_package)s;

import %(model_package)s.%(table_class_name)s;
import java.util.List;
%(key_params_import)s

public interface %(table_class_name)sMapperCore
{
    int create%(table_class_name)s(%(table_class_name)s %(table_field_name)s);
    
    %(table_class_name)s create%(table_class_name)sReturn(%(table_class_name)s %(table_field_name)s);

    int create%(table_class_name)sList(List<%(table_class_name)s> %(table_field_name)sList);

    %(table_class_name)s read%(table_class_name)s(%(table_class_name)s %(table_field_name)s); 

    %(table_class_name)s read%(table_class_name)sByKey(%(key_params)s);

    List<%(table_class_name)s> list%(table_class_name)s(%(table_class_name)s %(table_field_name)s);

    int update%(table_class_name)s(%(table_class_name)s %(table_field_name)s);

    %(table_class_name)s update%(table_class_name)sReturn(%(table_class_name)s %(table_field_name)s);

    int updateForce(%(table_class_name)s %(table_field_name)s);

    %(table_class_name)s updateForceReturn(%(table_class_name)s %(table_field_name)s);

    int delete%(table_class_name)s(%(table_class_name)s %(table_field_name)s);

    int delete%(table_class_name)sByKey(%(key_params)s);
%(sequence_mapper_src)s
}
"""
    return mapper % {'table_class_name' : table_class_name
        ,'table_field_name' : table_field_name
        ,'mapper_package':corePackage
        ,'model_package':model_package
        ,'sequence_mapper_src' : sequence_mapper_src
        ,'key_params' : key_params['params_str']
        ,'key_params_import' : key_params['import_str']
    }





def make_mapper_key_params(fields):
    imports = []
    params = []
    for field in fields:
        f = field.name
        java_type = field.java_type
        field_f_name = field.java_field_name
        if (_column_info.include_insert_dt_columns(f)
                or _column_info.include_update_dt_columns(f)
                or field.is_auto_increment()
                or field.is_pk == False):
            continue

        params.append("@Param(\"{}\") {} {},".format(field_f_name,java_type,field_f_name))
        if field.java_type_package :
            imports.append(make_import_code(field.java_type_package))

    if len(params) > 0:
        imports.append("import org.apache.ibatis.annotations.Param;")

    params[-1] = params[-1][0:-1]
    return {
        'params_str' : (" ").join(params)
        ,'import_str' : ("\n").join(imports)
    }




# TODO [Lilly 20240806] 여기부터
def makeWherePk(table) :
    fields = table.fields
    xml = []
    for field in fields:
        f = field.name
        if f == regist_column_nm or f == update_column_nm or field.is_pk == False:
            continue

        javaField = field.java_field_name
        xml.append("AND {} = #{{{}}}".format(f,javaField))
    return SP12 + ("\n" + SP12).join(xml)
