#!/usr/bin/python
# -*- coding: utf-8 -*-

import common as common

_column_info = None
_package_path_info = None


def make_mapper_ex(_c_info, _p_info, table, fields, mapper_package, model_package):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    mapper = """package %(mapper_package)s;

import %(gen_package)s.%(table_class_name)sMapperCore;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface %(table_class_name)sMapper extends %(table_class_name)sMapperCore
{
    
}
"""
    return mapper % {
        'table_class_name': common.to_class_name(table.table_name)
        , 'mapper_package': mapper_package
        , 'model_package': model_package
        , 'gen_package': _package_path_info.core_mapper_package}


def make_mapper_core(_c_info, _p_info, table, fields, mapper_package, model_package):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    key_params = make_mapper_key_params(fields)
    sequence_mapper_src = ''

    if table.sequence is not None:
        seq_cls_name = common.to_class_name(table.sequence)
        sequence_mapper_src = """
    Long getNext{seq_cls_name}();

    Long getLast{seq_cls_name}();

    Long setLast{seq_cls_name}(Long lastValue);
""".format(seq_cls_name=seq_cls_name, sequence_name=table.sequence)

    mapper = """package %(mapper_package)s;

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
    return mapper % {'table_class_name': common.to_class_name(table.table_name)
        , 'table_field_name': common.to_field_name(table.table_name)
        , 'mapper_package': _package_path_info.core_mapper_package
        , 'model_package': model_package
        , 'sequence_mapper_src': sequence_mapper_src
        , 'key_params': key_params['params_str']
        , 'key_params_import': key_params['import_str']
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
                # or field.is_auto_increment()
                or field.is_pk == False):
            continue

        params.append("@Param(\"{}\") {} {},".format(field_f_name, java_type, field_f_name))
        if field.java_type_package:
            imports.append(common.make_import_code(field.java_type_package))

    if len(params) > 0:
        imports.append(common.make_import_code(_package_path_info.annotations_param))

    params[-1] = params[-1][0:-1]
    return {
        'params_str': (" ").join(params)
        , 'import_str': ("\n").join(imports)
    }
