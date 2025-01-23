#cython: language_level=3
# note may want to use arr[::1] approach for proper continuguity/striding
# when passing data pointers to c function libraries

"""currently everything defined in this cython file uses bytes for characters
(these are the str type in python 2.7)

EDF requires 7-bit ascii
EDF+ allows only us-ascii in the header (values 32..126), the TAL annotions may contain unicode in UTF-8

see http://www.edfplus.info/specs/edfplus.html

So how to handle text in using this library

"""
from __future__ import print_function

import sys
cimport cpython
import numpy as np
cimport numpy as np

include "edf.pxi"

DEFAULT_ENCODING = 'UTF-8'

open_errors = {
    EDFLIB_MALLOC_ERROR : "malloc error",
    EDFLIB_NO_SUCH_FILE_OR_DIRECTORY   : "can not open file, no such file or directory",
    EDFLIB_FILE_CONTAINS_FORMAT_ERRORS : "the file is not EDF(+) or BDF(+) compliant (it contains format errors)",
    EDFLIB_MAXFILES_REACHED            : "to many files opened",
    EDFLIB_FILE_READ_ERROR             : "a read error occurred",
    EDFLIB_FILE_ALREADY_OPENED         : "file has already been opened",
    EDFLIB_FILETYPE_ERROR              : "Wrong file type",
    EDFLIB_FILE_WRITE_ERROR            : "a write error occured",
    EDFLIB_NUMBER_OF_SIGNALS_INVALID   : "The number of signals is invalid",
    EDFLIB_FILE_IS_DISCONTINUOUS       : "The file is discontinous and cannot be read",
    EDFLIB_INVALID_READ_ANNOTS_VALUE   : "an annotation value could not be read",
#    EDFLIB_FILE_ERRORS_STARTDATE      : "the file is not EDF(+) or BDF(+) compliant (startdate)",
#    EDFLIB_FILE_ERRORS_STARTTIME      : "the file is not EDF(+) or BDF(+) compliant (starttime)",
#    EDFLIB_FILE_ERRORS_NUMBER_SIGNALS : "the file is not EDF(+) or BDF(+) compliant (number of signals)",
#    EDFLIB_FILE_ERRORS_BYTES_HEADER   : "the file is not EDF(+) or BDF(+) compliant (Bytes Header)",
#    EDFLIB_FILE_ERRORS_RESERVED_FIELD : "the file is not EDF(+) or BDF(+) compliant (Reserved field)",
#    EDFLIB_FILE_ERRORS_NUMBER_DATARECORDS : "the file is not EDF(+) or BDF(+) compliant (Number of Datarecords)",
#    EDFLIB_FILE_ERRORS_DURATION : "the file is not EDF(+) or BDF(+) compliant (Duration)",
#    EDFLIB_FILE_ERRORS_LABEL : "the file is not EDF(+) or BDF(+) compliant (Label)",
#    EDFLIB_FILE_ERRORS_TRANSDUCER : "the file is not EDF(+) or BDF(+) compliant (Transducer)",
#    EDFLIB_FILE_ERRORS_PHYS_DIMENSION : "the file is not EDF(+) or BDF(+) compliant (Physical Dimension)",
#    EDFLIB_FILE_ERRORS_PHYS_MAX : "the file is not EDF(+) or BDF(+) compliant (Physical Maximum)",
#    EDFLIB_FILE_ERRORS_PHYS_MIN : "the file is not EDF(+) or BDF(+) compliant (Physical Minimum)",
#    EDFLIB_FILE_ERRORS_DIG_MAX : "the file is not EDF(+) or BDF(+) compliant (Digital Maximum)",
#    EDFLIB_FILE_ERRORS_DIG_MIN : "the file is not EDF(+) or BDF(+) compliant (Digital Minimum)",
#    EDFLIB_FILE_ERRORS_PREFILTER : "the file is not EDF(+) or BDF(+) compliant (Prefilter)",
#    EDFLIB_FILE_ERRORS_SAMPLES_DATARECORD : "the file is not EDF(+) or BDF(+) compliant (Sample in Datarecord)",
#    EDFLIB_FILE_ERRORS_FILESIZE : "the file is not EDF(+) or BDF(+) compliant (Filesize)",
#    EDFLIB_FILE_ERRORS_RECORDINGFIELD : "the file is not EDF(+) or BDF(+) compliant (EDF+ Recordingfield)",
#    EDFLIB_FILE_ERRORS_PATIENTNAME : "the file is not EDF(+) or BDF(+) compliant (EDF+ Patientname)",
    'default' : "unknown error"
    }


write_errors = {
    EDFLIB_MALLOC_ERROR : "malloc error",
    EDFLIB_NO_SUCH_FILE_OR_DIRECTORY   : "can not open file, no such file or directory",
    EDFLIB_FILE_CONTAINS_FORMAT_ERRORS : "the file is not EDF(+) or BDF(+) compliant (it contains format errors)",
    EDFLIB_MAXFILES_REACHED            : "to many files opened",
    EDFLIB_FILE_READ_ERROR             : "a read error occurred",
    EDFLIB_FILE_ALREADY_OPENED         : "file has already been opened",

    EDFLIB_FILETYPE_ERROR               : "Wrong file type",
    EDFLIB_FILE_WRITE_ERROR             : "a write error occured",
    EDFLIB_NUMBER_OF_SIGNALS_INVALID    : "The number of signals is invalid",
    EDFLIB_NO_SIGNALS                   : "no signals to write",
    EDFLIB_TOO_MANY_SIGNALS             : "too many signals",
    EDFLIB_NO_SAMPLES_IN_RECORD         : "no samples in record",
    EDFLIB_DIGMIN_IS_DIGMAX             : "digmin is equal to digmax",
    EDFLIB_DIGMAX_LOWER_THAN_DIGMIN     : "digmax is lower than digmin",
    EDFLIB_PHYSMIN_IS_PHYSMAX           : "physmin is physmax",

    'default' : "unknown error"
    }

# constants are redeclared here so we can access them from Python
FILETYPE_EDF = EDFLIB_FILETYPE_EDF
FILETYPE_EDFPLUS = EDFLIB_FILETYPE_EDFPLUS
FILETYPE_BDF = EDFLIB_FILETYPE_BDF
FILETYPE_BDFPLUS = EDFLIB_FILETYPE_BDFPLUS

def check_open_ok(result, error_type):
    """error_type should usually be hdr.filetype"""
    if result == 0:
        return True
    else:
        raise IOError, write_errors[error_type]
        # return False


def lib_version():
    return edflib_version()

cdef class CyEdfReader:
    """
    This provides a simple interface to read EDF, EDF+, and probably is ok with
    BDF and BDF+ files
    Note that edflib.c is encapsulated so there is no direct access to the file
    from here unless I add a raw interface or something

    EDF/BDF+ files are arranged into N signals sampled at rate Fs. The data is
    actually stored in chunks called  "datarecords" which have a file specific size
    (often 1 second chunks).

    A typical way to use this to read an EEG file would be to choose a certain
    number of seconds per page to display. Then figure out how many data records
    that is. Then read in that many data records at a time. Transform the data as
    needed according the montage and filter settings, then display the data.

    """


    cdef edf_hdr_struct hdr
    cdef size_t nsamples_per_record
    #I think it is ok not to do this in __cinit__(*,**)

    def __init__(self, file_name, annotations_mode='all'):
        # valid values for self.hdr.handleare int 0,1,2,.. MAX
        self.hdr.handle = -1  # good invalid value for handle
        self.open(file_name, mode='r', annotations_mode=annotations_mode)

    def __dealloc__(self):

        if self.hdr.handle >= 0:
            # print("autoclosing file via handle in __dealloc__")
            edfclose_file(self.hdr.handle)
            self.hdr.handle = -1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, ex_tb):
        self._close()  # cleanup the file


    def make_phys_datarecord_buffer(self):
        """
        utilty function to make a buffer that can hold a single datarecord. This will
        hold the physical samples for a single data record as a numpy tensor.

        -  might extend to provide for N datarecord size

        """
        # print("self.hdr.datarecords_in_file", self.hdr.datarecords_in_file)
        tmp = 0
        for ii in range(self.signals_in_file):
            tmp += self.samples_in_datarecord(ii)
        self.nsamples_per_record = tmp
        dbuffer = np.zeros(tmp, dtype='float64') # will get physical samples, not the orignal digital samples
        return dbuffer

    def open(self, file_name, mode='r', annotations_mode='all'):
        # bytes_file_name = file_name.encode(DEFAULT_ENCODING) # this encoding returns a byte string and this works in py2.7 and py3.5
        # print("bytes_file_name:", bytes_file_name, "type of this: ", type(bytes_file_name))
        # returns -1 if something weird happens and sets hdr.filetype to the result
        result = edfopen_file_readonly(file_name, &self.hdr, EDFLIB_READ_ALL_ANNOTATIONS)
        # self.handle = self.hdr.handle
        #if result < 0:
        #    print("self.hdr.filetype:", self.hdr.filetype, write_errors[self.hdr.filetype])
        return check_open_ok(result, self.hdr.filetype)

    def read_annotations_b(self):
        """return units of times in sensible units of float seconds
        [float(start_seconds), float(duration_seconds), b"text"]

        instead of the implementation integers of 100ns increments as stored
        """
        cdef edf_annotation_struct annot
        annotlist = [[0,'',''] for x in range(self.annotations_in_file)]
        for ii in range(self.annotations_in_file):
            edf_get_annotation(self.hdr.handle, ii, &(annot))
            #get_annotation(self.hdr.handle, ii, &annotation)
            annotlist[ii][0] = annot.onset*0.0000001 # annot.onset is units multiplied by 10000000 (10^7)
	    #  100ns resolution
            annotlist[ii][1] = annot.duration # or float(annot.duration)
            annotlist[ii][2] = annot.annotation
        return annotlist


    def read_annotations_b_100ns_units(self):
        """
        return integer units of times of 100ns
        this is the most precise way to get the annotation times but it is abit less
        convenient to use at times
        """
        cdef edf_annotation_struct annot
        annotlist = [[0,'',''] for x in range(self.annotations_in_file)]
        for ii in range(self.annotations_in_file):
            edf_get_annotation(self.hdr.handle, ii, &(annot))
            #get_annotation(self.hdr.handle, ii, &annotation)
            annotlist[ii][0] = annot.onset # annot.onset is units multiplied by 10000000 (10^7)
	    #  100ns resolution
            annotlist[ii][1] = annot.duration
            annotlist[ii][2] = annot.annotation
        return annotlist

    # properties and functions which return "raw" bytes have "_b" at end

    @property
    def handle(self):
        "edflib internal int handle"
        return self.hdr.handle

    @property
    def filetype(self):
         "0: EDF, 1: EDFplus, 2: BDF, 3: BDFplus, a negative number means an error"
         return self.hdr.filetype

    @property
    def signals_in_file(self):
        """number of EDF signals in the file, annotation channels not included
        self.hdr.edfsignals """
        return self.hdr.edfsignals

    @property
    def datarecords_in_file(self) -> int:
        """number of data records type (long long int) """
        return self.hdr.datarecords_in_file


    @property
    def file_duration_100ns(self) -> int:
        """file duration in integer units of 100 nanoseconds"""
        return self.hdr.file_duration

    @property
    def file_duration_seconds(self):
        "floating point file duration in seconds"
        return (<double> self.hdr.file_duration)/EDFLIB_TIME_DIMENSION

    @property
    def startdate_day(self):
        return self.hdr.startdate_day


    @property
    def startdate_month(self):
        return self.hdr.startdate_month

    @property
    def startdate_year(self):
        "returns an integer year"
        return self.hdr.startdate_year

    @property
    def starttime_subsecond(self):
        """long long starttime starttime offset expressed in units of 100
        nanoSeconds. Is always less than 10000000 (one second). Only used by
        EDFplus and BDFplus
        """
        return self.hdr.starttime_subsecond

    @property
    def starttime_second(self):
        return self.hdr.starttime_second

    @property
    def starttime_minute(self):
        return self.hdr.starttime_minute

    @property
    def starttime_hour(self):
        return self.hdr.starttime_hour



    @property
    def patient_b(self):
        """patient field char[81] null term string. Is always empty when filetype is EDF+/BDF+"""
        return self.hdr.patient

    @property
    def recording_b(self):
        """
        recording field char[81] null terminated string, is always empty when filetype
        is EDF+/BDF+"""
        return self.hdr.recording


    @property
    def patientcode_b(self):
        """null-terminated string, is always empty when filetype is EDF or BDF
        spec sets format constraints"""
        return self.hdr.patientcode


    @property
    def gender_b(self):
        """null-terminated string, is always empty when filetype is EDF or BDF"""
        return self.hdr.gender



    @property
    def annotations_in_file(self):
        return self.hdr.annotations_in_file


    @property
    def birthdate_b(self):
        """null-terminated string, is always empty when filetype is EDF or BDF"""
        return self.hdr.birthdate

    @property
    def patient_name_b(self):
        return self.hdr.patient_name

    @property
    def patient_additional_b(self):
        return self.hdr.patient_additional


    @property
    def admincode_b(self):
        return self.hdr.admincode

    @property
    def technician_b(self):
        return self.hdr.technician

    @property
    def equipment_b(self):
        return self.hdr.equipment

    @property
    def recording_additional_b(self):
        return self.hdr.recording_additional

    @property
    def datarecord_duration_seconds(self):
        "datarecord duration in seconds (as a double)"
        return (<double>self.hdr.datarecord_duration) / EDFLIB_TIME_DIMENSION

    @property
    def datarecord_duration_100ns(self):
        "datarecord duration in units of 100ns as integer"
        return self.hdr.datarecord_duration


    # signal parameters
    def signal_label_b(self, channel) -> bytes:
        return self.hdr.signalparam[channel].label

    def samples_in_file(self,channel) -> int:  # long long int smp_in_file
        return self.hdr.signalparam[channel].smp_in_file

    def samples_in_datarecord(self, channel) -> int:
        return self.hdr.signalparam[channel].smp_in_datarecord

    def physical_dimension_b(self, channel) -> bytes:  # char physdimension[9]
        return self.hdr.signalparam[channel].physdimension

    def physical_max(self, channel) -> float: # double
        return self.hdr.signalparam[channel].phys_max

    def physical_min(self, channel) -> float:
        return self.hdr.signalparam[channel].phys_min

    def digital_max(self, channel) -> int: # C int dig_max
        return self.hdr.signalparam[channel].dig_max

    def digital_min(self, channel) -> int:
        return self.hdr.signalparam[channel].dig_min

    def prefilter(self, channel) -> bytes: # char prefilter[81]
        return self.hdr.signalparam[channel].prefilter

    def transducer(self, channel) -> bytes: #char transducer[81]
        return self.hdr.signalparam[channel].transducer

    def samplefrequency(self, channel) -> float:
        """returns a floating point approximation to the sampling frequency
        for more exact calculations instead using the number of samples per data record
        and also get the length of time each data record occupies"""
        return (<double>self.hdr.signalparam[channel].smp_in_datarecord / self.hdr.datarecord_duration) * EDFLIB_TIME_DIMENSION

    # def _tryoffset0(self):
    #     """
    #     fooling around to find offset in file to allow shortcut mmap interface
    #     """
    #     # cdef long offset = self.hdr.hdrsize  # from edflib.c read_physical_samples()
    #     print("trying to find data offset in file")
    #     nrecords = self.hdr.datarecords_in_file
    #     print("nrecords in file:", nrecords)
    #     return 1,2
    #     # return offset, nrecords
    #     # print("offset via edftell:",  edftell(self.hdr.handle, 0))


    def _close(self):   # should not be closed from python
        if self.hdr.handle >= 0:
            edfclose_file(self.hdr.handle)
        self.hdr.handle = -1

    def read_digital_signal(self, signalnum, start, n, np.int32_t[:] sigbuf) -> int:
       """
       read_digital_signal(self, signalnum, start, n, np.int32_t[:] sigbuf)
       read @n number of samples from signal number @signum starting at @start
          into preallocated numpy int32 array @sigbuf
          - sigbuf must be at least n long

       returns @readn number of samples actually read
       """
       edfseek(self.hdr.handle, signalnum, start, EDFSEEK_SET)
       readn = read_int_samples(self.hdr.handle, signalnum, n, sigbuf)

       # probably should handle this better as it is not abnormal to read the end
       # of a record
       # if want to alert
       # if readn != n:
       #     print("read %d, less than %d requested!!!" % (readn, n))
       return readn

    def read_phys_signal(self, signalnum, start, n, np.float64_t[:] sigbuf):
        """
        read_phys_signal(self, signalnum, start, n, np.float64_t[:] sigbuf)
        read @n number of samples from signal number @signum starting at
        @start into numpy float64 array @sigbuf sigbuf must be at least n long
        the signal is converted to a physical real value from its digitally sampled form
        """

        edfseek(self.hdr.handle, signalnum, start, EDFSEEK_SET)
        readn = edfread_physical_samples(self.hdr.handle, signalnum, n, &sigbuf[0])
        # print("read %d samples" % readn)
        # if readn != n:
        #    print("read %d, less than %d requested!!!" % (readn, n) )

        return readn

    def load_phys_datarecord(self, np.float64_t[:] db, n=0):
        """
        every edf file has a block size called a data record
        I think this is block of data that can be reshaped into a (often) rectangular
        (though possibly ragged) array of the N channels of samples_in_datarecord(n)

        this function is supposed to make reading a datarecord easier assumming you provide
        a block of the correct size = $\sum_n samples_in_datarecord(n)$

        it is not yet clear to be me if this is a useful function to keep around
        """
        cdef size_t offset =0

        if n < self.hdr.datarecords_in_file:
            for ii in range(self.signals_in_file):
                edfseek(self.hdr.handle, ii, n*self.samples_in_datarecord(ii), EDFSEEK_SET) # just a guess
                readn = edfread_physical_samples(self.hdr.handle, ii, self.samples_in_datarecord(ii),
                                                 &db[offset])
                # print("readn this many samples", readn)
                offset += self.samples_in_datarecord(ii)


###############################
# low level functions

cdef set_patientcode(int handle, char *patientcode):
    # check if rw?
    return edf_set_patientcode(handle, patientcode)



cdef int write_annotation_latin1(int handle, long long onset, long long duration, char *description):
        return edfwrite_annotation_latin1(handle, onset, duration, description)

cdef int write_annotation_utf8(int handle, long long onset, long long duration, char *description):
    """int edfwrite_annotation_utf8(int handle, long long onset, long long duration, const char *description)"""
    return edfwrite_annotation_utf8(handle, onset, duration, description)


cpdef set_technician(int handle, char *technician):
    return edf_set_technician(handle, technician)

cdef class EdfAnnotation:
    cdef edf_annotation_struct annotation


cdef int get_annotation(int handle, int n, EdfAnnotation edf_annotation):
    return edf_get_annotation(handle, n, &(edf_annotation.annotation))

# need to use npbuffers

def read_int_samples(int handle, int edfsignal, int n, np.int32_t[:] buf):
    """
    reads n samples from edfsignal, starting from the current sample position indicator, into buf (edfsignal starts at 0)
    the values are the "raw" digital values
    bufsize should be equal to or bigger than sizeof(int[n])
    the sample position indicator will be increased with the amount of samples read
    returns the amount of samples read (this can be less than n or zero!)
    or -1 in case of an error


    ToDO!!!
    assert that these are stored as EDF/EDF+ files with int16 sized samples
    returns how many were actually read
    doesn't currently check that buf can hold all the data
    """
    return edfread_digital_samples(handle, edfsignal, n,<int*> &buf[0]) # try this with int* cast


cdef int blockwrite_digital_samples(int handle, np.int32_t[:] buf):
    """int edf_blockwrite_digital_samples(int handle, int *buf)"""
    return edf_blockwrite_digital_samples(handle,<int*> &buf[0])

cdef int blockwrite_digital_short_samples(int handle, np.int16_t[:] buf):
    """int edf_blockwrite_digital_short_samples(int handle, short *buf)"""
    return edf_blockwrite_digital_short_samples(handle,<short*> &buf[0])

cdef int blockwrite_physical_samples(int handle, np.float64_t[:] buf):
    return edf_blockwrite_physical_samples(handle, &buf[0])

def set_recording_additional(int handle, char *recording_additional):
    return edf_set_recording_additional(handle,recording_additional)

# return int
def write_physical_samples(int handle, np.float64_t[:] buf):
    return edfwrite_physical_samples(handle, &buf[0])

    # int edfwrite_annotation_utf8(int, long long int, long long int, char *)

# returns int
def set_patientname(int handle, char *name):
    return edf_set_patientname(handle, name)

# returns int
def set_physical_minimum(int handle, int edfsignal, double phys_min):
    edf_set_physical_minimum(handle, edfsignal, phys_min)

# returns int
def read_physical_samples(int handle, int edfsignal, int n,
                                np.ndarray[np.float64_t] buf):
    return edfread_physical_samples(handle, edfsignal, n, &buf[0])

def close_file(handle):
    return edfclose_file(handle)

# so you can use the same name if defining a python only function
def set_physical_maximum(handle, edfsignal, phys_max):
    return edf_set_physical_maximum(handle, edfsignal, phys_max)

def open_file_writeonly(path, filetype, number_of_signals):
    """int edfopen_file_writeonly(char *path, int filetype, int number_of_signals)"""
    return edfopen_file_writeonly(path, filetype, number_of_signals)

def set_patient_additional(handle, patient_additional):
    """int edf_set_patient_additional(int handle, const char *patient_additional)"""
    return edf_set_patient_additional(handle, patient_additional)

def set_digital_maximum(handle, edfsignal, dig_max):
    "int edf_set_digital_maximum(int handle, int edfsignal, int dig_max)"
    return edf_set_digital_maximum(handle, edfsignal, dig_max)


# see CyEdfreader() class
# int edfopen_file_readonly(const char *path, struct edf_hdr_struct *edfhdr, int read_annotations)

def set_birthdate(handle, birthdate_year, birthdate_month, birthdate_day):
    """int edf_set_birthdate(int handle, int birthdate_year, int birthdate_month, int birthdate_day)"""
    return edf_set_birthdate(handle, birthdate_year,  birthdate_month, birthdate_day)

def set_digital_minimum(handle, edfsignal, dig_min):
    """int edf_set_digital_minimum(int handle, int edfsignal, int dig_min)"""
    return edf_set_digital_minimum(handle,  edfsignal, dig_min)

def write_digital_samples(handle, np.ndarray[np.int32_t] buf):
    """write_digital_samples(int handle, np.ndarray[np.int32_t] buf)
    call to
    int edfwrite_digital_samples(int handle, int *buf)"""
    return edfwrite_digital_samples(handle,<int*> &buf[0])

def write_digital_short_samples(handle, np.ndarray[np.int16_t] buf):
    """int edfwrite_digital_short_samples(int handle, short *buf)"""
    return edfwrite_digital_short_samples(handle,<short*> &buf[0])

def set_equipment(handle, equipment):
    """int edf_set_equipment(int handle, const char *equipment)"""
    return edf_set_equipment(handle, equipment)

def set_samplefrequency(handle, edfsignal, samplefrequency):
    """int edf_set_samplefrequency(int handle, int edfsignal, int samplefrequency)"""
    return edf_set_samplefrequency(handle, edfsignal, samplefrequency)

def set_admincode(handle, admincode):
    """int edf_set_admincode(int handle, const char *admincode)"""
    return edf_set_admincode(handle, admincode)

def set_label(handle, edfsignal, label):
    """int edf_set_label(int handle, int edfsignal, const char *label)"""
    return edf_set_label(handle, edfsignal, label)

def set_number_of_annotation_signals(handle, annot_signals):
    """int edf_set_number_of_annotation_signals(int handle, int annot_signals)"""
    return edf_set_number_of_annotation_signals(handle, annot_signals)

#FIXME need to make sure this gives the proper values for large values
def tell(handle, edfsignal):
    """long long edftell(int handle, int edfsignal)"""
    return edftell(handle,  edfsignal)

def rewind(handle, edfsignal):
    """void edfrewind(int handle, int edfsignal)"""
    edfrewind(handle, edfsignal)

def set_gender(handle, gender):
    """int edf_set_gender(int handle, int gender)"""
    return edf_set_gender(handle, gender)

def set_physical_dimension(handle, edfsignal, phys_dim):
    """int edf_set_physical_dimension(int handle, int edfsignal, const char *phys_dim)"""
    return edf_set_physical_dimension(handle, edfsignal, phys_dim)

def set_transducer(handle, edfsignal, transducer):
    """int edf_set_transducer(int handle, int edfsignal, const char *transducer)"""
    return edf_set_transducer(handle, edfsignal, transducer)

def set_prefilter(handle, edfsignal, prefilter):
    """int edf_set_prefilter(int handle, int edfsignal, const char*prefilter)"""
    return edf_set_prefilter(handle, edfsignal, prefilter)

def seek(handle, edfsignal, offset, whence):
    """long long edfseek(int handle, int edfsignal, long long offset, int whence)"""
    return edfseek(handle, edfsignal, offset, whence)

def set_startdatetime(handle, startdate_year, startdate_month, startdate_day,
                          starttime_hour, starttime_minute, starttime_second):
    """int edf_set_startdatetime(int handle, int startdate_year, int startdate_month, int startdate_day,
                                      int starttime_hour, int starttime_minute, int starttime_second)"""
    return edf_set_startdatetime(handle, startdate_year, startdate_month, startdate_day,
                                 starttime_hour, starttime_minute, starttime_second)


def set_datarecord_duration(handle, duration):
    """int edf_set_datarecord_duration(int handle, int duration)"""
    return edf_set_datarecord_duration(handle, duration)

## old test function ###


# def test1_edfopen():
#     print("hi")
#     # based upon main.c
#     cdef:
#         int i, hdl, channel, n
#         double *buf
#         edf_hdr_struct hdr
#         np.ndarray[np.float64_t, ndim=1] carr

#     result = edfopen_file_readonly("test_generator.edf", &hdr, EDFLIB_READ_ALL_ANNOTATIONS)
#     print("result:", result)
#     check_open_ok(result, hdr.filetype)
#     hdl = hdr.handle
#     print("hdr.edfsignals", hdr.edfsignals)

#     print("edflib_version:", edflib_version())
#     print("hdr.filetype", hdr.filetype)
#     print("hdr.file_duration / EDFLIB_TIME_DIMENSION", hdr.file_duration / EDFLIB_TIME_DIMENSION)
#     print(hdr.startdate_day, hdr.startdate_month, hdr.startdate_year)
#     print(hdr.recording)
#     print("hdr.datarecords_in_file", hdr.datarecords_in_file)
#     print("hdr.annotations_in_file", hdr.annotations_in_file)

#     array_list = []
#     N = 200
#     for channel in range(hdr.edfsignals):
#         print(channel)
#         print("hdr.signalparam[channel].label",hdr.signalparam[channel].label)
#         print("hdr.signalparam[channel].smp_in_file", hdr.signalparam[channel].smp_in_file)
#         print("hdr.signalparam[channel].smp_in_datarecord / <double>hdr.datarecord_duration) * EDFLIB_TIME_DIMENSION", (hdr.signalparam[channel].smp_in_datarecord / <double>hdr.datarecord_duration) * EDFLIB_TIME_DIMENSION)

#         # print("annot.onset / EDFLIB_TIME_DIMENSION",annot.onset / EDFLIB_TIME_DIMENSION)
#         # print("annot.duration", annot.duration)

#         x = 10 # start reading x seconds from start
#         edfseek(hdl, channel, <long long>(((<double>x) / (<double>hdr.file_duration / <double>EDFLIB_TIME_DIMENSION)) * (<double>hdr.signalparam[channel].smp_in_file)), EDFSEEK_SET)

#         n = N
#         print("data[%d]:" % N)
#         arr = np.zeros(N, dtype='float64')
#         carr = arr
#         n = edfread_physical_samples(hdl, channel, n, <double*>carr.data);
#         #arr = carr.copy() # hmm
#         array_list.append(arr)
#         print(carr)
#     return array_list

if sys.version_info < (3,):
    import codecs

    def u(x):
        return codecs.unicode_escape_decode(x)[0]

    def du(x):
        if isinstance(x, unicode):
            return x.encode("utf-8")
        else:
            return x
else:
    def u(x):
        return x.decode("utf-8", "strict")

    def du(x):
        if isbytestr(x):
            return x
        else:
            return x.encode("utf-8")


def isstr(s):
    try:
        return isinstance(s, basestring)
    except NameError:
        return isinstance(s, str)


def isbytestr(s):
    return isinstance(s, bytes)


class ChannelDoesNotExist(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class WrongInputSize(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)



cdef class CyEdfWriter:
    """
    This provides a simple interface to write EDF, EDF+, and probably is ok with
    BDF and BDF+ files
    Note that edflib.c is encapsulated so there is no direct access to the file
    from here unless I add a raw interface or something

    EDF/BDF+ files are arranged into N signals sampled at rate Fs. The data is
    actually stored in chunks called  "datarecords" which have a file specific size.

    I believe that the way the edflib.c is structured need to first define all the header
    information before writing any samples:

    *  Perhaps should use a flag to signal once samples have started to be written
    to raise an error if try to update the header further.

    """


    cdef edf_hdr_struct hdr

    def __init__(self, file_name, n_channels, file_type=FILETYPE_EDFPLUS):
        """Initialises an EDF file at file_name.
        file_type is one of
            edflib.FILETYPE_EDFPLUS
            edflib.FILETYPE_BDFPLUS
        n_channels is the number of channels without the annotation channel
        """
        self.hdr.handle = -1 # initial invalid vlaue

        self.hdr.handle = open_file_writeonly(file_name, file_type, n_channels)

from datetime import datetime, date

class EdfWriter(object):
    def __exit__(self, exc_type, exc_val, ex_tb):
        self.close()  # cleanup the file

    def __enter__(self):
        return self

    def __del__(self):
        self.close()

    def __init__(self, file_name, n_channels,
                 file_type=FILETYPE_EDFPLUS):
        """Initialises an EDF file at file_name.
        file_type is one of
            edflib.FILETYPE_EDFPLUS
            edflib.FILETYPE_BDFPLUS
        n_channels is the number of channels without the annotation channel

        channel_info should be a
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
        self.path = file_name
        self.file_type = file_type
        self.patient_name = ''
        self.patient_code = ''
        self.technician = ''
        self.equipment = ''
        self.recording_additional = ''
        self.patient_additional = ''
        self.admincode = ''
        self.gender = None
        self.recording_start_time = datetime.now()
        self.birthdate = ''
        self.duration = 1
        self.number_of_annotations = 1 if file_type in [FILETYPE_EDFPLUS, FILETYPE_BDFPLUS] else 0
        self.n_channels = n_channels
        self.channels = []
        self.sample_buffer = []
        for ii in np.arange(self.n_channels):
            if self.file_type == FILETYPE_BDFPLUS or self.file_type == FILETYPE_BDF:
                self.channels.append({'label': 'test_label', 'dimension': 'mV', 'sample_rate': 100,
                                      'physical_max': 1.0, 'physical_min': -1.0,
                                      'digital_max': 8388607,'digital_min': -8388608,
                                      'prefilter': 'pre1', 'transducer': 'trans1'})
            elif self.file_type == FILETYPE_EDFPLUS or self.file_type == FILETYPE_EDF:
                self.channels.append({'label': 'test_label', 'dimension': 'mV', 'sample_rate': 100,
                                      'physical_max': 1.0, 'physical_min': -1.0,
                                      'digital_max': 32767, 'digital_min': -32768,
                                      'prefilter': 'pre1', 'transducer': 'trans1'})

                self.sample_buffer.append([])

        self.handle = open_file_writeonly(self.path, self.file_type, self.n_channels)
        if (self.handle < 0):
            raise IOError(write_errors[self.handle])

    def update_header(self):
        """
        Updates header to edffile struct
        """
        set_technician(self.handle, du(self.technician))
        set_recording_additional(self.handle, du(self.recording_additional))
        set_patientname(self.handle, du(self.patient_name))
        set_patientcode(self.handle, du(self.patient_code))
        set_patient_additional(self.handle, du(self.patient_additional))
        set_equipment(self.handle, du(self.equipment))
        set_admincode(self.handle, du(self.admincode))
        if isinstance(self.gender, int):
            set_gender(self.handle, self.gender)
        elif self.gender == "Male":
            set_gender(self.handle, 0)
        elif self.gender == "Female":
            set_gender(self.handle, 1)

        set_datarecord_duration(self.handle, self.duration)

        set_number_of_annotation_signals(self.handle, self.number_of_annotations)
        set_startdatetime(self.handle, self.recording_start_time.year, self.recording_start_time.month,
                          self.recording_start_time.day, self.recording_start_time.hour,
                          self.recording_start_time.minute, self.recording_start_time.second)
        if isstr(self.birthdate):
            if self.birthdate != '':
                birthday = datetime.strptime(self.birthdate, '%d %b %Y').date()
                set_birthdate(self.handle, birthday.year, birthday.month, birthday.day)
        else:
            set_birthdate(self.handle, self.birthdate.year, self.birthdate.month, self.birthdate.day)
        for i in np.arange(self.n_channels):
            set_samplefrequency(self.handle, i, self.channels[i]['sample_rate'])
            set_physical_maximum(self.handle, i, self.channels[i]['physical_max'])
            set_physical_minimum(self.handle, i, self.channels[i]['physical_min'])
            set_digital_maximum(self.handle, i, self.channels[i]['digital_max'])
            set_digital_minimum(self.handle, i, self.channels[i]['digital_min'])
            set_label(self.handle, i, du(self.channels[i]['label']))
            set_physical_dimension(self.handle, i, du(self.channels[i]['dimension']))
            set_transducer(self.handle, i, du(self.channels[i]['transducer']))
            set_prefilter(self.handle, i, du(self.channels[i]['prefilter']))

    def setHeader(self, fileHeader):
        """
        Sets the file header based upon dictionary-like paramters in @fileHeader
        """
        self.technician = fileHeader["technician"]
        self.recording_additional = fileHeader["recording_additional"]
        self.patient_name = fileHeader["patientname"]
        self.patient_additional = fileHeader["patient_additional"]
        self.patient_code = fileHeader["patientcode"]
        self.equipment = fileHeader["equipment"]
        self.admincode = fileHeader["admincode"]
        self.gender = fileHeader["gender"]
        self.recording_start_time = fileHeader["startdate"]
        self.birthdate = fileHeader["birthdate"]
        self.update_header()

    def setSignalHeader(self, edfsignal, channel_info):
        """
        Sets the parameter for signal edfsignal.

        channel_info should be a dict with
        these values:

            'label' : channel label (string, <= 16 characters, must be unique)
            'dimension' : physical dimension (e.g., mV) (string, <= 8 characters)
            'sample_rate' : sample frequency in hertz (int)
            'physical_max' : maximum physical value (float)
            'physical_min' : minimum physical value (float)
            'digital_max' : maximum digital value (int, -2**15 <= x < 2**15)
            'digital_min' : minimum digital value (int, -2**15 <= x < 2**15)
        """
        if edfsignal < 0 or edfsignal > self.n_channels:
            raise ChannelDoesNotExist(edfsignal)
        self.channels[edfsignal] = channel_info
        self.update_header()

    def setSignalHeaders(self, signalHeaders):
        """
        Sets the parameter for all signals

        Parameters
        ----------
        signalHeaders : array_like
            containing dict with
                'label' : str
                          channel label (string, <= 16 characters, must be unique)
                'dimension' : str
                          physical dimension (e.g., mV) (string, <= 8 characters)
                'sample_rate' : int
                          sample frequency in hertz
                'physical_max' : float
                          maximum physical value
                'physical_min' : float
                         minimum physical value
                'digital_max' : int
                         maximum digital value (-2**15 <= x < 2**15)
                'digital_min' : int
                         minimum digital value (-2**15 <= x < 2**15)
        """
        for edfsignal in np.arange(self.n_channels):
            self.channels[edfsignal] = signalHeaders[edfsignal]
        self.update_header()

    def setTechnician(self, technician):
        """
        Sets the technicians name to `technician`.

        Notes
        -----
        This function is optional and can be called only after opening a file in writemode and before the first sample write action.
        """
        self.technician = technician
        self.update_header()

    def setRecordingAdditional(self, recording_additional):
        """
        Sets the additional recordinginfo

        Notes
        -----
        This function is optional and can be called only after opening a file in writemode and before the first sample write action.
        """
        self.recording_additional = recording_additional
        self.update_header()

    def setPatientName(self, patient_name):
        """
        Sets the patientname to `patient_name`.

        Notes
        -----
        This function is optional and can be called only after opening a file in writemode and before the first sample write action.
        """
        self.patient_name = patient_name
        self.update_header()

    def setPatientCode(self, patient_code):
        """
        Sets the patientcode to `patient_code`.

        Notes
        -----
        This function is optional and can be called only after opening a file in writemode and before the first sample write action.
        """
        self.patient_code = patient_code
        self.update_header()

    def setPatientAdditional(self, patient_additional):
        """
        Sets the additional patientinfo to `patient_additional`.

        Notes
        -----
        This function is optional and can be called only after opening a file in writemode and before the first sample write action.
        """
        self.patient_additional = patient_additional
        self.update_header()

    def setEquipment(self, equipment):
        """
        Sets the name of the param equipment used during the aquisition.
        This function is optional and can be called only after opening a file in writemode and before the first sample write action.

        Parameters
        ----------
        equipment : str
            Describes the measurement equpipment

        """
        self.equipment = equipment
        self.update_header()

    def setAdmincode(self, admincode):
        """
        Sets the admincode.

        This function is optional and can be called only after opening a file in writemode and before the first sample write action.

        Parameters
        ----------
        admincode : str
            admincode which is written into the header

        """
        self.admincode = admincode
        self.update_header()

    def setGender(self, gender):
        """
        Sets the gender.
        This function is optional and can be called only after opening a file in writemode and before the first sample write action.

        Parameters
        ----------
        gender : int
            1 is male, 0 is female
        """
        self.gender = gender
        self.update_header()

    def setDatarecordDuration(self, duration):
        """
        Sets the datarecord duration. The default value is 100000 which is 1 second.
        ATTENTION: the argument "duration" is expressed in units of 10 microSeconds!
        So, if you want to set the datarecord duration to 0.1 second, you must give
        the argument "duration" a value of "10000".
        This function is optional, normally you don't need to change
        the default value. The datarecord duration must be in the range 0.001 to 60  seconds.
        Returns 0 on success, otherwise -1.

        Parameters
        ----------
        duration : integer
            Sets the datarecord duration in units of 10 microSeconds

        Notes
        -----
        This function is NOT REQUIRED but can be called after opening a file in writemode and
        before the first sample write action. This function can be used when you want
        to use a samplerate which is not an integer. For example, if you want to use
        a samplerate of 0.5 Hz, set the samplefrequency to 5 Hz and
        the datarecord duration to 10 seconds. Do not use this function,
        except when absolutely necessary!
        """
        self.duration = duration
        self.update_header()

    def set_number_of_annotation_signals(self, number_of_annotations):
        """
        Sets the number of annotation signals. The default value is 1
        This function is optional and can be called only after opening a file in writemode
        and before the first sample write action
        Normally you don't need to change the default value. Only when the number of annotations
        you want to write is more than the number of seconds of the duration of the recording, you can use
        this function to increase the storage space for annotations
        Minimum is 1, maximum is 64

        Parameters
        ----------
        number_of_annotations : integer
            Sets the number of annotation signals
        """
        number_of_annotations = max((min((int(number_of_annotations), 64)), 1))
        self.number_of_annotations = number_of_annotations
        self.update_header()

    def setStartdatetime(self, recording_start_time):
        """
        Sets the recording start Time

        Parameters
        ----------
        recording_start_time: datetime object
            Sets the recording start Time
        """
        if isinstance(recording_start_time,datetime):
            self.recording_start_time = recording_start_time
        else:
            self.recording_start_time = datetime.strptime(recording_start_time,"%d %b %Y %H:%M:%S")
        self.update_header()

    def setBirthdate(self, birthdate):
        """
        Sets the birthdate.

        Parameters
        ----------
        birthdate: date object from datetime

        Examples
        --------
        >>> import pyedflib
        >>> from datetime import datetime, date
        >>> f = pyedflib.EdfWriter('test.bdf', 1, file_type=pyedflib.FILETYPE_BDFPLUS)
        >>> f.setBirthdate(date(1951, 8, 2))
        >>> f.close()

        Notes
        -----
        This function is optional and can be called only after opening a file in writemode and before the first sample write action.
        """
        self.birthdate = birthdate
        self.update_header()

    def setSamplefrequency(self, edfsignal, samplefrequency):
        """
        Sets the samplefrequency of signal edfsignal.

        Notes
        -----
        This function is required for every signal and can be called only after opening a file in writemode and before the first sample write action.
        """
        if edfsignal < 0 or edfsignal > self.n_channels:
            raise ChannelDoesNotExist(edfsignal)
        self.channels[edfsignal]['sample_rate'] = samplefrequency
        self.update_header()

    def setPhysicalMaximum(self, edfsignal, physical_maximum):
        """
        Sets the physical_maximum of signal edfsignal.

        Parameters
        ----------
        edfsignal: int
            signal number
        physical_maximum: float
            Sets the physical maximum

        Notes
        -----
        This function is required for every signal and can be called only after opening a file in writemode and before the first sample write action.
        """
        if edfsignal < 0 or edfsignal > self.n_channels:
            raise ChannelDoesNotExist(edfsignal)
        self.channels[edfsignal]['physical_max'] = physical_maximum
        self.update_header()

    def setPhysicalMinimum(self, edfsignal, physical_minimum):
        """
        Sets the physical_minimum of signal edfsignal.

        Parameters
        ----------
        edfsignal: int
            signal number
        physical_minimum: float
            Sets the physical minimum

        Notes
        -----
        This function is required for every signal and can be called only after opening a file in writemode and before the first sample write action.
        """
        if (edfsignal < 0 or edfsignal > self.n_channels):
            raise ChannelDoesNotExist(edfsignal)
        self.channels[edfsignal]['physical_min'] = physical_minimum
        self.update_header()

    def setDigitalMaximum(self, edfsignal, digital_maximum):
        """
        Sets the samplefrequency of signal edfsignal.
        Usually, the value 32767 is used for EDF+ and 8388607 for BDF+.

        Parameters
        ----------
        edfsignal : int
            signal number
        digital_maximum : int
            Sets the maximum digital value

        Notes
        -----
        This function is optional and can be called only after opening a file in writemode and before the first sample write action.
        """
        if (edfsignal < 0 or edfsignal > self.n_channels):
            raise ChannelDoesNotExist(edfsignal)
        self.channels[edfsignal]['digital_max'] = digital_maximum
        self.update_header()

    def setDigitalMinimum(self, edfsignal, digital_minimum):
        """
        Sets the minimum digital value of signal edfsignal.
        Usually, the value -32768 is used for EDF+ and -8388608 for BDF+. Usually this will be (-(digital_maximum + 1)).

        Parameters
        ----------
        edfsignal : int
            signal number
        digital_minimum : int
            Sets the minimum digital value

        Notes
        -----
        This function is optional and can be called only after opening a file in writemode and before the first sample write action.
        """
        if (edfsignal < 0 or edfsignal > self.n_channels):
            raise ChannelDoesNotExist(edfsignal)
        self.channels[edfsignal]['digital_min'] = digital_minimum
        self.update_header()

    def setLabel(self, edfsignal, label):
        """
        Sets the label (name) of signal edfsignal ("FP1", "SaO2", etc.).

        Parameters
        ----------
        edfsignal : int
            signal number on which the label should be changed
        label : str
            signal label

        Notes
        -----
        This function is recommended for every signal and can be called only after opening a file in writemode and before the first sample write action.
        """
        if (edfsignal < 0 or edfsignal > self.n_channels):
            raise ChannelDoesNotExist(edfsignal)
        self.channels[edfsignal]['label'] = label
        self.update_header()

    def setPhysicalDimension(self, edfsignal, physical_dimension):
        """
        Sets the physical dimension of signal edfsignal ("uV", "BPM", "mA", "Degr.", etc.)

        :param edfsignal: int
        :param physical_dimension: str

        Notes
        -----
        This function is recommended for every signal and can be called only after opening a file in writemode and before the first sample write action.
        """
        if edfsignal < 0 or edfsignal > self.n_channels:
            raise ChannelDoesNotExist(edfsignal)
        self.channels[edfsignal]['dimension'] = physical_dimension
        self.update_header()

    def setTransducer(self, edfsignal, transducer):
        """
        Sets the transducer of signal edfsignal

        :param edfsignal: int
        :param transducer: str

        Notes
        -----
        This function is optional for every signal and can be called only after opening a file in writemode and before the first sample write action.
        """
        if (edfsignal < 0 or edfsignal > self.n_channels):
            raise ChannelDoesNotExist(edfsignal)
        self.channels[edfsignal]['transducer'] = transducer
        self.update_header()

    def setPrefilter(self, edfsignal, prefilter):
        """
        Sets the prefilter of signal edfsignal ("HP:0.1Hz", "LP:75Hz N:50Hz", etc.)

        :param edfsignal: int
        :param prefilter: str

        Notes
        -----
        This function is optional for every signal and can be called only after opening a file in writemode and before the first sample write action.
        """
        if edfsignal < 0 or edfsignal > self.n_channels:
            raise ChannelDoesNotExist(edfsignal)
        self.channels[edfsignal]['prefilter'] = prefilter
        self.update_header()

    def writePhysicalSamples(self, data):
        """
        Writes n physical samples (uV, mA, Ohm) belonging to one signal where n
        is the samplefrequency of the signal.

        data_vec belonging to one signal. The size must be the samplefrequency of the signal.

        Notes
        -----
        Writes n physical samples (uV, mA, Ohm) from data_vec belonging to one signal where n
        is the samplefrequency of the signal. The physical samples will be converted to digital
        samples using the values of physical maximum, physical minimum, digital maximum and digital
        minimum. The number of samples written is equal to the samplefrequency of the signal.
        Call this function for every signal in the file. The order is important! When there are 4
        signals in the file, the order of calling this function must be: signal 0, signal 1, signal 2,
        signal 3, signal 0, signal 1, signal 2, etc.

        All parameters must be already written into the bdf/edf-file.
        """
        return write_physical_samples(self.handle, data)

    def writeDigitalSamples(self, data):
        """writes int32 data to the file
        need to determine how this is set"""
        return write_digital_samples(self.handle, data)

    def writeDigitalShortSamples(self, data):
        """write int16 data"""
        return write_digital_short_samples(self.handle, data)

    def blockWritePhysicalSamples(self, data):
        """
        Writes physical samples (uV, mA, Ohm)
        must be filled with samples from all signals
        where each signal has n samples which is the samplefrequency of the signal.

        @data must be be an float64 array with shape (nchan, samples_per_datarecord)

        data_vec belonging to one signal. The size must be the samplefrequency of the signal.

        Notes
        -----
        data buf must be filled with samples from all signals, starting with signal 0, 1, 2, etc.
        one block equals one second
        The physical samples will be converted to digital samples using the
        values of physical maximum, physical minimum, digital maximum and digital minimum
        The number of samples written is equal to the sum of the samplefrequencies of all signals
        Size of buf should be equal to or bigger than sizeof(double) multiplied by the sum of the samplefrequencies of all signals
        Returns 0 on success, otherwise -1

        All parameters must be already written into the bdf/edf-file.
        """
        return blockwrite_physical_samples(self.handle, data)

    def blockWriteDigitalSamples(self, data):
        """@data is int32 array
        I think with shape (nchan, num_samples_per_datarecord)"""
        return blockwrite_digital_samples(self.handle, data)

    def blockWriteDigitalShortSamples(self, data):
        """@data is int16 array
        I think with shape (nchan, num_samples_per_datarecord)"""

        return blockwrite_digital_short_samples(self.handle, data)

    def writeSamples(self, data_list, digital = False):
        """
        Writes physical samples (uV, mA, Ohm) from data belonging to all signals
        The physical samples will be converted to digital samples using the values
        of physical maximum, physical minimum, digital maximum and digital minimum.
        if the samplefrequency of all signals are equal, then the data could be
        saved into a matrix with the size (N,signals) If the samplefrequency
        is different, then sample_freq is a vector containing all the different
        samplefrequencys. The data is saved as list. Each list entry contains
        a vector with the data of one signal.

        If digital is True, digital signals (as directly from the ADC) will be expected.
        (e.g. int16 from 0 to 2048)

        All parameters must be already written into the bdf/edf-file.
        """


        if (len(data_list) != len(self.channels)):
            raise WrongInputSize(len(data_list))

        if digital:
            if any([not np.issubdtype(a.dtype, np.integer) for a in data_list]):
                raise TypeError('Digital = True requires all signals in int')


        ind = []
        notAtEnd = True
        for i in np.arange(len(data_list)):
            ind.append(0)

        sampleLength = 0
        sampleRates = np.zeros(len(data_list), dtype=np.int)
        for i in np.arange(len(data_list)):
            sampleRates[i] = self.channels[i]['sample_rate']
            if (np.size(data_list[i]) < ind[i] + self.channels[i]['sample_rate']):
                notAtEnd = False
            sampleLength += self.channels[i]['sample_rate']

        dataOfOneSecond = np.array([], dtype=np.int if digital else None)

        while notAtEnd:
            # dataOfOneSecondInd = 0
            del dataOfOneSecond
            dataOfOneSecond = np.array([], dtype=np.int if digital else None)
            for i in np.arange(len(data_list)):
                # dataOfOneSecond[dataOfOneSecondInd:dataOfOneSecondInd+self.channels[i]['sample_rate']] = data_list[i].ravel()[int(ind[i]):int(ind[i]+self.channels[i]['sample_rate'])]
                dataOfOneSecond = np.append(dataOfOneSecond,data_list[i].ravel()[int(ind[i]):int(ind[i]+sampleRates[i])])
                # self.writePhysicalSamples(data_list[i].ravel()[int(ind[i]):int(ind[i]+self.channels[i]['sample_rate'])])
                ind[i] += sampleRates[i]
                # dataOfOneSecondInd += sampleRates[i]
            if digital:
                self.blockWriteDigitalSamples(dataOfOneSecond)
            else:
                self.blockWritePhysicalSamples(dataOfOneSecond)

            for i in np.arange(len(data_list)):
                if (np.size(data_list[i]) < ind[i] + sampleRates[i]):
                    notAtEnd = False

        # dataOfOneSecondInd = 0
        for i in np.arange(len(data_list)):
            lastSamples = np.zeros(sampleRates[i], dtype=np.int if digital else None)
            lastSampleInd = int(np.max(data_list[i].shape) - ind[i])
            lastSampleInd = int(np.min((lastSampleInd,sampleRates[i])))
            if lastSampleInd > 0:
                lastSamples[:lastSampleInd] = data_list[i].ravel()[-lastSampleInd:]
                # dataOfOneSecond[dataOfOneSecondInd:dataOfOneSecondInd+self.channels[i]['sample_rate']] = lastSamples
                # dataOfOneSecondInd += self.channels[i]['sample_rate']
                if digital:
                    self.writeDigitalSamples(lastSamples)
                else:
                    self.writePhysicalSamples(lastSamples)
        # self.blockWritePhysicalSamples(dataOfOneSecond)

    def writeAnnotation(self, onset_in_seconds, duration_in_seconds, description, str_format='utf-8'):
        """
        Writes an annotation/event to the file
        """
        if str_format == 'utf-8':
            if duration_in_seconds >= 0:
                return write_annotation_utf8(self.handle, np.round(onset_in_seconds*10000).astype(int), np.round(duration_in_seconds*10000).astype(int), du(description))
            else:
                return write_annotation_utf8(self.handle, np.round(onset_in_seconds*10000).astype(int), -1, du(description))
        else:
            if duration_in_seconds >= 0:
                return write_annotation_latin1(self.handle, np.round(onset_in_seconds*10000).astype(int), np.round(duration_in_seconds*10000).astype(int), u(description).encode('latin1'))
            else:
                return write_annotation_latin1(self.handle, np.round(onset_in_seconds*10000).astype(int), -1, u(description).encode('latin1'))

    def close(self):
        """
        Closes the file.
        """
        close_file(self.handle)
        self.handle = -1
