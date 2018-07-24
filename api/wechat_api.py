# -*- coding: utf-8 -*-
import urllib
import requests

from api import api
from flask_util import RequestData, HttpError
from flask import jsonify
from app import rpc

APPID = "wxb2bb8a7fd152e6a3"
APPSECRET = "e07387089538d8b4feda0b7e93ec7ab7"


@api.route("/wechat/user/info", methods=["POST"])
def get_user_info():
    rdata = RequestData()
    openid = rdata["openid"]
    info = rpc.invbox.get_user(openid)
    del info["resultCode"]
    del info["resultMsg"]
    return jsonify(info)


@api.route("/wechat/sms/send", methods=["POST"])
def send_wechat_sms():
    "发送手机验证码"
    rdata = RequestData()
    mobile = rdata["mobile"]
    res = rpc.invbox.send_message_for_wechat(mobile)

    if res["resultCode"]:
        raise HttpError(400, res["resultMsg"])
    return jsonify(res)


@api.route("/wechat/mobile/bind", methods=["POST"])
def bind_mobile():
    rdata = RequestData()
    openid = rdata["openid"]
    mobile = rdata["mobile"]
    code = rdata["code"]
    info = rpc.invbox.modify_user(openid, mobile, code)
    if info["resultCode"]:
        raise HttpError(400, info["resultMsg"])
    del info["resultCode"]
    del info["resultMsg"]
    return jsonify(info)


@api.route("/wechat/getUserByCode", methods=["GET"])
def wechat_auth_redirect():
    rdata = RequestData()
    code = rdata.get("code", default="")
    if not code:
        raise HttpError(400, "授权失败")

    url = "https://api.weixin.qq.com/sns/oauth2/access_token"
    params = {
        "appid": APPID,
        "secret": APPSECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    url = "%s?%s" % (url, urllib.urlencode(params))

    r = requests.get(url, timeout=15)
    data = r.json()
    if "access_token" not in data:
        raise HttpError(400, data["errmsg"])

    # access_token = data["access_token"]
    openid = data["openid"]
    info = rpc.invbox.get_user(openid)
    return jsonify({
        "openid": openid,
        "mobile": info["mobile"],
    })
