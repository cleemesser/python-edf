#!/usr/bin/env python
# -*- coding: utf-8 -*
""" """

from __future__ import division, print_function, absolute_import
import os
import os.path
from pprint import pprint

import numpy as np
from numpy import pi

# import pylab

import edflib.edfreader as edfreader
import edflib.edfwriter as edfwriter

TESTDIR = os.path.dirname(__file__)
OUT_FILE_NAME = "writer_test.edf"
OUT_FILE_NAME = os.path.join(TESTDIR, OUT_FILE_NAME)

# 200:210
compare = np.array(
    [
        -99.96185245,
        -98.954757,
        -97.9781796,
        -96.97108415,
        -95.96398871,
        -94.95689326,
        -93.98031586,
        -92.97322042,
        -91.96612497,
        -90.95902953,
    ]
)


def test_write_sine_file():
    # define two sine waves

    ch0 = {
        "label": "EEG sine 10",
        "dimension": "uV",
        "sample_rate": 200,
        "physical_max": 500.0,
        "physical_min": -500.0,
        "digital_max": 16000,
        "digital_min": -16000,
    }

    # 1/scale -> inverse bitvalues
    scale = (ch0["digital_max"] - ch0["digital_min"]) / (
        ch0["physical_max"] - ch0["physical_min"]
    )
    foffset = ch0["physical_max"] * scale - ch0["digital_max"]
    # dig = phys*scale - foffset = phys/gain - foffset
    label0 = ch0["label"]

    print(ch0["digital_max"])

    print(repr(ch0))

    ef = edfwriter.EdfWriter(file_name=OUT_FILE_NAME, channel_info=[ch0])
    # note this seems to consume the channel_info dictionaries

    fs = 200
    T = 1
    t = np.arange(T * fs, dtype="float64") / fs  # 5 seconds
    s10 = 500.0 * np.sin(2 * pi * 10.0 * t)  # 10 hz sine +/- 500.0 uV
    print("scale:", scale, "foffset:", foffset)
    s10_up = scale * s10 - foffset  # integer conversion
    dig_s10 = s10_up.astype("int16", casting="unsafe")
    print("\ndig_s10::")
    print(dig_s10)
    # do it the slow way for ch0 to test this function
    for ii in dig_s10:
        print(ii)
        ef.write_sample(label0, ii)
    # pprint(ef.channels)
    # ef.write_sample(label0, 16)
    ef.close()


if __name__ == "__main__":
    # test_write_sine_file()
    ch0 = {
        "label": "EEG sine 10",
        "dimension": "uV",
        "sample_rate": 200,
        "physical_max": 500.0,
        "physical_min": -500.0,
        "digital_max": 16000,
        "digital_min": -16000,
    }

    # 1/scale -> inverse bitvalues
    scale = (ch0["digital_max"] - ch0["digital_min"]) / (
        ch0["physical_max"] - ch0["physical_min"]
    )
    foffset = ch0["physical_max"] * scale - ch0["digital_max"]
    # dig = phys*scale - foffset = phys/gain - foffset
    label0 = ch0["label"]
    ef = edfwriter.EdfWriter(file_name=OUT_FILE_NAME, channel_info=[ch0])
