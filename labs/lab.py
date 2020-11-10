import re


def parseMaterialTXT(txtPath):
    with open(txtPath, 'r', encoding='utf8') as f:
        data = f.read()
    print(data)
    cmp = re.compile(
        'W=\".(\d+\.?\d+)\" n=\".(\d*\.\d*)\" k=\".(\d*\.?\d*(E-\d+)?)')
    nks = re.findall(cmp, data)
    for nk in nks:
        print('{0}\t{1}\t{2}'.format(float(nk[0]), float(nk[1]), float(nk[2])))


if __name__ == '__main__':
    path = 'F:\\研究生\\计算及工作整理\\截止膜\\TFC设计\\sio2.txt'
    parseMaterialTXT(path)
    pass
