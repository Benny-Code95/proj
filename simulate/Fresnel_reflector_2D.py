import pandas as pd
import math
import os


class Reflector:

    def __init__(self, mount=2, focus=1.0, width=0.3, gap=0.1, x_center=0, y_center=0, x_inc=0, y_inc=-1):
        self.mt = mount
        self.fs = focus
        self.wth = width
        self.gap = gap
        self.xc = x_center
        self.yc = y_center
        self.xin = x_inc
        self.yin = y_inc
        self.x_f = self.xc
        self.y_f = self.yc + self.fs

    def get_coordinate_per(self, xs, ys, xf, yf, x_inc=0.0, y_inc=-1.0, w=1.0):
        x_ref, y_ref = xf - xs, yf - ys
        x_ref, y_ref = self.get_unit_vetor(x_ref, y_ref)
        x_inc, y_inc = self.get_unit_vetor(x_inc, y_inc)
        x_normal, y_normal = x_ref - x_inc, y_ref - y_inc
        angle_deflection = math.atan(x_normal / y_normal)
        x_left, y_left = xs - w * math.cos(angle_deflection) / 2, ys + w * math.sin(angle_deflection) / 2
        x_rihgt, y_right = xs + w * math.cos(angle_deflection) / 2, ys - w * math.sin(angle_deflection) / 2
        return x_left, y_left, x_rihgt, y_right

    @staticmethod
    def get_unit_vetor(x0, y0):
        norm = math.sqrt(x0 * x0 + y0 * y0)
        return x0 / norm, y0 / norm

    @staticmethod
    def get_coodinate_str_tuple(x1, y1, x2, y2):
        s1 = str(x1) + ',' + str(y1)
        s2 = str(x2) + ',' + str(y2)
        return s1, s2

    def get_cad_coordinate(self):
        m_half = self.mt / 2
        if m_half % 1 != 0:
            print("镜面数量不为偶数，请重新输入！")
            raise Exception
        gap_c = self.wth + self.gap
        x_lc, y_lc = -gap_c / 2, self.yc
        x_rc, y_rc = gap_c / 2, self.yc
        coors = []
        x_f, y_f = self.x_f, self.y_f
        for i in range(int(m_half)):
            x_ll, y_ll, x_lr, y_lr = self.get_coordinate_per(x_lc, y_lc, x_f, y_f, x_inc=self.xin, y_inc=self.yin,
                                                             w=self.wth)
            coors.append(self.get_coodinate_str_tuple(x_ll, y_ll, x_lr, y_lr))
            x_rl, y_rl, x_rr, y_rr = self.get_coordinate_per(x_rc, y_rc, x_f, y_f, x_inc=self.xin, y_inc=self.yin,
                                                             w=self.wth)
            coors.append(self.get_coodinate_str_tuple(x_rl, y_rl, x_rr, y_rr))
            x_lc -= gap_c
            x_rc += gap_c
        return coors

    def get_x_int(self, length=1.0):
        # 计算接收辐照的面积（仅光线垂直地面入射）
        data = self.get_cad_coordinate()
        x_len = 0
        for i in data:
            x1 = float(i[0].split(',')[0])
            x2 = float(i[1].split(',')[0])
            x_len += x2 - x1
        sc = x_len * length
        print('计算出的聚光面积为：{0}'.format(sc))

    def cal_concentration_ratio(self):
        # 仅计算光线垂直入射至地面时的聚光比
        data = self.get_cad_coordinate()
        eta = 0.00465
        Cn = 0
        for i in data:
            x1 = float(i[0].split(',')[0])
            x2 = float(i[1].split(',')[0])
            y1 = float(i[0].split(',')[1])
            y2 = float(i[1].split(',')[1])
            ang = math.atan(abs((y1 - y2) / (x1 - x2)))
            dd = self.wth * math.cos(ang) / math.cos(2 * ang)
            ii = (self.fs + abs(y1)) * math.sin(eta) / (math.cos(ang * 2) * math.cos(2 * ang + eta))
            uu = (self.fs - abs(y1)) * math.sin(eta) / (math.cos(ang * 2) * math.cos(2 * ang - eta))
            Cn += self.wth * math.cos(ang) / (dd + ii + uu)
        print('计算出的聚光比为：{0}'.format(Cn))
        return Cn

    def get_excel_data(self):
        coordinate_tuples = self.get_cad_coordinate()
        ds = []
        for i in coordinate_tuples:
            ds.append('L')
            ds.append(i[0])
            ds.append(i[1])
            ds.append('')
        data = pd.DataFrame({'坐标': ds})
        print(data)
        return data

    def write_in_excel(self, path, file_name):

        for root, dirs, files in os.walk(path):
            if file_name in files:
                print('该文件已存在，若覆盖，请输入0；若更改请输入新文件名（默认文件为xlsx文件，无需输入‘.xlsx’）')
                print('input:')
                file_root = input()
                file_name = file_name if file_root == '0' else file_root + '.xlsx'
                break

        new_path = path + '\\' + file_name
        new = pd.ExcelWriter(new_path)
        data = self.get_excel_data()
        data.to_excel(new, sheet_name='sheet1', index=False)
        new.close()
        print('文件({0})写入完成！'.format(file_name))


if __name__ == '__main__':
    # 默认尺寸为m,如若尺寸有变，请根据需要调整
    mounts = 14  # 镜面数量
    focus_length = 1300  # 焦距
    mirror_width = 100  # 镜面宽度
    gap_reflectors = 30  # 镜面间距
    root_path = 'F:\work\CAD\\xlsx'
    f_name = 'art6.xlsx'

    cls = Reflector(mount=mounts, focus=focus_length, width=mirror_width, gap=gap_reflectors)

    # 写入数据
    cls.write_in_excel(root_path, f_name)

    # 计算接收辐照的面积（仅光线垂直地面入射）
    cls.get_x_int(length=2170)

    # 计算聚光比（仅光线垂直地面入射）
    cls.cal_concentration_ratio()
