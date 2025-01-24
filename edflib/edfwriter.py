# -*- coding: utf-8 -*
from __future__ import print_function, division, absolute_import
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    import _cython_3_0_11
from builtins import range

import numpy as np
from . import _edflib

DEFAULT_TEXT_ENCODING = "UTF-8"


class EdfWriter(object):
    def tb(self: Self, x: int) -> bytes | int:
        "general to bytes function"
        if hasattr(x, "encode"):
            return x.encode(self.TEXT_ENCODING)
        else:
            return x

    def __exit__(self, exc_type, exc_val, ex_tb):
        self.close()

    def __init__(
        self: Self,
        file_name: str,
        channel_info: list[dict[str, int]],
        file_type: int = _edflib.FILETYPE_EDFPLUS,
        **kwargs: None,
    ) -> None:
        """Initialises an EDF file at @file_name.
        @file_type is one of
            edflib.FILETYPE_EDF
            edflib.FILETYPE_EDFPLUS
            edflib.FILETYPE_BDF
            edflib.FILETYPE_BDFPLUS

        @channel_info should be a
        list of dicts, one for each channel in the data. Each dict needs
        these values:

            'label' : channel label (string, <= 16 characters, must be unique)
            'dimension' : physical dimension (e.g., mV) (string, <= 8 characters)
            'sample_rate' : sample frequency in hertz (int)
            'physical_max' : maximum physical value (float)
            'physical_min' : minimum physical value (float)
            'digital_max' : maximum digital value (int, -2**15 <= x < 2**15)
            'digital_min' : minimum digital value (int, -2**15 <= x < 2**15)
        """
        self.TEXT_ENCODING = DEFAULT_TEXT_ENCODING  # UTF-8, latin-1 etc.
        self.path = file_name
        self.file_type = file_type
        self.n_channels = len(channel_info)
        self.channels = {}
        for c in channel_info:
            if c["label"] in self.channels:
                raise ChannelLabelExists(c["label"])
            self.channels[c["label"]] = c
        self.sample_buffer = dict([(c["label"], []) for c in channel_info])
        self.handle = _edflib.open_file_writeonly(
            file_name.encode(self.TEXT_ENCODING), file_type, self.n_channels
        )
        self._init_constants(**kwargs)
        self._init_channels(channel_info)

    def write_sample(self: Self, channel_label: str, sample: np.int16) -> None:
        """Queues a digital sample for @channel_label for recording; the data won't
        actually be written until one second's worth of data has been queued."""
        if channel_label not in self.channels:
            raise ChannelDoesNotExist(channel_label)
        self.sample_buffer[channel_label].append(sample)
        if (
            len(self.sample_buffer[channel_label])
            == self.channels[channel_label]["sample_rate"]
        ):
            self._flush_samples()

    def close(self: Self) -> None:
        if self.handle >= 0:
            _edflib.close_file(self.handle)

    def _init_constants(self: Self, **kwargs: None) -> None:
        def call_if_set(
            fn: "_cython_3_0_11.cython_function_or_method", kw_name: str
        ) -> None:
            item = kwargs.pop(kw_name, None)
            if item is not None:
                fn(self.handle, item)

        call_if_set(_edflib.set_technician, "technician")
        call_if_set(_edflib.set_recording_additional, "recording_additional")
        call_if_set(_edflib.set_patientname, "patient_name")
        call_if_set(_edflib.set_patient_additional, "patient_additional")
        call_if_set(_edflib.set_equipment, "equipment")
        call_if_set(_edflib.set_admincode, "admincode")
        call_if_set(_edflib.set_gender, "gender")
        call_if_set(_edflib.set_datarecord_duration, "duration")
        call_if_set(
            (
                lambda hdl, dt: _edflib.set_startdatetime(
                    hdl, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
                )
            ),
            "recording_start_time",
        )
        call_if_set(
            (lambda hdl, dt: _edflib.set_birthdate(hdl, dt.year, dt.month, dt.day)),
            "patient_birthdate",
        )
        if len(kwargs) > 0:
            raise Exception("Unhandled argument(s) given: %r" % list(kwargs.keys()))

    def _init_channels(self: Self, channels: list[dict[str, float]]) -> None:
        hdl = self.handle
        print("in init channels")

        print("channels::\n", repr(channels))

        def call_per_channel(
            fn: "_cython_3_0_11.cython_function_or_method",
            name: str,
            optional: bool = False,
        ) -> None:
            for i, c in enumerate(channels):
                if optional and not name in c:
                    continue
                fn(hdl, i, self.tb(c[name]))

        call_per_channel(_edflib.set_samplefrequency, "sample_rate")
        call_per_channel(_edflib.set_physical_maximum, "physical_max")
        call_per_channel(_edflib.set_digital_maximum, "digital_max")
        call_per_channel(_edflib.set_digital_minimum, "digital_min")
        call_per_channel(_edflib.set_physical_minimum, "physical_min")
        call_per_channel(_edflib.set_label, "label")
        call_per_channel(_edflib.set_physical_dimension, "dimension")
        call_per_channel(_edflib.set_transducer, "transducer", optional=True)
        call_per_channel(_edflib.set_prefilter, "prefilter", optional=True)

    def _flush_samples(self: Self) -> None:
        for c in self.channels:
            buf = np.array(
                self.sample_buffer[c], dtype="int32"
            )  # changed to dtype='int32'
            _edflib.write_digital_samples(self.handle, buf)
            self.sample_buffer[c] = []

    # property handle:
    #     "edflib internal int handle"
    #     def __get__(self):
    #         return self.hdr.handle

    # strategy: see if can write whole class in python calling into _edflib
    # keep a copy of all text in python to avoid encoding issues
    # for an attribute "x", this will be stored as self._x
    #
    # then encode to TEXT_ENCODING before writing to file
    # it is not clear to me how text should be encoded in an EDF+ file
    # T has latin-1 encoding for annotations

    @property
    def patient_name(self):
        """patient name: convention to store as lastname, firstname middle..."""
        # self._patient_name = edflib_get_patient_name(self.handle) # decode from utf or latin1
        return self._patient_name

    @patient_name.setter
    def patient_name(self, name):
        self._patient_name = name
        bname = name.encode(self.TEXT_ENCODING)
        _edflib.set_patientname(self.handle, bname)

    @property
    def patientcode(self):
        return self._patientcode

    @patientcode.setter
    def patientcode(self, patientcode):
        self._patientcode = patientcode
        bs = patientcode.encode(self.TEXT_ENCODING)
        _edflib.set_patientcode(self.handle, bs)

    #     def __get__(self):
    #         return self.hdr.patientcode

    # property datarecords_in_file:
    #     "number of data records"
    #     def __get__(self):
    #         return self.hdr.datarecords_in_file

    # property signals_in_file:
    #     def __get__(self):
    #         return self.hdr.edfsignals

    # property file_duration_seconds:
    #     "file duration in seconds"
    #     def __get__(self):
    #         return self.hdr.file_duration/EDFLIB_TIME_DIMENSION

    # property datarecord_duration_seconds:
    #     "datarecord duration in seconds (as a double)"
    #     def __get__(self):
    #         return (<double>self.hdr.datarecord_duration) / EDFLIB_TIME_DIMENSION

    # property annotations_in_file:
    #     def __get__(self):
    #         return self.hdr.annotations_in_file

    # property gender_b:
    #     def __get__(self):
    #         return self.hdr.gender

    # property birthdate_b:
    #     def __get__(self):
    #         return self.hdr.birthdate

    # property patientname:
    #     def __get__(self):
    #         return self.hdr.patient_name

    # property patient_additional:
    #     def __get__(self):
    #         return self.hdr.patient_additional

    # property startdate_year:
    #     def __get__(self):
    #         return self.hdr.startdate_year

    # property startdate_month:
    #     def __get__(self):
    #         return self.hdr.startdate_month

    # property startdate_day:
    #     def __get__(self):
    #         return self.hdr.startdate_day

    # property starttime_hour:
    #     def __get__(self):
    #         return self.hdr.starttime_hour

    # property starttime_minute:
    #     def __get__(self):
    #         return self.hdr.starttime_minute

    # property starttime_second:
    #     def __get__(self):
    #         return self.hdr.starttime_second

    # property admincode:
    #     def __get__(self):
    #         return self.hdr.admincode

    # property technician:
    #     def __get__(self):
    #         return self.hdr.technician

    # property equipment:
    #     def __get__(self):
    #         return self.hdr.equipment

    # property recording_additional:
    #     def __get__(self):
    #         return self.hdr.recording_additional
