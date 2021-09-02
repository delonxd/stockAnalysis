from method.mainMethod import *

if __name__ == '__main__':
    res = read_pkl(
        root='../bufferData',
        file_name='Fs_600416.pkl'
    )
    print(res)
    print(type(res))
