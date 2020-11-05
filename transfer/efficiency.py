import csv
import datetime
import re


def cal_efficiency(f_path, t_region, area, mass, cap, T_code):
    with open(f_path, "rt", encoding="utf-8") as f:
        pre_data = csv.reader(f)
        data = list(pre_data)

    info = []
    _date = re.search('\\\(\d+)\.csv', f_path)
    date = _date.group(1) if _date else '19000101'
    for index, d in enumerate(data):
        if index < 2:
            continue
        d[0] = date + ' ' + d[0]
        d[0] = datetime.datetime.strptime(d[0], '%Y%m%d %H:%M:%S')
        info.append(d)

    DNI_pos = data[1].index('DNI')
    G_pos = data[1].index('FlowM')
    Tout_pos = data[1].index(T_code)
    DNIs, Gs = 0, 0
    _time = [datetime.datetime.strptime(date + ' ' + t, '%Y%m%d %H:%M:%S') for t in t_region]
    info = [i for i in info if _time[0] <= i[0] <= _time[1]]
    T_delta = float(info[-1][Tout_pos]) - float(info[0][Tout_pos])
    for index, i in enumerate(info):
        DNIs += float(i[DNI_pos])
        Gs += float(i[G_pos])
    Q_act = mass * (cap * 1000) * T_delta / 1000
    Q_in = DNIs * area / 1000
    efficiency = Q_act / Q_in
    print('系统吸收热量为：{0} kJ'.format(Q_act))
    print('整个系统的效率为：{0}'.format(efficiency))
    return Q_act, efficiency


if __name__ == '__main__':
    file_path = 'G:\研究生\科研资料\实验数据\动力楼顶槽式太阳能数据\\20181017.csv'
    time_region = ('19:05:00', '19:10:00')
    S = 2.55 * 8  # 集热面积 m2
    M = 17.5  # 油的总质量 kg
    c = 2.44  # 比热容 kJ/(kg * K)
    code = 'T02'  # 集热管出口端温度代码
    cal_efficiency(file_path, time_region, S, M, c, code)
