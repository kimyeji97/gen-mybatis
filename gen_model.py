#!/usr/bin/python
# -*- coding: utf-8 -*-

import common as common

_column_info = None
_package_path_info = None


def make_java_domain_core(_c_info, _p_info, table, fields, mapper_package, model_gen_package):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    table_class_name = common.to_class_name(table.table_name) + 'Core'

    # 중복 제어해야함
    source_prefix = [
        common.make_import_code(_package_path_info.base_domain_package)
        , common.make_import_code(_package_path_info.lombok_toString)
    ]

    source = [
        "@ToString"
        , "public class {} extends BaseDomain".format(table_class_name)
        , "{"
    ]

    write_only_source = []

    # 매개변수 추가
    for field in fields:

        # BaseDomain에 존재하는 컬럼이면 -> skip
        if field.name in _column_info.base_domain_columns:
            continue

        # Class Type import문 추가
        if field.java_type_package is not None:
            source_prefix.append(common.make_import_code(field.java_type_package))

        # JsonProperty 추가
        if field.jackson_prop is not None:
            source_prefix.append(common.make_import_code(_package_path_info.json_property))

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
        if _column_info.is_use_date_format and field.is_date():
            source_prefix.append(common.make_import_code(_package_path_info.date_time_format))
            source_prefix.append(common.make_import_code(_package_path_info.json_format))
            source.append('    @DateTimeFormat(pattern="' + _column_info.date_format_pattern + '")')
            source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.date_format_pattern + '")')
        # 날짜 시간 Type 인 경우
        if (_column_info.is_use_time_format is True):
            source_prefix.append(common.make_import_code(_package_path_info.date_time_format))
            source_prefix.append(common.make_import_code(_package_path_info.json_format))
            if field.is_datetime3():
                source.append('    @DateTimeFormat(pattern="' + _column_info.date_time3_format_pattern + '")')
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.date_time3_format_pattern + '")')
            elif field.is_datetime():
                source.append('    @DateTimeFormat(pattern="' + _column_info.date_time_format_pattern + '")')
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.date_time_format_pattern + '")')
            elif field.is_time():
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "' + _column_info.time_format_pattern + '")')

        # Field 추가
        source.append("    private {} {};".format(field.java_type, field.java_field_name))

        # 검색용 Field 추가 (WRITE_ONLY)
        if field.is_date() or field.is_datetime() or field.is_datetime3() or field.is_time():
            source_prefix.append(common.make_import_code(_package_path_info.json_property))
            source_prefix.append(common.make_import_code(_package_path_info.json_format))

            write_only_source.append('    @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)')
            write_only_source.append("    private {} {}{};".format(field.java_type, field.java_field_name,_column_info.period_search_start_postfix))
            write_only_source.append('    @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)')
            write_only_source.append("    private {} {}{};".format(field.java_type, field.java_field_name,_column_info.period_search_end_postfix))

    source += write_only_source
    source.append("}")

    source_prefix = list(set(source_prefix))
    source_prefix.insert(0,common.make_package_code(model_gen_package))
    source_prefix.insert(1, "")
    source_prefix.append("")
    source_prefix.append("")
    return "\n".join(map(str, source_prefix + source))


# Model 생성
def make_java_domain_ex(_c_info, _p_info, table, fields, mapper_package, model_package):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    tname = table.table_name
    core_table_class_name = common.to_class_name(tname) + 'Core'
    table_class_name = common.to_class_name(tname)

    source_prefix = [
        common.make_import_code(_package_path_info.core_domain_package + "." + core_table_class_name)
        , common.make_import_code(_package_path_info.lombok_data)
        , common.make_import_code(_package_path_info.lombok_extend_hashcode)
    ]

    source = [
        "@Data"
        , "@EqualsAndHashCode(callSuper = false)"
        , "public class {} extends {}".format(table_class_name, core_table_class_name)
        , "{"
        , "}"
    ]

    source_prefix = list(set(source_prefix))
    source_prefix.insert(0,common.make_package_code(model_package))
    source_prefix.insert(1, "")
    source_prefix.append("")
    source_prefix.append("")
    return "\n".join(map(str, source_prefix + source))
