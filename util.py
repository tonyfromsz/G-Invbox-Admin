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


def to_xlsx(titles, mapping, filename=None, body=None):
    assert isinstance(titles, list) and isinstance(mapping, list)
    # if not body:
    #     return
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

    # file_name = app.config["MEDIA_PATH"] + "/" + filename + ".xlsx"
    # workbook = xlsxwriter.Workbook(filename=file_name)
    # worksheet = workbook.add_worksheet()
    # worksheet.write_row(0, 0, titles)
    # for i, record in enumerate(body):
    #     item = [record.get(key) for key in mapping]
    #     worksheet.write_row(i+1, 0, data=item)
    # workbook.close()
    # return filename



class Xlsx:
    def __init__(self):
        self.xslx_mapping = {
            "order": {
                "map": ["year", "month", "day",
                        "device_id", "address_type",
                        "user_id", "user_mobile", "wx_ali_user_id", "user_name",
                        "item_no", "item_brand", "item_name", "count", "pay_money", "consume_code"],
                "titles": ["年", "月", "日",
                           "小粉盒ID", "点位",
                           "小粉盒ID（会员一级ID）", "手机号（会员二级ID）", "微信号/支付宝ID（会员三级ID）", "用户名（默认的微信名）",
                           "商品编号", "商品品牌", "产品名", "购买数量", "支付金额", "兑换码"],
                "filename": "invbox_orders"
            },
            "inventory": {
                "map": ["year", "month", "day", "hour", "minute", "second",
                        "device_id", "address_type", "road_id", "item_name", "amount"],
                "title": ["年", "月", "日", "时", "分",
                          "小粉盒ID", "小粉盒所在地", "货道ID", "产品名称", "剩余库存"],
                "filename": "invbox_invents"
            },
            "user-monitor": {
                "map": ["", "", "", "", "",
                           "", "", "", "", "",
                           "", "", ""],
                "titles": ["起始年", "月", "日", "时", "分",
                           "截止年", "月", "日", "时", "分",
                           "触达用户数", "深度触达用户数", "互动用户数"],
                "filename": "invbox_user_monitor"
            }
        }

    def run(self, data, item, filename=None):
        # assert callable(function)
        data_dict = self.xslx_mapping[item]
        titles = data_dict.get("titles")
        mapping = data_dict.get("map")
        for field in data["del_field"]:
            mapping.remove(field)
        for field in data["del_tb_field"]:
            titles.remove(field)
        body = data["data"]
        out_put = to_xlsx(body=body, titles=titles, mapping=mapping)
        # out_put = to_xlsx(body=body, titles=titles, mapping=mapping, filename=filename)
        if not out_put:
            return
        else:
            return out_put
        # out_put = to_xlsx(body=body, titles=titles, mapping=mapping, filename=filename)
        # return out_put
