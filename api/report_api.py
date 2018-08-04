# -*- coding: utf-8 -*-
import datetime
import logging
import api_service as apiser
from flask import send_file, request
from api import api
from flask_util import RequestData, HttpError, login_required, current_user
from flask import jsonify
from app import rpc
from util import to_xlsx, Xlsx


log = logging.getLogger(__name__)

data_mapping = {"order": apiser.order_export_handling,
                "inventory": apiser.invnetory_export_handling,
                "user-monitor": apiser.monitor_export_handling
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
    pass


@api.route("/export/test")
def test():
    new_args = request.args
    result = rpc.invbox.get_test_data(new_args)
    return jsonify({"code": 1, "message": "成功", "data": result})