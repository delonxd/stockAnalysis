import urllib.request
import json
import pickle


if __name__ == '__main__':
    url = 'https://open.lixinger.com/api/a/company'

    data = {"token": "e7a7f2e5-181b-4caa-9142-592ab6787871"}
    post_data = json.dumps(data)
    header_dict = {'Content-Type': 'application/json'}

    req = urllib.request.Request(url, data=bytes(post_data, 'gbk'), headers=header_dict)

    res = urllib.request.urlopen(req).read().decode()

    dict0 = json.loads(res)
    res = json.dumps(dict0, indent=4, ensure_ascii=False)

    # print(res)
    with open("../basicData/res_basicData.txt", "w", encoding='utf-8') as f:
        f.write(res)
