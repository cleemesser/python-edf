from __future__ import division, print_function

import sys
import numpy as np
import pylab

import edflib.edfreader as edfreader

ef = edfreader.EdfReader("../tests/test_generator.edf")

signal_labels = []
signal_nsamples = []


def fileinfo(edf):
    print("datarecords_in_file", edf.datarecords_in_file)
    print("signals_in_file:", edf.signals_in_file)
    nsigs = edf.signals_in_file
    for ii in range(nsigs):
        signal_labels.append(edf.signal_label(ii))
        print("signal_label(%d)" % ii, edf.signal_label(ii), end=" ")
        print(edf.samples_in_file(ii), edf.samples_in_datarecord(ii), end=" ")
        signal_nsamples.append(edf.samples_in_file(ii))
        print(edf.samplefrequency(ii))


fileinfo(ef)
nsamples = signal_nsamples[0]
nsigs = ef.signals_in_file
fs = ef.samplefrequency(0)  # again know that this is uniform
# check this is rectangular
for ii in range(ef.signals_in_file):
    assert nsamples == signal_nsamples[ii]

allsig = np.zeros((ef.signals_in_file, nsamples), dtype="float64")


def read_all():
    readpt = 0
    for ii in range(nsigs):
        ef.read_phys_signal(ii, readpt, nsamples, allsig[ii])


def plot_epoch(start=0.0, duration=10.0):
    "plot all the signals one above another in a 10 second epoch"
    from stacklineplot import stackplot

    x0 = start * fs
    x1 = (start + duration) * fs
    stackplot(
        allsig[:, x0:x1], seconds=duration, start_time=start, ylabels=signal_labels
    )


if False:
    # try pickout signal 5
    _edflib.rewind(ef.handle, 5)
    _edflib.read_int_samples(ef.handle, 5, Nibuf, ibuf)

    # figure()
    # stackplot(sigbufs,seconds=10.0, start_time = 5.0, ylabels=signal_labels)

    # this doesn't work
    # offset, nr = ef.tryoffset()
    # dbuffer = ef.make_buffer()
    # ef.load_datarecord(dbuffer, 0)

    # ef.close()

    # f = _edflib.EdfReader("examples/PA32135H_1-1+.edf")
    # fileinfo(f)
