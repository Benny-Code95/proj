import math


class EnergyVerify:

    def __init__(self, eta, eta_opt, Ib, to, ti):

        # 物理常数
        self.gra = 9.8  # 重力加速度
        self.sigma = 5.67E-8  # 斯特潘-玻尔兹曼常数

        # 吸收器结构参数
        self.d = 0.04  # 窗口宽度
        self.dep = 0.048  # 腔体深度
        self.R0 = 0.03  # 腔体弧面流道内半径
        self.w = self.dep - self.R0  # 腔体圆心与窗口的距离

        self.R1 = 0.06  # 保温层外半径
        self.S_ins = 0.396
        # self.k = self.R1 * 2  # 吸收器外部宽度
        # self.n = self.k - self.d
        # self.m = self.w + self.R1  # 保温层高度
        self.cd_ins = 0.04  # 保温层导热系数

        self.S = 9.0E-4  # 流道截面积
        self.C_wet = 0.08  # 流道截面湿周
        self.De = 0.011  # 流道截面当量直径
        self.S_arc = 0.198  # 流道内弧面面积
        self.S_fin = 0.257  # 吸收面肋片面积
        # self.S_abs = 1.236  # 吸热面面积

        self.S_gc = 0.056  # 盖板面积
        self.thick = 0.001  # 盖板厚度
        self.cd_g = 1.4  # 玻璃导热系数

        # 槽结构参数
        self.L = 1.4  # 槽的长度
        self.D = 1.1  # 槽的宽度

        # 进出口油温
        self.to = to  # 进口温度
        self.ti = ti  # 出口温度

        # 能量
        self.Ib = Ib  # 辐照度
        self.eta = eta  # 集热器效率
        self.eta_opt = eta_opt  # 集热器光学效率
        self.Q_all = self.Ib * self.L * self.D  # 总辐射能
        self.Q_in = self.Q_all * self.eta_opt  # 接收到的辐射能
        self.Q_use = self.Q_all * self.eta  # 有效利用的热量
        self.Q_loss = self.Q_in - self.Q_use  # 热损失
        # self.Q_abs_gc = self.Ib * self.S_gc * 0.08
        self.Q_abs_gc = 0
        self.Q_abs_ins = self.Ib * self.S_ins * 0.07

    @staticmethod
    def get_par_of_air(t):
        tc = t - 273.15
        kv = 1.14E-7 * tc + 1.23E-5
        pr = 3.48E-7 * tc ** 2 - 2.11E-4 * tc + 0.71
        cd = 7.27E-5 * tc + 2.46E-2
        pars = {
            'kv': kv,
            'pr': pr,
            'cd': cd
        }
        return pars

    @staticmethod
    def get_par_of_htf(t):
        kv = 0.000298033 - 1.96358E-06 * t + 4.35784E-09 * t ** 2 - 3.24421E-12 * t ** 3
        cd = 0.39728 - 0.00185 * t + 4.25744E-6 * t ** 2 - 3.47222E-9 * t ** 3
        cp = 860.82 + 3.57429 * t
        rho = 1151.44 - 1.05526 * t + 4.3306E-4 * t ** 2
        pr = rho * kv * cp / cd
        pars = {
            'kv': kv,
            'pr': pr,
            'cd': cd,
            'cp': cp,
            'rho': rho
        }
        return pars

    def get_Re_of_flow(self, t_out):
        t = (t_out + self.ti) / 2
        pars_htf = self.get_par_of_htf(t)
        rho, cp, kv = pars_htf['rho'], pars_htf['cp'], pars_htf['kv']
        qm = self.Q_use / (t_out - self.ti) / cp
        v = qm / (rho * self.S)
        Re = self.De * v / kv
        return Re

    # 保温层与环境换热量
    def cal_Q1(self, t_ins=0.0, ta=0.0, t2=0.0):
        while t_ins == 0:
            print('绝热层温度为0，请输入假定值（单位为K）：')
            t_ins = float(input())
        while ta == 0:
            print('环境温度为0，请输入假定值（单位为K）：')
            ta = float(input())
        while t2 == 0:
            print('保温层内侧温度为0，请输入假定值（单位为K）：')
            t2 = float(input())
        tm = (t_ins + ta) / 2
        a = 1 / tm
        pars_air = self.get_par_of_air(tm)
        kv, pr, cd = pars_air['kv'], pars_air['pr'], pars_air['cd']
        Gr = self.gra * a * (t_ins - ta) * (self.R1 ** 3) / (kv ** 2)
        h = 0.48 * cd * (Gr * pr) ** 0.25 / self.R1
        # lv = self.m
        # lh = self.k / (2 * (self.k + 1))
        # Grv = self.gra * a * (t_ins - ta) * (lv ** 3) / (kv ** 2)
        # Grh = self.gra * a * (t_ins - ta) * (lh ** 3) / (kv ** 2)
        # Nuu, Nud, Nuv = 0.54 * (Grh * pr) ** 0.25, 0.27 * (Grh * pr) ** 0.25, 0.59 * (Grv * pr) ** 0.25
        # hu, hd, hv = cd * Nuu / lh, cd * Nud / lh, cd * Nuv / lv

        Qcv_ins_a = h * (t_ins - ta) * self.S_ins
        e = 0.1  # 保温层发射率
        Qr_ins_a = self.sigma * e * ((t_ins ** 4) - (ta ** 4)) * self.S_ins
        Q1 = Qcv_ins_a + Qr_ins_a
        Q1_ = 2 * math.pi * (t2 - t_ins) * self.L * self.cd_ins / math.log(self.R1 / self.R0)
        print(Qr_ins_a, '-------', Qcv_ins_a)
        return Q1, Q1_

    # 导热油与保温层换热量
    def cal_Q2(self, to=0.0, t2=0.0):
        while to == 0:
            print('流体出口温度为0，请输入假定值（单位为K）：')
            to = float(input())
        while t2 == 0:
            print('流道内侧温度为0，请输入假定值（单位为K）：')
            t2 = float(input())
        tf = (self.ti + to) / 2
        pars_htf = self.get_par_of_htf(tf)
        kv, pr, cd, = pars_htf['kv'], pars_htf['pr'], pars_htf['cd']
        Re = self.get_Re_of_flow(t_out=to)
        ss = Re * pr * self.De / self.L
        nu = 3.669 + (0.169 * ss ** 0.25) / (1 + 0.191 * ss ** (7 / 12))
        hf = cd * nu / self.De
        Q2 = self.S_arc * hf * (tf - t2)
        return Q2

    # 吸热面与流体换热量
    def cal_Q3(self, t1=0.0, to=0.0):
        while to == 0:
            print('流体出口温度为0，请输入假定值（单位为K）：')
            to = float(input())
        while t1 == 0:
            print('吸收面温度为0，请输入假定值（单位为K）：')
            t1 = float(input())
        tf = (self.ti + to) / 2
        pars_htf = self.get_par_of_htf(tf)
        kv, pr, cd, = pars_htf['kv'], pars_htf['pr'], pars_htf['cd']
        Re = self.get_Re_of_flow(to)
        ss = Re * pr * self.De / self.L
        nu = (4.36 + 0.023 * ss) / (1.0 + 0.0012 * ss ** 0.8)
        h = cd * nu / self.De
        Q3 = self.S_fin * h * (t1 - tf)
        return Q3

    # 盖板与环境换热量
    def cal_Q4(self, tg=0.0, ta=0.0):
        while tg == 0:
            print('盖板温度为0，请输入假定值（单位为K）：')
            tg = float(input())
        while ta == 0:
            print('空气温度为0，请输入假定值（单位为K）：')
            ta = float(input())
        tm = (tg + ta) / 2
        a = 1 / tm
        pars_air = self.get_par_of_air(tm)
        kv, pr, cd = pars_air['kv'], pars_air['pr'], pars_air['cd']
        Gr = self.gra * a * (tg - ta) * (self.d ** 3) / (kv ** 2)
        h = cd * 0.27 * (Gr * pr) ** 0.25 / self.d
        e = 0.8  # 玻璃板发射率
        Qr_g_a = self.S_gc * self.sigma * e * (tg ** 4 - ta ** 4)
        Qcv_g_a = self.S_gc * h * (tg - ta)
        Q4 = Qcv_g_a + Qr_g_a
        return Q4

    # 吸收面与盖板间的换热量
    def cal_Q4f(self, t1, tg):
        while tg == 0:
            print('盖板温度为0，请输入假定值（单位为K）：')
            tg = float(input())
        while t1 == 0:
            print('吸收面温度为0，请输入假定值（单位为K）：')
            t1 = float(input())
        tm = (t1 + tg) / 2
        a = 1 / tm
        l = self.dep
        pars_air = self.get_par_of_air(tm)
        kv, pr, cd = pars_air['kv'], pars_air['pr'], pars_air['cd']
        Gr = self.gra * a * (t1 - tg) * (l ** 3) / (kv ** 2)
        h = 0.59 * cd * (Gr * pr) ** 0.5 / self.dep
        Qcv_1_g = h * self.S_gc * (t1 - tg)
        e_g = 0.95
        e1 = 0.15
        e = 1 / (1 / e_g + 1 / e1 - 1.0)
        Qr_1_g = self.sigma * e * self.S_gc * (t1 ** 4 - tg ** 4)
        Q4f = Qcv_1_g + Qr_1_g
        print(Qr_1_g, '===========', Qcv_1_g)
        return Q4f

    # 盖板处的热平衡校核
    def verify_Q4_Q4f(self, tt1, ttg, tta):
        count = 0
        print('---校验盖板热平衡中...')
        while count < 300:
            Q4, Q4f = self.cal_Q4(tg=ttg, ta=tta), self.cal_Q4f(t1=tt1, tg=ttg)
            er_4_4f = (Q4 - self.Q_abs_gc - Q4f) / Q4
            if abs(er_4_4f) <= 1E-2:
                break
            if er_4_4f > 0:
                ttg -= 0.1
            else:
                ttg += 0.1
            count += 1
        if count >= 300:
            print('迭代后的值为t1:{0},tg:{1},ta:{2}'.format(tt1, ttg, tta))
            print('超过迭代次数，请重新设定t1、tg、ta!!!!')
            return
        print('校验盖板热平衡完成')
        return {
            '1': tt1,
            'g': ttg,
            'Q4': Q4
        }

    # 保温层处热平衡校核
    def verify_Q1_Q1f_Q2(self, to, t2, t_ins, ta):
        ct2 = 0
        print('---校验保温层热平衡中...')
        while ct2 < 300:
            ct1 = 0
            while ct1 < 300:
                Q1, Q1f = self.cal_Q1(t_ins=t_ins, ta=ta, t2=t2)
                error = (Q1 - self.Q_abs_ins - Q1f) / Q1
                if abs(error) <= 2E-2:
                    break
                if error < 0:
                    t_ins += 0.1
                else:
                    t_ins -= 0.1
                ct1 += 1
            if ct1 >= 300:
                print('迭代后的值为t2:{0},t_ins:{1},ta:{2}\n超过迭代次数，请重新设定t2、t_ins、ta'.format(t2, t_ins, ta))
                return

            Q2 = self.cal_Q2(to=to, t2=t2)
            error2 = (Q2 - Q1) / Q2
            if abs(error2) <= 2E-2:
                break
            if error2 > 0:
                t2 += 0.1
            else:
                t2 -= 0.1
            ct2 += 1
        if ct2 >= 300:
            print('迭代后的值为to:{0},t2:{1}'.format(to, t2))
            print('超过迭代次数，请重新设定to、t2!!!!')
            return
        print('校验保温层热平衡完成~')
        return {
            'o': to,
            '2': t2,
            'ins': t_ins,
            'Q1': Q1,
            'Q2': Q2
        }

    # 吸收面温度及导热出口油温度校核
    def verify(self, t1, t2, to, t_ins, tg, ta):
        ct = 0
        print('---校验吸收面温度及导热油温度中...')
        while ct < 3000:
            ct1 = 0
            while ct1 < 3000:
                c1 = self.verify_Q4_Q4f(t1, tg, ta)
                c2 = self.verify_Q1_Q1f_Q2(to, t2, t_ins, ta)
                if (not c1) or (not c2):
                    print('校准后的数据为\nt1:{0}\ntg:{1}\nto:{2}\nt2:{3}\nt_ins:{4}\n'.format(t1, tg, to, t2, t_ins))
                    return
                t1, tg, Q4 = c1['1'], c1['g'], c1['Q4']
                to, t2, t_ins, Q1, Q2 = c2['o'], c2['2'], c2['ins'], c2['Q1'], c2['Q2']
                error = (Q1 + Q4 - self.Q_loss) / self.Q_loss
                if abs(error) < 2E-2:
                    break
                if error < 0:
                    t1 += 0.1
                else:
                    t1 -= 0.1
                ct1 += 1
            if ct1 >= 3000:
                print('迭代后的值为t1:{0}\n超过迭代次数，请重新设定t1'.format(t1))
                print('\n========校准后的数据为\nt1:{0}\ntg:{1}\ntf:{2}\nt2:{3}\nt_ins:{4}\n'.format(t1, tg, to, t2, t_ins))
                return
            Q3_bal = Q1 + self.Q_use
            Q3_cal = self.cal_Q3(t1, to)
            error0 = (Q3_cal - Q3_bal) / Q3_cal
            if abs(error0) < 2E-2:
                break
            if error0 > 0:
                to += 0.1
            else:
                to -= 0.1
            ct += 1
        if ct >= 3000:
            print('迭代后的值为to:{0}\n超过迭代次数，请重新设定to'.format(to))
            print('\n========校准后的数据为\nt1:{0}\ntg:{1}\nto:{2}\nt2:{3}\nt_ins:{4}\n'.format(t1, tg, to, t2, t_ins))
            return
        print('校验吸收面温度及导热油出口温度完成~')
        print('\n========校准后的数据为\nt1:{0}\ntg:{1}\nto:{2}\nt2:{3}\nt_ins:{4}\n'
              'Q1:{5}\nQ2:{6}\nQ3:{7}\nQ4:{8}'.format(t1, tg, to, t2, t_ins, Q1, Q2, Q3_cal, Q4))


def verify():
    # 文献给予的参数
    eta_all = 0.6216
    I = 1003.0
    Ta = 290.15
    T_in = 300

    # 假定值
    eta_optical = 0.722
    T_out = 386
    Tf = (T_in + T_out) / 2
    print('导热油平均温度为：{0}'.format(Tf))
    T1 = 363
    T2 = 300
    Tg = 320
    T_ins = 300

    # 校验
    ins = EnergyVerify(eta=eta_all, eta_opt=eta_optical, Ib=I, to=T_out, ti=T_in)
    ins.verify(t1=T1, t2=T2, to=T_out, ta=Ta, tg=Tg, t_ins=T_ins)


def verify_glass():
    # 文献给予的参数
    eta_all = 0.6216
    I = 1003.0
    Ta = 290.15
    T_in = 300

    # 假定值
    eta_optical = 0.722
    T_out = 386
    Tf = (T_in + T_out) / 2
    print('导热油平均温度为：{0}'.format(Tf))
    T1 = 363
    T2 = 300
    Tg = 330
    T_ins = 300

    ins1 = EnergyVerify(eta=eta_all, eta_opt=eta_optical, Ib=I, to=T_out, ti=T_in)
    cons = ins1.verify_Q4_Q4f(tt1=T1, ttg=Tg, tta=Ta)
    print(cons)


if __name__ == '__main__':
    # verify()
    verify_glass()
