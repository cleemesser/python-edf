#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import division, print_function, absolute_import

import numpy as np
import _edflib
from stacklineplot import stackplot, figure, plot
from pylab import *
e = _edflib.Edfreader("shortAFIB_CA46803D_1-1+_1-2+.edf")


signal_labels = []
signal_nsamples = []
def fileinfo(edf):
    print ("datarecords_in_file", edf.datarecords_in_file)
    print("signals_in_file:", edf.signals_in_file)

    for ii in range(edf.signals_in_file):
        signal_labels.append(edf.signal_label(ii))
        print("signal_label(%d)" % ii, edf.signal_label(ii),end='')
        print( edf.samples_in_file(ii), edf.samples_in_datarecord(ii), end='')
        signal_nsamples.append(edf.samples_in_file(ii))
        print( edf.samplefrequency(ii))


def readsignals(edf, start_time, end_time, buf=None):
    """times in seconds"""
    # assume same sampling rate for all channels for a moment and use signal#0
    assert end_time <= edf.file_duration
    
    readpt = int(edf.samplefrequency(0)*(start_time))
    print( "readpt:", readpt)
    readlen = int( edf.samplefrequency(0)*(end_time-start_time))
    assert readlen <= MAXSIGLEN
    print( "readlen:", readlen)
    for ii in range(nsigs):
        e.readsignal(ii, readpt, readlen, sigbufs[ii])
    return readpt, readlen


if __name__=='__main__':
    fileinfo(e)
    sig1 = np.zeros(2000.0, dtype='float64')
    e.readsignal(1,0, 2000, sig1)

    nsigs = e.signals_in_file
    MAXSIGLEN = 20000
    sigbufs = np.zeros((nsigs,MAXSIGLEN), dtype='float64')
    # read the first 10 sec
    readpt = 0
    for ii in range(nsigs):
        e.readsignal(ii, readpt, 2000, sigbufs[ii])

    # stackplot(sigbufs,seconds=10.0, start_time=0.0, ylabels=signal_labels)

    L = 8.0
    s,l = readsignals(e, 0, L)
    stackplot(sigbufs[:, s:s+l], seconds = L, ylabels=signal_labels)

    # findx2 = [ (ii, signal_labels[ii]) for ii in range(len(signal_labels))] 
    # X2 is signal 27
    # A2 is signal 23

    ekg = sigbufs[27][0:l] - sigbufs[23][0:l]

    from scipy.signal import kaiserord, lfilter, firwin, freqz
    sample_rate = e.samplefrequency(0)
    nyq_rate = sample_rate/2.0
    width = 5.0/nyq_rate
    ripple_db = 60.0
    N, beta = kaiserord(ripple_db, width)
    cutoff_hz = 10.0
    taps = firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
    filtered_ekg = lfilter(taps, 1.0, ekg)
    figure()
    plot(taps, 'bo-', linewidth=2)
    title('Filter Coefficients (%d taps)' % N)
    grid(True)

    phase_delay = 0.5 * (N-1) / sample_rate
    t = arange(len(ekg))/sample_rate
    figure()
    plot(t,ekg)
    filtered_ekg[0:N-1] = 0 # the first N-1 samples are corrupted
    plot(t-phase_delay, filtered_ekg)


