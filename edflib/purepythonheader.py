from __future__ import print_function, division, unicode_literals, absolute_import

# from url = http://www.edfplus.info/specs/edf.html
"""
HEADER RECORD (we suggest to also adopt the 12 simple additional EDF+ specs)
8 ascii : version of this data format (0) 
80 ascii : local patient identification (mind item 3 of the additional EDF+ specs)
80 ascii : local recording identification (mind item 4 of the additional EDF+ specs)
8 ascii : startdate of recording (dd.mm.yy) (mind item 2 of the additional EDF+ specs)
8 ascii : starttime of recording (hh.mm.ss) 
8 ascii : number of bytes in header record 
44 ascii : reserved 
8 ascii : number of data records (-1 if unknown, obey item 10 of the additional EDF+ specs) 
8 ascii : duration of a data record, in seconds 
4 ascii : number of signals (ns) in data record 
ns * 16 ascii : ns * label (e.g. EEG Fpz-Cz or Body temp) (mind item 9 of the additional EDF+ specs)
ns * 80 ascii : ns * transducer type (e.g. AgAgCl electrode) 
ns * 8 ascii : ns * physical dimension (e.g. uV or degreeC) 
ns * 8 ascii : ns * physical minimum (e.g. -500 or 34) 
ns * 8 ascii : ns * physical maximum (e.g. 500 or 40) 
ns * 8 ascii : ns * digital minimum (e.g. -2048) 
ns * 8 ascii : ns * digital maximum (e.g. 2047) 
ns * 80 ascii : ns * prefiltering (e.g. HP:0.1Hz LP:75Hz) 
ns * 8 ascii : ns * nr of samples in each data record 
ns * 32 ascii : ns * reserved

DATA RECORD 
nr of samples[1] * integer : first signal in the data record 
nr of samples[2] * integer : second signal 
.. 
.. 
nr of samples[ns] * integer : last signal 
"""


class EdfHeader:
    EDF_FILE_MAGIC = b"0       "  # 8 byte start of valid edf file

    def __init__(self, file_name_or_obj, mode="rb"):
        if isinstance(file_name_or_obj, str):
            self.fp = open(file_name_or_obj, mode=mode)
        else:
            self.fp = file_name_or_obj

    def has_edf_file_magic(self):
        self.fp.seek(0)
        return self.fp.read(8) == EDF_FILE_MAGIC

    def read_raw_header_b(self):
        fp = self.fp
        rawh = {}
        fp.seek(8, 0)  # go past first 8 bytes

        rawh["local_patient_identification"] = fp.read(80)
        rawh["local_recording_identification"] = fp.read(80)
        rawh["startdate_of_recording"] = fp.read(
            8
        )  # dd.mm.yy (1985 is clipping date) ug!
        rawh["starttime_of_recording"] = fp.read(8)
        rawh["number_of_bytes_in_header_record"] = fp.read(8)
        rawh["reserved"] = fp.read(44)
        rawh["number_of_data_records"] = fp.read(8)
        rawh["duration_of_dta_record_sec"] = fp.read(8)
        rawh["number_of_signals_in_data_record"] = fp.read(4)  # 4 ascii

        return rawh


if __name__:
    import sys

    if len(sys.argv) == 2:
        eh = EdfHeader(sys.argv[1])
        raw = eh.read_raw_header_b()
