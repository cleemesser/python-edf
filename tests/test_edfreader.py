#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
test of the underlying cython module _edflib.so
"""

from __future__ import division, print_function, absolute_import
import os
import os.path
import datetime
from pprint import pprint

import numpy as np
from past.builtins import long

import edflib.edfreader as edfreader

TESTDIR = os.path.dirname(__file__)
FILE_NAME = "test_generator.edf"
FILE_NAME = os.path.join(TESTDIR, FILE_NAME)
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

# FILE_NAME2 = "/Users/clee/code/eegml/nk_database_proj/private/lpch_edfs/XA2731AX_1-1+.edf"


def test_make_buffer() -> None:
    assert os.path.isfile(FILE_NAME)
    with edfreader.EdfReader(FILE_NAME) as ef:
        drecbuf = ef.make_phys_datarecord_buffer()
        print("file duration (sec): ", ef.file_duration_seconds)
        print("file duration (100 ns): ", ef.file_duration_100ns)
        # convert seconds to units of 100ns and test for a difference
        assert (
            abs(ef.file_duration_seconds * 10**9 / 100.0 - ef.file_duration_100ns)
            < 0.000001
        )
        assert ef.file_duration_seconds == 600
        print("data record duration: ", ef.datarecord_duration_seconds)
        ef.load_phys_datarecord(drecbuf, n=0)
        dif = np.abs(drecbuf[200:210] - compare)
        print("difference:", dif)
        assert all(dif < 0.00001)

    return None


def test_raw_properties(fn: str = FILE_NAME) -> None:
    assert os.path.isfile(fn)
    with edfreader.EdfReader(fn) as ef:
        true_birthdate = b"30 jun 1969"
        true_name = b"X"
        true_additional_info = b""
        true_startdate = "04 apr 2011"
        true_device = b"test generator"
        true_starttime = "4 apr 2011 12:57:02"
        true_duration = "0:10:00"
        true_labels_b = [
            b"squarewave      ",
            b"ramp            ",
            b"pulse           ",
            b"noise           ",
            b"sine 1 Hz       ",
            b"sine 8 Hz       ",
            b"sine 8.1777 Hz  ",
            b"sine 8.5 Hz     ",
            b"sine 15 Hz      ",
            b"sine 17 Hz      ",
            b"sine 50 Hz      ",
        ]
        print(repr(ef.handle))
        print(repr(ef.datarecords_in_file))
        print(repr(ef.signals_in_file))
        print(repr(ef.file_duration_seconds), "seconds")
        print(repr(ef.patient_b))
        print(repr(ef.patient))
        print(repr(ef.patient_name_b))
        print(repr(ef.patient_name))
        print("ef.birthdate:", repr(ef.birthdate), "<- ef.birthdate_b:", ef.birthdate_b)
        print("ef.birthdate_date:", ef.birthdate_date)
        assert ef.birthdate_date == datetime.date(1969, 6, 30)
        print(
            "ef.startdate_year, month, day:",
            repr(ef.startdate_year),
            repr(ef.startdate_month),
            repr(ef.startdate_day),
        )
        assert ef.startdate_year == 2011
        assert ef.startdate_month == 4
        assert ef.startdate_day == 4

        print(
            "ef.starttime_hour,min,second:",
            repr(ef.starttime_hour),
            repr(ef.starttime_minute),
            repr(ef.starttime_second),
        )
        assert ef.starttime_hour == 12
        assert ef.starttime_minute == 57
        assert ef.starttime_second == 2

        print("ef.admincode_b:", ef.admincode_b)
        print("ef.admincode:", ef.admincode)
        print("technician_b:", ef.technician_b)
        print("technician:", ef.technician)

        print("equipment:", ef.equipment)
        print("equipment_b:", ef.equipment_b)

        print("recording_additional:", repr(ef.recording_additional))
        print("patient_additional:", repr(ef.patient_additional), "<- ", end="")
        print("patient_additional_:", repr(ef.patient_additional_b))
        print("len(patient_additional_b):", repr(len(ef.patient_additional_b)))
        print("admincode:", repr(ef.admincode))

        for ch in range(ef.signals_in_file):
            print(ef.signal_label(ch), "<-", ef.signal_label_b(ch))
            assert ef.signal_label_b(ch) == true_labels_b[ch]
            print(ef.physical_dimension(ch), "<-", ef.physical_dimension_b(ch))
            assert ef.physical_dimension_b(ch) == b"uV      "


def test_print_raw_properties(fn: str = FILE_NAME) -> None:
    assert os.path.isfile(fn)
    with edfreader.EdfReader(fn) as ef:
        true_birthdate = b"30 jun 1969"
        true_name = b"X"
        true_additional_info = b""
        true_startdate = "04 apr 2011"
        true_device = b"test generator"
        true_starttime = "4 apr 2011 12:57:02"
        true_duration = "0:10:00"
        true_labels_b = [
            b"squarewave      ",
            b"ramp            ",
            b"pulse           ",
            b"noise           ",
            b"sine 1 Hz       ",
            b"sine 8 Hz       ",
            b"sine 8.1777 Hz  ",
            b"sine 8.5 Hz     ",
            b"sine 15 Hz      ",
            b"sine 17 Hz      ",
            b"sine 50 Hz      ",
        ]
        print(repr(ef.handle))
        print(repr(ef.datarecords_in_file))
        print(repr(ef.signals_in_file))
        print(repr(ef.file_duration_seconds), "seconds")
        print(repr(ef.patient_b))
        print(repr(ef.patient))
        print(repr(ef.patient_name_b))
        print(repr(ef.patient_name))
        print("ef.birthdate:", repr(ef.birthdate), "<- ef.birthdate_b:", ef.birthdate_b)
        print("ef.birthdate_date:", ef.birthdate_date)
        # assert ef.birthdate_date == datetime.date(1969,6,30)
        print(
            "ef.startdate_year, month, day:",
            repr(ef.startdate_year),
            repr(ef.startdate_month),
            repr(ef.startdate_day),
        )

        print(
            "ef.starttime_hour,min,second,subsecond100ns units:",
            repr(ef.starttime_hour),
            repr(ef.starttime_minute),
            repr(ef.starttime_second),
            repr(ef.starttime_subsecond),
        )

        print("ef.admincode_b:", ef.admincode_b)
        print("ef.admincode:", ef.admincode)
        print("technician_b:", ef.technician_b)
        print("technician:", ef.technician)

        print("equipment:", ef.equipment)
        print("equipment_b:", ef.equipment_b)

        print("recording_additional:", repr(ef.recording_additional))
        print("patient_additional:", repr(ef.patient_additional), "<- ", end="")
        print("patient_additional_:", repr(ef.patient_additional_b))
        print("len(patient_additional_b):", repr(len(ef.patient_additional_b)))
        print("admincode:", repr(ef.admincode))

        for ch in range(ef.signals_in_file):
            print(ef.signal_label(ch), "<-", ef.signal_label_b(ch))
            print(ef.physical_dimension(ch), "<-", ef.physical_dimension_b(ch))


def test_read_annotations() -> None:
    assert os.path.isfile(FILE_NAME)
    with edfreader.EdfReader(FILE_NAME) as ef:
        # pprint(ef.read_annotations())
        annots = ef.read_annotations()
        assert type(annots) == list
        # [[0.0, 0.0, 'Recording starts'], [600.0, 0.0, 'Recording ends']]
        assert annots[0] == [0.0, 0.0, "Recording starts"]
        assert annots[-1] == [600.0, 0.0, "Recording ends"]


def test_get_samples_per_signal() -> None:
    assert os.path.isfile(FILE_NAME)
    with edfreader.EdfReader(FILE_NAME) as ef:
        sps = ef.get_samples_per_signal()
        pprint(sps)
        pprint(sps.shape)
        pprint(sps.dtype)
        assert np.all(
            sps
            == array(
                [
                    120000,
                    120000,
                    120000,
                    120000,
                    120000,
                    120000,
                    120000,
                    120000,
                    120000,
                    120000,
                    120000,
                ]
            )
        )


# I am not sure how to write this yet, so removing
# def test_read_annotations_as_array_b():
#     assert os.path.isfile(FILE_NAME)
#     with edfreader.EdfReader(FILE_NAME) as ef:
#         pprint(ef.read_annotations_as_array_b())


def test_get_signal_text_labels() -> None:
    assert os.path.isfile(FILE_NAME)
    with edfreader.EdfReader(FILE_NAME) as ef:
        pprint(ef.get_signal_text_labels())


def test_file_duration_seconds() -> None:
    assert os.path.isfile(FILE_NAME)
    with edfreader.EdfReader(FILE_NAME) as ef:
        file_duration = ef.file_duration_seconds
        assert isinstance(file_duration, float)

        file_duration_100ns = ef.file_duration_100ns
        assert isinstance(file_duration_100ns, (int, long))
        assert file_duration_100ns / 10**7 == file_duration


def test_annotations_in_file() -> None:
    with edfreader.EdfReader(FILE_NAME) as ef:
        assert type(ef.annotations_in_file) == int
        assert ef.annotations_in_file == 2


def test_patientcode() -> None:
    with edfreader.EdfReader(FILE_NAME) as ef:
        assert type(ef.patientcode) == str
        assert ef.patientcode == "12345678"


if __name__ == "__main__":
    import sys
    # import argparse
    # parser = argparse.ArgumentParser("load an edf file")
    # parser.add_argument('edf_file', type=str, help='name of an edf file', default=FILE_NAME,required=False)
    # args = parser.parse_args()

    import sys

    # test_make_buffer()
    # test_raw_properties()
    # test_read_annotations()
    # test_read_annotations_as_array_b()
    # test_get_signal_text_labels()
    test_raw_properties()
    if len(sys.argv) > 1:
        test_print_raw_properties(sys.argv[1])
