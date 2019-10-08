#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example of looking at the header information for the patient and the signals in an EDF file
note it requires some additional packages such as dateutil

$ python edf_header_dump.py ../tests/test_generator.edf
"""
from __future__ import print_function, division, absolute_import  # py2.6  with_statement

import sys
from pprint import pprint
import datetime

import edflib
import dateutil.parser

import numpy as np
import os.path

# import future # not sure if I need this


def dump_edf_info(filename):
    """
    test out what all the information looks like in the header for a file 

    """

    with edflib.EdfReader(filename) as ef:
        # all the data point related stuff
        nsigs = ef.signals_in_file

        fs0 = ef.samplefrequency(0)  # again know/assume that this is uniform sampling across signals
        nsamples0 = ef.samples_in_file(0)
        print('nsigs=%s, fs0=%s, nsamples0=%s\n' % (nsigs, fs0, nsamples0))

        num_samples_per_signal = ef.get_samples_per_signal()
        print("num_samples_per_signal::\n", repr(num_samples_per_signal), '\n')

        file_duration_seconds = ef.file_duration_seconds
        print("file_duration_seconds", repr(file_duration_seconds))
        signal_frequency_array = ef.get_signal_freqs()
        print("signal_frequency_array::\n", repr(signal_frequency_array))

        annotations = ef.read_annotations_b()
        print("annotations::\n", repr(annotations))

        signal_text_labels = ef.get_signal_text_labels()
        print("signal_text_labels::\n", repr(signal_text_labels))

        # ef.recording_additional

        print()
        signal_digital_mins = [ef.digital_min(ch) for ch in range(nsigs)]
        signal_digital_total_min = min(signal_digital_mins)
        print("digital mins:", repr(signal_digital_mins))
        print("digital total min:", repr(signal_digital_total_min))

        signal_digital_maxs = [ef.digital_max(ch) for ch in range(nsigs)]
        signal_digital_total_max = max(signal_digital_maxs)
        print("digital maxs:", repr(signal_digital_maxs))
        print("digital total max:", repr(signal_digital_total_max))

        signal_physical_dims = [ef.physical_dimension(ch) for ch in range(nsigs)]
        print('\nsignal_physical_dims::')
        pprint(signal_physical_dims)

        signal_physical_maxs = [ef.physical_max(ch) for ch in range(nsigs)]
        print('\nsignal_physical_maxs::')
        pprint(signal_physical_maxs)

        signal_physical_mins = [ef.physical_max(ch) for ch in range(nsigs)]
        print('\nsignal_physical_mins::')
        pprint(signal_physical_mins)

        print('gender:', repr(ef.gender_b))
        print('admincode:', repr(ef.admincode))
        print('birthdate:', repr(ef.birthdate_b))  # this is a string
        if ef.birthdate_b:
            try:
                birthdate = dateutil.parser.parse(ef.birthdate_b)
            except ValueError:
                birthdate = None
        else:
            birthdate = None

        print('birthdate as datetime:', repr(birthdate))
        print('equipment:', repr(ef.equipment))
        print('patient:', repr(ef.patient))
        print('patientname:', repr(ef.patientname))
        print('patientcode:', repr(ef.patientcode_b))
        print('patient_additional:', repr(ef.patient_additional))
        print('recording_additional:', repr(ef.recording_additional))

        # or use arrow
        start_date_time = datetime.datetime(ef.startdate_year, ef.startdate_month, ef.startdate_day, ef.starttime_hour,
                                            ef.starttime_minute, ef.starttime_second)  # tz naive
        print('start_date_time:', start_date_time)

        print()
        # this don't seem to be used much so I will put at end
        signal_prefilters = [ef.prefilter(ch) for ch in range(nsigs)]
        print('signal_prefilters::\n')
        pprint(signal_prefilters)
        signal_transducer = [ef.transducer(ch) for ch in range(nsigs)]
        print('signal_transducer::\n')
        pprint(signal_transducer)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help='edf file name')
    args = parser.parse_args()
    print(args.filename)
    if args.filename:
        dump_edf_info(args.filename)
