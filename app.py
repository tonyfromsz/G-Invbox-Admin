# -*- coding: utf-8 -*-

import os
import sys

from flask import Flask
from config import Config
from flask_nameko import FlaskPooledClusterRpcProxy
from log import init_logger
from flask_util import login_manager

reload(sys)
sys.setdefaultencoding("utf-8")

BASE_DIR = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]

rpc = FlaskPooledClusterRpcProxy()


def setup_app():
    init_logger(level=Config.LOG_LEVEL, path=Config.LOG_PATH)

    app = Flask(__name__)
    app.secret_key = "d9e9d4bf-4fbb-4b0a-a600-a4773f2ca61a"
    app.config.from_object(Config)
    Config.init_app(app)

    rpc.init_app(app)
    login_manager.init_app(app)

    from api import api
    app.register_blueprint(api)
    return app
