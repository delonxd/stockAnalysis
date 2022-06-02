import pickle
import json
import os
import shutil
from method.logMethod import MainLog


def dump_pkl(path, data):
    with open(path, "wb") as f:
        pickle.dump(data, f)
    MainLog.add_log('dump pkl --> %s' % path)


def load_pkl(path):
    with open(path, "rb") as f:
        ret = pickle.load(f)
    MainLog.add_log('load pkl --> %s' % path)
    return ret


def write_json_txt(path, data):
    res = json.dumps(data, indent=4, ensure_ascii=False)
    with open(path, "w", encoding='utf-8') as f:
        f.write(res)
    MainLog.add_log('write json txt --> %s' % path)


def load_json_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        ret = json.loads(f.read())
    MainLog.add_log('loads json txt --> %s' % path)
    return ret


def clear_dir(dir_path):
    for file in os.listdir(dir_path):
        path = '%s\\%s' % (dir_path, file)
        MainLog.add_log('Delete --> %s' % path)
        os.remove(path)


def copy_dir(dir1, dir2):
    for file in os.listdir(dir1):
        path1 = '%s\\%s' % (dir1, file)
        path2 = '%s\\%s' % (dir2, file)
        # command = 'copy %s %s' % (path1, path2)
        # shutil.copytree(path1, path2)
        if os.path.isfile(path1):
            shutil.copy(path1, path2)
            MainLog.add_log('Copy %s --> %s' % (path1, path2))


def copy_file(path1, path2):
    import json

    type1 = path1[-3:]
    type2 = path2[-3:]

    if type1 == type2 == 'txt':
        with open(path1, "r", encoding='utf-8') as f:
            data = json.loads(f.read())

        res = json.dumps(data, indent=4, ensure_ascii=False)
        with open(path2, "w", encoding='utf-8') as f:
            f.write(res)

        MainLog.add_log('Copy %s --> %s' % (path1, path2))

    elif type1 == type2 == 'pkl':
        with open(path1, "rb") as f:
            data = pickle.load(f)

        with open(path2, "wb") as f:
            pickle.dump(data, f)
        MainLog.add_log('Copy %s --> %s' % (path1, path2))

    else:
        MainLog.add_log("CopyError: invalid type for copy_file(): '%s' --> '%s'" % (path1, path2))
