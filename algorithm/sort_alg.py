# 快速排序（找出中位值，大小分列右左，持续递归）
def quick_sort(sequence):
    def partition(arr, low, high):
        i = low - 1  # 最小元素索引
        pivot = arr[high]

        for j in range(low, high):
            # 当前元素小于或等于 pivot
            if arr[j] <= pivot:
                i = i + 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    def quick_sort_process(arr, low, high):
        if low < high:
            pi = partition(arr, low, high)
            quick_sort_process(arr, low, pi - 1)
            quick_sort_process(arr, pi + 1, high)

    quick_sort_process(sequence, 0, len(sequence) - 1)


def quick_sort_benny(sequence):
    # 递归调用
    def quick_sort_process(seq, low, high):
        if low >= high:
            return
        piv = partition(seq, low, high)
        quick_sort_process(seq, low, piv - 1)
        quick_sort_process(seq, piv + 1, high)

    # 定位中位值并分解
    def partition(sq, low, high):
        left, right = low + 1, high
        pivot = sq[low]

        while left <= right:
            while sq[left] <= pivot and left < high:
                left += 1
            while sq[right] > pivot and right > low:
                right -= 1
            if left >= right:
                break
            sq[left], sq[right] = sq[right], sq[left]
        sq[low], sq[right] = sq[right], sq[low]
        return right

    quick_sort_process(sequence, 0, len(sequence) - 1)


# 归并排序
def merge_sort(seq):
    if len(seq) <= 1:
        return seq

    # 分解
    middle = len(seq) // 2
    left = merge_sort(seq[:middle])
    right = merge_sort(seq[middle:])

    # 合并
    merged = []
    while left and right:
        if left[0] < right[0]:
            merged.append(left.pop(0))
        else:
            merged.append(right.pop(0))
    merged.extend(right if right else left)

    return merged


# 插入排序
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


if __name__ == '__main__':
    test_list = [1, 1]
    quick_sort(test_list)
    print(test_list)
