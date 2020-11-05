# 数字表示在该点花费的费用，求出发点到右下角（4,4）最少费用
len_list = [
    [1, 8, 2, 4],
    [3, 9, 1, 6],
    [5, 8, 2, 3],
    [7, 8, 4, 8]
]

# 动态规划算法
min_paths = [[0]*4 for i in range(4)]
ends = (4, 4)

for i in range(ends[0]):
    for j in range(ends[1]):
        if i == 0 and j == 0:
            min_paths[0][0] = len_list[0][0]
        elif i == 0 and j != 0:
            min_paths[i][j] = sum(len_list[0][:j+1])
        elif j == 0:
            min_path = 0
            for i0 in range(i+1):
                min_path += len_list[i0][0]
            min_paths[i][j] = min_path
        else:
            min_paths[i][j] = min(len_list[i][j]+min_paths[i-1][j], len_list[i][j]+min_paths[i][j-1])

print(min_paths)
