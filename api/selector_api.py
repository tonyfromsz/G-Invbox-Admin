# -*- coding: utf-8 -*-
from flask import jsonify
from api import api
from app import rpc
from flask_util import login_required


@api.route('/admin/<string:name>/selector', methods=["GET"])
@login_required
def get_selector_info(name):
    res = rpc.invbox.get_selectors(name)
    return jsonify(res)
