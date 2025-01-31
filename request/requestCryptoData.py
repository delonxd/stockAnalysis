import urllib.request
import json
import time
import pandas as pd

from method.logMethod import MainLog
from method.fileMethod import load_json_txt, write_json_txt


def request_crypto_data():
    MainLog.add_log('request_crypto_data was called...')

    path1 = "..\\basicData\\crypto\\crypto_btc.txt"
    path2 = "..\\basicData\\crypto\\crypto_btc_sz.txt"
    data_dict = load_json_txt(path1)

    sz_date = load_json_txt('..\\basicData\\akshare_sz_date.txt')

    str0 = 'https://data-api.cryptocompare.com'
    str1 = '/index/cc/v1/historical/'

    ts0 = str(int(time.time()))

    str2 = 'days?market=cadli&instrument=BTC-USD&limit=5000&aggregate=1&to_ts=%s&groups=OHLC' % ts0
    api_key = '&api_key=9dbd828be9f87a775f3f17a095662f3e16dea80906d21dee3f7140fdccfd2eab'
    url = '%s%s%s%s' % (str0, str1, str2, api_key)

    req = urllib.request.Request(url)
    res_txt = urllib.request.urlopen(req).read().decode()
    res = json.loads(res_txt)['Data']

    counter = 0
    for data in res:
        counter += 1
        timestamp = data.get('TIMESTAMP')
        close = data.get('CLOSE')

        if timestamp is None:
            continue

        struct_time = time.localtime(timestamp)
        time_str = time.strftime("%Y-%m-%d", struct_time)
        close = float(close)
        data_dict[time_str] = close

    s0 = pd.Series(data_dict)
    s0.sort_index(ascending=False, inplace=True)

    s1 = s0.reindex(index=sz_date).dropna()
    s1.sort_index(ascending=False, inplace=True)

    data_dict1 = s0.to_dict()
    data_dict2 = s1.to_dict()

    write_json_txt(path1, data_dict1)
    write_json_txt(path2, data_dict2)
    MainLog.add_log('request_crypto_data complete.')


if __name__ == '__main__':
    import warnings
    from scipy.optimize import OptimizeWarning
    warnings.simplefilter("ignore", OptimizeWarning)
    warnings.simplefilter(action='ignore', category=FutureWarning)

    request_crypto_data()
