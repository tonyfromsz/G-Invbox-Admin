# -*- coding: utf-8 -*-
import datetime
import logging
from flask import send_file, request
from api import api
from flask_util import RequestData, HttpError, login_required
from flask import jsonify
from app import rpc
from util import to_xlsx, Xlsx

log = logging.getLogger(__name__)

data_mapping = {"order": rpc.invbox.get_export_order,
                "inventory": rpc.invbox.get_export_inventory,
                "user-monitor": rpc.invbox.get_export_user_monitor}

xlsx = Xlsx()


@api.route("/export/<string:item>")
@login_required
def export(item):
    if item not in data_mapping.keys():
        return jsonify({"code": -1, "message": "错误的参数", "data": {}})
    data_function = data_mapping[item]
    new_args = request.args
    # if not new_args:
    #     return jsonify({"code": -1, "message": "缺少必要参数", "data": {}})
    output = xlsx.run(data_function=data_function, new_args=new_args,
                      item=item)
    if not output:
        return jsonify({"code": -1, "message": "无数据", "data": {}})
    date_string = datetime.date.today().strftime("%Y%m%d_")
    filename = date_string + xlsx.xslx_mapping[item].get("filename")
    return send_file(output,
                     mimetype="",
                     as_attachment=True,
                     attachment_filename="%s.xlsx" % (bytes(filename).decode("latin-1")))
    pass