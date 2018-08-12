# -*- coding: utf-8 -*-

from flask import jsonify, current_app
from api import api
from app import rpc
from flask_util import RequestData, login_required, HttpError, current_user
from flask.views import MethodView


class OverviewAPI(MethodView):

    def init_params(self):
        rdata = RequestData()
        self.stype = rdata["type"]
        self.start_date = rdata["startDate"]
        self.end_date = rdata["endDate"]
        self.item = rdata.get("item", default=None)
        self.device = rdata.get("device", default=None)
        self.user_group = rdata.get("userGroup", default=None)

    @login_required
    def get(self):
        "关键指标"
        self.init_params()
        stype = self.stype

        if stype == "item":
            panels = self.get_item_overview()
        elif stype == "order":
            panels = self.get_order_overview()
        elif stype == "device":
            panels = self.get_device_overview()
        elif stype == "user":
            panels = self.get_user_overview()
        else:
            raise HttpError(400, "未实现")

        res = {
            "startDate": self.start_date,
            "endDate": self.end_date,
            "panels": panels
        }
        return jsonify(res)

    def get_user_overview(self,):
        stats = rpc.invbox.stat_overview_of_user(self.start_date,
                                                 self.end_date,
                                                 user_group=self.user_group)
        if stats["resultCode"]:
            raise HttpError(400, stats["resultMsg"])
        panels = [
            {
                "title": "总用户",
                "value": stats["totalUsers"],
                "subTitle": "",
                "subValue": "",
            },
            {
                "title": "活跃用户",
                "value": stats["totalActives"],
                "subTitle": "日活跃",
                "subValue": stats["avgActives"]
            },
            {
                "title": "净增购买用户",
                "value": stats["totalRegisters"],
                "subTitle": "日净增",
                "subValue": stats["avgRegisters"]
            },
            {
                "title": "留存率",
                "value": stats["retention"],
                "subTitle": "",
                "subValue": ""
            },
        ]
        return panels

    def get_item_overview(self,):
        stats = rpc.invbox.stat_overview_of_item(self.start_date,
                                                 self.end_date,
                                                 item=self.item)
        if stats["resultCode"]:
            raise HttpError(400, stats["resultMsg"])
        panels = [
            {
                "title": "总访问量",
                "value": stats["totalClicks"],
                "subTitle": "日均访问量",
                "subValue": stats["avgClicks"]
            },
            {
                "title": "总访客数",
                "value": stats["totalVisitors"],
                "subTitle": "日均访客数",
                "subValue": stats["avgVisitors"]
            },
            {
                "title": "支付笔数",
                "value": stats["totalOrdersPay"],
                "subTitle": "日支付笔数",
                "subValue": stats["avgOrdersPay"]
            },
            {
                "title": "平均购物转化率",
                "value": stats["conversion"],
                "subTitle": "",
                "subValue": ""
            },
        ]
        return panels

    def get_device_overview(self,):
        stats = rpc.invbox.stat_overview_of_device(self.start_date,
                                                   self.end_date,
                                                   device=self.device)
        if stats["resultCode"]:
            raise HttpError(400, stats["resultMsg"])
        panels = [
            {
                "title": "总访问量",
                "value": stats["totalClicks"],
                "subTitle": "日均访问量",
                "subValue": stats["avgClicks"]
            },
            {
                "title": "总访客数",
                "value": stats["totalVisitors"],
                "subTitle": "日均访客数",
                "subValue": stats["avgVisitors"]
            },
            {
                "title": "支付笔数",
                "value": stats["totalOrdersPay"],
                "subTitle": "日支付笔数",
                "subValue": stats["avgOrdersPay"]
            },
            {
                "title": "平均购物转化率",
                "value": stats["conversion"],
                "subTitle": "",
                "subValue": ""
            },
        ]
        return panels

    def get_order_overview(self,):
        stats = rpc.invbox.stat_overview_of_order(self.start_date, self.end_date)
        if stats["resultCode"]:
            raise HttpError(400, stats["resultMsg"])

        panels = [
            {
                "title": "总销售额",
                "value": stats["totalSalesVolume"],
                "subTitle": "日均销售额",
                "subValue": stats["avgSalesVolume"]
            },
            {
                "title": "支付客户数",
                "value": stats["totalUsersPay"],
                "subTitle": "日均客户数",
                "subValue": stats["avgUsersPay"]
            },
            {
                "title": "支付笔数",
                "value": stats["totalOrdersPay"],
                "subTitle": "日支付笔数",
                "subValue": stats["avgOrdersPay"]
            },
            {
                "title": "客单价",
                "value": stats["userUnitPrice"],
                "subTitle": "",
                "subValue": ""
            },
        ]
        return panels


class TrendAPI(MethodView):

    def init_params(self):
        rdata = RequestData()
        self.stype = rdata["type"]
        self.start_date = rdata["startDate"]
        self.end_date = rdata["endDate"]
        self.item = rdata.get("item", default=None)
        self.device = rdata.get("device", default=None)
        self.user_group = rdata.get("userGroup", default=None)

    @login_required
    def get(self):
        self.init_params()
        stype = self.stype

        if stype == "item":
            chart_keys, table_keys, values = self.get_item_trend()
        elif stype == "order":
            chart_keys, table_keys, values = self.get_order_trend()
        elif stype == "device":
            chart_keys, table_keys, values = self.get_device_trend()
        elif stype == "user":
            chart_keys, table_keys, values = self.get_user_trend()
        else:
            raise HttpError(400, "未实现")

        return jsonify({
            "lineChartKeys": chart_keys,
            "tableKeys": table_keys,
            "values": values,
            "startDate": self.start_date,
            "endDate": self.end_date,
        })

    def get_user_trend(self):
        stats = rpc.invbox.stat_trend_of_user(self.start_date,
                                              self.end_date,
                                              user_group=self.user_group)
        if stats["resultCode"]:
            raise HttpError(400, stats["resultMsg"])

        chart_keys = [
            {
                "title": "总数量",
                "name": "users",
            },
            {
                "title": "活跃数",
                "name": "actives",
            },
            {
                "title": "新增数",
                "name": "registers",
            },
        ]
        table_keys = chart_keys[:]
        table_keys.extend([
            {
                "title": "销售额",
                "name": "salesVolume",
            },
            {
                "title": "客单价",
                "name": "userUnitPrice",
            },
        ])

        values = []
        for info in stats["days"]:
            values.append({
                "day": info["day"],
                "users": info["users"],
                "actives": info["actives"],
                "registers": info["registers"],
                "salesVolume": info["salesVolume"],
                "userUnitPrice": info["userUnitPrice"]
            })
        return chart_keys, table_keys, values

    def get_item_trend(self):
        stats = rpc.invbox.stat_trend_of_item(self.start_date,
                                              self.end_date,
                                              item=self.item)
        if stats["resultCode"]:
            raise HttpError(400, stats["resultMsg"])

        chart_keys = [
            {
                "title": "访问量",
                "name": "clicks",
            },
            {
                "title": "访客数",
                "name": "visitors",
            },
            {
                "title": "支付数",
                "name": "ordersPay",
            },
        ]
        table_keys = chart_keys[:]
        table_keys.extend([
            {
                "title": "转化率",
                "name": "conversion",
            },
            {
                "title": "客单数",
                "name": "usersPay",
            },
        ])

        values = []
        for info in stats["days"]:
            values.append({
                "day": info["day"],
                "clicks": info["clicks"],
                "visitors": info["visitors"],
                "usersPay": info["usersPay"],
                "ordersPay": info["ordersPay"],
                "conversion": info["conversion"]
            })
        return chart_keys, table_keys, values

    def get_device_trend(self):
        stats = rpc.invbox.stat_trend_of_device(self.start_date,
                                                self.end_date,
                                                device=self.device)
        if stats["resultCode"]:
            raise HttpError(400, stats["resultMsg"])

        chart_keys = [
            {
                "title": "访问量",
                "name": "clicks",
            },
            {
                "title": "访客数",
                "name": "visitors",
            },
            {
                "title": "支付数",
                "name": "ordersPay",
            },
        ]
        table_keys = chart_keys[:]
        table_keys.extend([
            {
                "title": "转化率",
                "name": "conversion",
            },
            {
                "title": "客单数",
                "name": "usersPay",
            },
        ])

        values = []
        for info in stats["days"]:
            values.append({
                "day": info["day"],
                "clicks": info["clicks"],
                "visitors": info["visitors"],
                "usersPay": info["usersPay"],
                "ordersPay": info["ordersPay"],
                "conversion": info["conversion"]
            })
        return chart_keys, table_keys, values

    def get_order_trend(self):
        stats = rpc.invbox.stat_trend_of_order(self.start_date,
                                               self.end_date)
        if stats["resultCode"]:
            raise HttpError(400, stats["resultMsg"])

        chart_keys = [
            {
                "title": "访问量",
                "name": "clicks",
            },
            {
                "title": "访客数",
                "name": "visitors",
            },
            {
                "title": "支付数",
                "name": "ordersPay",
            },
        ]
        table_keys = chart_keys[:]
        table_keys.extend([
            {
                "title": "转化率",
                "name": "conversion",
            },
            {
                "title": "销售额",
                "name": "salesVolume",
            },
            {
                "title": "客单价",
                "name": "userUnitPrice",
            },
        ])

        values = []
        for info in stats["days"]:
            values.append({
                "day": info["day"],
                "clicks": info["clicks"],
                "visitors": info["visitors"],
                "ordersPay": info["ordersPay"],
                "conversion": info["conversion"],
                "salesVolume": info["salesVolume"],
                "userUnitPrice": info["userUnitPrice"],
            })
        return chart_keys, table_keys, values


class TableAPI(MethodView):

    def init_params(self):
        rdata = RequestData()
        self.stype = rdata["type"]
        self.start_date = rdata["startDate"]
        self.end_date = rdata["endDate"]
        self.item = rdata.get("item", default=None)

    @login_required
    def get(self):
        self.init_params()
        stype = self.stype
        if stype == "item":
            columns, values = self.get_item_table()
        if stype == "user":
            columns, values = self.get_user_table()
        else:
            raise HttpError(400, "未实现")

        return jsonify({
            "columns": columns,
            "values": values,
        })

    def get_user_table(self):
        stats = rpc.invbox.stat_day_of_user(self.start_date, self.end_date)
        if stats["resultCode"]:
            raise HttpError(400, stats["resultMsg"])
        columns = [
            {
                "title": "用户群",
                "name": "userGroupName",
            },
            {
                "title": "总数量",
                "name": "users",
            },
            {
                "title": "活跃数",
                "name": "actives",
            },
            {
                "title": "新增数",
                "name": "registers",
            },
            {
                "title": "留存率",
                "name": "retention",
            },
            {
                "title": "销售额",
                "name": "salesVolume",
            },
            {
                "title": "客单价",
                "name": "userUnitPrice",
            },
        ]

        values = []
        for info in stats["items"]:
            values.append({
                "userGroupId": info["userGroupId"],
                "userGroupName": info["userGroupName"],
                "users": info["users"],
                "actives": info["actives"],
                "registers": info["registers"],
                "userUnitPrice": info["userUnitPrice"],
                "salesVolume": info["salesVolume"],
                "retention": info["retention"],
            })
        return columns, values

    def get_item_table(self):
        stats = rpc.invbox.stat_day_of_item(self.start_date, self.end_date)
        if stats["resultCode"]:
            raise HttpError(400, stats["resultMsg"])
        columns = [
            {
                "title": "商品编号",
                "name": "itemNo",
            },
            {
                "title": "商品名称",
                "name": "itemName",
            },
            {
                "title": "访问量",
                "name": "clicks",
            },
            {
                "title": "访客数",
                "name": "visitors",
            },
            {
                "title": "支付数",
                "name": "usersPay",
            },
            {
                "title": "转化率",
                "name": "conversion",
            },
            {
                "title": "客单数",
                "name": "usersPay",
            },
        ]

        values = []
        for info in stats["items"]:
            values.append({
                "itemNo": info["itemNo"],
                "itemName": info["itemName"],
                "clicks": info["clicks"],
                "visitors": info["visitors"],
                "usersPay": info["usersPay"],
                "ordersPay": info["ordersPay"],
                "conversion": info["conversion"]
            })
        return columns, values


class ConversionAPI(MethodView):

    def init_params(self):
        rdata = RequestData()
        self.stype = rdata["type"]
        self.start_date = rdata["startDate"]
        self.end_date = rdata["endDate"]
        self.item = rdata.get("item", default=None)

    @login_required
    def get(self):
        self.init_params()
        stype = self.stype

        if stype == "order":
            stats = self.get_order_conversion()
        else:
            raise HttpError(400, "未实现")

        return jsonify({
            "startDate": self.start_date,
            "endDate": self.end_date,
            "stats": stats
        })

    def get_order_conversion(self):
        stats = rpc.invbox.stat_conversion_of_order(self.start_date, self.end_date)
        if stats["resultCode"]:
            raise HttpError(400, stats["resultMsg"])
        stats = [
            {
                "title": "人流量",
                "name": "flows",
                "value": stats["totalFlows"],
            },
            {
                "title": "停留人数",
                "name": "stays",
                "value": stats["totalStays"],
            },
            {
                "title": "进入结算页",
                "name": "ordersCreate",
                "value": stats["totalOrdersCreate"],
            },
            {
                "title": "付款成功",
                "name": "ordersPay",
                "value": stats["totalOrdersPay"]
            },
        ]
        return stats


@api.route("/admin/stats/flows")
@login_required
def day_device_stats():
    rdata = RequestData()
    if current_user.get("role") == 1 or current_user.get("role") == 2:
        return jsonify({
            "resultCode": 1,
            "resultMsg": "补货员和场地方没有流量查看权限"
        })
    admin_info = {"id": current_user["id"],
                  "role": current_user["role"]}

    data = rpc.invbox.get_flow_stats(page=rdata.page,
                                     page_size=rdata.page_size,
                                     query=rdata.condition,
                                     base_url=current_app.config["DOMAIN"],
                                     admin_info=admin_info
                                     )
    return jsonify(data)


@api.route("/admin/dashboard/<string:scale>")
@login_required
def dashboard(scale):
    data = {}
    if scale == "flows":
        data = rpc.invbox.dashboard_flow_volume()
    if scale == "flowsRank":
        data = rpc.invbox.dashboard_flow_volume_rank()
    if scale == "userStats":
        data = rpc.invbox.dashboard_user_stats()
    if scale == "deviceStats":
        data = rpc.invbox.dashboard_device_stats()
    if scale == "salesStats":
        data = rpc.invbox.dashboard_sales_stats()
    if scale == "itemDeviceRank":
        data = rpc.invbox.dashboard_item_device_rank()
    if scale == "payConversionTrend":
        data = rpc.invbox.dashboard_pay_conversion_trend()

    return jsonify(data)


api.add_url_rule('/admin/stat/overview', view_func=OverviewAPI.as_view('StatOverview'))
api.add_url_rule('/admin/stat/trend', view_func=TrendAPI.as_view('StatTrend'))
api.add_url_rule('/admin/stat/table', view_func=TableAPI.as_view('StatTable'))
api.add_url_rule('/admin/stat/conversion', view_func=ConversionAPI.as_view('StatConversion'))
