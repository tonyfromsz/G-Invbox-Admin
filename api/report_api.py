# -*- coding: utf-8 -*-
import datetime
import logging
from api_service import Report
from flask import send_file, request, current_app, send_from_directory, make_response, Response
from api import api
from flask_util import RequestData, HttpError, login_required, current_user
from flask import jsonify
from app import rpc
from util import to_xlsx, Xlsx


log = logging.getLogger(__name__)

Rpt = Report()

data_mapping = {"order": Rpt.order_export_handling,
                "inventory": Rpt.inventory_export_handling,
                "user-monitor": Rpt.flow_stat_export_handling
                }

xlsx = Xlsx()


@api.route("/media/export/<string:item>")
@login_required
def export(item):
    if item not in data_mapping.keys():
        return jsonify({
            "resultCode": 1,
            "resultMsg": "错误的参数%s" % item
        })
    rdata = RequestData()
    data = data_mapping[item](rdata)

    role = current_user.get("role")
    username = current_user.get("username")

    if not username:
        username = ""

    if role in [0, 1, 2, 3]:
        role_string = "role" + str(role)
    else:
        role_string = ""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M_")

    filename = timestamp + username + "_" + role_string + "_" + xlsx.xslx_mapping[item].get("filename")
    # output = xlsx.run(data=data, item=item, filename=filename)
    output = xlsx.run(data=data, item=item)
    if not output:
        return jsonify({"resultCode": 1, "resultMsg": "无数据"})

    return send_file(output,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True,
                     attachment_filename="%s.xlsx" % filename)
    # print(file_dir + "/" + filename + '.xlsx')
    # return jsonify({"1":"haha"})
    # return send_from_directory(directory=current_app.config["MEDIA_PATH"],
    #                            filename=filename+'.xlsx',
    #                            as_attachment=True,
    #                            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    #                            attachment_filename="%s.xlsx" % (bytes(filename).decode("latin-1"))
    #                            )
                         # )



@api.route("/export/test")
def test():
    new_args = request.args
    result = rpc.invbox.get_test_data(new_args)
    return jsonify({"code": 1, "message": "成功", "data": result})