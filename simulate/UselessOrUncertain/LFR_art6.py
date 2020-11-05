# from math import sin, cos, tan, atan


def cal_efficiency(cr, ti, ta, ira):
    eta = (0.0042 * cr ** 2 + 0.0345 * cr - 4.7083) * (ti - ta) / ira - 0.0297 * cr + 1.0198
    return eta


if __name__ == '__main__':
    CR = 11.4
    T_in = 60
    T_amb = 20
    DNI = 850
    print(cal_efficiency(CR, T_in, T_amb, DNI))
