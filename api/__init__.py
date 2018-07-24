# -*- coding: utf-8 -*-
import logging

from flask import Blueprint, request

api = Blueprint('api', __name__)
logger = logging.getLogger(__name__)


# TODO 用autodiscover模块代替下面代码
import device_api
import admin_api
import item_api
import file_api
import order_api
import ads_api
import selector_api
import markting_api
import stats_api
import wechat_api


@api.before_request
def log_request():
    if request.method == "OPTIONS":
        return ""
    logger.info("[request] %s %s \n%s", request.method, request.path, request.get_data())


@api.after_request
def after_request(response):
    if "media" not in request.path:
        logger.info("[response] %s %s \n%s", request.method, request.path, response.get_data())

    response.headers['Access-Control-Allow-Origin'] = request.headers.get("Origin")
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = "true"
    return response
