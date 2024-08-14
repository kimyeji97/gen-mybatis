#!/usr/bin/python
# -*- coding: utf-8 -*-

import config as config
import common as common

_column_info = None
_package_path_info = None


def make_sql_where_all(fields):
    xml = []
    javaFieldList = ['uri', 'host', 'method']
    for field in fields:
        f = field.name
        if _column_info.include_update_dt_columns(f) or _column_info.include_insert_dt_columns(f):
            continue

        javaField = field.java_field_name
        null_check_string = field.null_check_string
        oper = '='
        if (javaField in javaFieldList) or common.endswith_ignore_case(f, "NM", "NAME"):
            oper = 'ILIKE'

        xml.append("<if test=\"{}\">".format(null_check_string[0]))
        xml.append("    AND {} {} #{{{}}}".format(f, oper, javaField))
        xml.append("</if>")

        if field.is_date() or field.is_datetime() or field.is_datetime3() or field.is_time():
            xml.append("<if test=\"{}\">".format(null_check_string[1]))
            xml.append("    AND {} BETWEEN #{{{}{}}} AND #{{{}{}}}".format(f, javaField, _column_info.period_search_start_postfix, javaField, _column_info.period_search_end_postfix))
            xml.append("</if>")

    return config._SP8 + ("\n" + config._SP8).join(xml)


def make_sql_where_pk(table):
    fields = table.fields
    xml = []
    for field in fields:
        f = field.name
        if _column_info.include_update_dt_columns(f) or _column_info.include_insert_dt_columns(f) or field.is_pk == False:
            continue

        xml.append("AND {} = #{{{}}}".format(f, field.java_field_name))
    return config._SP12 + ("\n" + config._SP12).join(xml)


def make_sql_columns(table, fields, with_alias, only_pk):
    alias = ""
    if with_alias:
        alias = table.table_alias + "."

    xml = []
    for field in fields:
        f = field.name

        if field.is_auto_increment() or only_pk == True and field.is_pk == False:
            continue

        xml.append("    {}{},".format(alias, f))

    if len(xml) > 0:
        xml[-1] = xml[-1][0:-1]
    return config._SP8 + ("\n" + config._SP8).join(xml)


def make_sql_values(table, fields):
    xml = []
    for field in fields:
        f = field.name
        if field.is_auto_increment():
            continue

        if (_column_info.include_insert_dt_columns(f)) or (_column_info.include_update_dt_columns(f)):
            xml.append("    COALESCE(#{{{}}},CURRENT_TIMESTAMP),".format(field.java_field_name))
        else:
            if field.sequence_name:
                xml.append("    COALESCE(#{{{}}},NEXTVAL('{}')),".format(field.java_field_name, field.sequence_name))
            elif field.nullable == False and field.default:
                xml.append("    COALESCE(#{{{}}},{}),".format(field.java_field_name, field.default))
            elif _column_info.include_delete_columns(f):
                xml.append("    COALESCE(#{{{}}},FALSE),".format(field.java_field_name))
            else:
                xml.append("    #{{{}}},".format(field.java_field_name))

    xml[-1] = xml[-1][0:-1]
    return config._SP8 + ("\n" + config._SP8).join(xml)


def make_sql_foreach_values(table, fields):
    tname = table.table_name
    table_field_name = common.to_field_name(tname)
    xml = []
    xml.append("    <foreach collection=\"list\" item=\"item\" separator=\",\">".format(table_field_name))
    xml.append("    (")
    for field in fields:
        f = field.name
        if field.is_auto_increment():
            continue

        if (_column_info.include_insert_dt_columns(f)) or (_column_info.include_update_dt_columns(f)):
            xml.append("        COALESCE(#{{item.{}}},CURRENT_TIMESTAMP),".format(field.java_field_name))
        else:
            if field.sequence_name:
                xml.append("        COALESCE(#{{item.{}}},NEXTVAL('{}')),".format(field.java_field_name, field.sequence_name))
            elif field.nullable == False and field.default:
                xml.append("        COALESCE(#{{item.{}}},{}),".format(field.java_field_name, field.default))
            elif _column_info.include_delete_columns(f):
                xml.append("        COALESCE(#{{item.{}}},FALSE),".format(field.java_field_name))
            else:
                xml.append("        #{{item.{}}},".format(field.java_field_name))

    xml[-1] = xml[-1][0:-1]
    xml.append("    )")
    xml.append("    </foreach>")
    return config._SP8 + ("\n" + config._SP8).join(xml)


def make_sql_insert(table, fields):
    table_name = table.table_name
    xml = []
    xml.append("INSERT INTO {} (".format(table_name))
    for field in fields:
        f = field.name
        if field.is_auto_increment():
            continue
        xml.append("    {},".format(f))

    xml[-1] = xml[-1][0:-1]
    xml.append(")")
    xml.append("VALUES (")

    for field in fields:
        f = field.name
        if field.is_auto_increment():
            continue

        if (_column_info.include_insert_dt_columns(f)) or (_column_info.include_update_dt_columns(f)):
            xml.append("    COALESCE(#{{{}}},CURRENT_TIMESTAMP),".format(field.java_field_name))
        else:
            if field.sequence_name:
                xml.append("    COALESCE(#{{{}}},NEXTVAL('{}')),".format(field.java_field_name, field.sequence_name))
            elif field.nullable == False and field.default:
                xml.append("    COALESCE(#{{{}}},{}),".format(field.java_field_name, field.default))
            elif _column_info.include_delete_columns(f):
                xml.append("    COALESCE(#{{{}}},FALSE),".format(field.java_field_name))
            else:
                xml.append("    #{{{}}},".format(field.java_field_name))

    xml[-1] = xml[-1][0:-1]
    xml.append("    )")
    return config._SP8 + ("\n" + config.SP8).join(xml)


def make_sql_upadate_set(table, fields):
    table_name = table.table_name
    xml = []
    xml.append("UPDATE {} ".format(table_name))
    xml.append("<set>")
    for field in fields:
        f = field.name
        if _column_info.include_insert_dt_columns(f) or field.is_auto_increment():
            continue

        javaField = field.java_field_name
        if _column_info.include_update_dt_columns(f):
            xml.append("    {} = CURRENT_TIMESTAMP".format(javaField))
        else:
            xml.append("    <if test=\"{} != null\">".format(javaField))
            xml.append("        {} = #{{{}}},".format(f, javaField))
            xml.append("    </if>")

    xml.append("</set>")

    return config._SP8 + ("\n" + config._SP8).join(xml)


def make_sql_update(table, fields):
    table_name = table.table_name
    xml = []
    xml.append("UPDATE {} ".format(table_name))
    xml.append("<set>")
    for field in fields:
        f = field.name
        if field.is_auto_increment() or field.is_pk == True:
            continue

        if _column_info.include_update_dt_columns(f):
            xml.append("    {} = CURRENT_TIMESTAMP".format(f))
        else:
            xml.append("    {} = #{{{}}},".format(f, field.java_field_name))

    xml.append("</set>")

    return config._SP8 + ("\n" + config._SP8).join(xml)


def make_sql_update_where(table):
    fields = table.fields
    xml = []
    is_first = True
    for field in fields:
        f = field.name
        if _column_info.include_update_dt_columns(f) or _column_info.include_insert_dt_columns(f) or field.is_pk == True:
            continue

        javaField = field.java_field_name
        if is_first:
            xml.append("AND {} = #{{{}}}".format(f, javaField))
            is_first = False
        else:
            null_check_string = field.null_check_string
            xml.append("<if test=\"{}\">".format(null_check_string))
            xml.append("    AND {} = #{{{}}}".format(f, javaField))
            xml.append("</if>")

    return config._SP12 + ("\n" + config._SP12).join(xml)


def make_sql_select_default(table, fields):
    table_name = table.table_name
    field_str = ""
    for field in fields:
        f = field.name
        field_name = f
        field_str = field_str + "\n            {},".format(field_name)

    field_str = field_str[0:-1]

    return """
        SELECT  {field_str}
        FROM {table_name}
    """.format(field_str=field_str, table_name=table_name)


def make_xml_core(_c_info, _p_info, table, fields):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    tname = table.table_name
    tname_alias = table.table_alias
    table_ns = table.table_namespace
    where_if = make_sql_where_all(fields)
    where_pk_if = make_sql_where_pk(table)
    columns_sql = make_sql_columns(table, fields, False, False)
    columns_alias_sql = make_sql_columns(table, fields, True, False)
    pks_sql = make_sql_columns(table, fields, False, True)
    pks_alias_sql = make_sql_columns(table, fields, True, True)
    values_sql = make_sql_values(table, fields)
    values_foreach_sql = make_sql_foreach_values(table, fields)
    update_set = make_sql_upadate_set(table, fields)
    update_set_force = make_sql_update(table, fields)
    update_where = make_sql_update_where(table)

    return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="{table_ns}">

    <sql id="ifConditionSql">
{where_if}
    </sql>
    
    <sql id="pkConditionSql">
{where_pk_if}
    </sql>

    <sql id="columnsSql">
{columns_sql}
    </sql>

    <sql id="columnsWithAliasSql">
{columns_alias_sql}
    </sql>
    
    <sql id="pkColumnsSql">
{pks_sql}
    </sql>
    
    <sql id="pkColumnsWithAliasSql">
{pks_alias_sql}
    </sql>

    <sql id="valuesSql">
{values_sql}
    </sql>

    <sql id="valuesForeachSql">
{values_foreach_sql}
    </sql>

    <sql id="selectFromSql">
        SELECT
            <include refid="{table_ns}.columnsSql" />
        FROM {tname}
    </sql>

    <sql id="selectFromWithAliasSql">
        SELECT
            <include refid="{table_ns}.columnsWithAliasSql" />
        FROM {tname} AS {tname_alias}
    </sql>

    <sql id="whereSql">
        <where>
            <include refid="{table_ns}.ifConditionSql" />
        </where>
    </sql>

    <sql id="limitSql">
        <if test="size != null">
            LIMIT #{{size}} 
            <if test="page != null ">
                OFFSET (#{{size}}*(#{{page}}-1))
            </if>
        </if>
    </sql>
    
    <sql id="createSql">
        INSERT INTO {tname} (
            <include refid="{table_ns}.columnsSql" />
        )
        VALUES (
            <include refid="{table_ns}.valuesSql" />
        )
    </sql>
    
    <sql id="createListSql">
        INSERT INTO {tname} (
            <include refid="{table_ns}.columnsSql" />
        )
        VALUES
        <include refid="{table_ns}.valuesForeachSql" />
    </sql>

    <sql id="updateSelectiveSet">
{update_set}
    </sql>

    <sql id="updateSelectiveSql">
        <include refid="{table_ns}.updateSelectiveSet" />
        <where>
{update_where}
        </where>
    </sql>

    <sql id="updateForceSql" >
{update_set_force}
        <where>
            <include refid="{table_ns}.pkConditionSql" />
        </where>
    </sql>

    <sql id="deleteSql">
        DELETE FROM {tname}
        <where>
            <include refid="{table_ns}.ifConditionSql" />
        </where>
    </sql>
    
    <sql id="deleteByKeySql">
        DELETE FROM {tname}
        <where>
            <include refid="{table_ns}.pkConditionSql" />
        </where>
    </sql>

    <sql id="returningSql">
        RETURNING <include refid="{table_ns}.columnsSql" />
    </sql>
    
    <sql id="returningWithAliasSql">
        RETURNING <include refid="{table_ns}.columnsWithAliasSql" />
    </sql>
    
    <sql id="onConflictKeyDoUpdateSql">
        ON CONFLICT (
            <include refid="{table_ns}.pkColumnsSql" />
        ) DO UPDATE
    </sql>
    
    <sql id="onConflictKeyDoNothingSql">
        ON CONFLICT (
            <include refid="{table_ns}.pkColumnsSql" />
        ) DO NOTHING
    </sql>
</mapper>

""".format(table_ns=table_ns
           , where_if=where_if
           , where_pk_if=where_pk_if
           , columns_sql=columns_sql
           , columns_alias_sql=columns_alias_sql
           , pks_sql=pks_sql
           , pks_alias_sql=pks_alias_sql
           , values_sql=values_sql
           , values_foreach_sql=values_foreach_sql
           , update_set=update_set
           , update_set_force=update_set_force
           , update_where=update_where
           , tname=tname
           , tname_alias=tname_alias)


def make_xml_ex(_c_info, _p_info, table, fields, mapper_package, model_package):
    global _column_info
    global _package_path_info
    _column_info = _c_info
    _package_path_info = _p_info

    table_ns = table.table_namespace
    table_class_name = common.to_class_name(table.table_name)

    sequence_xml = ''
    if table.sequence is not None:
        seq_cls_name = common.to_class_name(table.sequence)
        sequence_xml = """
    <select id="getNext{seq_cls_name}" resultType="java.lang.Long" useCache="false" flushCache="true">
        SELECT NEXTVAL('{sequence_name}')
    </select>
    <select id="getLast{seq_cls_name}" resultType="java.lang.Long" useCache="false" flushCache="true">
        SELECT CURRVAL('{sequence_name}')
    </select>
    <select id="setLast{seq_cls_name}" parameterType="java.lang.Long" resultType="java.lang.Long" useCache="false" flushCache="true">
        SELECT SETVAL('{sequence_name}', #{{_parameter}})
    </select>
""".format(seq_cls_name=seq_cls_name
           , sequence_name=table.sequence)

    return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="{mapper_package}.{table_class_name}Mapper">

    <sql id="selectSql">
        <include refid="{table_ns}.selectFromSql" />
        <where>
            <include refid="{table_ns}.ifConditionSql" />
        </where>
        <include refid="{table_ns}.limitSql" />
    </sql>

    <select id="read{table_class_name}" parameterType="{model_package}.{table_class_name}" resultType="{model_package}.{table_class_name}">
        <include refid="selectSql" />
    </select>

    <select id="read{table_class_name}ByKey" resultType="{model_package}.{table_class_name}">
        <include refid="{table_ns}.selectFromSql" />
        <where>
            <include refid="{table_ns}.pkConditionSql" />
        </where>
    </select>

    <select id="list{table_class_name}" parameterType="{model_package}.{table_class_name}" resultType="{model_package}.{table_class_name}">
        <include refid="selectSql" />
    </select>
    
    <insert id="create{table_class_name}" parameterType="{model_package}.{table_class_name}">
        <include refid="{table_ns}.createSql" />
    </insert>
    
    <select id="create{table_class_name}Return" parameterType="{model_package}.{table_class_name}" resultType="{model_package}.{table_class_name}">
        <include refid="{table_ns}.createSql" />
        <include refid="{table_ns}.returningSql" />
    </select>

    <insert id="create{table_class_name}List" parameterType="java.util.List">
        <include refid="{table_ns}.createListSql" />
    </insert>

    <update id="update{table_class_name}" parameterType="{model_package}.{table_class_name}">
        <include refid="{table_ns}.updateSelectiveSql" />
    </update>

    <select id="update{table_class_name}Return" parameterType="{model_package}.{table_class_name}" resultType="{model_package}.{table_class_name}">
        <include refid="{table_ns}.updateSelectiveSql" />
        <include refid="{table_ns}.returningSql" />
    </select>

    <update id="updateForce" parameterType="{model_package}.{table_class_name}">
        <include refid="{table_ns}.updateForceSql" />
    </update>

    <select id="updateForceReturn" parameterType="{model_package}.{table_class_name}" resultType="{model_package}.{table_class_name}">
        <include refid="{table_ns}.updateForceSql" />
        <include refid="{table_ns}.returningSql" />
    </select>

    <delete id="delete{table_class_name}" parameterType="{model_package}.{table_class_name}">
        <include refid="{table_ns}.deleteSql" />
    </delete>

    <delete id="delete{table_class_name}ByKey">
        <include refid="{table_ns}.deleteByKeySql" />
    </delete>

    {sequence_xml}

    <!--
    #############################################################
    #
    # Please fill out the new SQLs below.
    #
    #############################################################
    -->
</mapper>

""".format(mapper_package=mapper_package
           , model_package=model_package
           , table_ns=table_ns
           , table_class_name=table_class_name
           , sequence_xml=sequence_xml)
