import urllib.request
import json


def data_request(url, api_dict):
    api = json.dumps(api_dict)

    header_dict = {'Content-Type': 'application/json'}

    req = urllib.request.Request(url, data=bytes(api, 'gbk'), headers=header_dict)
    # res = urllib.request.urlopen(req).read()

    handler = urllib.request.ProxyHandler(proxies={})
    opener = urllib.request.build_opener(handler)
    res = opener.open(req).read()

    return res


if __name__ == '__main__':
    pass
