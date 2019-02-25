import base64
import hashlib
import time
import random
import string
from urllib.parse import quote
import requests

url = "https://api.ai.qq.com/fcgi-bin/ocr/ocr_generalocr"
def curlmd5(src):
    m = hashlib.md5(src.encode('UTF-8'))
    return m.hexdigest().upper()


# 请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效）
def get_params(base64_data):
    t = time.time()
    time_stamp = str(int(t))
    # 请求随机字符串，用于保证签名不可预测
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    # 应用标志，这里修改成自己的id和key
    app_id = '2110218671'
    app_key = '9GkQT0jSiRz2HCEY'
    params = {'app_id': app_id,
              'image': base64_data,
              'time_stamp': time_stamp,
              'nonce_str': nonce_str,
              }
    sign_before = ''
    # 要对key排序再拼接
    for key in sorted(params):
        # 键值拼接过程value部分需要URL编码，URL编码算法用大写字母，例如%E8。quote默认大写。
        sign_before += '{}={}&'.format(key, quote(params[key], safe=''))
    # 将应用密钥以app_key为键名，拼接到字符串sign_before末尾
    sign_before += 'app_key={}'.format(app_key)
    # 对字符串sign_before进行MD5运算，得到接口请求签名
    sign = curlmd5(sign_before)
    params['sign'] = sign
    return params

def invoke_api_file(image_filepath):
    with open(image_filepath, 'rb') as fin:
        image_data = fin.read()
    base64_data = base64.b64encode(image_data)
    params = get_params(base64_data)
    r = requests.post(url, data=params)
    print(r.status_code)
    if r.status_code != 200:
        return []
    item_list = r.json()['data']['item_list']
    lines = []
    for s in item_list:
        lines.append(s['itemstring'])
    return lines

def test_api():
    #url = "https://api.ai.qq.com/fcgi-bin/ocr/ocr_generalocr"
    with open('cn_1.jpg', 'rb') as fin:
        image_data = fin.read()
    base64_data = base64.b64encode(image_data)
    params = get_params(base64_data)
    r = requests.post(url, data=params)
    item_list = r.json()['data']['item_list']
    for s in item_list:
        print(s['itemstring'])

#test_api()