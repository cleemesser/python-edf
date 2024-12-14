#!/usr/bin/env python
"""
test of the underlying cython module _edflib.so
"""

from __future__ import print_function, division

import os, os.path
import numpy as np
import pylab

import edflib._edflib as _edflib

TESTDIR = os.path.dirname(__file__)


e = _edflib.CyEdfReader("test_generator.edf")

signal_labels = []
signal_nsamples = []


def fileinfo(edf):
    print("datarecords_in_file", edf.datarecords_in_file)
    print("signals_in_file:", edf.signals_in_file)
    for ii in range(edf.signals_in_file):
        signal_labels.append(edf.signal_label(ii))
        print("signal_label(%d)" % ii, edf.signal_label(ii), end=" ")
        print(edf.samples_in_file(ii), edf.samples_in_datarecord(ii), end=" ")
        signal_nsamples.append(edf.samples_in_file(ii))
        print(edf.samplefrequency(ii))


fileinfo(e)
sig1 = np.zeros(2000, dtype="float64")
e.read_phys_signal(1, 0, 2000, sig1)

nsigs = e.signals_in_file
sigbufs = np.zeros((nsigs, 2000), dtype="float64")
# read the first 10 sec
readpt = 0
for ii in range(nsigs):
    e.read_phys_signal(ii, readpt, 2000, sigbufs[ii])


from stacklineplot import stackplot, figure

stackplot(sigbufs, seconds=10.0, start_time=0.0, ylabels=signal_labels)


# now read the next 10 seconds
readpt = 2000
for ii in range(nsigs):
    e.read_phys_signal(ii, readpt, 2000, sigbufs[ii])
figure()
stackplot(sigbufs, seconds=10.0, start_time=10.0, ylabels=signal_labels)

# now read the overlap 5-15 seconds
readpt = 1000
for ii in range(nsigs):
    e.read_phys_signal(ii, readpt, 2000, sigbufs[ii])

Nibuf = 1000
ibuf = np.zeros(Nibuf, dtype="int32")

# try pickout signal 5
_edflib.rewind(e.handle, 5)
_edflib.read_int_samples(e.handle, 5, Nibuf, ibuf)

# figure()
# stackplot(sigbufs,seconds=10.0, start_time = 5.0, ylabels=signal_labels)

# this doesn't work
# offset, nr = e.tryoffset()
# dbuffer = e.make_buffer()
# e.load_datarecord(dbuffer, 0)


# e.close()


# f = _edflib.Edfreader("examples/PA32135H_1-1+.edf")
# fileinfo(f)
