import requests
import re
import json


def do():
    url = 'https://mod-api.xinpianchang.com/mod/api/v2/media/WDGPB72WVqewdrm5?appKey=61a2f329348b3bf77&extend=userInfo%2CuserStatus'
    response = requests.get(url)
    re_json = json.loads(response.text)
    print(re_json['data']['title'])


if __name__ == '__main__':
    do()
