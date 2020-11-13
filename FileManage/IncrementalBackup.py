import os
import shutil


def increment():
    test_path = 'F:\\研究生\\每周汇报\\2020-11-12-陈立智.pptx'
    date = os.path.getmtime(test_path)
    print(date, type(date))


def copyAndRename(src_dir, dst_dir, f_name):
    source = src_dir + f_name
    destination = dst_dir + f_name
    shutil.copy(source, destination)


if __name__ == '__main__':
    increment()
