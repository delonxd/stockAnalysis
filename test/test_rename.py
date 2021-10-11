import re
import os


if __name__ == '__main__':

    path = '../bufferData/marketData\\'

    file_list = [x for x in os.listdir(path) if os.path.isfile(path + x)]

    for file in file_list:

        code = file[17:23]

        new_name = 'marketSheet_%s.pkl' % code

        old_path = path + file
        new_path = path + new_name

        print(old_path, '-->', new_path)

        # os.rename(old_path, new_path)
