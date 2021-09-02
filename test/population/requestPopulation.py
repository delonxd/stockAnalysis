import urllib.request
import json
import pickle
import re

url = 'https://open.lixinger.com/api/macro/population'


apiKeyText = r"""
总人口 :tp
男性总人口 :tmp
女性总人口 :tfp
人口增长率 :pb_r
人口死亡率 :pm_r
人口自然增长率 :png_r
14岁以下 :tp_a_0_14
15至64岁 :tp_a_15_64
65岁以上 :tp_a_65
少儿抚养比 :cr_r
老年抚养比 :or_r
"""

keyList = re.findall(r'\n(.*) :(.*)', apiKeyText)

print(keyList)

data = {
        "token": "e7a7f2e5-181b-4caa-9142-592ab6787871",
        "areaCode": "cn",
        "startDate": "1900-08-31",
        "endDate": "2021-08-31",
        "metricsList": [
            "y.tp.t",
            "y.tmp.t",
            "y.tfp.t",
            "y.pb_r.t",
            "y.pm_r.t",
            "y.png_r.t",
            "y.tp_a_0_14 .t",
            "y.tp_a_15_64 .t",
            "y.tp_a_65 .t",
            "y.cr_r .t",
            "y.or_r .t"
        ]
        }

post_data = json.dumps(data)
header_dict = {'Content-Type': 'application/json'}

req = urllib.request.Request(url, data=bytes(post_data, 'gbk'), headers=header_dict)

res = urllib.request.urlopen(req).read().decode()
print(res)

with open('../population/populationData.pkl', 'wb') as pk_f:
    pickle.dump(res, pk_f)


# with open('../population/popKeyText.pkl', 'wb') as pk_f:
#     pickle.dump(name_dict, pk_f)
