#!/usr/bin/env python
"""
test of the underlying cython module _edflib.so
note, everything in this module needs to supply bytes to the _edflib calls
"""

from __future__ import print_function, division
import os
import os.path

# , range, zip, super, open, input, int, pow, object
from builtins import str, bytes

import numpy as np


import edflib._edflib as _edflib

TESTDIR = os.path.dirname(__file__)
FILE_NAME = "test_generator.edf"
FILE_NAME = os.path.join(TESTDIR, FILE_NAME)
TEXT_ENCODING = "UTF-8"


def fileinfo(edf):
    signal_labels = []
    signal_nsamples = []

    print("datarecords_in_file", edf.datarecords_in_file)
    print("signals_in_file:", edf.signals_in_file)
    for ii in range(edf.signals_in_file):
        signal_labels.append(edf.signal_label_b(ii))
        print(
            "signal_label(%d)" % ii,
            edf.signal_label_b(ii),
        )
        print(
            edf.samples_in_file(ii),
            edf.samples_in_datarecord(ii),
        )
        signal_nsamples.append(edf.samples_in_file(ii))
        print(edf.samplefrequency(ii))

    return signal_labels, signal_nsamples


def test_edflibpyx():
    bfile_name = FILE_NAME.encode(TEXT_ENCODING)
    with _edflib.CyEdfReader(bfile_name, TEXT_ENCODING) as efc:
        signal_labels, signal_nsamples = fileinfo(efc)
        # convert byte strings to regular string
        signal_labels = [label.decode(TEXT_ENCODING) for label in signal_labels]
        sig1 = np.zeros(2000, dtype="float64")
        efc.read_phys_signal(1, 0, 2000, sig1)

        nsigs = efc.signals_in_file
        sigbufs = np.zeros((nsigs, 2000), dtype="float64")
        # read the first 10 sec
        readpt = 0
        for ii in range(nsigs):
            efc.read_phys_signal(ii, readpt, 2000, sigbufs[ii])

        if __name__ == "__main__":
            import matplotlib.pyplot as plt
            from stacklineplot import stackplot, figure

            fig1 = plt.figure(1, figsize=(8, 6))
            stackplot(sigbufs, seconds=10.0, start_time=0.0, ylabels=signal_labels)
            fig1.savefig("test_edflibpyx_fig1.png", bbox_inches="tight")

        # now read the next 10 seconds
        readpt = 2000
        for ii in range(nsigs):
            efc.read_phys_signal(ii, readpt, 2000, sigbufs[ii])

        if __name__ == "__main__":
            fig2 = plt.figure(2, figsize=(8, 6))
            stackplot(sigbufs, seconds=10.0, start_time=10.0, ylabels=signal_labels)
            fig2.savefig("test_edflibpyx_fig2.png", bbox_inches="tight")

        # now read the overlap 5-15 seconds
        readpt = 1000
        for ii in range(nsigs):
            efc.read_phys_signal(ii, readpt, 2000, sigbufs[ii])

        Nibuf = 1000
        ibuf = np.zeros(Nibuf, dtype="int32")

        # try pickout signal 5
        _edflib.rewind(efc.handle, 5)
        _edflib.read_int_samples(efc.handle, 5, Nibuf, ibuf)

        # figure()
        # stackplot(sigbufs,seconds=10.0, start_time = 5.0, ylabels=signal_labels)

        # this doesn't work
        # offset, nr = efc.tryoffset()
        # dbuffer = efc.make_buffer()
        # efc.load_phys_datarecord(dbuffer, 0)

        # efc.close()

        # f = _edflib.Edfreader("examples/PA32135H_1-1+.edf")
        # fileinfo(f)

        # efc._close() # this may be a no-no

        # del e # this should trigger a __dealloc__ right?


if __name__ == "__main__":
    test_edflibpyx()
