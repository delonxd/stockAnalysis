import urllib.request
import json
import pickle

url = 'https://open.lixinger.com/api/a/company'

data = {"token": "e7a7f2e5-181b-4caa-9142-592ab6787871"}
post_data = json.dumps(data)
header_dict = {'Content-Type': 'application/json'}

req = urllib.request.Request(url, data=bytes(post_data, 'gbk'), headers=header_dict)

res = urllib.request.urlopen(req).read().decode()
print(res)

with open('../basicData/BasicData.pkl', 'wb') as pk_f:
    pickle.dump(res, pk_f)

