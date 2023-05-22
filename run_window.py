from PyQt5.QtWidgets import *
from gui.main_window import MainWidget


if __name__ == '__main__':
    import sys
    sys.path.append('D:\\PycharmProjects\\stockAnalysis')

    import os
    os.chdir("D:\\PycharmProjects\\stockAnalysis\\gui")

    import warnings
    from scipy.optimize import OptimizeWarning
    warnings.simplefilter("ignore", OptimizeWarning)

    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 100000)

    app = QApplication(sys.argv)
    # main = MainWindow()
    main = MainWidget()
    main.showMaximized()
    # main.showMinimized()
    sys.exit(app.exec_())
