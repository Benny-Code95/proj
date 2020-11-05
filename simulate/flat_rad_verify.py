from simulate.cal_rad_Fb import cal_fb_via_band
from CalTools.GetValues import get_line_value_via_lists
from simulate.FilterSpectrum import pars_spectrum_via_excel
import numpy as np

inf = float('inf')


class NotConvergent(Exception):
    pass


# 计算能量守恒
class CalFlatRadiation:

    def __init__(self):
        self.Ta = 298.15
        self.em_out = 1
        self.sigma = 5.67E-8
        self.hga = 10
        self.eba = self.get_ebs_via_band(self.Ta)

    # 计算波段内的黑体辐射力（单位：W/m^2）
    def get_ebs_via_band(self, *tmp, wave_start=0.0, wave_end=float('inf')):
        if not tmp:
            return
        ebs = []
        for t in tmp:
            fbi = cal_fb_via_band(t, wave_start, wave_end)
            ebi = fbi * self.sigma * pow(float(t), 4)
            ebs.append(ebi)
        if len(ebs) == 1:
            return ebs[0]
        return ebs

    # 不透明表面计算（单位：W）
    @staticmethod
    def qr_opaque(eb1, eb2, em1, em2, area1=1.0, area2=1.0):
        if not em1 or not em2:
            return 0.0
        agl = area2 / area1
        fct1 = (1.0 - em1) / em1
        fct2 = 1.0 / agl
        fct3 = (1 - em2) / (em2 * agl)
        qr = area1 * (eb1 - eb2) / (fct1 + fct2 + fct3)
        return qr

    # 半透明表面计算（单位：W）
    def qr_semi_transparent(self, eb1, eb2, eba, em1, em2, tr2, area1=1.0,
                            area2=1.0):
        _em2 = em2 + tr2
        if _em2 == 0:
            return 0.0
        _eb2 = (em2 * eb2 + tr2 * eba) / _em2
        qr = self.qr_opaque(eb1, _eb2, em1, _em2, area1, area2)
        return qr

    # 计算盖板内的导热通量（单位：W）
    @staticmethod
    def cal_qcd_via_tgs(tg_up, tg_down, cond, thick, area=1.0):
        qcd = area * cond * (tg_up - tg_down) / thick
        return qcd

    # 计算平均发射率
    @staticmethod
    def cal_avg_em(tg, pars_spectrum):
        waves, trans = pars_spectrum['trs'][0], pars_spectrum['trs'][1]
        refs = pars_spectrum['rfs'][1]
        emg = 0.0
        for i, w in enumerate(waves):
            w_end = float('inf') if i == len(waves) - 1 else waves[i + 1]
            fbi = cal_fb_via_band(tg, w, w_end)
            emg += fbi * (1 - refs[i] - trans[i])
        return emg

    # 计算玻璃盖板与外界的换热量（单位：W）
    def cal_qg(self, tg, pars_spectrum, area=1.0, hga=0.0):
        emg = self.cal_avg_em(tg, pars_spectrum)
        qrg = area * emg * self.sigma * (pow(tg, 4) - pow(self.Ta, 4))
        qcv = area * hga * (tg - self.Ta)
        return qrg + qcv

    @staticmethod
    def get_average_via_scatter_points(x_list, y_list):
        dx = x_list[-1] - x_list[0]
        if dx == 0:
            return 0.0
        area = 0.0
        for ind, x in enumerate(x_list):
            if ind == 0:
                continue
            area += (y_list[ind] + y_list[ind - 1]) * (x - x_list[ind - 1]) / 2
        return area / dx

    # 对散点分布式的光谱参数转化为分段式的光谱参数
    # 如[[0.3, 0.4][0.8, 0.6]]转化为[[0, 0.3, 0.4], [0.8, 0.7, 0.6]]
    # 即0.3-0.4um:反射率0.7；0.4-inf:反射率0.6
    def pars_transform_useless(self, pars):
        waves, trs, rfs = [0.0], [pars['trs'][1][0]], [pars['rfs'][1][0]]
        ptr, ptr_pre, prf, prf_pre = 0, 0, 0, 0
        w, w_init = 0.3, 0.3
        delta = 1
        count = int(10 / delta)
        tr_pre, rf_pre = None, None
        for i in range(count):
            waves.append(w)
            w_next = w + delta

            if tr_pre is None:
                tr_pre, ptr_pre = get_line_value_via_lists(w_init,
                                                           pars['trs'][0],
                                                           pars['trs'][1],
                                                           pos=0, get_pos=True)
            tr_next, ptr = get_line_value_via_lists(w_next, pars['trs'][0],
                                                    pars['trs'][1], pos=ptr,
                                                    get_pos=True)
            w_list, tr_list = [w], [tr_pre]
            if w < pars['trs'][0][0] < w_next:
                w_list, tr_list = [w, pars['trs'][0][0]], [tr_pre,
                                                           pars['trs'][1][0]]
            w_list.extend(pars['trs'][0][ptr_pre + 1: ptr + 1])
            tr_list.extend(pars['trs'][1][ptr_pre + 1: ptr + 1])
            w_list.append(w_next)
            tr_list.append(tr_next)
            trs.append(self.get_average_via_scatter_points(w_list, tr_list))
            tr_pre, ptr_pre = tr_next, ptr

            if rf_pre is None:
                rf_pre, prf_pre = get_line_value_via_lists(w_init,
                                                           pars['rfs'][0],
                                                           pars['rfs'][1],
                                                           pos=0, get_pos=True)
            rf_next, prf = get_line_value_via_lists(w_next, pars['rfs'][0],
                                                    pars['rfs'][1], pos=prf,
                                                    get_pos=True)
            w_list, rf_list = [w], [rf_pre]
            if w < pars['rfs'][0][0] < w_next:
                w_list, rf_list = [w, pars['rfs'][0][0]], [rf_pre,
                                                           pars['rfs'][1][0]]
            w_list.extend(pars['rfs'][0][prf_pre + 1: prf + 1])
            rf_list.extend(pars['rfs'][1][prf_pre + 1: prf + 1])
            w_list.append(w_next)
            rf_list.append(rf_next)
            rfs.append(self.get_average_via_scatter_points(w_list, rf_list))
            rf_pre, prf_pre = rf_next, prf

            w = w_next

        pars['trs'], pars['rfs'] = [waves, trs], [waves, rfs]

    def pars_transform(self, pars):
        trs, rfs = [], []
        ptr, ptr_pre, prf, prf_pre = 0, 0, 0, 0
        tr_pre, rf_pre = None, None

        w_init, step = 0.3, 0.01
        w_end = 10.0 + step
        waves = [0.0] + list(np.arange(w_init, w_end, step=step))
        # waves = [0.0, 0.3, 1.2, 1.9, 3.1, 7.5, 10.0]

        for ind, w in enumerate(waves):
            if ind == len(waves) - 1:
                trs.append(pars['trs'][1][-1])
                rfs.append(pars['rfs'][1][-1])
                break
            w_next = waves[ind + 1]

            if ind == 0:
                tr_pre, ptr_pre = get_line_value_via_lists(w, pars['trs'][0],
                                                           pars['trs'][1],
                                                           pos=0, get_pos=True)
            tr_next, ptr = get_line_value_via_lists(w_next, pars['trs'][0],
                                                    pars['trs'][1], pos=ptr,
                                                    get_pos=True)
            w_list, tr_list = [w], [tr_pre]
            if w < pars['trs'][0][0] < w_next:
                w_list, tr_list = [w, pars['trs'][0][0]], [tr_pre,
                                                           pars['trs'][1][0]]
            w_list.extend(pars['trs'][0][ptr_pre + 1: ptr + 1])
            tr_list.extend(pars['trs'][1][ptr_pre + 1: ptr + 1])
            w_list.append(w_next)
            tr_list.append(tr_next)
            trs.append(self.get_average_via_scatter_points(w_list, tr_list))
            tr_pre, ptr_pre = tr_next, ptr

            if rf_pre is None:
                rf_pre, prf_pre = get_line_value_via_lists(w, pars['rfs'][0],
                                                           pars['rfs'][1],
                                                           pos=0, get_pos=True)
            rf_next, prf = get_line_value_via_lists(w_next, pars['rfs'][0],
                                                    pars['rfs'][1], pos=prf,
                                                    get_pos=True)
            w_list, rf_list = [w], [rf_pre]
            if w < pars['rfs'][0][0] < w_next:
                w_list, rf_list = [w, pars['rfs'][0][0]], [rf_pre,
                                                           pars['rfs'][1][0]]
            w_list.extend(pars['rfs'][0][prf_pre + 1: prf + 1])
            rf_list.extend(pars['rfs'][1][prf_pre + 1: prf + 1])
            w_list.append(w_next)
            rf_list.append(rf_next)
            rfs.append(self.get_average_via_scatter_points(w_list, rf_list))
            rf_pre, prf_pre = rf_next, prf

        pars['trs'], pars['rfs'] = [waves, trs], [waves, rfs]

    # 根据光谱参数计算吸收面的辐射热通量和吸收面透射至环境的辐射热通量
    # pars_spectrum = {'trs':[[0, 2], [0.8, 0.2]],
    # 'rfs':[[0, 2], [0.1, 0.7]], 'scatter':False}
    # [[0, 3],[0.1, 0.9],[0.8, 0.05]]代表  0-3um:反射率0.1，透射率0.8；
    # 3-inf:反射率0.9，透射率0.05
    def cal_qrh_via_spectrum(self, tmp_h, tmp_g, emh, pars_spectrum, area1=1.0,
                             area2=1.0):
        waves, trans, refs = pars_spectrum['trs'][0], pars_spectrum['trs'][1], \
                             pars_spectrum['rfs'][1]
        qrh, qro, qrt = 0.0, 0.0, 0.0
        agl = area2 / area1
        for i in range(len(waves)):
            wave_start = waves[i]
            wave_end = float('inf') if i == len(waves) - 1 else waves[i + 1]
            eb1, eb2, eba = self.get_ebs_via_band(tmp_h, tmp_g, self.Ta,
                                                  wave_start=wave_start,
                                                  wave_end=wave_end)
            emi = 1 - refs[i] - trans[i]
            qri = self.qr_semi_transparent(eb1, eb2, eba, emh, emi, trans[i],
                                           area1=area1, area2=area2)  # 半透明面辐射计算
            J1 = eb1 - qri * (1 - emh) / (emh * area1)  # 表面1的有效辐射力
            G2 = agl * J1 * area1 / area2  # 表面2的投射辐射力
            qr_tr = trans[i] * area2 * (G2 - eba)  # 从表面2穿透至环境的辐射能量
            qr_opq = qri - qr_tr  # 盖板处未穿透至外界的辐射热通量
            qrh += qri
            qro += qr_opq
            qrt += qr_tr
        return qrh, qro, qrt

    def balance_energy(self, tmp_h, emh, pars_up, pars_down, cond, thc,
                       area1=1.0, area2=1.0, q_source=0.0):
        if pars_up.get('scatter'):
            self.pars_transform(pars_up)
            pars_up.pop('scatter')
        if pars_down.get('scatter'):
            self.pars_transform(pars_down)
            pars_down.pop('scatter')
        tg_down = (tmp_h + self.Ta) / 2
        tg_up = tg_down
        err_max = 0.0001
        qrh, qrg = 0.0, 0.0
        tg_down_min, tg_down_max = self.Ta, tmp_h
        err, count = 1.0, 1
        while abs(err) > err_max and count <= 300:
            err1, count1 = 1.0, 1
            tg_up_min, tg_up_max = tg_down, tmp_h + 30
            while abs(err1) > err_max and count1 <= 30:
                qrg = self.cal_qg(tg_down, pars_down, area2)
                qcd = self.cal_qcd_via_tgs(tg_up, tg_down, cond, thc, area2)
                err1 = (qrg - qcd) / qrg
                if err1 > err_max:
                    tg_up_min, tg_up = tg_up, (tg_up + tg_up_max) / 2
                elif err1 < -err_max:
                    tg_up_max, tg_up = tg_up, (tg_up + tg_up_min) / 2
                count1 += 1

            qrh, qro, qrt = self.cal_qrh_via_spectrum(tmp_h, tg_up, emh,
                                                      pars_up, area1, area2)
            err = (qro + q_source * area2 * 2 - qrg) / qrg
            if err > err_max:
                tg_down_min, tg_down = tg_down, (tg_down + tg_down_max) / 2
            elif err < -err_max:
                tg_down_max, tg_down = tg_down, (tg_down + tg_down_min) / 2
            count += 1
        return qrh, qrg, tg_up, tg_down

    # 透明表面计算（fit COMSOL）（单位：W）
    def qr_transparent(self, ebh, em, area1=1.0, area2=1.0):
        eb0, em0 = 0.0, 1.0
        qr = self.qr_opaque(ebh, eb0, em, em0, area1, area2)
        return qr

    # 找到透明波段截止点和低波段发射率（fit COMSOL）
    def get_wave_seg_and_eml(self, tmp1, tmp2, em1, em2, tr2, wave_start=0.0,
                             wave_end=float('inf'), a1=1.0, a2=1.0):
        eb1, eb2, eba = self.get_ebs_via_band(tmp1, tmp2, self.Ta,
                                              wave_start=wave_start,
                                              wave_end=wave_end)
        agl = a2 / a1

        qr = self.qr_semi_transparent(eb1, eb2, eba, em1, em2, tr2, area1=a1,
                                      area2=a2)  # 半透明面辐射计算
        J1 = eb1 - qr * (1 - em1) / (em1 * a1)  # 表面1的有效辐射力
        G2 = agl * J1 * a1 / a2  # 表面2的投射辐射力
        qra = tr2 * a2 * (G2 - eba)  # 从表面2穿透至环境的辐射能量
        qrg = qr - qra  # 盖板处未穿透至外界的辐射热通量

        qr_tr, qr_opq = 0.0, 0.0
        if tr2 == 0.0:
            return wave_start, em2, qr, qr, qr_tr
        if tr2 == 1.0 or qr == 0.0:
            return wave_end, 0.0, qr, qr_opq, qr

        err_max = 0.001  # 定义最大误差
        count_max = 100

        # 获取透明波段截止点
        seg_min, seg_max = wave_start, wave_end
        seg = (seg_min + seg_max) / 2 if seg_max != float(
            'inf') else 5.0E4 / tmp2
        err1, count = 1.0, 1
        while abs(err1) > err_max and count <= count_max:
            eb1 = self.get_ebs_via_band(tmp1, wave_start=wave_start,
                                        wave_end=seg)
            qr_tr = self.qr_transparent(eb1, em1, area1=a1,
                                        area2=a2)  # COMSOL中透射辐射的计算
            err1 = (qr_tr - qra) / qra
            if err1 > err_max:
                seg_max, seg = seg, (seg_min + seg) / 2
            elif err1 < -err_max:
                seg_min, seg = seg, (seg_max + seg) / 2
            count += 1

        if abs(err1) > 0.01:
            print('截止点错误')
            raise NotConvergent

        # 获取低波段发射率
        em_max, em_min, eml = 1.0, 0.0, 0.5
        err2, count, = 1.0, 1
        eb1, eb2 = self.get_ebs_via_band(tmp1, tmp2, wave_start=seg,
                                         wave_end=wave_end)
        while abs(err2) > err_max and count <= count_max:
            qr_opq = self.qr_opaque(eb1, eb2, em1, eml, area1=a1, area2=a2)
            err2 = (qr_opq - qrg) / qrg
            if err2 > err_max:
                em_max, eml = eml, (em_min + eml) / 2
            elif err2 < -err_max:
                em_min, eml = eml, (em_max + eml) / 2
            count += 1

        if abs(err2) > 0.01:
            print('发射率错误')
            raise NotConvergent
        return seg, eml, qr, qrg, qra

    # 找到各个谱带内的截止点和低波段发射率（fit COMSOL）
    def cal_segments_via_spectrum(self, tmp_h, tmp_g, emh, pars_spectrum,
                                  area1=1.0, area2=1.0):
        waves, trans = pars_spectrum['trs'][0], pars_spectrum['trs'][1]
        refs = pars_spectrum['rfs'][1]
        new_pars = np.array([[], [], []])
        qrs = np.array([0.0, 0.0, 0.0])
        for i in range(len(waves)):
            wave_start = waves[i]
            wave_end = float('inf') if i == len(waves) - 1 else waves[i + 1]
            emi = 1 - refs[i] - trans[i]
            weq = self.get_wave_seg_and_eml(tmp_h, tmp_g, emh, emi, trans[i],
                                            wave_start, wave_end, area1, area2)
            seg, eml, qri, qr_opq, qr_tr = weq
            qrs += [qri, qr_opq, qr_tr]
            pars_i = np.array([[wave_start, seg], [0, eml], [1, 0]])
            if seg in (wave_start, wave_end):
                pars_i = np.array([[wave_start], [eml], [bool(qri == qr_tr)]])
            new_pars = np.hstack((new_pars, pars_i))

        print('总辐射，非透射辐射， 透射辐射', qrs)
        return new_pars

    # 找到全光谱截止点和低波段发射率（fit COMSOL）
    def cal_seg_and_eml_all_spectrum(self, tmp_h, tmp_g, emh, pars_spectrum,
                                     area1=1.0, area2=1.0):
        qrh, qro, qrt = self.cal_qrh_via_spectrum(tmp_h, tmp_g, emh,
                                                  pars_spectrum, area1, area2)
        if qro == 0.0:
            return float('inf'), 0.0, qrh, qro, qrt

        err_max = 0.001  # 定义最大误差
        count_max = 100

        # 获取透明波段截止点
        seg_min, seg_max = 0.0, 1.0E5 / tmp_g
        seg = (seg_min + seg_max) / 2
        err1, count = 1.0, 1
        while abs(err1) > err_max and count <= count_max:
            eb1 = self.get_ebs_via_band(tmp_h, wave_end=seg)
            # COMSOL中透射辐射的计算
            qr_tr = self.qr_transparent(eb1, emh, area1=area1, area2=area2)
            err1 = (qr_tr - qrt) / qrt
            if err1 > err_max:
                seg_max, seg = seg, (seg_min + seg) / 2
            elif err1 < -err_max:
                seg_min, seg = seg, (seg_max + seg) / 2
            count += 1

        if abs(err1) > 0.01:
            print('截止点错误')
            raise NotConvergent

        # 获取低波段发射率
        em_max, em_min, eml = 1.0, 0.0, 0.5
        err2, count, = 1.0, 1
        eb1, eb2 = self.get_ebs_via_band(tmp_h, tmp_g, wave_start=seg)
        while abs(err2) > err_max and count <= count_max:
            qr_opq = self.qr_opaque(eb1, eb2, emh, eml, area1=area1,
                                    area2=area2)
            err2 = (qr_opq - qro) / qro
            if err2 > err_max:
                em_max, eml = eml, (em_min + eml) / 2
            elif err2 < -err_max:
                em_min, eml = eml, (em_max + eml) / 2
            count += 1

        if abs(err2) > 0.01:
            print('发射率错误')
            raise NotConvergent
        return seg, eml, qrh, qro, qrt


def tst_cal_tg():
    ins = CalFlatRadiation()
    # ttt = ins.qr_semi_transparent(1000, 712.53, 0.9, 0.53237, 0.34015, 1.4137,
    #                               0.9)
    # print(ttt)

    # p_glass = {
    #     'rfs': [[0, 3.6, 7.5, 10.0], [0.131, 0.059, 0.473, 0.133]],
    #     'trs': [[0, 3.6, 7.5, 10.0], [0.814, 0.027, 0, 0]]
    # }
    # p_coating = {
    #     'rfs': [[0, 3.6, 7.5, 10.0], [0.131, 0.059, 0.473, 0.133]],
    #     'trs': [[0, 3.6, 7.5, 10.0], [0.814, 0.027, 0, 0]]
    # }
    # p_coating = {
    #     'trs': [[0, 2.5], [0.99, 0]],
    #     'rfs': [[0, 2.5], [0, 1]]
    # }
    # filter_path = 'F:\\研究生\\计算及工作整理\\模型验证\\截止膜验证.xlsx'
    # p_glass = pars_spectrum_via_excel(filter_path, 'RIF-solar')
    # p_coating = pars_spectrum_via_excel(filter_path, 'RIF-coating')
    # filter_path = 'F:\\研究生\\计算及工作整理\\截止膜\\计算\\AZO-Ag.xlsx'
    filter_path = 'F:\\研究生\\计算及工作整理\\截止膜\\计算\\AZO-Ag.xlsx'
    pars = pars_spectrum_via_excel(filter_path)
    p_class = {'rfs': [[0, 1.5, 3.5, 10.0], [0.07, 0.03, 0.07, 0.07]],
               'trs': [[0, 1.5, 3.5, 10.0], [0.825, 0.26, 0, 0]]}
    # ttt = ins.balance_energy(1373, 1, pars, p_class, 4, 0.005, area1=0.35476,
    #                          area2=0.05657, q_source=0)
    # print('mean:{0}\tmax:{1}'.format((ttt[2] + ttt[3]) / 2 - 273.15,
    #                                  ttt[2] - 273.15))
    th, tgu, tgd = 773.15, 489.0, 479.2
    print('盖板下发射率：{:.4f}'.format(ins.cal_avg_em(tgd, p_class)))
    tt = ins.cal_seg_and_eml_all_spectrum(th, tgu, 1.0, p_class,
                                          area1=1, area2=1)
    print('无膜--截止点：{0:.4f} 盖板上发射率：{1:.4f}'.format(tt[0], tt[1]))

    tt = ins.cal_seg_and_eml_all_spectrum(th, tgu, 1.0, pars,
                                          area1=0.35476, area2=0.05657)
    print('有膜--截止点：{0:.4f} 盖板上发射率：{1:.4f}'.format(tt[0], tt[1]))
    print(tt)


def tst_cal_wave_seg():
    ins = CalFlatRadiation()
    t = ins.get_ebs_via_band(200.0, 300.0, wave_end=10.0)
    print(t)
    pass


if __name__ == '__main__':
    tst_cal_tg()
    # tst_cal_wave_seg()
