# -*- coding: utf-8 -*-

from flask import jsonify, current_app as app
from api import api
from app import rpc
from flask_util import HttpError, RequestData, login_required
from flask.views import MethodView


class CategoryAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        data = rpc.invbox.get_item_categories(page=rdata.page,
                                              page_size=rdata.page_size,
                                              query=rdata.condition,
                                              base_url=app.config["DOMAIN"])
        return jsonify(data)

    @login_required
    def post(self):
        rdata = RequestData()
        new = rpc.invbox.add_category(rdata["name"].strip(),
                                      rdata.get("thumbnail", default=None),
                                      rdata.get("image", default=None),
                                      base_url=app.config["DOMAIN"])

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])

        result = {
            "id": new["id"],
            "name": new["name"] or "",
            "thumbnail": new["thumbnail"],
            "image": new["image"],
            "createdAt": new["createdAt"],
        }
        return jsonify(result)

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
            params.append({
                "id": d["id"],
                "name": d["name"].strip(),
            })

        res = rpc.invbox.modify_categories(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


class BrandAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        data = rpc.invbox.get_brands(page=rdata.page,
                                     query=rdata.condition,
                                     page_size=rdata.page_size)
        return jsonify(data)

    @login_required
    def post(self):
        rdata = RequestData()
        new = rpc.invbox.add_brand(rdata["name"].strip())

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
        data = rpc.invbox.delete_brands(rdata.array)

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

        res = rpc.invbox.modify_brands(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


class ItemAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        data = rpc.invbox.get_items(page=rdata.page,
                                    page_size=rdata.page_size,
                                    query=rdata.condition,
                                    base_url=app.config["DOMAIN"])
        return jsonify(data)

    @login_required
    def post(self):
        rdata = RequestData()

        basic_price = rdata.get("basicPrice", type=int)
        cost_price = rdata.get("costPrice", type=int)
        if basic_price <= 0 or cost_price <= 0:
            raise HttpError(400, "价格必须为正数")

        new = rpc.invbox.add_item(
            rdata["name"],
            rdata["no"] or "",
            rdata["category"],
            rdata["brand"],
            rdata["thumbnails"],
            basic_price,
            cost_price
        )

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])

        del new["resultCode"]
        del new["resultMsg"]
        return jsonify(new)

    @login_required
    def delete(self):
        rdata = RequestData()
        data = rpc.invbox.delete_items(rdata.array)

        if data["resultCode"]:
            raise HttpError(400, data["resultMsg"])
        return ""

    @login_required
    def put(self):
        rdata = RequestData()

        params = []
        for d in rdata:
            if int(d["basicPrice"]) <= 0 or int(d["costPrice"]) <= 0:
                raise HttpError(400, "价格必须为正数")
            params.append(d)
        res = rpc.invbox.modify_items(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


api.add_url_rule('/admin/itemcategory', view_func=CategoryAPI.as_view('itemcategory'))
api.add_url_rule('/admin/itembrand', view_func=BrandAPI.as_view('itembrand'))
api.add_url_rule('/admin/item', view_func=ItemAPI.as_view('item'))
