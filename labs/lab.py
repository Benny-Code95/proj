import time
import os


def tst():
    root_path = 1
    print(root_path)
    for r, d, f in os.walk('G:\\'):
        print(r, d, f)

    pass


def tst1():
    num_max = 3 * 10 ** 3
    count = len(
        [num for num in range(num_max + 1) if str(num) == str(num)[::-1]])
    print(count)
    # print('12345'[:-len('1234'):-1])


if __name__ == '__main__':
    start = time.time()
    for i in range(1):
        tst()
    end = time.time()
    print(end - start)

    pass
