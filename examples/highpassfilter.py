# -*- coding: utf-8 -*
from __future__ import division, print_function, absolute_import

import scipy.signal as signal


def highpass_firwin(n, cutoff=0.1, window="hanning"):
    """
    highpass_firwin(n, cutoff = 0.1, window='hanning')
    create a highpass finite impulse response filter (FIR) with normalized
    cutoff frequency of @cutoff  (i.e., as a percentage of nyquist frequency)

    calculated using spectral inversion method on a lowpass filter
    """
    a = signal.firwin(n, cutoff=0.3, window="hanning")
    a = -a
    a[n / 2] = a[n / 2] + 1
    return a
