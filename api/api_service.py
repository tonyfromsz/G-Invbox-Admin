# -*- coding: utf-8 -*-

import datetime as dte
from flask import current_app as app
from flask_util import current_user, jsonify
from app import rpc


class Report:

    def order_export_handling(self, rdata):
        if current_user["role"] not in [0, 2, 3]:
            return jsonify({
                "resultCode": 1,
                "resultMsg": "补货员没有订单导出订单数据权限"
            })
        admin_info = {"id": current_user["id"],
                      "role": current_user["role"]}
        data = rpc.invbox.get_orders(query=rdata.condition,
                                     base_url=app.config["DOMAIN"],
                                     admin_info=admin_info,
                                     export=True
                                     )
        result = []
        for rec in data["items"]:
            device = rec["device"]
            item = rec["item"]
            redeem = rec["redeem"]
            road = rec["road"]
            user = rec["user"]
            wxuserid = user.get("wxuserid") or ""
            aliuserid = user.get("aliuserid") or ""

            create_at = dte.datetime.strptime(rec["createdAt"], "%Y-%m-%d %H:%M:%S")

            record = {
                "year": create_at.year,      # 年
                "month": create_at.month,    # 月
                "day": create_at.day,        # 日
                "device_id": device["id"],          # 小粉盒ID
                "address_type": device["address"],    # 点位
                "user_id": user["id"],              # 后台会员ID
                "user_mobile": user["mobile"],      # 手机号
                "wx_ali_user_id": wxuserid + "/" + aliuserid,   # 微信号/支付宝id
                "user_name": user["username"],      # 用户名
                "item_no": item["no"],              # 商品编号
                "item_brand": item["brand_name"],   # 商品品牌
                "item_name": item["name"],          # 产品名
                "count": rec["count"],             # 购买数量
                "pay_money": rec["payMoney"],      # 支付金额
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

    def inventory_export_handling(self, rdata):
        admin_info = {
            "id": current_user["id"],
            "role": current_user["role"]
        }
        data = rpc.invbox.get_roads(query=rdata.condition,
                                    base_url=app.config["DOMAIN"],
                                    admin_info=admin_info,
                                    export=True)
        print("data", data)
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


def monitor_export_handling():
    pass