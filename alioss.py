# -*- coding: utf-8 -*-

import time
import datetime
import json
import base64
import hmac
from hashlib import sha1 as sha
from config import Config

accessKeyId = 'LTAIRGfSTC0oRLRG'
accessKeySecret = 'Ww9lyFjL2FUmT7iv2BBDio1ztib2B0'

if Config.DOMAIN.startswith("https"):
    host = 'https://invbox.oss-cn-shenzhen.aliyuncs.com'
else:
    host = 'http://invbox.oss-cn-shenzhen.aliyuncs.com'

expire_time = 30 * 60
upload_dir = ''     # 强制要求文件名前缀必须是upload_dir


def get_iso_8601(expire):
    gmt = datetime.datetime.fromtimestamp(expire).isoformat()
    gmt += 'Z'
    return gmt


def get_token():
    now = int(time.time())
    expire_syncpoint = now + expire_time
    expire = get_iso_8601(expire_syncpoint)

    policy_dict = {}
    policy_dict['expiration'] = expire
    condition_array = []
    array_item = []
    array_item.append('starts-with')
    array_item.append('$key')
    array_item.append(upload_dir)
    condition_array.append(array_item)
    policy_dict['conditions'] = condition_array
    policy = json.dumps(policy_dict).strip()
    # policy_encode = base64.encodestring(policy)
    policy_encode = base64.b64encode(policy)
    h = hmac.new(accessKeySecret, policy_encode, sha)
    sign_result = base64.encodestring(h.digest()).strip()

    token_dict = {}
    token_dict['accessid'] = accessKeyId
    token_dict['host'] = host
    token_dict['policy'] = policy_encode
    token_dict['signature'] = sign_result
    token_dict['expire'] = expire_syncpoint
    token_dict['dir'] = upload_dir
    return token_dict


if __name__ == "__main__":
    print get_token()
