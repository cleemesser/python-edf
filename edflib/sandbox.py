# -*- coding: utf-8 -*-
# sandbox to try out different things
from __future__ import print_function, division, absolute_import

import numpy as np
import edflib
from pprint import pprint
import tables


class EdfFile(object):

    def __init__(self, fn):
        self.efile = _edflib.Edfreader(fn)
        efile = self.efile
        self.duration_sec = efile.file_duration_seconds
        nsignals = efile.signals_in_file
        self.nsignals = nsignals
        nsamples = np.array([efile.samples_in_file(chn) for chn in range(nsignals)])
        self.nsamples = nsamples
        sample_freqs = np.array([efile.samplefrequency(chn) for chn in range(nsignals)])
        self.signal_sample_freqs = sample_freqs
        signal_text_labels = [efile.signal_label(chn).strip() for chn in range(nsignals)]
        # note the original EDF file may need the extra spaces
        self.signal_text_labels = signal_text_labels


def edf2hdf5(fn):
    ef = _edflib.Edfreader(fn)
    # nf = tables.createFile(fn+'.h5')
    nsigs = ef.signals_in_file
    print("nsigs:", nsigs)

    nsamples = [ef.samples_in_file(ii) for ii in range(nsigs)]
    nsample0 = nsamples[0]
    nsamples = np.array(nsamples)

    if any(nsamples != nsample0):
        raise Exception("Assumption error: should be equal rate or shoudl all something else")

    print("nsample0", nsample0)

    bigarr = np.empty(nsample0, dtype='int32')
    big16arr = np.empty(nsample0, dtype='int16')

    ii = 5
    _edflib.read_int_samples(ef.handle, ii, N, bigarr)

    big16arr[:] = bigarr

    compfilter = tables.Filters(complevel=6, complib='zlib')

    h5 = tables.openFile('tstint16.h5', mode="w", title="test int16 file", filters=compfilter)

    atom16 = tables.Int16Atom()
    shape = big16arr.shape

    dataset = h5.createCArray(h5.root, 'int16 array', atom16, shape, filters=compfilter)
    dataset[:] = big16arr
    h5.flush()
    h5.close()


if __name__ == '__main__':
    import os
    f = EdfFile('/home/clee/datasets/huse/pa3213ip_1-1+.edf')

    print("channel\tlabel\tsample freqs")
    for chn in range(f.nsignals):
        print ("%d\t%s\t%d" % (chn, f.signal_text_labels[chn], f.signal_sample_freqs[chn]))

    fs0 = f.signal_sample_freqs[0]
    if all(f.signal_sample_freqs == fs0):
        fs = fs0
    else:
        print ("not all signals sampled at same rate!")

    L = f.nsamples[0]
    if not all(f.nsamples == L):
        print ("we have problem")

    data = np.zeros(L * f.nsignals, dtype=np.float64)
    for chn in range(f.nsignals):
        print("reading signal %d" % chn, end='')
        v = data[chn * L:(chn + 1) * L]
        f.efile.read_phys_signal(chn, 0, L, v)
        print ("signal max = %f" % v.max())

    data.shape = (f.nsignals, L)  # for continuity

    if not os.path.isfile('huse1.npy'):
        np.save('huse1.npy', data)

    fn = 'huse.h5'
    compfilter = tables.Filters(complevel=6, complib='zlib')
    h5 = tables.openFile(fn, mode="w", title="eeg file", filters=compfilter)
    print('=' * 30)
    print(h5)
    # bag = h5.createGroup(h5.root, "Datasets", "EEG signal data", filters=tables.Filters(complevel=1))
    # Array does not support compression
    #datasets = h5.createArray(h5.root, 'signals', data, 'float64 (number channels,number samples)=(%s,%s), sample rate = %d Hz' % (f.nsignals, L, fs), filters=compfilter)
    atom = tables.Float64Atom()
    shape = data.shape
    datasets = h5.createCArray(h5.root, 'signals', atom, shape, filters=compfilter)
    datasets[:, :] = data

    sf = h5.createArray(
        h5.root,
        'signal_sample_freqs',
        f.signal_sample_freqs,
        'sampling frequency for each signal')
    slab = h5.createArray(h5.root, 'signal_text_labels', f.signal_text_labels, 'signal text labels')

    h5.flush()
    h5.close()
