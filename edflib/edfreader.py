# -*- coding: utf-8 -*-
# , unicode_literals
from __future__ import print_function, division, absolute_import
from typing import TYPE_CHECKING, Any, Self
from numpy.typing import NDArray

if TYPE_CHECKING:
    import numpy.dtypes
    import jaxtyping
from typing import Self

import datetime
from builtins import range, super, bytes
from . import _edflib
import numpy as np

DEFAULT_TEXT_ENCODING = "UTF-8"


class EdfReader(_edflib.CyEdfReader):
    def __init__(self: Self, file_name: str, annotations_mode: str = "all") -> None:
        bytes_file_name = bytes(
            file_name, DEFAULT_TEXT_ENCODING
        )  # technically might need to be ascii
        super().__init__(file_name=bytes_file_name, annotations_mode=annotations_mode)

    def __enter__(self: Self) -> Self:
        return self

    def __exit__(self: Self, exc_type: None, exc_val: None, ex_tb: None) -> None:
        self._close()  # cleanup the file

    def close(self):  # should this function exist?
        self._close()

    # per channel functions
    def signal_label(self: Self, channel: int) -> str:
        return self.signal_label_b(channel).decode(DEFAULT_TEXT_ENCODING).strip()

    def physical_dimension(self: Self, channel: int) -> str:
        return self.physical_dimension_b(channel).decode(DEFAULT_TEXT_ENCODING).strip()

    # return arrays

    def get_samples_per_signal(self: Self) -> NDArray[np.int64]:
        """return a numpy array with number of samples for each signal in the edf file"""
        return np.array(
            [self.samples_in_file(chn) for chn in range(self.signals_in_file)]
        )

    def read_annotations(self: Self) -> list[list[float]]:
        annot = self.read_annotations_b()
        for ii in range(len(annot)):
            floatstr = annot[ii][1]
            if floatstr:
                floatstr = floatstr.decode("ascii")
                annot[ii][1] = float(floatstr)
            else:
                annot[ii][1] = 0.0
            annot[ii][2] = annot[ii][2].decode("UTF-8")
        return annot

    # this is broken under py 3.5, 2.7 tests
    # def read_annotations_as_array_b(self):
    #     """return a numpy array of the annotations instead of list as returned by
    #     read_annotation()
    #     """
    #     annot = self.read_annotations_b()
    #     dt = np.dtype("ffO")
    #     # need to specify the dtype correctly TODO float,float, string (bytes) !!!
    #     arr_annot = np.array(annot, dtype=dt)
    #     return arr_annot

    def get_signal_freqs(self) -> NDArray[np.float64]:
        return np.array(
            [self.samplefrequency(chn) for chn in range(self.signals_in_file)]
        )

    def get_signal_text_labels(self: Self) -> list[str]:
        """
        get_signal_text_labels(self)
        get a list holding all of the channel labels
        returns str list rather than bytes in modern python
        """

        return [self.signal_label(chn) for chn in range(self.signals_in_file)]

    def get_signal(self, chn) -> NDArray[np.float64]:
        """
        convenience function to read the entirety of a physical channel and get back
        a numpy array holding all the data
        @chn - integer starting at zero determining which channel to read
        """
        # not sure how useful this is in practice but was useful for testing
        nsamples = self.get_samples_per_signal()
        n_chan = len(nsamples)  # one way to infer this
        if (chn < n_chan) and (chn >= 0):
            x = np.zeros(nsamples[chn], dtype=np.float64)
            v = x[chn * nsamples[chn] : (chn + 1) * nsamples[chn]]
            self.read_phys_signal(chn, 0, nsamples[chn], v)
            return x
        else:
            return np.array([])

    # properties which need conversion from bytes
    # integer properties are defined in _edflib

    @property
    def gender(self) -> str:
        """string to represent gender, often F,M or O etc."""
        return self.gender_b.decode(DEFAULT_TEXT_ENCODING)

    @property
    def birthdate(self: Self) -> str:
        return self.birthdate_b.decode(DEFAULT_TEXT_ENCODING)

    @property
    def birthdate_date(self: Self) -> datetime.date:
        """returns the birthdate as a datetime.date() object if possible this expects a
        specific format for the birthday ex '09 apr 1999' so may not be robust,
        could use dateutil.parser instead but slower and would introduce another
        dependency

        """

        bday = self.birthdate
        if bday:
            dt = datetime.datetime.strptime(
                bday, "%d %b %Y"
            )  # not sure if this format even complies with spec
            # dt = dateutil.parser.parse(bday) # this will guess at a bunch of different formats
            # dt = arrow.get(bday)
            return dt.date()
        else:
            return bday  # None

    @property
    def patient_name(self: Self) -> str:
        return self.patient_name_b.decode(DEFAULT_TEXT_ENCODING)

    @property
    def patient(self: Self) -> str:
        "patient field char[81] null term string. Is always empty when filetype is EDF+/BDF+"
        return self.patient_b.decode(DEFAULT_TEXT_ENCODING)

    @property
    def patient_additional(self: Self) -> str:
        return self.patient_additional_b.decode(DEFAULT_TEXT_ENCODING).strip()

    @property
    def admincode(self: Self) -> str:
        return self.admincode_b.decode(DEFAULT_TEXT_ENCODING)

    @property
    def technician(self: Self) -> str:
        return self.technician_b.decode(DEFAULT_TEXT_ENCODING)

    @property
    def equipment(self: Self) -> str:
        return self.equipment_b.decode(DEFAULT_TEXT_ENCODING)

    @property
    def recording_additional(self: Self) -> str:
        return self.recording_additional_b.decode(DEFAULT_TEXT_ENCODING)

    @property
    def patientcode(self) -> str:
        return self.patientcode_b.decode(DEFAULT_TEXT_ENCODING)


class Edfinfo(object):
    """class to just get info about an edf file and print it
    just use the cython type to do so as we work on EdfReader

    probably this should be moved to the tests folder
    """

    def __init__(self, file_name, text_encoding=DEFAULT_TEXT_ENCODING):
        self.TEXT_ENCODING = (
            text_encoding  # you may have to guess what the correct one is
        )

        self.cedf = _edflib.CyEdfReader(file_name)
        self.file_name = file_name
        self.signal_labels = []
        self.signal_nsamples = []
        self.samplefreqs = []
        # do a lot of silly copying?
        self.signals_in_file = self.cedf.signals_in_file
        self.datarecords_in_file = self.cedf.datarecords_in_file
        for ii in range(self.signals_in_file):
            self.signal_labels.append(
                self.cedf.signal_label(ii).decode(DEFAULT_TEXT_ENCODING).strip()
            )
            self.signal_nsamples.append(self.cedf.samples_in_file(ii))
            self.samplefreqs.append(self.cedf.samplefrequency(ii))

    def file_info(self):
        print("file name:", self.file_name)
        print("signals in file:", self.signals_in_file)

    def file_info_long(self):
        self.file_info()
        for ii in range(self.signals_in_file):
            print(
                "label:",
                self.signal_labels[ii],
                "fs:",
                self.samplefreqs[ii],
                "nsamples",
                self.signal_nsamples[ii],
            )
