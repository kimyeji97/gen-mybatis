#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys , os, io ,re
import datetime

from gen_config import FIELD_NAME_ENUM_TYPES, ENUM_PACKAGE, con_opts, con_schema

class PackagePathInfo:
    def __init__(self, xml_path, mapper_path, model_path, gen_domain_package, base_domain_path):
        self.xml_path = xml_path
        self.mapper_path = mapper_path
        self.model_path = model_path
        self.gen_domain_package = gen_domain_package
        self.base_domain_path = base_domain_path

class ColumnInfo:
    def __int__(self, is_remove_cd, is_remove_yn, is_use_date_format, is_use_time_format, base_domain_colums):
        self.is_remove_cd = is_remove_cd
        self.is_remove_yn = is_remove_yn
        self.is_use_date_format = is_use_date_format
        self.is_use_time_format = is_use_time_format
        self.base_domain_colums = base_domain_colums



__IS_VERSION_3__= sys.version_info.major == 3
_IS_WINDOW_ = os.name == 'Windows' or os.name == 'nt'

SP4  = ' '*4
SP8  = ' '*8
SP12 = ' '*12


_package_path_info=None
_column_info=None

def set_base_info(p_info, c_info):
    _package_path_info = p_info
    _column_info = c_info

def rreplace(s, old, new, occurrence):
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
        return "".join(c.__next__()(x) if x else '_' for x in re.split('[-_ ]',value))
    else:
        return "".join(c.next()(x) if x else '_' for x in re.split('[-_ ]',value))

def bool_str(boo):
    if boo : return 'true'
    else : return 'false'


def to_class_name(value):
    tmpval = to_field_name(value)
    return tmpval[0].upper() + tmpval[1:]


def get_model_code(table,fields , mapper_package, model_gen_package):
    tname = table.table_name
    table_class_name = to_class_name(tname) + 'Core'
    # table_field_name = to_field_name(tname)
    source_prefix = []
    source_prefix.append("package {};".format(model_gen_package))
    source_prefix.append("")
    source_prefix.append("import com.innerwave.core.domain.Column;")
    source_prefix.append("import "+ _package_path_info.base_domain_path + ";")
    source_prefix.append("import lombok.ToString;")

    source = []
    source.append("@ToString")
    source.append("public class {} extends BaseDomain".format(table_class_name))
    source.append("{")
    for field in fields:
        f = field.name

        #if f == 'REG_DT' or f == 'REGR_ID' or f == 'REG_ID' or f == 'UPD_DT' or f == 'UPDR_ID' or f == 'UPD_ID':
        if f in _column_info.base_domain_colums:
            continue

        if field.java_type_package is not None:
            import_str = "import " + field.java_type_package + ";"
            if import_str not in source_prefix:
                source_prefix.append(import_str)
        if field.jackson_prop is not None:
            imp_str = "import com.fasterxml.jackson.annotation.JsonProperty;"
            if imp_str not in source_prefix:
                source_prefix.append(imp_str)
            prop_str = []
            if 'value' in field.jackson_prop:
                prop_str.append('value = "{}"'.format(field.jackson_prop['value']))
            if 'access' in field.jackson_prop:
                prop_str.append('access = {}'.format(field.jackson_prop['access']))
            source.append('    @JsonProperty({})'.format(','.join(prop_str) ) )

        if(_column_info.is_use_date_format):
            if field.type.startswith("date") or field.type.startswith("timestamp"):
                imp_str = "import org.springframework.format.annotation.DateTimeFormat;"
                if imp_str not in source_prefix:
                    source_prefix.append(imp_str)
                imp_str = "import com.fasterxml.jackson.annotation.JsonFormat;"
                if imp_str not in source_prefix:
                    source_prefix.append(imp_str)
        elif(_column_info.is_use_date_format is False and _column_info.is_use_time_format):
            if field.type == 'time':
                imp_str = "import com.fasterxml.jackson.annotation.JsonFormat;"
                if imp_str not in source_prefix:
                    source_prefix.append(imp_str)

        if(_column_info.is_use_date_format):
            if field.type.startswith("datetime(3") or field.type.startswith("timestamp(3"):
                source.append('    @DateTimeFormat(pattern="yyyy-MM-dd HH:mm:ss.SSS")')
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd HH:mm:ss.SSS")')
            elif field.type == 'date':
                source.append('    @DateTimeFormat(pattern="yyyy-MM-dd")')
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd")')
            elif field.type == 'datetime'or field.type == 'timestamp':
                source.append('    @DateTimeFormat(pattern="yyyy-MM-dd HH:mm:ss")')
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd HH:mm:ss")')


        if(_column_info.is_use_time_format):
            if field.type == 'time':
                source.append('    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "HH:mm:ss")')

        # source.append('    @Column(columnName = "{}", type = "{}", length = {}, nullable = {})'.format(f, field.type, f.))
        source.append('    @Column(columnName = "{}", type = "{}", nullable = {}, primary = {})'.format(f, field.type, bool_str(field.nullable), bool_str(field.is_pk)))
        source.append("    private {} {};".format(field.java_type, field.java_field_name))

    for field in fields:
        f = field.name
        #if f == 'REG_DT' or f == 'REGR_ID' or f == 'REG_ID' or f == 'UPD_DT' or f == 'UPDR_ID' or f == 'UPD_ID':
        if f in _column_info.base_domain_colums:
            continue
        field_t_name = field.java_field_name[0].upper() + field.java_field_name[1:]
        field_f_name = field.java_field_name
        java_type = field.java_type
        get_set_format = """
    public void set{field_t_name}({java_type} {field_f_name})
    {{
        this.{field_f_name} = {field_f_name};
    }}

    public {java_type} get{field_t_name}()
    {{
        return this.{field_f_name};
    }}"""

        # java_type이 배열이면 get,set clone해서.
        if java_type.endswith('[]') :
            get_set_format = """
    public void set{field_t_name}({java_type} {field_f_name})
    {{
    	if({field_f_name} != null)
    	{{
    		this.{field_f_name} = {field_f_name}.clone();
    	}}
    }}

    public {java_type} get{field_t_name}()
    {{
    	if(this.{field_f_name} != null)
    	{{
    		return this.{field_f_name}.clone();
    	}}
    	else
    	{{
    		return null;
    	}}
    }}"""

        get_set = get_set_format.format(field_t_name = field_t_name
                                        ,field_f_name = field_f_name
                                        ,java_type = java_type)
        source.append(get_set)
    source.append("}")

    source_prefix.append("")
    source_prefix.append("")
    return "\n".join(source_prefix + source)