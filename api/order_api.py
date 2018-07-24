# -*- coding: utf-8 -*-

from flask import jsonify, request, current_app as app
from datetime import datetime as dte
from api import api
from app import rpc
from flask_util import RequestData, login_required
from flask.views import MethodView


class OrderAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        data = rpc.invbox.get_orders(page=rdata.page,
                                     page_size=rdata.page_size,
                                     query=rdata.condition,
                                     base_url=app.config["DOMAIN"])
        return jsonify(data)


@api.route("/admin/order/overview")
@login_required
def order_overview():
    now = dte.now()
    page = int(request.args.get("page", "1"))

    start_date = request.args.get("startDate", "")
    end_date = request.args.get("endDate", "")
    if not start_date:
        start_date = "%4d-%02d-%02d" % (now.year, now.month, 1)

    if not end_date:
        end_date = "%4d-%02d-%02d" % (now.year, now.month, now.day)
    data = rpc.invbox.order_overview(start_date, end_date, page=page)
    return jsonify(data)


api.add_url_rule('/admin/order', view_func=OrderAPI.as_view('order'))
