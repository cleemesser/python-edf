# -*- coding: utf-8 -*
from __future__ import division, print_function, absolute_import

import _edflib
from pylab import *
import scipy.signal as signal
import highpassfilter as hpf
import os

if os.path.isfile("ekg.npy"):
    ekg = np.load("ekg.npy")
    L = len(ekg)
    fs = 200
else:
    e = _edflib.Edfreader(r"/home/clee/Dropbox/data/swainAFIB_CA46803E_1-1+.edf")
    L = e.samples_in_file(27)
    fs = e.samplefrequency(27)

    X1 = np.zeros(float(L))
    e.readsignal(27, 0, L, X1)
    A2 = np.zeros(float(L))
    e.readsignal(23, 0, L, A2)
    e.close()
    ekg = A2 - X1
    # may as well clean these up
    del X1, A2

# psd(ekg[:2000])

# make a 5Hz filter
# cf5 = 5.0/(fs/2.0)
# filt5hz = hpf.highpass_firwin(200,cutoff=cf5)
# don't like how this looks


def plott(s):
    plot(arange(len(s)) / fs, s)


def makegaussian(freq):
    T = 1 / freq * fs
    g = linspace(-2.0, 2.0, int(2 * T))
    g = exp(-(g**2) / 2)
    N = sum(g)
    g = g / N
    return g


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


gf = makegaussian(1.0)
cekg = signal.convolve(ekg, gf, "valid")
ekgtr = ekg[200:]  # because we lose first 200 pts from filtering
cekgtr = cekg[: len(ekgtr)]
fekgtr = ekgtr[0 : len(cekgtr)] - cekgtr[:]
