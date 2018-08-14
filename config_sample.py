# -*- coding: utf-8 -*-
import os


class Config:
    DEBUG = False

    DOMAIN = "http://api.invgirls.com/"

    MEDIA_PATH = "/src/data/media"

    NAMEKO_AMQP_URI = "pyamqp://rbt:rbt123@172.18.224.101:5673"

    LOG_LEVEL = "INFO"
    LOG_PATH = "/src/logs"

    SECRET_KEY = "a0c23007-f1c0-11e7-b62a-c8e0eb182c79"

    @staticmethod
    def init_app(app):
        app.config["IMAGE_UPLOAD_PATH"] = os.path.join(app.config["MEDIA_PATH"], "image")
        app.config["APK_UPLOAD_PATH"] = os.path.join(app.config["MEDIA_PATH"], "apk")
        app.config["VIDEO_UPLOAD_PATH"] = os.path.join(app.config["MEDIA_PATH"], "video")
