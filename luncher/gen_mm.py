#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append(os.path.abspath("../"))

import gen_mybatis_temp as gen

arguments = sys.argv
print(arguments)
gen_targets = []
category_targets = []
all_targets = True

for gt in arguments[1:]:
    if gt.startswith("-C"):
        all_targets = False
        category_targets.append(gt[2:])
    else:
        gen_targets.append(gt)

dir_path = os.path.dirname(os.path.realpath(__file__))
_package_path_info = gen.PackagePathInfo(
    xml_path='/Users/yjkim/project_source/_mm/MetaMarket/src/main/resources/mapper/core'
    , mapper_path='/Users/yjkim/project_source/_mm/MetaMarket/src/main/java/com/techlabs/platform/metamarketing/framework/core/mapper'
    , model_path='/Users/yjkim/project_source/_mm/MetaMarket/src/main/java/com/techlabs/platform/metamarketing/framework/core/domain'
    , base_domain_package='com.techlabs.platform.metamarketing.business.domain.BaseDomain'
    , enum_package='com.techlabs.platform.metamarketing.framework.gen.data.PlatformCodes'
    , domain_package='com.techlabs.platform.metamarketing.business.domain'
    , mapper_package='com.techlabs.platform.metamarketing.business.mapper'
    , core_domain_package='com.techlabs.platform.metamarketing.framework.core.domain'
    , core_mapper_package='com.techlabs.platform.metamarketing.framework.core.mapper'
)

_column_info = gen.ColumnInfo(
    is_remove_cd=False
    , is_remove_yn=False
    , is_use_date_format=True
    , is_use_time_format=True
    , base_domain_columns=['insert_dt', 'update_dt']
    , insert_dt_columns=['insert_dt', 'register_dt']
    , update_dt_columns=['update_dt']
    , delete_columns=['is_del']
)


def generate_mybatis_files():
    #########################################
    mapper_base_pkg = _package_path_info.mapper_package
    model_base_pkg = _package_path_info.domain_package
    #########################################

    category = 'report'
    if all_targets or category in category_targets:
        mapper_package = mapper_base_pkg + "." + category
        model_package = model_base_pkg + "." + category

        # gen.generate_mybatis(gen_targets,'테이블명', category, mapper_package, model_package, {
        #     'pk': '시퀀스명'
        #     , '필드명': {
        #         'field_name': ''
        #         , 'java_type': ''
        #         , 'json_props': ''
        #         , 'sequence_name': ''
        #     }
        # })

        gen.generate_mybatis(gen_targets,'i_daily_rev', category, mapper_package, model_package, {
            'pk': 'rev_id'
            # , 'id': {
            #     'field_name': ''
            #     , 'java_type': ''
            #     , 'json_props': ''
            #     , 'sequence_name': ''
            # }
        })


gen.set_base_info(_package_path_info, _column_info)
generate_mybatis_files()
