from simulate.cal_rad_Fb import cal_fb
from simulate.AM_cal import AmCal
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
    T = 673.15  # 集热温度
    DNI, C = 1000, 70  # 直照辐射强度和聚光比
    eps_rec = 0.9  # 吸收面发射率
    fb = cal_fb(Tk=T, n=ct_point)
    q_loss = eps_rec * 5.67E-8 * (pow(T, 4) - pow(293.15, 4)) * (
                fb * tr_short + (1 - fb) * tr_long)
    q_solar = DNI * C
    ef_loss = q_loss / q_solar

    ef_col = ef_opt - ef_loss
    return ef_col


if __name__ == '__main__':
    # 短波透射率
    # short_wave = np.arange(0, 1.1, 1)
    # # 长波透射率
    # long_wave = np.arange(0, 1.1, 1)
    #
    # for l in long_wave:
    #     for s in short_wave:
    #         eff = cal_eff(tr_short=s, tr_long=l, ct_point=2.5)
    #         print('{0:.3}'.format(eff), end='\t')
    #     print('')

    # 获取对应截止点的热效率
    cut_points = np.arange(1, 3.1, 0.1)
    for c in cut_points:
        print('{0:.4}'.format(cal_eff(ct_point=c)))

    print(cal_eff(tr_short=1, tr_long=1, ct_point=2.5))
    print(cal_eff(tr_short=0.85, tr_long=0.06, ct_point=2.5))
    pass
