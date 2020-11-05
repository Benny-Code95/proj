import pandas as pd
from matplotlib import pyplot as plt


def plot_am15(xls_path):
    am15 = pd.read_excel(xls_path, index_col='wave')
    am15.plot()
    plt.show()


if __name__ == '__main__':
    path = 'F:\\研究生\\计算及工作整理\\截止膜\\太阳光谱数据\\太阳光谱.xlsx'
    plot_am15(path)
