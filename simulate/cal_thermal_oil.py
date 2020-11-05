import re


def calc(s, T=0):
    def eval_str(st):
        st = re.sub('T\^(\d)', 'pow(T,\\1)', st)
        return st

    s = eval_str(s)
    a = eval(s)
    print(s)
    print(a)
    return a


def turn(l1):
    te = [i for i in l1 if i]
    if not te:
        return 0
    l1 = [str(i) for i in l1]
    s = l1[0]
    for n, i in enumerate(l1):
        if i != '0' and n != 0:
            s += '+' + i + '*T^' + str(n)
    s = re.sub('\+-', '-', s)
    return s


if __name__ == '__main__':
    con = 860.82
    x1 = 3.57429
    x2 = 0
    x3 = 0
    x4 = 0
    x5 = 0

    li = [con, x1, x2, x3, x4, x5]

    T0 = 433
    运动黏度 = '0.000298033-1.96358E-06*T^1+4.35784E-09*T^2-3.24421E-12*T^3'
    密度 = '1151.44-1.05526*T+4.3306E-4*T^2'
    比热 = '860.82+3.57429*T^1'
    导热 = '0.39728-0.00185*T^1+4.25744E-6*T^2-3.47222E-9*T^3'
    # ss = turn(li)
    # print('表达式：', ss)
    print('运动黏度为:')
    kv = calc(运动黏度, T0)
    print('密度为:')
    rho = calc(密度, T0)
    print('比热为：')
    calc(比热, T0)
    print('导热系数为：')
    calc(导热, T0)
    动力粘度 = kv * rho
    print('动力粘度为：', 动力粘度)
