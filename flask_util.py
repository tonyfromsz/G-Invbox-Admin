# -*- coding: utf-8 -*-
import logging
import ujson as json
import functools
import hmac

from hashlib import sha512
from werkzeug.exceptions import HTTPException
from werkzeug.local import LocalProxy
from werkzeug.security import safe_str_cmp
from flask import (_request_ctx_stack, current_app, request, session, jsonify,
                   has_request_context)
from datetime import datetime, timedelta


logger = logging.getLogger()


class HttpError(HTTPException):

    def __init__(self, code, errmsg):
        self.code = code
        self.errmsg = errmsg

    def get_response(self, environ=None):
        resp = jsonify({"errmsg": self.errmsg})
        resp.status_code = self.code
        return resp


class RequestData(object):

    def __init__(self):
        raw = request.data
        if raw:
            try:
                self.data = json.loads(raw)
            except Exception, e:
                logger.info(e)
                raise HttpError(400, "Json格式错误：%s" % raw)
        else:
            self.data = {}

        self.query = request.args
        self.is_array = isinstance(self.data, list)

    def get(self, name, type=None, **kwargs):
        if name in self.data:
            val = self.data[name]
        elif name in self.query:
            val = self.query[name]
        elif "default" in kwargs:
            val = kwargs["default"]
        else:
            raise HttpError(400, "缺少参数：%s" % name)

        if isinstance(val, (str, unicode)):
            val = val.strip()

        if type in [str, unicode]:
            return type(val or "")
        elif type in [int, float]:
            return type(val or 0)
        elif type:
            return type(val)
        else:
            return val

    def __getitem__(self, name):
        if self.is_array:
            return self.data[name]
        return self.get(name)

    def get_condition(self):
        if "query" not in self.query:
            return []

        cond_str = self.query["query"]
        try:
            condition = json.loads(cond_str)
        except Exception, e:
            logger.info(e)
            raise HttpError(400, "Json格式错误：%s" % cond_str)
        return condition

    @property
    def condition(self):
        if not hasattr(self, "_condition"):
            self._condition = self.get_condition()
        return self._condition

    @property
    def page(self):
        if not hasattr(self, "_page"):
            self._page = int(self.query.get("page", 1))
        return self._page

    @property
    def page_size(self):
        if not hasattr(self, "_page_size"):
            self._page_size = int(self.query.get("pageSize", 10))
        return self._page_size

    @property
    def array(self):
        if not self.is_array:
            raise HttpError(400, "不是数组：%s" % self.data)
        return self.data

    def is_array(self):
        return self.is_array

    def base_get(self, data, key, type=None):
        if key not in data:
            raise HttpError(400, "缺少字段：%s" % key)
        val = data[key]

        if isinstance(val, (str, unicode)):
            val = val.strip()

        if type in [str, unicode]:
            return type(val or "")
        elif type in [int, float]:
            return type(val or 0)
        elif type:
            return type(val)
        else:
            return val


class LoginManager(object):

    def _get_user(self):
        if has_request_context() and not hasattr(_request_ctx_stack.top, 'user'):
            self._load_user()
        return getattr(_request_ctx_stack.top, 'user', None)

    def _load_user(self):
        cookie_name = "user"
        has_cookie = (cookie_name in request.cookies)
        user = None
        if has_cookie:
            cookie = request.cookies[cookie_name]
            user = self._load_user_from_cookie(cookie)
        return self._update_request_context_with_user(user)

    def user_loader(self, callback):
        self._user_callback = callback
        return callback

    def _load_user_from_cookie(self, cookie):
        user_id = self.decode_cookie(cookie)
        if user_id is not None:
            session['user_id'] = user_id
            user = None
            if self._user_callback:
                user = self._user_callback(user_id)
            if user is not None:
                return user
        return None

    def _update_request_context_with_user(self, user=None):
        ctx = _request_ctx_stack.top
        ctx.user = user

    def decode_cookie(self, cookie):
        try:
            payload, digest = cookie.rsplit(u'|', 1)
            if hasattr(digest, 'decode'):
                digest = digest.decode('ascii')  # pragma: no cover
        except ValueError:
            return

        if safe_str_cmp(self._cookie_digest(payload), digest):
            return payload

    def encode_cookie(self, payload):
        return u'{0}|{1}'.format(payload, self._cookie_digest(payload))

    def _cookie_digest(self, payload, key=None):
        key = self._secret_key(key)
        return hmac.new(key, payload.encode('utf-8'), sha512).hexdigest()

    def _secret_key(self, key=None):
        if key is None:
            key = current_app.config['SECRET_KEY']

        if isinstance(key, unicode):
            key = key.encode('latin1')  # ensure bytes
        return key

    def _update_remember_cookie(self, response):
        operation = session.pop('remember', None) if session else None
        if 'user_id' in session and operation == "set":
            self._set_cookie(response)
        elif operation == "clear":
            self._clear_cookie(response)
        return response

    def _set_cookie(self, response):
        duration = timedelta(seconds=7 * 24 * 60 * 60)
        data = self.encode_cookie(unicode(session['user_id']))

        if isinstance(duration, int):
            duration = timedelta(seconds=duration)
        expires = datetime.utcnow() + duration

        response.set_cookie("user",
                            value=data,
                            expires=expires,
                            path="/",
                            secure=None)

    def _clear_cookie(self, response):
        response.delete_cookie("user", path="/")

    def init_app(self, app):
        app.after_request(self._update_remember_cookie)

    def login_user(self, user):
        session['user_id'] = user["id"]
        session['remember'] = 'set'
        self._update_request_context_with_user(user)
        return True

    def logout_user(self):
        if 'user_id' in session:
            session.pop('user_id')
        session['remember'] = 'clear'
        self._update_request_context_with_user()
        return True


login_manager = LoginManager()
current_user = LocalProxy(lambda: login_manager._get_user())


def login_required(arg):
    """
    装饰器

    @login_required     # 需要登录
    def get():
        pass
    """
    method = arg

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if not current_user:
            raise HttpError(403, u"请先登陆")
        return method(*args, **kwargs)
    return wrapper
