import pandas as pd


def get_rad_data(text, xls):
    with open(text) as f:
        txt = f.read()
    di = dict(eval(txt))
    data = di['DS']
    res = {'Station_Id_C': '武汉', 'V14311': '总辐照度', 'V14320': '总辐照曝辐量'}
    for d in data:
        for r in res:
            d.update({res[r]: d.pop(r)})
    ddi = dict()
    for d in data:
        for k in d:
            if k not in ddi:
                ddi.update({k: [d[k]]})
            else:
                ddi[k].append(d[k])
    nd = pd.DataFrame(ddi)
    write(nd, xls)


def write(data, path):
    new = pd.ExcelWriter(path)
    data.to_excel(new, sheet_name='sheet1', index=False)
    new.close()
    print('finish!')


if __name__ == '__main__':
    txt_path = 'D:\\rad_data.txt'
    xlsx_path = 'D:\\rad_data.xlsx'
    try:
        get_rad_data(txt_path, xlsx_path)
    except FileNotFoundError or ImportError:
        print('aaaa')
