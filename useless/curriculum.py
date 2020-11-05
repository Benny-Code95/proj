import pandas as pd


def curriculum_week(path):
    full_currs = pd.read_excel(path)

    new_column = ['课次', '周一', '周二', '周三', '周四', '周五']
    nc = pd.DataFrame(columns=new_column)
    kc = []
    for r in range(0, 6):
        kc.append(str(r * 2 + 1) + '-' + str(r * 2 + 2))
    nc['课次'] = kc

    for i in range(0, 17):
        week = i+1
        curr_name = '第{0}周课表'.format(week)
        new_path = 'F:\研究生\课程相关\\2018-2019下学期课表\每周课表\\' + curr_name + '.xlsx'
        ncw = nc.copy()

        for index, w in enumerate(full_currs['周次']):
            if type(w) == str and w != 'nan':
                ws = w.split('-')
                if (week >= int(ws[0])) and (week <= int(ws[1])+1):
                    data = full_currs.iloc[index]
                    wn = '周' + data['星期'] if type(data['星期']) == str else '周' + full_currs['星期'].iloc[index - 1]
                    t = data['时间'] if type(data['时间']) == str else full_currs['时间'].iloc[index - 1]
                    t_index = int((int(t[0]) - 1)/2)
                    ncw[wn].iloc[t_index] = data['课程名称'] + '；' + data['周次'] + '周；' + data['地点']

        new_curr = pd.ExcelWriter(new_path)
        ncw.to_excel(new_curr, index=False)
        new_curr.close()
        print('第{0}周课表写完'.format(week))


if __name__ == '__main__':
    curriculum_week('F:\研究生\课程相关\\2018-2019下学期课表\\2018-2019下学期课表.xlsx')
