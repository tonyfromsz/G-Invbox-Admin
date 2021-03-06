# -*- coding: utf-8 -*-

import datetime as dte
from flask import current_app as app
from flask_util import current_user, jsonify
from app import rpc

order_status_dict = {
    1: "等待付款",
    2: "已付款；出货中",
    3: "出货成功",
    10: "订单失效",
    11: "出货失败",
    13: "退款完成",
    15: "出货超时"
}


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
        if data.get("items"):
            for rec in data.get("items"):
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
                    "device_id": device.get("no"),          # 小粉盒ID
                    "address_type": device.get("address"),    # 点位
                    "user_id": user.get("id"),              # 后台会员ID
                    "user_mobile": user.get("mobile"),      # 手机号
                    "wx_ali_user_id": wxuserid + "/" + aliuserid,   # 微信号/支付宝id
                    "user_name": user.get("username"),      # 用户名
                    "item_no": item.get("no"),              # 商品编号
                    "item_brand": item.get("brand_name"),   # 商品品牌
                    "item_name": item.get("name"),          # 产品名
                    "count": rec.get("count"),             # 购买数量
                    "pay_money": rec.get("payMoney"),      # 支付金额
                    "consume_code": redeem.get("code"),    # 兑换吗
                    "order_status": order_status_dict.get(rec.get("status"))      # 订单状态
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
                "device_id": device.get("no"),
                "address_type": device.get("address"),
                "road_id": rec.get("no"),
                "item_name": item.get("name"),
                "amount": rec.get("amount")
            }
            result.append(record)
        return {
            "data": result,
            "del_field": [],
            "del_tb_field": []
        }

    def flow_stat_export_handling(self, rdata):
        admin_info = {
            "id": current_user["id"],
            "role": current_user["role"]
        }
        data = rpc.invbox.get_flow_stats(query=rdata.condition,
                                         base_url=app.config["DOMAIN"],
                                         admin_info=admin_info,
                                         export=True)
        # print("data", data)

        result = []
        for rec in data["items"]:
            date = rec["day"]
            record = {
                "year": date[:4],
                "month": date[5:7],
                "day": date[8:],
                "device": rec["device"],
                "address_type": rec["address_type"],
                "flows": rec["flows"],
                "stays": rec["stays"],
                "clicks": rec["clicks"],
            }
            result.append(record)
        return {
            "data": result,
            "del_field": [],
            "del_tb_field": []
        }