import pandas as pd


def write(data, path):
    new = pd.ExcelWriter(path)
    data.to_excel(new, sheet_name='sheet1', index=False)
    new.close()


def operation(old_path, new_path):
    sheets = pd.read_excel(old_path, sheet_name=['点检信息', '数据表'])
    djxx, sjb = sheets['点检信息'], sheets['数据表']

    column = list(djxx) + list(sjb)
    column.remove('rw_id')
    nd = pd.DataFrame(columns=column)

    for i in range(len(djxx['ID'])):
        a = sjb[sjb['rw_id'] == djxx.loc[i]['ID']]
        if not a.empty:
            row = list(a.loc[i].values)
            del row[0]
        else:
            row = [None] * 4
        nd.loc[i] = list(djxx.loc[i].values) + row

    write(nd, new_path)


if __name__ == '__main__':
    老路径 = ''
    新路径 = ''
    operation(老路径, 新路径)
