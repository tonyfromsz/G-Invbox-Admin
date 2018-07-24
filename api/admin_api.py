# -*- coding: utf-8 -*-

from flask import jsonify
from api import api
from app import rpc
from flask.views import MethodView
from flask_util import HttpError, RequestData, login_manager, login_required
from util import is_mobile


@login_manager.user_loader
def get_admin_detail(user_id):
    res = rpc.invbox.get_admin(user_id)
    if res["resultCode"]:
        return {}
    del res["resultCode"]
    del res["resultMsg"]
    return res


@api.route("/admin/login", methods=["POST"])
def login():
    "管理员登录"
    rdata = RequestData()
    username = rdata["username"]
    password = rdata["password"]

    res = rpc.invbox.check_login(username, password)

    if res["resultCode"]:
        raise HttpError(400, res["resultMsg"])

    resp = jsonify({
        "username": res["username"],
        "id": res["id"],
        "role": res["role"],
        "createdAt": res["createdAt"]
    })
    login_manager.login_user(res)
    return resp


@api.route("/admin/sendloginsms", methods=["POST"])
def send_code_sms():
    "发送登录验证码"
    rdata = RequestData()
    mobile = rdata["mobile"]
    res = rpc.invbox.send_login_message(mobile)

    if res["resultCode"]:
        raise HttpError(400, res["resultMsg"])
    return jsonify(res)


@api.route("/admin/loginwithsms", methods=["POST"])
def login_with_smscode():
    "短信验证码登录"
    rdata = RequestData()
    mobile = rdata["mobile"]
    code = rdata["code"]

    res = rpc.invbox.check_login_with_sms(mobile, code)

    if res["resultCode"]:
        raise HttpError(400, res["resultMsg"])

    resp = jsonify({
        "username": res["username"],
        "id": res["id"],
        "role": res["role"],
        "createdAt": res["createdAt"]
    })
    login_manager.login_user(res)
    return resp


@api.route('/admin/logout', methods=["POST", "GET"])
def logout():
    "管理员退出"
    resp = jsonify({"status": "logout successed!"})
    login_manager.logout_user()
    return resp


class SupplyerAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        supplyers = rpc.invbox.get_supplyers(page=rdata.page,
                                             page_size=rdata.page_size)
        return jsonify(supplyers)

    @login_required
    def post(self):
        rdata = RequestData()

        name = rdata.get("name", type=str)
        mobile = rdata.get("mobile", type=str)
        if not name:
            raise HttpError(400, "名字不能为空")
        if not is_mobile(mobile):
            raise HttpError(400, "手机号码格式不正确")

        new = rpc.invbox.add_supplyer(name, mobile)

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])

        result = {
            "id": new["id"],
            "name": new["name"] or "",
            "mobile": new["mobile"],
            "deviceCount": new["deviceCount"],
            "createdAt": new["createdAt"],
        }
        return jsonify(result)

    @login_required
    def delete(self):
        rdata = RequestData()
        data = rpc.invbox.delete_supplyers(rdata.array)

        if data["resultCode"]:
            raise HttpError(400, data["resultMsg"])
        return ""

    @login_required
    def put(self):
        rdata = RequestData()

        params = []
        for d in rdata:
            name = d["name"].strip()
            if not name:
                raise HttpError(400, "名字不能为空")
            if not is_mobile(d["mobile"]):
                raise HttpError(400, "手机号码格式不正确")
            params.append({
                "id": d["id"],
                "name": name,
                "mobile": d["mobile"],
            })

        res = rpc.invbox.modify_supplyers(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


class UserAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        users = rpc.invbox.get_users(page=rdata.page,
                                     page_size=rdata.page_size,
                                     query=rdata.condition)
        return jsonify(users)


class UserGroupAPI(MethodView):

    @login_required
    def get(self):
        rdata = RequestData()
        users = rpc.invbox.get_user_groups(page=rdata.page,
                                           page_size=rdata.page_size)
        return jsonify(users)

    @login_required
    def post(self):
        rdata = RequestData()
        new = rpc.invbox.add_user_group(rdata["name"],
                                        rdata["condition"])

        if new["resultCode"]:
            raise HttpError(400, new["resultMsg"])

        del new["resultCode"]
        del new["resultMsg"]
        return jsonify(new)

    @login_required
    def delete(self):
        rdata = RequestData()
        data = rpc.invbox.delete_user_groups(rdata.array)

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

        res = rpc.invbox.modify_user_groups(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return ""


api.add_url_rule('/admin/supplyer', view_func=SupplyerAPI.as_view('supplers'))
api.add_url_rule('/admin/user', view_func=UserAPI.as_view('users'))
api.add_url_rule('/admin/usergroup', view_func=UserGroupAPI.as_view('usergroups'))
