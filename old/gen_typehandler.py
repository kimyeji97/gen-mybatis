#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys , os, re
import datetime
import psycopg2


print("generate the 'Typehandler' with payment code.")

__IS_VERSION_3__= sys.version_info.major == 3

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

from old.gen_config import ENUM_PACKAGE, con_opts

DATE_FORMAT="%Y%m%d.%H%M%S"
tmpfolder = datetime.datetime.strftime(datetime.datetime.now(),DATE_FORMAT)

main_path = os.path.realpath(os.path.join(dir_path, '../../../innerwave-core/src/main' ))
th_path = os.path.join(main_path, 'java', 'com','innerwave','core','gen','mybatis','th')
deserializer_path = os.path.join(main_path, 'java', 'com','innerwave','core','gen','jackson','th')
code_groups = []


class CodeGroup:
    def __init__(self, **kwargs):
        # print (kwargs)
        self.gcode    = kwargs['cd_id']
        self.gname    = kwargs['cd_nm']
        self.gname_disp = "" if kwargs['cd_disp_nm'] == "None" else kwargs['cd_disp_nm']
        self.gname_disp_eng = "" if kwargs['cd_disp_nm_eng'] == "None" else kwargs['cd_disp_nm_eng']
        self.desc    = kwargs['dscrpt']
        self.genum_name = kwargs['src_nm'].replace(' ','').replace('-','').replace('/','')
        self.codes    = []
    def __str__(self):
        return self.gcode + ", " + self.gname + ", codes => [" + ', '.join(map(str,self.codes)) + "]"

class Code:
    def __init__(self, **kwargs):
        self.code    = kwargs['cd_id']
        self.pcode   = kwargs['cd_pid']
        self.name    = kwargs['cd_nm']
        self.name_disp = "" if kwargs['cd_disp_nm'] == "None" else kwargs['cd_disp_nm']
        self.name_disp_eng = "" if kwargs['cd_disp_nm_eng'] == "None" else kwargs['cd_disp_nm_eng']
        self.desc    = kwargs['dscrpt']
        self.enum_name = kwargs['src_nm'].replace(' ','').replace('-','').replace('/','')
        self.value   = self.get_value()
    def __str__(self):
        return self.code + ":" + self.name + "[" + self.enum_name + "]"

    def get_value(self):
        if self.name_disp != 'None':
            return self.name_disp
        else:
            return self.name

    def to_enum_name(self, val):
        if __IS_VERSION_3__:
            return "".join(x if x else '' for x in re.split('[-_/ ]',val))
        else:
            return "".join(x if x else '' for x in re.split('[-_/ ]',val))

def get_code_groups(connection_opts, table_name):
    cnx = psycopg2.connect(**connection_opts)
    cursor = cnx.cursor()
    #cursor.execute('SELECT * FROM tb_group_cd WHERE group_cd_pid IS NULL',False)
    cursor.execute('SELECT * FROM {} where cd_pid is null order by cd_id'.format(table_name),False)
    def to_lower(s):
        return s.lower()
    #col_names = map(to_lower,cursor.column_names)
    col_names = map(to_lower,[desc[0] for desc in cursor.description])
    if __IS_VERSION_3__:
        col_names = list(col_names)

    fetchedCursor = cursor.fetchall()
    rows = []
    for row in fetchedCursor:
        str_row = None
        if __IS_VERSION_3__:
            str_row = list(map(str, row))
        else:
            str_row = row
        map_row = dict(zip(col_names, str_row))

        row_obj = CodeGroup(**map_row)
        rows.append(row_obj)
    cursor.close()
    cnx.close()
    return rows

def to_field_name(value):
    def camelcase(): 
        yield str.lower
        while True:
            yield str.capitalize
    c = camelcase()
    if __IS_VERSION_3__:
        return "".join(c.__next__()(x) if x else '_' for x in value.split("_"))
    else:
        return "".join(c.next()(x) if x else '_' for x in value.split("_"))

def to_class_name(value):
    tmpval = to_field_name(value)
    return tmpval[0].upper() + tmpval[1:]


def generate_mybatis_type_handler():
    for cg in code_groups:
        enum = cg.genum_name
        cls_name = to_class_name(enum) + 'TypeHandler'

        src = """package com.innerwave.core.gen.mybatis.th;

import java.sql.CallableStatement;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import org.apache.ibatis.type.BaseTypeHandler;
import org.apache.ibatis.type.JdbcType;

import {enumpackage};
import {enumpackage}.{type_name};

public class {cls_name} extends BaseTypeHandler<{type_name}>
{{
    @Override
    public void setNonNullParameter(PreparedStatement ps, int i, {type_name} parameter, JdbcType jdbcType)
        throws SQLException
    {{
        ps.setLong(i, parameter.getCode());
    }}

    @Override
    public {type_name} getNullableResult(ResultSet rs, String columnName) throws SQLException
    {{
        Long code = rs.getLong(columnName);
        if (rs.wasNull())
        {{
            return null;
        }}
        return getEnum(code);
    }}

    @Override
    public {type_name} getNullableResult(ResultSet rs, int columnIndex) throws SQLException
    {{
        Long code = rs.getLong(columnIndex);
        if (rs.wasNull())
        {{
            return null;
        }}
        return getEnum(code);
    }}

    @Override
    public {type_name} getNullableResult(CallableStatement cs, int columnIndex) throws SQLException
    {{
        Long code = cs.getLong(columnIndex);
        if (cs.wasNull())
        {{
            return null;
        }}
        return getEnum(code);
    }}
    
    private {type_name} getEnum(Long code)
    {{
        return PlatformCodes.enumByCode({type_name}.class, code);
    }}
}}
""".format(enumpackage = ENUM_PACKAGE, cls_name = cls_name, type_name = enum)
        #tmpdir = os.path.join('C:\\Temp','typehandler-' + tmpfolder , 'mybatis')

        #if not os.path.exists(tmpdir):
        #    print ('Generated sources will be saved into : {}'.format(tmpdir))
        #    os.makedirs(tmpdir)
        
        #with open(os.path.join(tmpdir,cls_name + '.java'), 'w') as f :
        #    f.write(src.replace(r'\n', '\r\n'))
        write_file_core(th_path,cls_name + '.java',src)

    print ('Mybatis Type handlers have been generated. Copy the sources and paste to source directory.')




def generate_jackson_de_and_serializer():
    def write_src(cname, data):
        tmpdir = os.path.join('C:\\Temp','typehandler-' + tmpfolder , 'jackson')
        
        if not os.path.exists(tmpdir):
            print ('Generated jackson sources will be saved into : {}'.format(tmpdir))
            os.makedirs(tmpdir)
        
        with open(os.path.join(tmpdir,cname + '.java'), 'w') as f :
            f.write(data.replace(r'\n', '\r\n'))

    for cg in code_groups:
        enum = cg.genum_name
        de_cls_name = to_class_name(enum) + 'Deserializer'

        deserializer_src = """package com.innerwave.core.gen.jackson.th;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import org.springframework.core.convert.converter.Converter;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.math.NumberUtils;
import java.io.IOException;

import {enumpackage};
import {enumpackage}.PlatformCode;
import {enumpackage}.{type_name};

public class {cls_name} extends JsonDeserializer<{type_name}> implements Converter<String,{type_name}>
{{
    @Override
    public {type_name} deserialize(JsonParser jp, DeserializationContext ctxt)
        throws IOException, JsonProcessingException
    {{
        if (jp.isExpectedStartObjectToken())
        {{
            PlatformCode cd = jp.readValueAs(PlatformCode.class);
            if (cd == null)
            {{
                return null;
            }}

            if (cd.getCode() != null)
            {{
                return PlatformCodes.enumByCode({type_name}.class, cd.getCode());
            }}

            if (StringUtils.isNotEmpty(cd.getValue()))
            {{
                return PlatformCodes.enumByValue({type_name}.class, cd.getValue());
            }} else
            {{
                // Invalid Data
                return null;
            }}
        }}
        else
        {{
            return convertFromString(jp.getValueAsString());
        }}
    }}

    private {type_name} convertFromString(String value)
    {{
        if (StringUtils.isEmpty(value))
        {{
            return null;
        }}
        {type_name} pr = PlatformCodes.enumByValue({type_name}.class, value);
        if (pr == null)
        {{
            pr = PlatformCodes.enumByCode({type_name}.class, NumberUtils.toLong(value, -1));
        }}

        return pr;
    }}

    @Override
    public Class<{type_name}> handledType()
    {{
        return {type_name}.class;
    }}

    // Converter Implementation
    @Override
    public {type_name} convert(String source)
    {{
        return convertFromString(source);
    }}
}}
""".format(enumpackage = ENUM_PACKAGE,cls_name = de_cls_name, type_name = enum)
        #write_src(de_cls_name,deserializer_src)
        write_file_core(deserializer_path,de_cls_name + '.java',deserializer_src)

    print ('Jackson Deserializer have been generated. Copy the sources and paste to source directory.')


def write_file_core(path,  file_name, data):
    with open(os.path.join(path,file_name), 'w') as f :
        f.write(data)

############################################
## main()
############################################
code_groups = get_code_groups(con_opts,'tb_common_cd')
generate_mybatis_type_handler()
generate_jackson_de_and_serializer()
