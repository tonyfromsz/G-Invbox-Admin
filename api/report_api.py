# -*- coding: utf-8 -*-
import datetime
import logging
import api_service as apiser
from flask import send_file, request, current_app
from api import api
from flask_util import RequestData, HttpError, login_required, current_user
from flask import jsonify
from app import rpc
from util import to_xlsx, Xlsx


log = logging.getLogger(__name__)


def _order_export_handling(rdata):
    if current_user["role"] not in [0, 2, 3]:
        return jsonify({
            "resultCode": 1,
            "resultMsg": "补货员没有订单导出订单数据权限"
        })
    admin_info = {"id": current_user["id"],
                  "role": current_user["role"]}
    data = rpc.get_orders(query=rdata.condition,
                          base_url=current_app.config["DOMAIN"],
                          admin_info=admin_info,
                          export=True
                          )
    result = []
    for rec in data["item"]:
        device = rec["device"]
        item = rec["item"]
        redeem = rec["redeem"]
        road = rec["road"]
        user = rec["user"]
        wxuserid = user.get("wxuserid") or ""
        aliuserid = user.get("aliuserid") or ""
        record = {
            "year": rec["createdAt"].year,      # 年
            "month": rec["createdAt"].month,    # 月
            "day": rec["createdAt"].day,        # 日
            "device_id": device["id"],          # 小粉盒ID
            "address_type": device["address"],    # 点位
            "user_id": user["id"],              # 后台会员ID
            "user_mobile": user["mobile"],      # 手机号
            "wx_ali_user_id": wxuserid + "/" + aliuserid,   # 微信号/支付宝id
            "user_name": user["username"],      # 用户名
            "item_no": item["no"],              # 商品编号
            "item_brand": item["brand_name"],   # 商品品牌
            "item_name": item["name"],          # 产品名
            "count": item["count"],             # 购买数量
            "pay_money": item["payMoney"],      # 支付金额
            "consume_code": redeem.get("code")  # 兑换吗
        }
        result.append(record)
    if current_user["role"] == 0:
        return {
            "data": result,
            "del_field": [],
            "del_tb_field": []
        }

    elif current_user["role"] == 2:
        return {
            "data": result,
            "del_field": ["user_id", "user_mobile", "wx_ali_user_id", "user_name"],
            "del_tb_field": ["小粉盒ID（会员一级ID）", "手机号（会员二级ID）", "微信号/支付宝ID（会员三级ID）",
                             "用户名（默认的微信名）"]
        }
    elif current_user["role"] == 3:
        return {
            "data": result,
            "del_field": ["user_mobile", "wx_ali_user_id", "user_name"],
            "del_tb_field": ["手机号（会员二级ID）", "微信号/支付宝ID（会员三级ID）", "用户名（默认的微信名）"]
        }


def _invnetory_export_handling(rdata):
    admin_info = {
        "id": current_user["id"],
        "role": current_user["role"]
    }
    data = rpc.get_roads(query=rdata.conditions,
                         base_url=current_app.config["DOMAIN"],
                         admin_info=admin_info,
                         export=True)
    result = []
    for rec in data["items"]:
        device = rec["device"]
        item = rec["item"]
        now = dte.datetime.now()
        record = {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
            "device_id": device["id"],
            "address_type": device["address_type"],
            "road_id": rec["id"],
            "item_name": item["name"],
            "amount": rec["amount"]
        }
        result.append(record)
    return {
        "data": result,
        "del_field": [],
        "del_tb_field": []
    }


data_mapping = {"order": _order_export_handling(),
                "inventory": _invnetory_export_handling(),
                # "user-monitor": apiser.monitor_export_handling
                }

xlsx = Xlsx()


@api.route("/export/<string:item>")
@login_required
def export(item):
    if item not in data_mapping.keys():
        return jsonify({
            "resultCode": 1,
            "resultMsg": "错误的参数%s" % item
        })

    rdata = RequestData()
    data = data_mapping[item](rdata)

    output = xlsx.run(data=data, item=item)
    if not output:
        return jsonify({"code": -1, "message": "无数据", "data": {}})
    date_string = datetime.date.today().strftime("%Y%m%d_")
    filename = date_string + xlsx.xslx_mapping[item].get("filename")
    return send_file(output,
                     mimetype="",
                     as_attachment=True,
                     attachment_filename="%s.xlsx" % (bytes(filename).decode("latin-1")))


@api.route("/export/test")
def test():
    new_args = request.args
    result = rpc.invbox.get_test_data(new_args)
    return jsonify({"code": 1, "message": "成功", "data": result})