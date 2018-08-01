# -*- coding: utf-8 -*-

from flask import jsonify
from api import api
from app import rpc
from flask.views import MethodView
from flask_util import HttpError, RequestData, login_manager, login_required, current_user
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
        "createdAt": res["createdAt"],
        "adminRange": res["adminRange"],    # 补货员-补货员id， 场地方-场地id， 品牌方-商品id
        "adminRange2": res["adminRange2"]   # 品牌方-场地id
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


@api.route("/admin/test")
@login_required
def login_test():
    # print(type(current_user))
    print(current_user['username'])
    # print(dict(current_user))
    return jsonify(dict(current_user))


class AccountAPI(MethodView):

    @login_required
    def get(self):
        if current_user["role"] != 0:
            return {
                "resultCode": 1,
                "resultMsg": "您没有操作权限"
            }
        rdata = RequestData()
        accounts = rpc.invbox.get_accounts(page=rdata.page,
                                           page_size=rdata.page_size)
        return jsonify(accounts)

    @login_required
    def post(self):
        if current_user["role"] != 0:
            return {
                "resultCode": 1,
                "resultMsg": "您没有操作权限"
            }
        rdata = RequestData()

        name = rdata.get('name', type=str)
        mobile = rdata.get('mobile', type=str)
        password = rdata.get('password', type=str)
        com_pwd = rdata.get('comPwd', type=str)
        role = rdata.get('role')
        admin_range = rdata.get('range')
        info_list = rdata.get('infoList')
        if not name:
            raise HttpError(400, "用户名不能为空")
        if not is_mobile(mobile):
            raise HttpError(400, "手机号码格式不正确")
        if not password == com_pwd:
            raise HttpError(400, "两次输入密码不一致")
        if not role:
            raise HttpError(400, "请输入用户角色")
        if str(role) not in ["1", "2", "3"]:
            raise HttpError(400, "不存在的用户角色")
        if not admin_range:
            raise HttpError(400, "请输入管理范围")

        # TODO:检查修改添加人的管理员权限
        # privilege =

        new_account = rpc.invbox.add_account(name, mobile, password, int(role), admin_range, info_list)
        if new_account.get("resultCode"):
            raise HttpError(400, "%s" % new_account.get("resultMsg"))
        return jsonify(new_account)

    @login_required
    def delete(self):
        if current_user["role"] != 0:
            print(current_user["role"])
            return jsonify({
                "resultCode": 1,
                "resultMsg": "您没有操作权限"
            })
        rdata = RequestData()
        data = rpc.invbox.delete_account(rdata.array)

        if data["resultCode"]:
            raise HttpError(400, data["resultMsg"])

        return jsonify(data)

    @login_required
    def put(self):
        if current_user["role"] != 0:
            return {
                "resultCode": 1,
                "resultMsg": "您没有操作权限"
            }
        rdata = RequestData()

        params = []
        for d in rdata:
            id = d.get("id")
            mobile = d.get("mobile")
            name = d.get("name")
            new_pwd = d.get("password")
            com_pwd = d.get("comPwd")
            role = d.get("role")
            admin_range = d.get("range")
            info_list = d.get("infoList")
            if mobile:
                if not is_mobile(d["mobile"]):
                    raise HttpError(400, "手机号码格式不正确")
            if new_pwd:
                if not new_pwd == com_pwd:
                    raise HttpError(400, "两次输入密码不一致")
            if role:
                if int(role) not in [1, 2, 3]:
                    raise HttpError(400, "不存在的角色")
            params.append({
                "id": id,
                "name": name,
                "mobile": mobile,
                "password": new_pwd,
                "role": int(role),
                "admin_range": admin_range,
                "info_list": info_list
            })
        res = rpc.invbox.modify_accounts(params)

        if res["resultCode"]:
            raise HttpError(400, res["resultMsg"])
        return jsonify(res)


api.add_url_rule('/admin/supplyer', view_func=SupplyerAPI.as_view('supplers'))
api.add_url_rule('/admin/user', view_func=UserAPI.as_view('users'))
api.add_url_rule('/admin/usergroup', view_func=UserGroupAPI.as_view('usergroups'))
api.add_url_rule('/admin/account', view_func=AccountAPI.as_view('accounts'))
