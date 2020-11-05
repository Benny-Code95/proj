from math import sin, cos, tan, atan, pi


# 各形状（三角形、梯形、圆弧形）的腔体面积计算
class AreaShape:
    def __init__(self, ap=50.0):
        self.ap = ap  # 窗口宽度

    def area_tria(self, lb, ang):
        area = lb / cos(ang)
        print(area)
        return area

    def area_trap(self, lb, ang, hei):
        area = lb - hei * 2 / tan(ang) + hei * 2 / sin(ang)
        print(area)
        return area

    def area_arc(self, rc, ang):
        apr = rc * 2 * sin(pi - ang / 2)
        if apr < self.ap:
            print('error')
            return
        area = rc * ang
        print(area)
        return area

    def area_trapc(self, lb, ang1, h1, ang2, h2):
        lbc = lb + h1 * 2 / tan(ang1)
        area = lbc - h2 * 2 / tan(ang2) + h2 * 2 / sin(ang2)
        print(area)
        return area


if __name__ == '__main__':
    Area = AreaType(ap=50.0)

    Area.area_tria(lb=70.0, ang=60 * pi / 180)

    Area.area_trap(lb=90.0, ang=80 * pi / 180, hei=54)

    Area.area_arc(rc=32, ang=pi * 215 / 180)

    Area.area_trapc(lb=60, ang1=64 * pi / 180, h1=35, ang2=75 * pi / 180, h2=30)
