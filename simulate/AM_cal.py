import pandas as pd
from simulate.AM_spectrum import AM15_waves, AM15_DNI
from CalTools.GetValues import get_line_value


class AmCal:

    # 根据透射率曲线取得对应波长的透射率
    # nt_list = [[1, 1] ,[1.01, 0.1]] # [波长um 透射率]
    @staticmethod
    def get_tr_via_wave(n, trs, pos=0):
        if pos >= len(trs['wave']):
            pos = len(trs['wave']) - 2
        while n > trs['wave'][pos + 1] and pos < len(trs['wave']) - 2:
            pos += 1
        tr = get_line_value(n, trs['wave'][pos], trs['wave'][pos + 1],
                            trs['tran'][pos], trs['tran'][pos + 1])
        return tr, pos

    # 计算AM1.5投射辐射强度和透射率（直照辐射强度默认值为900.1W/m^2）
    def cal_dni_900(self, nt_df, dni=900.1, wave_start=0.0,
                    wave_end=float('inf')):
        trans = pd.DataFrame(nt_df, columns=['wave', 'tran']) if type(
            nt_df) == list else nt_df
        sum_tr_dni, sum_dni = 0.0, 0.0
        pos_wave = 0
        len_waves = len(AM15_waves)
        for i in range(len_waves):

            # 获取透射率
            wave_cur = AM15_waves[i]
            tr, pos_wave = self.get_tr_via_wave(wave_cur, trans, pos=pos_wave)
            if wave_cur < wave_start or wave_cur > wave_end:
                continue

            # 获取波长间距
            last = len_waves - 1
            i_minus, i_plus = i - 1, i + 1
            if i == 0:
                i_minus += 1
                i_plus += 1
            elif i == last:
                i_minus -= 1
                i_plus -= 1

            # 波段间距nm
            d_wave = (AM15_waves[i_plus] - AM15_waves[i_minus]) * 1000 / 2

            # 计算波段内的透射辐射及总辐射
            sum_tr_dni += d_wave * AM15_DNI[i] * tr
            sum_dni += d_wave * AM15_DNI[i]

        sum_tr_dni *= dni / 900.1
        sum_dni *= dni / 900.1
        tr_dni = sum_tr_dni / sum_dni
        # print('透射率为：{0}\n透射强度为：{1} W/m^2（波段内直照辐射强度为{2}W/m^2）'.format(tr_dni, sum_tr_dni, sum_dni))
        return tr_dni, sum_dni, sum_tr_dni

    # 梯形法计算AM1.5投射辐射强度和透射率
    def cal_dni_900_via_trap(self, nt_df, dni=900.1, wave_start=0.0,
                             wave_end=float('inf')):
        nt_df = pd.DataFrame(nt_df, columns=['wave', 'tran']) if type(
            nt_df) == list else nt_df
        sum_tr_dni, sum_dni = 0.0, 0.0
        dni_ratio = dni / 900.1
        pos_wave = 0
        trans = []
        for i in range(len(AM15_waves)):

            # 获取透射率
            wave_cur = AM15_waves[i]
            tr, pos_wave = self.get_tr_via_wave(wave_cur, nt_df, pos=pos_wave)
            trans.append(tr)
            if wave_cur < wave_start or wave_cur > wave_end or i == 0:
                continue

            # 波段间距nm
            d_wave = (AM15_waves[i] - AM15_waves[i - 1]) * 1000

            # 计算波段内的透射辐射及总辐射
            sum_tr_dni += d_wave * (AM15_DNI[i] * tr + AM15_DNI[i - 1] * trans[
                i - 1]) * dni_ratio / 2
            sum_dni += d_wave * (AM15_DNI[i] + AM15_DNI[i - 1]) / 2

        sum_tr_dni *= dni / 900.1
        sum_dni *= dni / 900.1
        tr_dni = sum_tr_dni / sum_dni
        print('透射率为：{0}\n透射强度为：{1} W/m^2（波段内直照辐射强度为{2}W/m^2）'.format(tr_dni,
                                                                     sum_tr_dni,
                                                                     sum_dni))
        return tr_dni, sum_dni, sum_tr_dni

    # 通过截止膜文件获取AM1.5透射率
    def cal_am_tr_via_path(self, if_path, wave_start=0.0,
                           wave_end=float('inf')):
        nt_df = pd.read_excel(if_path)
        return self.cal_dni_900_via_trap(nt_df, wave_start=wave_start,
                                         wave_end=wave_end)


if __name__ == '__main__':
    AM15_path = 'F:\\研究生\\计算及工作整理\\截止膜\\太阳光谱数据\\太阳光谱.xlsx'
    IF_path = 'F:\\研究生\\计算及工作整理\\截止膜\\计算\\AZO-Ag.xlsx'
    root = AmCal()
    # DNI = 900.1
    # cut_point = 1.8
    # tr_low, tr_high = 0.8, 1
    # tr_list = [[cut_point, tr_low],
    #            [cut_point, tr_high]]
    # ttt1 = root.cal_dni_900(tr_list, wave_start=0.0, wave_end=cut_point)
    ttt1 = root.cal_am_tr_via_path(IF_path)
    # ttt = root.cal_dni_900_via_trap(tr_list, wave_start=0.0, wave_end=cut_point)
    # print(ttt)
