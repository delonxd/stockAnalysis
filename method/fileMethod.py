import pickle
import json
from method.logMethod import MainLog


def dump_pkl(path, data):
    with open(path, "wb") as f:
        pickle.dump(data, f)
    MainLog.add_log('write pkl --> %s' % path)


def write_json_txt(path, data):
    res = json.dumps(data, indent=4, ensure_ascii=False)
    with open(path, "w", encoding='utf-8') as f:
        f.write(res)
    MainLog.add_log('write json txt --> %s' % path)
