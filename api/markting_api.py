# -*- coding: utf-8 -*-

from flask import jsonify
from app import rpc
from api import api
from flask.views import MethodView
from flask_util import HttpError, RequestData, login_required


class RedeemActivityAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        data = rpc.invbox.get_redeem_activities(page=rdata.page,
                                                page_size=rdata.page_size)
        return jsonify(data)

    @login_required
    def post(self):
        rdata = RequestData()
        new = rpc.invbox.add_redeem_activity(rdata["name"],
                                             rdata["userGroup"],
                                             rdata["validStartAt"],
                                             rdata["validEndAt"],
                                             rdata["item"])

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])

        del new["resultCode"]
        del new["resultMsg"]

        return jsonify(new)

    @login_required
    def delete(self):
        rdata = RequestData()
        data = rpc.invbox.delete_redeem_activities(rdata.array)

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
                "validStartAt": d["validStartAt"],
                "validEndAt": d["validEndAt"],
                "item": d["item"],
                "userGroup": d["userGroup"],
            })

        res = rpc.invbox.modify_redeem_activities(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


class VoiceActivityAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        data = rpc.invbox.get_voice_activities(page=rdata.page,
                                               page_size=rdata.page_size)
        return jsonify(data)

    @login_required
    def post(self):
        rdata = RequestData()
        limit = rdata.get("limit", type=int)

        if limit <= 0:
            raise HttpError(400, "上限值只能输入正数")

        new = rpc.invbox.add_voice_activity(rdata["code"],
                                            rdata["deviceGroup"],
                                            rdata["validStartAt"],
                                            rdata["validEndAt"],
                                            limit,
                                            rdata["item"])

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])

        del new["resultCode"]
        del new["resultMsg"]

        return jsonify(new)

    @login_required
    def delete(self):
        rdata = RequestData()
        data = rpc.invbox.delete_voice_activities(rdata.array)

        if data["resultCode"]:
            raise HttpError(400, data["resultMsg"])
        return ""

    @login_required
    def put(self):
        rdata = RequestData()

        params = []
        for d in rdata:
            if int(d["limit"]) <= 0:
                raise HttpError(400, "上限值只能输入正数")
            params.append({
                "id": d["id"],
                "code": d["code"],
                "validStartAt": d["validStartAt"],
                "validEndAt": d["validEndAt"],
                "item": d["item"],
                "limit": d["limit"],
                "deviceGroup": d["deviceGroup"],
            })

        res = rpc.invbox.modify_voice_activities(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


class VoiceWordAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        data = rpc.invbox.get_voice_words(page=rdata.page,
                                          query=rdata.condition,
                                          page_size=rdata.page_size)
        return jsonify(data)


class RedeemAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        data = rpc.invbox.get_redeems(page=rdata.page,
                                      query=rdata.condition,
                                      page_size=rdata.page_size)
        return jsonify(data)


api.add_url_rule('/admin/redeemactivity', view_func=RedeemActivityAPI.as_view('redeemactivity'))
api.add_url_rule('/admin/voiceactivity', view_func=VoiceActivityAPI.as_view('voiceactivity'))
api.add_url_rule('/admin/redeem', view_func=RedeemAPI.as_view('redeem'))
api.add_url_rule('/admin/voiceword', view_func=VoiceWordAPI.as_view('voiceword'))
