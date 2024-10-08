#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

######################################################################################
# 전역 변수
######################################################################################


__IS_VERSION_3__ = sys.version_info.major == 3
__IS_WINDOW__ = os.name == 'Windows' or os.name == 'nt'
__GEN_TARGET__ = ['domain', 'mapper', 'xml']
__TEMP_DIR__ = 'C:\\Temp\generator' if __IS_WINDOW__ else os.path.join(os.path.expanduser("~"), "Temp", "generator")

_SP4 = ' ' * 4
_SP8 = ' ' * 8
_SP12 = ' ' * 12

######################################################################################
# 디비 접속 정보
######################################################################################

DB_ENGIN = ['postgresql', 'mysql']

# gen 작업 디비 접속 옵션
DB_CONNECTION_OPTS = {
    'engin': DB_ENGIN[1]
    , 'options': {
        'host': 'metamarketing-instance-1.cnzcxy7quzcs.ap-northeast-2.rds.amazonaws.com'
        , 'port': 3306
        , 'database': 'metamarket'
        , 'user': 'adopadmin'
        , 'password': 'Adop*^14'
    }
}

# 스키마 비교 대상 디비 접속 옵션
CMP_DB_CONNECTIONS_OPTS = [
    {
        'engin': DB_ENGIN[0]
        , 'user': 'mainn'
        , 'password': 'qhdks@00'
        , 'host': '192.168.10.11'
        , 'port': 8433
        , 'database': 'mainn'
    },
    {
        'engin': DB_ENGIN[0]
        , 'user': 'mainn'
        , 'password': 'qhdks@00'
        , 'host': '192.168.10.240'
        , 'port': 15432
        , 'database': 'mainn'
    }
]

# 디비 스키마
DB_SCHEMA = "public"

######################################################################################
# Enum <-> Columns 매핑
######################################################################################
# enum_name = interface_package
ENUM_TYPE_INTERFACE_PACKAGE = {}

# FIELD_NAME_ENUM_TYPES[column_name] = enum_name
FIELD_NAME_ENUM_TYPES = {}
FIELD_NAME_ENUM_TYPES['ACNT_STTS_CD'] = 'ACNT_STTS_CD'
FIELD_NAME_ENUM_TYPES['LOGIN_PRVNT_STTS_CD'] = 'LOGIN_PRVNT_STTS_CD'
FIELD_NAME_ENUM_TYPES['SVC_STTS_CD'] = 'SVC_STTS_CD'
FIELD_NAME_ENUM_TYPES['MENU_TYPE_CD'] = 'MENU_TYPE_CD'
FIELD_NAME_ENUM_TYPES['DATA_TYPE_CD'] = 'DATA_TYPE_CD'
FIELD_NAME_ENUM_TYPES['EMP_POS_CD'] = 'EMP_POS_CD'
FIELD_NAME_ENUM_TYPES['GENDER_TYPE_CD'] = 'GENDER_TYPE_CD'
FIELD_NAME_ENUM_TYPES['EMP_JOBRESP_CD'] = 'EMP_JOBRESP_CD'
FIELD_NAME_ENUM_TYPES['EMP_SCHDL_TYPE_CD'] = 'EMP_SCHDL_TYPE_CD'
FIELD_NAME_ENUM_TYPES['OFCL_SCHDL_TYPE_CD'] = 'EMP_SCHDL_TYPE_CD'
FIELD_NAME_ENUM_TYPES['BREAK_TYPE_CD'] = 'BREAK_TYPE_CD'
FIELD_NAME_ENUM_TYPES['ANNUAL_LEAVE_TYPE_CD'] = 'ANNUAL_LEAVE_TYPE_CD'
FIELD_NAME_ENUM_TYPES['CNTRY_TYPE_CD'] = 'CNTRY_TYPE_CD'
FIELD_NAME_ENUM_TYPES['CITY_TYPE_CD'] = 'CITY_TYPE_CD'
FIELD_NAME_ENUM_TYPES['TRNSP_TYPE_CD'] = 'TRNSP_TYPE_CD'
FIELD_NAME_ENUM_TYPES['MET_ATTND_METHOD_CD'] = 'MET_ATTND_METHOD_CD'
FIELD_NAME_ENUM_TYPES['DOCU_TYPE_CD'] = 'DOCU_TYPE_CD'
FIELD_NAME_ENUM_TYPES['PROJECT_TYPE_CD'] = 'PROJECT_TYPE_CD'
FIELD_NAME_ENUM_TYPES['TECH_LEVEL_CD'] = 'TECH_LEVEL_CD'
FIELD_NAME_ENUM_TYPES['RNR_POS_CDS'] = 'RNR_POS_CD'
FIELD_NAME_ENUM_TYPES['MESSAGE_TYPE_CD'] = 'MESSAGE_TYPE_CD'
FIELD_NAME_ENUM_TYPES['MESSAGE_TPL_TYPE_CD'] = 'MESSAGE_TPL_TYPE_CD'
FIELD_NAME_ENUM_TYPES['DYNAMIC_CD'] = 'DYNAMIC_CD'
