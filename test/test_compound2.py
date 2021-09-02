import numpy as np

import random

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from mpl_toolkits.mplot3d import Axes3D


if __name__ == '__main__':

    fig = plt.figure(1, figsize=(24, 12), dpi=70)
    ax = fig.add_subplot(1, 1, 1)

    ax.set_xlabel('length')
    ax.set_ylabel('abs')
    ax.xaxis.grid(True, which='both')
    ax.yaxis.grid(True, which='both')

    for i in range(1000):
        xx = []
        yy = []

        aa = 100
        bb = 0

        while 1 < aa < 10000:
            xx.append(bb)
            yy.append(np.log(aa)/np.log(10))

            tab1 = random.random()

            if tab1 > 0.33:
                aa = aa * 1.1
            else:
                aa = aa / 1.1

            bb += 1

        print(bb)
        ax.plot(xx, yy, linestyle='-', alpha=0.8, color='r', label='legend1')

    plt.show()