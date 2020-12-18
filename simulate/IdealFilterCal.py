from simulate.cal_rad_Fb import cal_fb
from simulate.AM_cal import AmCal
from simulate.FilterSpectrum import pars_spectrum_via_excel
from CalTools.GetValues import get_line_value_via_lists
import numpy as np


# 计算理想截止膜的效率
def cal_eff(tr_short=1.0, tr_long=0.0, ct_point=2.5):
    # 光学效率
    abs_rec = 1.0  # 吸收面吸收率
    ref_mirror = 1.0  # 反射镜反射率
    nt_list = [[ct_point, tr_short],
               [ct_point, tr_long]]
    tr = AmCal().cal_dni_900_via_trap(nt_list)[0]
    ef_opt = ref_mirror * abs_rec * tr

    # 热性能
    T = 773.15  # 集热温度
    DNI, C = 1000, 30  # 直照辐射强度和聚光比
    eps_rec = 1.0  # 吸收面发射率
    fb = cal_fb(Tk=T, n=ct_point)
    q_loss = eps_rec * 5.67E-8 * (pow(T, 4) - pow(293.15, 4)) * (
            fb * tr_short + (1 - fb) * tr_long)
    q_solar = DNI * C
    ef_loss = q_loss / q_solar

    ef_col = ef_opt - ef_loss
    return ef_col


def get_avg_attr_of_band(di, attr, w_start=0.0, w_end=10.0):
    area = 0.0
    vs, attrs = di[attr]
    attr1, p1 = get_line_value_via_lists(w_start, vs, attrs, get_pos=True)
    attr2, p2 = get_line_value_via_lists(w_end, vs, attrs, p1, get_pos=True)
    if p1 == p2:
        area = (w_end - w_start) * (attr1 + attr2) / 2
    else:
        p1 += 1
        area += (vs[p1] - w_start) * (attrs[p1] + attr1) / 2
        while p1 < p2:
            area += (vs[p1 + 1] - vs[p1]) * (attrs[p1] + attrs[p1 + 1]) / 2
            p1 += 1
        area += (w_end - vs[p2]) * (attrs[p2] + attr2) / 2
    return area / (w_end - w_start)


def ideal():
    # 获取对应截止点的热效率
    cut_points = np.arange(1, 3.1, 0.1)
    for c in cut_points:
        print('{0:.4}'.format(cal_eff(ct_point=c)))

    cl = cal_eff(tr_short=1.0, tr_long=1.0, ct_point=2.5)
    print('{:.4}'.format(cl))

    # 平均透射率
    # path = 'F:\研究生\计算及工作整理\截止膜\TFC设计及膜参数\\AZO-Ag.xlsx'
    # di = pars_spectrum_via_excel(path, filter_type='no_sub')
    # print(get_avg_attr_of_band(di, 'trs', w_start=2.1, w_end=10.0))


if __name__ == '__main__':
    ideal()
    pass
