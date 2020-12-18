from simulate.flat_rad_verify import CalFlatRadiation, NotConvergent
from simulate.FilterSpectrum import pars_spectrum_via_excel
from numpy.linalg import solve as slv
import math
import numpy as np
import time


# 计算腔体的辐射热通量
class SurfaceRadiation(object):

    def __init__(self, pars):
        """
        :param pars: format {'abs':[Eh, Ah, eh], 'ref':[Er, Ar, er],
        'gc':[Eg, Ag, eg]}
        """
        self.pars = pars

    @staticmethod
    def cal_aki(k, i, ek, aki):
        delta = 1.0 if k == i else 0.0
        return (delta - (1.0 - ek) * aki) / ek

    def get_agl(self):
        da, dr, dg = self.pars['abs'], self.pars['ref'], self.pars['gc']
        lrg = math.sqrt(dr[1] ** 2 + dg[1] ** 2)

        agr = (dr[1] + dg[1] - lrg) / (2 * dg[1])
        agh = (lrg * 2 - dr[1] * 2) / (2 * dg[1])

        arr = (lrg * 2 - dg[1] * 2) / (2 * dr[1])
        arg = agr * dg[1] / dr[1]

        ahh = 1 - dg[1] / da[1]
        ahg = agh * dg[1] / da[1]
        ahr = arg * dr[1] / da[1]

        angles = [
            [ahh, ahr, ahr, ahg],
            [arg, 0.0, arr, arg],
            [arg, arr, 0.0, arg],
            [agh, agr, agr, 0.0]
        ]
        return angles

    def cal_aks(self):
        da, dr, dg = self.pars['abs'], self.pars['ref'], self.pars['gc']
        aks = self.get_agl()
        eks = [da[2], dr[2], dr[2], dg[2]]
        for i, js in enumerate(aks):
            for j, ak in enumerate(js):
                aks[i][j] = self.cal_aki(i, j, eks[i], aks[i][j])
        return aks

    def cal_Qs(self):
        Js = self.cal_Js()
        As = [self.pars['abs'][1], self.pars['ref'][1], self.pars['ref'][1],
              self.pars['gc'][1]]
        Gs = []
        angles = self.get_agl()
        for i in range(4):
            gi = 0.0
            for j in range(4):
                gi += Js[j] * As[j] * angles[j][i]
            Gs.append(gi / As[i])

        Qs = [(Js[i] - Gs[i]) * As[i] for i in range(4)]
        return Qs, Js, Gs

    def cal_Js(self):
        Ebs = [self.pars['abs'][0], self.pars['ref'][0], self.pars['ref'][0],
               self.pars['gc'][0]]
        aks = self.cal_aks()
        js = slv(np.mat(aks), np.mat(Ebs).T)
        Js = list(np.array(js.T)[0])
        return Js


class ArcRadiation(CalFlatRadiation):

    def __init__(self):
        self.Ah = 0.34573
        self.Ar = 0.015
        self.Ag = 0.05657
        self.Ta = 293.15
        super().__init__()

    def qr_semitransparent(self, ebh, ebr, ebg, eba, emh, emr, emg, trg):
        _emg = emg + trg
        _ebg = (emg * ebg + trg * eba) / _emg
        pars = {'abs': [ebh, self.Ah, emh], 'ref': [ebr, self.Ar, emr],
                'gc': [_ebg, self.Ag, _emg]}
        qs, js, gs = SurfaceRadiation(pars).cal_Qs()
        qrh = qs[0]
        qrt = trg * self.Ag * (gs[3] - eba)
        qro = qrh - qrt
        return qrh, qro, qrt

    def cal_qr_via_spectrum(self, tmp_h, tmp_r, tmp_g, emh, emr, parSpectrum):
        if parSpectrum.get('scatter'):
            self.pars_transform(parSpectrum)
            parSpectrum.pop('scatter')

        waves = parSpectrum['trs'][0]
        trans, refs = parSpectrum['trs'][1], parSpectrum['rfs'][1]
        qrh, qro, qrt = 0.0, 0.0, 0.0
        for i in range(len(waves)):
            wave_start = waves[i]
            wave_end = float('inf') if i == len(waves) - 1 else waves[i + 1]
            ebh, ebr, ebg, eba = self.get_ebs_via_band(tmp_h, tmp_r, tmp_g,
                                                       self.Ta,
                                                       wave_start=wave_start,
                                                       wave_end=wave_end)
            emi = 1 - refs[i] - trans[i]
            qs = self.qr_semitransparent(ebh, ebr, ebg, eba, emh, emr, emi,
                                         trans[i])  # 半透明面辐射计算
            qrh += qs[0]
            qro += qs[1]
            qrt += qs[2]
        return qrh, qro, qrt

    def get_seg_and_eml(self, tmp_h, tmp_r, tmp_g, emh, emr, parSpectrum):
        qrh, qro, qrt = self.cal_qr_via_spectrum(tmp_h, tmp_r, tmp_g, emh, emr,
                                                 parSpectrum)
        if qro == 0.0:
            return float('inf'), 0.0, qrh, qro, qrt

        err_max = 0.001  # 定义最大误差
        count_max = 100

        # 获取透明波段截止点
        seg_min, seg_max = 0.0, 1.0E5 / tmp_g
        seg = (seg_min + seg_max) / 2
        err1, count = 1.0, 1
        while abs(err1) > err_max and count <= count_max:
            ebh, ebr = self.get_ebs_via_band(tmp_h, tmp_r, wave_end=seg)
            # COMSOL中透射辐射的计算
            qr_tr = self.qr_semitransparent(ebh, ebr, 0.0, 0.0, emh, emr, 0.0,
                                            1.0)[2]

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
        ebh, ebr, ebg = self.get_ebs_via_band(tmp_h, tmp_r, tmp_g,
                                              wave_start=seg)
        while abs(err2) > err_max and count <= count_max:
            qr_opq = self.qr_semitransparent(ebh, ebr, ebg, 0.0, emh, emr, eml,
                                             0.0)[1]
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


def tst():
    ins = ArcRadiation()
    ins.__setattr__('Ta', 293.15)
    sub_path = 'F:\研究生\计算及工作整理\截止膜\TFC设计及膜参数\\silica_glass.xlsx'
    p_glass = pars_spectrum_via_excel(sub_path)
    th, trf, tgu, tgd = 873.15, 791.0, 683.0, 661.0
    tt = ins.get_seg_and_eml(th, trf, tgu, 1.0, 0.1, p_glass)
    print('无膜--盖板下发射率：{:.4f}'.format(ins.cal_avg_em(tgd, p_glass)))
    print('无膜--截止点：{0:.4f} 盖板上发射率：{1:.4f}'.format(tt[0], tt[1]))
    print(tt)

    filter_path = 'F:\研究生\计算及工作整理\截止膜\TFC设计及膜参数\\AZO-Ag.xlsx'
    p_filter_inner = pars_spectrum_via_excel(filter_path, filter_type='coating')
    p_filter_out = pars_spectrum_via_excel(filter_path, filter_type='glass')
    tt = ins.get_seg_and_eml(th, trf, tgu, 1.0, 0.1, p_filter_inner)
    print('有膜--盖板下发射率：{:.4f}'.format(ins.cal_avg_em(tgd, p_filter_out)))
    print('有膜--截止点：{0:.4f} 盖板上发射率：{1:.4f}'.format(tt[0], tt[1]))
    print(tt)
    pass


def tst1():
    pars = {'abs': [11642, 0.34573, 1], 'ref': [8464, 0.015, 0.1],
            'gc': [5566, 0.05657, 1.0]}
    ins = SurfaceRadiation(pars)
    s = time.time()
    print(ins.cal_Qs())
    s1 = time.time()
    s2 = time.time()
    print(s1 - s, s2 - s1)


if __name__ == '__main__':
    tst()
