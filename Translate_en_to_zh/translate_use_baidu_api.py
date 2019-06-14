import http.client
import hashlib
import urllib.parse
import random
import json


def call_baidu_api(q):
    appid = '****' #你的appid
    secretKey = '*****' #你的密钥
     
    httpClient = None
    myurl = '/api/trans/vip/translate'
    # q = 'apple'
    fromLang = 'en'
    toLang = 'zh'
    salt = random.randint(32768, 65536)

    sign = appid+q+str(salt)+secretKey

    m = hashlib.md5()
    m.update(sign.encode('utf8'))
    sign = m.hexdigest()
    myurl = myurl+'?appid='+appid+'&q='+urllib.parse.quote(q)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign

    result = ''
    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        #response是HTTPResponse对象
        response = httpClient.getresponse()
        dictionary = json.loads(response.read().decode("unicode-escape"))
        result = dictionary["trans_result"][0]["dst"]
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()

    return result


def en_to_zh(words):
    for ch in words:
        if u'\u4e00' <= ch <= u'\u9fff':
            return words

    return call_baidu_api(words)

if __name__ == '__main__':
    print(en_to_zh('San Francisco'))
    print(en_to_zh('加利福尼亚'))