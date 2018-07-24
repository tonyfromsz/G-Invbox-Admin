# -*- coding: utf-8 -*-
import os
import math
import alioss

from flask import jsonify, request, current_app as app, send_from_directory
from api import api
from flask_util import HttpError, RequestData, login_required
from util import md5, path_to_url
from app import rpc


@api.route("/admin/image/upload", methods=["POST"])
@login_required
def upload_image():
    if 'file' not in request.files:
        raise HttpError(400, "缺少file参数")
    file = request.files['file']
    if file.filename == '':
        raise HttpError(400, "未发现文件")
    content = file.read()

    # 图片格式限制
    extname = file.filename.rsplit('.', 1)[1].lower()
    if extname not in ['png', 'jpg', 'jpeg', 'gif']:
        raise HttpError(400, "不支持此格式图片上传")

    # 图片大小限制
    max_size = 5
    size = int(math.ceil(len(content) / 1024.0))   # size KB
    if size > max_size * 1024:
        raise HttpError(400, u"图片不能超过%sM" % max_size)

    md5sum = md5(content).lower()
    full_path = "%s/%s/%s/%s.%s" % (app.config["IMAGE_UPLOAD_PATH"],
                                    md5sum[:2],
                                    md5sum[2:4],
                                    md5sum,
                                    extname)

    directory = os.path.dirname(full_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    output_file = open(full_path, 'w+')
    output_file.write(content)

    url = path_to_url(full_path)
    res = rpc.invbox.check_add_image(md5sum,
                                     url,
                                     base_url=app.config["DOMAIN"])
    return jsonify(res)


@api.route('/media/<path:path>')
def static_file(path):
    return send_from_directory(app.config["MEDIA_PATH"], path)


@api.route("/admin/osstoken", methods=["GET"])
@login_required
def get_oss_token():
    token_info = alioss.get_token()
    return jsonify(token_info)


@api.route("/admin/video/detail", methods=["GET"])
@login_required
def get_single_video():
    if "md5" not in request.args:
        raise HttpError(400, "缺少参数：md5")
    md5 = request.args.get("md5")
    res = rpc.invbox.get_video_detail(md5)
    return jsonify(res)


@api.route("/admin/video", methods=["POST"])
@login_required
def post_video():
    rdata = RequestData()
    md5 = rdata["md5"]
    url = rdata["url"]

    if not md5 or not url:
        raise HttpError(400, "非法参数")

    res = rpc.invbox.get_video_detail(md5)
    if res:
        raise HttpError(400, "添加失败，已存在md5为%s的视频" % md5)

    res = rpc.invbox.add_video(md5, url)
    return jsonify(res)
