from math import *


def cal_v1():
    # 角度转弧度
    def angle_to_radian(angle):
        return angle * pi / 180

    # 变量定义
    x = -1
    y = 2
    tht = angle_to_radian(0)

    # 函数表达式
    ep0 = ((x + 1) * cos(tht) + y * sin(tht)) / sqrt((x + 1) ** 2 + y ** 2)
    ep1 = ((x - 1) * cos(tht) + y * sin(tht)) / sqrt((x - 1) ** 2 + y ** 2)
    ep = 0.5 * (ep0 - ep1)

    # 输出结果
    print(ep)
    return ep


if __name__ == '__main__':
    cal_v1()
