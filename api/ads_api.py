# -*- coding: utf-8 -*-

from flask import jsonify, request, current_app as app
from api import api
from app import rpc
from flask_util import HttpError, RequestData, login_required
from flask.views import MethodView


class ADImageAPI(MethodView):

    @login_required
    def get(self):
        page = int(request.args.get("page", "1"))
        data = rpc.invbox.get_adimages(page=page,
                                       base_url=app.config["DOMAIN"])
        return jsonify(data)

    @login_required
    def post(self):
        rdata = RequestData()
        new = rpc.invbox.add_adimage(rdata["name"],
                                     rdata["image"],
                                     base_url=app.config["DOMAIN"])

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])

        result = {
            "id": new["id"],
            "name": new["name"] or "",
            "image": new["image"],
            "createdAt": new["createdAt"],
        }
        return jsonify(result)

    @login_required
    def delete(self):
        rdata = RequestData()
        data = rpc.invbox.delete_adimages(rdata.array)

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
                "image": d["image"],
            })

        res = rpc.invbox.modify_adimages(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


class ADVideoAPI(MethodView):

    @login_required
    def get(self):
        page = int(request.args.get("page", "1"))
        data = rpc.invbox.get_advideos(page=page,
                                       base_url=app.config["DOMAIN"])
        return jsonify(data)

    @login_required
    def post(self):
        rdata = RequestData()
        new = rpc.invbox.add_advideo(rdata["name"],
                                     rdata["video"],
                                     base_url=app.config["DOMAIN"])

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])

        result = {
            "id": new["id"],
            "name": new["name"] or "",
            "video": new["video"],
            "createdAt": new["createdAt"],
        }
        return jsonify(result)

    @login_required
    def delete(self):
        rdata = RequestData()
        data = rpc.invbox.delete_advideos(rdata.array)

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
                "video": d["video"],
            })

        res = rpc.invbox.modify_advideos(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


class AdvertisementAPI(MethodView):

    @login_required
    def get(self):
        page = int(request.args.get("page", "1"))
        device = int(request.args.get("device", 0))
        data = rpc.invbox.get_ads(device=device,
                                  page=page,
                                  base_url=app.config["DOMAIN"])
        return jsonify(data)

    @login_required
    def put(self):
        rdata = RequestData()

        params = []
        for d in rdata:
            params.append(d)
        res = rpc.invbox.modify_ads(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


api.add_url_rule('/admin/adimage', view_func=ADImageAPI.as_view('adimage'))
api.add_url_rule('/admin/advideo', view_func=ADVideoAPI.as_view('advideo'))
api.add_url_rule('/admin/advertisement', view_func=AdvertisementAPI.as_view('advertisement'))
