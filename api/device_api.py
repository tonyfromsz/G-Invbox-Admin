# -*- coding: utf-8 -*-

from flask import jsonify, request, current_app as app
from api import api
from app import rpc
from flask_util import HttpError, RequestData, login_required
from flask.views import MethodView


@api.route("/admin/device/involved", methods=["GET"])
@login_required
def device_list():
    rdata = RequestData()
    condition = rdata.condition
    devices = rpc.invbox.get_involved_devices(page=rdata.page,
                                              page_size=rdata.page_size,
                                              query=condition)
    return jsonify(devices)


@api.route("/admin/device/uninvolved", methods=["GET"])
@login_required
def uninvolved_device_list():
    """获取待接入设备列表"""
    rdata = RequestData()
    devices = rpc.invbox.get_uninvolved_devices(page=rdata.page,
                                                page_size=rdata.page_size,
                                                query=rdata.condition)
    return jsonify(devices)


@api.route("/admin/device/involved", methods=["POST"])
@login_required
def involve_device():
    """接入设备"""
    rdata = RequestData()
    id = rdata["id"]
    res = rpc.invbox.involve_device(id,
                                    name=rdata["name"],
                                    province=rdata["province"],
                                    city=rdata["city"],
                                    district=rdata["district"],
                                    address=rdata["address"],
                                    address_type_id=rdata["address_type"],
                                    supplyer_id=rdata["supplyer"])
    if res["resultCode"]:
        raise HttpError(400, res["resultMsg"])
    return ""


class DeviceCategoryAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        data = rpc.invbox.get_device_categories(page=rdata.page,
                                                page_size=rdata.page_size)
        return jsonify(data)

    @login_required
    def post(self):
        rdata = RequestData()
        name = rdata.get("name", type=str)
        if not name:
            raise HttpError(400, "名称不能为空")
        new = rpc.invbox.add_device_category(name, rdata["roadList"])

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])
        del new["resultCode"]
        del new["resultMsg"]
        return jsonify(new)

    @login_required
    def delete(self):
        rdata = RequestData()
        data = rpc.invbox.delete_categories(rdata.array)
        if data["resultCode"]:
            raise HttpError(400, data["resultMsg"])
        return ""

    @login_required
    def put(self):
        rdata = RequestData()
        params = []
        for d in rdata:
            name = rdata.base_get(d, "name", type=str)
            if not name:
                raise HttpError(400, "名称不能为空")
            params.append({
                "id": rdata.base_get(d, "id"),
                "name": name,
                "roadList": rdata.base_get(d, "roadList"),
            })
            for rd in d["roadList"]:
                rdata.base_get(rd, "upperLimit")
                rdata.base_get(rd, "lowerLimit")

        res = rpc.invbox.modify_device_categories(params)
        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


class AddressTypeAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        data = rpc.invbox.get_address_types(page=rdata.page,
                                            page_size=rdata.page_size,
                                            query=rdata.condition)
        return jsonify(data)

    @login_required
    def post(self):
        rdata = RequestData()
        new = rpc.invbox.add_address_type(rdata.get("name", type=str))

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])

        result = {
            "id": new["id"],
            "name": new["name"] or "",
            "createdAt": new["createdAt"],
        }
        return jsonify(result)

    @login_required
    def delete(self):
        rdata = RequestData()
        data = rpc.invbox.delete_address_types(rdata.array)

        if data["resultCode"]:
            raise HttpError(400, data["resultMsg"])
        return ""

    @login_required
    def put(self):
        rdata = RequestData()

        params = []
        for d in rdata:
            params.append({
                "id": d["id"],
                "name": d["name"].strip(),
            })

        res = rpc.invbox.modify_address_types(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


@api.route("/admin/road/fault", methods=["GET"])
@login_required
def fault_road_list():
    "故障货道"
    rdata = RequestData()
    condition = rdata.condition
    condition.append([{
        "operator": "≠",
        "attribute": "fault",
        "value": 0,
    }])
    devices = rpc.invbox.get_roads(page=rdata.page,
                                   page_size=rdata.page_size,
                                   query=condition,
                                   base_url=app.config["DOMAIN"])
    return jsonify(devices)


@api.route("/admin/road/configurable", methods=["GET"])
@login_required
def configurable_road_list():
    "可配置货道"
    rdata = RequestData()
    condition = rdata.condition
    condition.append([{
        "operator": "=",
        "attribute": "fault",
        "value": 0
    }])
    condition.append([{
        "operator": "=",
        "attribute": "status",
        "value": 10
    }])
    devices = rpc.invbox.get_roads(page=rdata.page,
                                   page_size=rdata.page_size,
                                   query=condition,
                                   base_url=app.config["DOMAIN"])
    return jsonify(devices)


class RoadAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        condition = rdata.condition
        if "device" in request.args:
            condition.append([{
                "operator": "=",
                "attribute": "device",
                "value": int(request.args.get("device"))
            }])

        devices = rpc.invbox.get_roads(page=rdata.page,
                                       page_size=rdata.page_size,
                                       query=condition,
                                       base_url=app.config["DOMAIN"])

        return jsonify(devices)

    @login_required
    def put(self):
        rdata = RequestData()
        res = rpc.invbox.modify_roads(rdata.data)
        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


class DeviceGroupAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        users = rpc.invbox.get_device_groups(page=rdata.page,
                                             page_size=rdata.page_size)
        return jsonify(users)

    @login_required
    def post(self):
        rdata = RequestData()
        new = rpc.invbox.add_device_group(rdata["name"],
                                          rdata["condition"])

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])

        del new["resultCode"]
        del new["resultMsg"]
        return jsonify(new)

    @login_required
    def delete(self):
        rdata = RequestData()
        data = rpc.invbox.delete_device_groups(rdata.array)

        if data["resultCode"]:
            raise HttpError(400, data["resultMsg"])
        return ""

    @login_required
    def put(self):
        rdata = RequestData()

        params = []
        for d in rdata:
            params.append({
                "id": d["id"],
                "name": d["name"],
                "condition": d["condition"],
            })

        res = rpc.invbox.modify_device_groups(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


class SupplyListAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        lists = rpc.invbox.get_supplylist(page=rdata.page,
                                          page_size=rdata.page_size)
        return jsonify(lists)

    @login_required
    def post(self):
        rdata = RequestData()
        new = rpc.invbox.add_supplylist(rdata["device"],
                                        rdata["itemInfo"])

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])

        del new["resultCode"]
        del new["resultMsg"]
        return jsonify(new)


api.add_url_rule('/admin/addresstype', view_func=AddressTypeAPI.as_view('addresstypes'))
api.add_url_rule('/admin/road', view_func=RoadAPI.as_view('road'))
api.add_url_rule('/admin/devicegroup', view_func=DeviceGroupAPI.as_view('devicegroups'))
api.add_url_rule('/admin/devicecategory', view_func=DeviceCategoryAPI.as_view('devicecategory'))
api.add_url_rule('/admin/supplylist', view_func=SupplyListAPI.as_view('supplylist'))
