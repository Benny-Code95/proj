from simulate.flat_rad_verify import CalFlatRadiation, NotConvergent


class ArcRadiation(CalFlatRadiation):

    pass


def tst():
    ins = ArcRadiation()
    print(ins)
    pass


if __name__ == '__main__':
    tst()
