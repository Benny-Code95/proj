from sympy import *
# from collections import deque
import numpy as np


class RadiationCalculation:

    def __init__(self, face_mount=3, sigma_const=5.670373 * 10 ** (-8)):
        self.sigma = sigma_const
        self.faces = face_mount

    def cal_AngleFactors(self, coors):
        '''通过坐标计算封闭腔体任意两表面的角系数，且任意两表面均可以望到对方'''

        coors_len = len(coors)
        if coors_len < 2:
            print('x,y坐标列表长度不到3，请重新输入！')
            return
        afs = []
        for k in range(coors_len):
            k_plus = k + 1 if k != coors_len - 1 else 0
            coors_k = [coors[k], coors[k_plus]]
            af_k = []
            for i in range(coors_len):
                i_plus = i + 1 if i != coors_len - 1 else 0
                if i == k:
                    af_k.append(0)
                    continue
                coors_i = [coors[i], coors[i_plus]]
                coors_ki = coors_k + coors_i
                af_k.append(self.AngFact_2face_coors(coors_ki))
            afs.append(af_k)
        return np.array(afs)

    def AngFact_2face_coors(self, coors):
        '''点1与点2的连线为表面1，点3与点4的连线为表面2'''
        af12 = self.AngFact_faces_adj_coors([i for p, i in enumerate(coors) if p != 3])
        af14 = self.AngFact_faces_adj_coors([i for p, i in enumerate(coors) if p != 2])
        af13 = af14 - af12
        return af13

    def AngFact_faces_adj_coors(self, coors):
        '''点1与点2的连线为表面1，点2与点3的连线为表面2，通过坐标计算表面1对表面2的角系数'''
        if len(coors) != 3:
            print('坐标组输入有误，长度不为3，请检查！')
            return
        return self.AngFact_faces_area(self.areas_via_coors(coors))

    @staticmethod
    def areas_via_coors(coors):
        As = []
        for i in range(len(coors)):
            i_plus = i + 1 if i != len(coors) - 1 else 0
            Aix = coors[i][0] - coors[i_plus][0]
            Aiy = coors[i][1] - coors[i_plus][1]
            As.append(sqrt(Aix ** 2 + Aiy ** 2))
        return As

    @staticmethod
    def AngFact_faces_area(areas):
        '''通过面积计算相邻两表面的角系数'''
        len_as = len(areas)
        if len_as != 3:
            print('表面数不为3，请重新输入！')
            return
        af12 = (areas[0] + areas[1] - areas[2]) / (2 * areas[0])
        return af12

    def cal_aki(self, ems_list, coors):
        ems = np.array(ems_list)
        faces = self.faces
        ems = ems.repeat([faces] * faces).reshape([faces, faces])  # question
        krk = np.zeros(shape=[faces, faces])
        krk[range(faces), range(faces)] = 1  # question
        aki = (krk - (1 - ems) * self.cal_AngleFactors(coors)) / ems
        return aki

    def cal_Js(self, ems, coors, Ths):
        aki = self.cal_aki(ems_list=ems, coors=coors)
        Js = [Symbol('J' + str(i)) for i in range(self.faces)]
        eqs_left = np.dot(aki, Js)
        Ebs = self.sigma * np.array(Ths) ** 4
        eqs = eqs_left - Ebs
        return solve(eqs, Js), Ebs

    def cal_heat_flux(self, ems, coors, Ths):
        Js_dict, Ebs = self.cal_Js(ems, coors, Ths)
        Js = np.array([Js_dict[Symbol('J' + str(k))] for k in range(self.faces)])
        As = np.array(self.areas_via_coors(coors))
        ems = np.array(ems)
        ems_cmb = ems / (1 - ems)
        Qs = ems_cmb * (Ebs - Js) * As
        return Qs


def float_int_all(itr):
    if type(itr) == tuple:
        itr = tuple(float_int_all(list(itr)))
    elif type(itr) == list:
        for p, i in enumerate(itr):
            itr[p] = float(i) if type(i) == int else float_int_all(i)
    return itr


def symbol_all(mt, *vas):
    if not vas:
        return []
    syms = []
    for m in range(mt):
        if len(vas) == 1:
            syms.append(Symbol(str(vas[0]) + str(m)))
        else:
            syms.append(tuple(Symbol(str(v) + str(m)) for v in vas))
    return syms


def get_default_pars(mount, abs_faces, e_number=True, T_number=True, cor_number=True):
    cor = [(-1, 0), (1, 0)] + [(0, 0)] * (mount - 2)
    es = [0.9 if i == 0 else 0 for i in range(mount)]
    Ts = [300 if i == 0 else 0 for i in range(mount)]
    for m in range(1, mount):
        es[m] = 0.5 if m in abs_faces else 0.1
        Ts[m] = 400 if m in abs_faces else 350
    Ts = float_int_all(Ts)
    if not e_number:
        es = symbol_all(mount, 'e')
    if not T_number:
        Ts = symbol_all(mount, 'T')
    if not cor_number:
        cor = symbol_all(mount, 'x', 'y')
    return cor, es, Ts


def RadCal_via_coors():
    # 参数设置
    mount = 3
    abs_faces = [1, 2]
    cor, es, Ts = get_default_pars(mount, abs_faces)
    ins = RadiationCalculation(face_mount=mount)

    # 参数化扫描
    # for v in np.arange(1, 2.8, 0.2):
    #     cor = [(-1, 0), (1, 0), (v, 1.6), (0.8, 2.4), (-0.8, 2.4), (-v, 1.6)]
    #
    #     # 结果
    #     angle_factor = ins.cal_AngleFactors(coors=cor)  # 角系数计算
    #     heat_flux = ins.cal_heat_flux(ems=es, coors=cor, Ths=Ts)  # 热通量计算
    #
    #     # # 保留小数点输出
    #     angle_factor = float('%.3f' % angle_factor[2][0])
    #     heat_flux = float('%.2f' % abs(heat_flux[0]))
    #     print('{0}\t{1}\t{2}'.format(v, angle_factor, heat_flux))
    #
    #     # # 原始输出
    #     # print('角系数为：\n', angle_factor, sep='')
    #     # print('热通量为：\n', heat_flux, sep='')

    # 代数求解
    cor = [(-1, 0), (1, 0), (0, sqrt(3))]
    angle_factor = ins.cal_AngleFactors(coors=cor)  # 角系数计算
    heat_flux = ins.cal_heat_flux(ems=es, coors=cor, Ths=Ts)  # 热通量计算
    print('角系数为：\n', angle_factor, sep='')
    print('热通量为：\n', heat_flux, sep='')


def test(**kv):
    print(kv)


if __name__ == '__main__':
    # test()
    RadCal_via_coors()
    pass
