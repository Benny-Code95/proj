from sympy import *
import numpy as np


def solve_eqs():
    par = [[6.7294, -5.7294], [-0.11, 1.11]]
    mtr = np.array(par)
    arr = np.array([1451.52, 459.27])
    vs = [Symbol('J' + str(i)) for i in range(2)]
    eqs_left = np.dot(mtr, vs)
    return solve(eqs_left - arr, vs)


if __name__ == '__main__':
    print(solve_eqs())
