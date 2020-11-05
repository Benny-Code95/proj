import pandas as pd
# from collections import defaultdict


def new_round(_flt, _len=0):
    dcm_flt = str(_flt).split('.')
    if dcm_flt[1][_len] == '5':
        _flt = float(dcm_flt[0] + '.' + dcm_flt[1][:_len] + '6' + dcm_flt[1][_len+1:])
    return round(_flt, _len)


def lab():
    new_dt = pd.DataFrame(columns=['theta', 'Q', 'mt'], index=list(range(-90, 91)))
    new_dt['theta'] = list(range(-90, 91))
    new_dt['Q'], new_dt['mt'] = 0.0, 0

    dt = pd.read_excel(r'G:\研究生\计算及工作整理\comsol\\vac.xlsx')
    for i, r in dt.iterrows():
        print('this is {} row'.format(i))
        if r['X'] < 0:
            continue
        tht = int(new_round(r['theta']))
        if abs(tht) > 90:
            continue
        new_dt.loc[tht, 'Q'] += r['Q']
        new_dt.loc[tht, 'mt'] += 1
    for i in range(-90, 91):
        if new_dt.loc[i, 'mt'] == 0:
            continue
        new_dt.loc[i, 'Q'] = new_dt.loc[i, 'Q']/new_dt.loc[i, 'mt']
    print(new_dt)

    return


if __name__ == '__main__':
    new_round(2.5, 0)
    lab()
