# -*- encoding: utf-8 -*-
# %%
"""
A memory-mapped file is created by the mmap constructor, which is different on Unix and on Windows. In either case you must provide a file descriptor for a file opened for update. If you wish to map an existing Python file object, use its fileno() method to obtain the correct value for the fileno parameter. Otherwise, you can open the file using the os.open() function, which returns a file descriptor directly (the file still needs to be closed when done).
"""
# the header is supposed to use only ascii; 32..126
import mmap
import re
import datetime
import datetime as dt
import glob
import dateutil.parser

# import pyedflib
from typing import Union, Tuple

### constants

DEFAULT_BIRTHDATE = dt.date(1990, 1, 1)


def convert_except_yy(s):
    if s == "yy":
        return s  # return none or unknown?
    else:
        return int(s)


def edf_year_2k(yr: int) -> int:
    """function to guess how to interpret a two digit year
    see EDF+ 2.1.3 advice to use 1985 the pivot year
    https://www.edfplus.info/specs/edfplus.html#additionalspecs

    The 'startdate' and 'starttime' fields in the header should contain only
    characters 0-9, and the period (.) as a separator, for example "02.08.51". In
    the 'startdate', use 1985 as a clipping date in order to avoid the Y2K
    problem. So, the years 1985-1999 must be represented by yy=85-99 and the
    years 2000-2084 by yy=00-84. After 2084, yy must be 'yy' and only item 4 of
    this paragraph defines the date.

    """
    if yr <= 85:
        return 2000 + yr
    else:
        return 1900 + yr


# %%


def edf_longdate_fmt(date: dt.date):
    "convert a datetime.date into the format needed for birthdates, startdate"
    return date.strftime("%d-%b-%Y").upper()


def _none_to_X(s):
    """use the anonymous character 'X' if a field is not defined/empty"""
    if not s:
        return "X"
    else:
        return s


def date_str_or_dt_to_edfdate(s) -> Tuple[str, dt.date]:
    if s:
        if type(s) == str:
            date_dt = dateutil.parser.parse(s)
            date_s = date_dt.strftime("%d-%b-%Y").upper()
        if type(s) == dt.date:
            date_dt = s
            date_s = s.strftime("%d-%b-%Y").upper()
    else:
        date_s = ""  # datetime.date or ''
        date_dt = None

    return date_s, date_dt


class PatientId:
    hoi = (8, 88)

    def __init__(
        self,
        patientcode: str = "",
        sex: str = "",
        birthdate: Union[str, datetime.date] = "",
        name: str = "",
        barr=None,
    ):
        """birthdate if a string should be in dd-MMM-yyyy format though if parsible, it
        will be fixed

        """
        # without an ending these are the forward-facing representations
        self.patientcode = patientcode
        self.sex = sex

        if birthdate:
            if type(birthdate) == str:
                self.birth_dt = dateutil.parser.parse(birthdate)
                self.birthdate = self.birth_dt.strftime("%d-%b-%Y").upper()
            if type(birthdate) == dt.date:
                self.birth_dt = birthdate
                self.birthdate = birthdate.strftime("%d-%b-%Y").upper()
        else:
            self.birthdate = ""  # datetime.date or ''
            self.birth_dt = None

        self.name = name

        self.workingarr = bytearray(" " * 80, "ascii")

    def read_from_bytearray(self, barr):

        assert len(barr) == 80
        self.barr = barr
        self.workingarr[:] = barr
        (
            self.patientcode_r,
            self.sex_r,
            self.birthdate_r,
            self.name_r,
        ) = barr.decode().split()
        self.name = self.name_r.replace("_", " ")
        self.patientcode = "" if self.patientcode_r == "X" else self.patientcode_r
        self.sex = "" if self.sex_r == "X" else self.sex_r
        self.birthdate = "" if self.birthdate_r == "X" else self.birthdate_r

    def write_to_bytearray(self, barr):
        rawpt = [
            self.patientcode,
            self.sex,
            self.birthdate,
            self.name.replace(" ", "_"),
        ]
        rawpt = map(lambda xx: xx if xx else "X", rawpt)  # _none_to_X
        full_str = " ".join(rawpt)
        if len(full_str) > 80:
            print("warning, patient identfication will be truncated")
            print(full_str[:80])
        self.workingarr[:] = full_str.encode("ascii")
        barr[:] = self.workingarr

        return barr

    def write_to_mmap_array(self, mmarr):
        rawpt = [
            self.patientcode,
            self.sex,
            self.birthdate,
            self.name.replace(" ", "_"),
        ]
        rawpt = map(lambda xx: xx if xx else "X", rawpt)  # _none_to_X
        full_str = " ".join(rawpt)
        if len(full_str) > 80:
            print("warning, patient identfication will be truncated")
            print(full_str[:80])
            full_str = full_str[:80]

        self.workingarr[: len(full_str)] = full_str.encode("ascii")
        self.workingarr[len(full_str) :] = b" " * (len(self.workingarr) - len(full_str))
        # s0 = PatientId.hoi[0]
        # s1 = s0 + l
        mmarr[PatientId.hoi[0] : PatientId.hoi[1]] = self.workingarr

        return self.workingarr

    def __repr__(self):
        return (
            f"PatientId(patientcode={self.patientcode},"
            f"sex={self.sex},birthdate={self.birthdate},name={self.name})"
        )


class RecordId:
    """local recording identfication field https://www.edfplus.info/specs/edfplus.html#additionalspecs
        4. The 'local recording identification' field must start with the subfields (subfields do not contain, but are separated by, spaces):
        - The text 'Startdate'.
        - The startdate itself in dd-MMM-yyyy format using the English 3-character abbreviations of the month in capitals.
        - The hospital administration code of the investigation, i.e. EEG number or PSG number.
        - A code specifying the responsible investigator or technician.
        - A code specifying the used equipment.
    Any space inside any of these codes must be replaced by a different character, for instance
    an underscore. The 'local recording identification' field could contain:
     Startdate 02-MAR-2002 PSG-1234/2002 NN Telemetry03.
     Subfields whose contents are unknown, not applicable or must be made anonymous are replaced by a
     single character 'X'. So, if everything is unknown then the 'local recording identification' field
     would start with: 'Startdate X X X X'. Additional subfields may follow the ones described here."""

    hoi = (88, 168)

    def __init__(
        self,
        startdate: Union[dt.date, str] = "",
        admincode: str = "",
        technician: str = "",
        equipment: str = "",
    ):

        self.startdate, self.startdate_dt = date_str_or_dt_to_edfdate(startdate)
        self.admincode = admincode
        self.technician = technician
        self.equipment = equipment
        self.workingarr = bytearray(" " * 80, "ascii")

    def read_from_bytearray(self, barr):
        assert len(barr) == 80
        self.workingarr[:] = barr
        (
            starttext_r,
            self.startdate_r,
            self.admincode_r,
            self.technician_r,
            self.equipment_r,
        ) = barr.decode().split()
        self.startdate_r = "" if self.startdate_r == "X" else self.startdate_r
        self.admincode_r = "" if self.admincode_r == "X" else self.admincode_r
        self.technician_r = "" if self.technician_r == "X" else self.technician_r
        self.technician_r = "" if self.technician_r == "X" else self.technician_r

        self.startdate, self.startdate_dt = date_str_or_dt_to_edfdate(self.startdate_r)
        self.admincode = self.admincode_r.replace("_", " ")
        self.technician = self.technician_r.replace("_", " ")
        self.equipment = self.equipment_r.replace("_", " ")

    def write_to_mmap_array(self, mmarr):
        raw = [
            "Startdate",
            self.startdate,
            self.admincode.replace(" ", "_"),
            self.technician.replace(" ", "_"),
            self.equipment.replace(" ", "_"),
        ]
        raw = map(lambda xx: xx if xx else "X", raw)  # _none_to_X
        full_str = " ".join(raw)
        if len(full_str) > 80:
            print("warning, record identfication will be truncated")
            print(full_str[:80])
            full_str = full_str[:80]  # truncate to hard coded length of 80

        self.workingarr[: len(full_str)] = full_str.encode("ascii")
        self.workingarr[len(full_str) :] = b" " * (len(self.workingarr) - len(full_str))

        mmarr[RecordId.hoi[0] : RecordId.hoi[1]] = self.workingarr

        return self.workingarr

    def __repr__(self):
        return (
            f"RecordId(startdate={self.startdate},"
            f"admincode={self.admincode},"
            f"technician={self.technician},equiment={self.equipment})"
        )


# %%
class EdfHeader:
    """questions: EDF -> EDF+ handling
    start with just the patient information and recording PHI
    """

    regions = {  # half open intervals
        "version": (0, 8),
        "patient_id": (8, 88),
        "recording_id": (88, 168),
        "startdate8": (168, 176),  # 8 byte ascii date dd.mm.yy
        "starttime8": (176, 184),  # 8 byte ascii time hh.mm.ss
        "head_nbytes": (184, 192),
        "reserved_file_type": (192, 236),  # EDF+C  or EDF+D maybe EDF or BDF+ ?
        "n_data_recs": (236, 244),
        "duration_data_rec_sec": (244, 252),
    }
    default_length = 1024 * 16

    def __init__(self, file_name, mode="r+b"):
        # r+b reading and writing in binary mode
        # rb reading only
        # don't use 'w' modes unless you want to truncate files if they already exist
        with open(file_name, mode) as fp:
            # memory map the whole file I guess could limit to a few kb
            # mm = mmap(fp.fileno(), 0)
            mm = mmap.mmap(
                fp.fileno(), EdfHeader.default_length, access=mmap.ACCESS_WRITE
            )
            self.fp = fp
            self.mm = mm
            self.file_name = file_name

            regs = EdfHeader.regions
            self.version = mm[:8].decode()
            self.pt_id = PatientId()
            self.pt_id.read_from_bytearray(
                mm[regs["patient_id"][0] : regs["patient_id"][1]]
            )
            self.rec_id = RecordId()
            self.rec_id.read_from_bytearray(
                mm[regs["recording_id"][0] : regs["recording_id"][1]]
            )
            self.startdate8 = mm[regs["startdate8"][0] : regs["startdate8"][1]].decode()
            self.starttime8 = mm[regs["starttime8"][0] : regs["starttime8"][1]].decode()
            nbytes_str = mm[regs["head_nbytes"][0] : regs["head_nbytes"][1]].decode()
            self.hdr_num_bytes = int(nbytes_str)
            if self.hdr_num_bytes > EdfHeader.default_length:
                print("should re-open mmap to get whole header -- not yet implemented")

            self.n_data_records = int(
                mm[regs["n_data_recs"][0] : regs["n_data_recs"][1]].decode()
            )
            self.data_record_len_sec = float(
                mm[
                    regs["duration_data_rec_sec"][0] : regs["duration_data_rec_sec"][1]
                ].decode()
            )

    def record_duration_sec(self):
        return self.n_data_recs * self.data_record_len_sec

    def save_header(self, header_file_name=None):
        if not header_file_name:
            fn = self.file_name + ".hdr"
        else:
            fn = header_file_name
        with open(fn, "w+b") as wf:
            print(wf.write(self.mm[: self.hdr_num_bytes]))

    def deindentify(self):
        orig_birthdate = dateutil.parser.parse(self.pt_id.birthdate).date()
        delta_birthday = orig_birthdate - DEFAULT_BIRTHDATE
        self.pt_id.patientcode = ""
        self.pt_id.birthdate = edf_longdate_fmt(DEFAULT_BIRTHDATE)
        self.pt_id.name = "14,Subject"  # get rid of name
        self.pt_id.write_to_mmap_array(self.mm)
        # record
        orig_startdate = dateutil.parser.parse(self.rec_id.startdate).date()
        new_startdate_dt = orig_startdate - delta_birthday
        self.rec_id.startdate = edf_longdate_fmt(new_startdate_dt)
        orig_rec_id_admincode = self.rec_id.admincode
        self.rec_id.admincode = ""
        self.rec_id.technician = ""
        # leave equipment unchanged
        self.rec_id.write_to_mmap_array(self.mm)  # write the record_id info
        if new_startdate_dt.year < 2085 and new_startdate_dt.year >= 1985:
            self.startdate8 = new_startdate_dt.strftime("%d.%m.%y")
        else:
            self.startdate8 = new_startdate_dt.strftime("%d.%m.yy")
        self.mm[
            EdfHeader.regions["startdate8"][0] : EdfHeader.regions["startdate8"][1]
        ] = self.startdate8.encode("ascii")
        self.mm.flush()
        self.orig_birthdate = orig_birthdate
        self.delta_birthday = delta_birthday
        self.orig_startdate = orig_startdate

    def startdatetime(self):
        hour, minute, sec = [int(xx) for xx in self.starttime8.split(".")]
        date = dateutil.parser.parse(self.rec_id.startdate)
        return dt.datetime(date.year, date.month, date.day, hour, minute, sec)


# eh = EdfHeader(fn)
# eh.save_header()

## start de-identifying
# patient, time shift
if False:
    orig_birthdate = dateutil.parser.parse(eh.pt_id.birthdate).date()
    delta_birthday = orig_birthdate - DEFAULT_BIRTHDATE
    eh.pt_id.patientcode = ""
    eh.pt_id.birthdate = edf_longdate_fmt(DEFAULT_BIRTHDATE)
    eh.pt_id.name = "14,Subject"  # get rid of name
    eh.pt_id.write_to_mmap_array(eh.mm)
    # record
    orig_startdate = dateutil.parser.parse(eh.rec_id.startdate).date()
    new_startdate_dt = orig_startdate - delta_birthday
    eh.rec_id.startdate = edf_longdate_fmt(new_startdate_dt)
    orig_rec_id_admincode = eh.rec_id.admincode
    eh.rec_id.admincode = ""
    eh.rec_id.technician = ""
    # leave equipment unchanged
    eh.rec_id.write_to_mmap_array(eh.mm)  # write the record_id info
    if new_startdate_dt.year < 2085 and new_startdate_dt.year >= 1985:
        eh.startdate8 = new_startdate_dt.strftime("%d.%m.%y")
    else:
        eh.startdate8 = new_startdate_dt.strftime("%d.%m.yy")
    eh.mm[
        EdfHeader.regions["startdate8"][0] : EdfHeader.regions["startdate8"][1]
    ] = eh.startdate8.encode("ascii")
    eh.mm.flush()
# code end bookmark

# create list of file_name, starttime, sort it and save that (original and last)

# EDF: the first 256 bytes The first 256 bytes of the header record specify the version number of this format, local patient and recording identification, time information about the recording, the number of data records and finally the number of signals (ns) in each data record.
# Then for each signal another 256 bytes follow in the header record, each specifying the type of signal (e.g. EEG, body temperature, etc.), amplitude calibration and the number of samples in each data record (from which the sampling frequency can be derived since the duration of a data record is also known). In this way, the format allows for different gains and sampling frequencies for each signal. The header record contains 256 + (ns * 256) bytes. Figure 1 shows its detailed format.

# The information in the ASCII strings must be left-justified and filled out with spaces. Midnight time is 00:00:00. The duration of each data record is recommended to be a whole number of seconds and its size (number of bytes) is recommended not to exceed 61440. Only if a 1s data record exceeds this size limit, the duration is recommended to be smaller than 1s (e.g. 0.01).

# HEADER RECORD

# 8 ascii version of this data format (0)
# 80 ascii local patient identification
# 80 ascii local recording identification
# 8 ascii startdate of recording (dd.mm.yy)
# 8 ascii starttime of recording (hh.mm.ss)
# 8 ascii number of bytes in header record
# 44 ascii reserved (specific to EDF not EDF+)
# 8 ascii number of data records (-1 if unknown)
# 8 ascii duration of a data record, in seconds
# 4 ascii number of signals (ns) in data record
# ns * 16 ascii ns * label (e.g. EEG FpzCz or Body temp)
# ns * 80 ascii ns * transducer type (e.g. AgAgCI electrode)
# ns * 8 ascii ns * physical dimension(e.g. uV or degree C)
# ns * 8 ascii ns * physical minimum (e.g. -500 or 34)
# ns * 8 ascii ns * physical maximum (e.g. 500 or 40)
# ns * 8 ascii ns * digital minimum (e.g. -2048)
# ns * 8 ascii ns * digital maximum (e.g. 2047)
# ns * 80 ascii ns * prefiltering (e.g. HP:0.1Hz LP:75Hz)
# ns * 8 ascii ns * nr of samples in each data record
# ns * 32 ascii ns * reserved

# https://www.edfplus.info/specs/edfplus.html#additionalspecs
#
# 2.1.3. Additional specifications in EDF+
# 1. In the header, use only printable US-ASCII characters with byte values 32..126.
#
# 2. The 'startdate' and 'starttime' fields in the header should contain only
# characters 0-9, and the period (.) as a separator, for example "02.08.51". In
# the 'startdate', use 1985 as a clipping date in order to avoid the Y2K
# problem. So, the years 1985-1999 must be represented by yy=85-99 and the years
# 2000-2084 by yy=00-84. After 2084, yy must be 'yy' and only item 4 of this
# paragraph defines the date.
#
# 3. The 'local patient identification' field must start with the subfields
# (subfields do not contain, but are separated by, spaces):
# - the code by which the patient is known in the hospital administration.
# - sex (English, so F or M). # or N for non-binary?
# - birthdate in dd-MMM-yyyy format using the English 3-character abbreviations
#   of the month in capitals. 02-AUG-1951 is OK, while 2-AUG-1951 is not.
# - the patients name.
# Any space inside the hospital code or the name of the patient must be replaced
# by a different character, for instance an underscore. For instance, the 'local
# patient identification' field could start with: MCH-0234567 F 02-MAY-1951
# Haagse_Harry. Subfields whose contents are unknown, not applicable or must be
# made anonymous are replaced by a single character 'X'. So, if everything is
# unknown then the 'local patient identification' field would start with: 'X X X
# X'. Additional subfields may follow the ones described here.

# 4. The 'local recording identification' field must start with the subfields
# (subfields do not contain, but are separated by, spaces):
# - The text 'Startdate'.
# - The startdate itself in dd-MMM-yyyy format using the English 3-character
#   abbreviations of the month in capitals.
# - The hospital administration code of the investigation, i.e. EEG number or PSG number.
# - A code specifying the responsible investigator or technician.
# - A code specifying the used equipment.
# Any space inside any of these codes must be replaced by a different character,
# for instance an underscore. The 'local recording identification' field could
# contain: Startdate 02-MAR-2002 PSG-1234/2002 NN Telemetry03. Subfields whose
# contents are unknown, not applicable or must be made anonymous are replaced by
# a single character 'X'. So, if everything is unknown then the 'local recording
# identification' field would start with: 'Startdate X X X X'. Additional
# subfields may follow the ones described here.
#
# 5. 'Digital maximum' must be larger than 'Digital minimum'. In case of a
# negative amplifier gain the corresponding 'Physical maximum' is smaller than
# the 'Physical minimum'. Check item 9 on how to apply the 'negativity upward'
# rule in Clinical Neurophysiology to the physical ordinary signal. 'Physical
# maximum' must differ from 'Physical minimum'. In case of uncalibrated signals,
# physical dimension is left empty (that is 8 spaces), while 'Physical maximum'
# and 'Physical minimum' must still contain different values (this is to avoid
# 'division by 0' errors by some viewers).
#
# 6.  Never use any digit grouping symbol in numbers. Never use a comma "," for a
# for a decimal separator. When a decimal separator is required, use a dot (".").
#
# 7. The ordinary signal samples (2-byte two's complement integers) must be
# stored in 'little-endian' format, that is the least significant byte
# first. This is the default format in PC applications.

# 8. The 'starttime' should be local time at the patients location when the
# recording was started.

# 9. Use the standard texts and polarity rules at
# http://www.edfplus.info/specs/edftexts.html. These standard texts may in the
# future be extended with further texts, a.o. for Sleep scorings, ENG and various
# evoked potentials.
#
# 10. The 'number of data records' can only be -1 during recording. As soon as
# the file is closed, the correct number is known and must be entered.
#
# 11. If filters (such as HighPass, LowPass or Notch) were applied to the
# ordinary signals then, preferably automatically, specify them like "HP:0.1Hz
# LP:75Hz N:50Hz" in the "prefiltering" field of the header. If the file contains
# an analysis result, the prefiltering field should mention the relevant analysis parameters.
#
# 12. The "transducertype" field should specify the applied sensor, such as
# "AgAgCl electrode" or "thermistor".

# %%
if __name__ == "__main__":
    from pathlib import Path
    import shutil

    file_list = glob.glob("*.edf")
    print(file_list)

    # copystat so that files auto-sort
    # for fn in file_list:
    #     eeg_rptkey = fn[:-9]

    #     eeg_path = Path(eeg_rptkey + ".eeg")
    #     print(eeg_rptkey, str(eeg_path), eeg_path.exists())
    #     shutil.copystat(eeg_path, fn)
    #     backpath = Path(fn + ".backup")
    #     shutil.copystat(eeg_path, backpath)
    # make backups if they don't exist
    for fn in file_list:
        fpath = Path(fn)
        backpath = Path(fn + ".backup")
        if backpath.exists():
            print(f"backup already exists for {fpath}")
        else:
            shutil.copy2(fpath, backpath)
            # shutil.copystat(fpath, backpath)
    for fn in file_list:
        eh = EdfHeader(fn)
        if Path(fn + ".hdr").exists():
            print("header already written")
        else:
            eh.save_header()
        eh.deindentify()
