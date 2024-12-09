# -*- coding: utf-8 -*
from __future__ import division, print_function, absolute_import


def refractfilt(x, fs=200.0):
    """remove indices that occur within 200ms of the last index"""
    lasti = x[0]
    ok = []
    delta = int(0.2 * fs)
    if lasti:
        ok.append(lasti)
    for y in x[1:]:
        # print(y)
        if y - lasti > delta:
            ok.append(y)
            lasti = y

    return ok
