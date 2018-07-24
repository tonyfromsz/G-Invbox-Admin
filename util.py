# -*- coding: utf-8 -*-

import hashlib
import os
import re
import xlrd
import xlsxwriter
from io import BytesIO

from flask import current_app as app


def md5(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()


def url_to_path(image_url):
    relpath = os.path.relpath(image_url, "/media")
    return os.path.join(app.config["MEDIA_PATH"], relpath)


def path_to_url(fullpath):
    relpath = os.path.relpath(fullpath, app.config["MEDIA_PATH"])
    return os.path.join("/media", relpath)


def is_mobile(number):
    rule = "^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\\d{8}$"
    if re.match(rule, number):
        return True
    return False


def to_xlsx(titles, mapping, body=None):
    assert isinstance(titles, list) and isinstance(mapping, list)
    if not body:
        return
    out_put = BytesIO()
    workbook = xlsxwriter.Workbook(out_put, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    worksheet.write_row(0, 0, titles)
    for i, record in enumerate(body):
        item = [record.get(key) for key in mapping]
        worksheet.write_row(i+1, 0, data=item)
    workbook.close()
    out_put.seek(0)
    return out_put


class Xlsx:
    def __init__(self):
        self.xslx_mapping = {
            "order": {
                "map": ["", "", "",
                        "", "",
                        "", "", "", "",
                        "", "", "", "", "", "", ""],
                "titles": ["年", "月", "日",
                           "小粉盒ID", "小粉盒所在地",
                           "小粉盒ID（会员一级ID）", "手机号（会员二级ID）", "用户名（默认的微信名）",
                           "商品编号", "商品品牌", "产品名", "购买数量", "支付金额", "兑换码"],
                "filename": "table_invbox_member_order"
            },
            "inventory": {
                "map": ["", "", "", "", "", "",
                        "", "", "", "", ""],
                "title": ["年", "月", "日", "时", "分",
                          "小粉盒ID", "小粉盒所在地", "货道ID", "产品名称", "剩余库存"],
                "filename": "table_invbox_current_inventory"
            },
            "user-monitor": {
                "map": ["", "", "", "", "",
                           "", "", "", "", "",
                           "", "", ""],
                "titles": ["起始年", "月", "日", "时", "分",
                           "截止年", "月", "日", "时", "分",
                           "触达用户数", "深度触达用户数", "互动用户数"],
                "filename": "table_invbox_user_monitor"
            }
        }

    def run(self, data_function, new_args, item):
        assert callable(function)
        body = data_function(**new_args)
        data_dict = self.xslx_mapping[item]
        out_put = to_xlsx(body=body.get('list'), titles=body.get('titles'), mapping=data_dict.get('map'))
        return out_put
