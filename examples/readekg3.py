#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import division, print_function, absolute_import

import numpy as np
import _edflib
from stacklineplot import stackplot, figure, plot
from pylab import *

# bdir =  r"c:/Users/clee/Documents/My Dropbox/data/swainAFIB_CA46803E_1-1+.edf"
bdir = r"/media/Windows7_OS/Users/clee/Documents/datasets/swaineeg/swainAFIB_CA46803E_1-1+.edf"
e = _edflib.Edfreader(bdir)


signal_labels = []
signal_nsamples = []


def fileinfo(edf):
    print("datarecords_in_file", edf.datarecords_in_file)
    print("signals_in_file:", edf.signals_in_file)
    for ii in range(edf.signals_in_file):
        signal_labels.append(edf.signal_label(ii))
        print("signal_label(%d)" % ii, edf.signal_label(ii), end="")
        print(edf.samples_in_file(ii), edf.samples_in_datarecord(ii), end="")
        signal_nsamples.append(edf.samples_in_file(ii))
        print(edf.samplefrequency(ii))


fileinfo(e)
L = e.samples_in_file(27)
x1s = 27
a2s = 23
X1 = np.zeros(L, dtype="float64")
A2 = np.zeros(L, dtype="float64")
t = arange(L, dtype="float64") / e.samplefrequency(x1s)

e.readsignal(x1s, 0, L, X1)
e.readsignal(a2s, 0, L, A2)
ekg = X1 - A2
