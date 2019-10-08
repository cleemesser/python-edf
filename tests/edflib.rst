
Important on EDF from teuniz
----------------------------
source: https://www.teuniz.net/edflib/ or see README
In EDF, the sensitivity (e.g. uV/bit) and offset are stored using four parameters:
digital maximum and minimum, and physical maximum and minimum.
Here, digital means the raw data coming from a sensor or ADC. Physical means the units like uV.
The sensitivity in units/bit is calculated as follows:

units per bit = (physical max - physical min) / (digital max - digital min)

The digital offset is calculated as follows:

offset = (physical max / units per bit) - digital max

For a better explanation about the relation between digital data and physical data, read the document Coding Schemes Used with Data Converters.

note: An EDF file usually contains multiple so-called datarecords. One datarecord usually has a duration of one second (this is the default but it is not mandatory!).
In that case a file with a duration of five minutes contains 300 datarecords. The duration of a datarecord can be freely choosen but, if possible, use values from
0.1 to 1 second for easier handling. Just make sure that the total size of one datarecord, expressed in bytes, does not exceed 10MByte (15MBytes for BDF(+)).

The recommendation of a maximum datarecordsize of 61440 bytes in the EDF and EDF+ specification was usefull in the time people were still using DOS as their main operating system.
Using DOS and fast (near) pointers (16-bit pointers), the maximum allocatable block of memory was 64KByte.
This is not a concern anymore so the maximum datarecord size now is limited to 10MByte for EDF(+) and 15MByte for BDF(+).
This helps to accommodate for higher samplingrates used by modern, fast Analog to Digital Converters.

EDF header character encoding: The EDF specification says that only ASCII characters are allowed.
EDFlib will automatically convert characters with accents, umlauts, tilde, etc. to their "normal" equivalent without the accent/umlaut/tilde/etc.

The description/name of an EDF+ annotation on the other hand, is encoded in UTF-8.
