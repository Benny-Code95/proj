# 获取线性插值（若x=x_start=x_end，取y_start）
def get_line_value(x, x_start, x_end, y_start, y_end):
    if x <= x_start:
        return y_start
    if x >= x_end:
        return y_end
    return (x - x_start) / (x_end - x_start) * (y_end - y_start) + y_start


# 二分查找有序列表中元素位置
# 0：小于列表第二个元素；i(1~n-2)：[list[i], list[i+1])；n-1：大于等于列表所有元素
def get_pos_via_bin_search(arr, x, left=None, right=None):
    if len(arr) == 1:
        return 0
    if left is None and right is None:
        left, right = 0, len(arr) - 1
    if x <= arr[left]:
        return left
    if x >= arr[right]:
        return right

    mid = (left + right) // 2
    if mid == left:
        return left
    if x == arr[mid]:
        return mid
    if x > arr[mid]:
        return get_pos_via_bin_search(arr, x, mid, right)
    else:
        return get_pos_via_bin_search(arr, x, left, mid)


# 根据元素一一对应的双列表（变量列表有序）求出对应的线性插值和元素对应位置
# 0：列表左侧；i(1-n)：列表i-i+1（左闭右开）；n+1：列表右侧
def get_line_value_via_lists(ind_var, var_list, value_list, pos=0, get_pos=False):
    if len(var_list) != len(value_list):
        print('自变量和因变量列表长度不一致！')
        return
    ind_var, var_tuple, value_tuple = float(ind_var), tuple(var_list), tuple(value_list)
    if len(var_list) == 1:
        return value_tuple[0]
    while ind_var > var_tuple[pos + 1] and pos < len(var_tuple) - 2:
        pos += 1
    value = get_line_value(ind_var, var_tuple[pos], var_tuple[pos + 1], value_tuple[pos], value_tuple[pos + 1])
    if get_pos:
        return value, pos
    else:
        return value


def tst_cal():
    eff = 0.5336
    x1, x2 = -0.0846, 0.602
    y1, y2 = 0.0, 1.0
    print('{:.4}'.format(get_line_value(eff, x1, x2, y1, y2)))


if __name__ == '__main__':
    tst_cal()
    pass
    # a = [1, 2]
    # print(get_pos_via_bin_search(a, 1.2))
