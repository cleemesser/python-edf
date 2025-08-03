This directory contains code to wrap Teunis van Beelen's edflib for python.

It provides access to EDF files, the european data format---commonly used for EEG and other biosignal recordings.

python-edf/
   src/  -> holds the a version of edflib from Teunis's web site
   edflib/ -> holds the python/cython code to wrap edflib
   tests/  -> tests
   examples/ -> example code and short samples

Almost all of the low-level C functions in Teunis's edflib are wrapped in edflib._edflib which is created in cython.
I have started creating more pythonic wrappers.

License
-------
This code is licensed under the same BSD-style license that Teunis released
edflib under and with the same disclaimer. (See src/edflib.c and README-edflib.txt)

Authors/Contributors
--------------------
 * Chris Lee-Messer
 * Sharif Olorin <sio@tesser.org>
 * simondub
 * backports from https://github.com/holgern/pyedflib

Status
------

This is currently "research quality" code. I initially developed it for my
limited purposes to read a few dozen EEGs for a research project. It is inching
towards respectability as it is being updated as we have project that needs it to process
through tens of thousands of edf files.

It still needs more tests and refactoring to make a
real pythonic api before heading to towards a polished package.

I am currently updating edfwriter for 0.8 as I will be needing to use this functionality again.

edfreader - now has tests - needs more
edfwriter likely needs re-writing

I continue to make it available in the hopes that it may be useful for others. As
I need to use it, I may continue to improve and update it, but I can make no
promises.

Installation
------------
To install from pypi::
  pip install edflib

Many binary wheels are available for mac, windows and linux so you may not need a compiler to get this working now.

If you have trouble or want to work on the code, the most reliable way to
install edflib currently is to download the source (or git clone it).  After
unpacking the source, from the command line change to the directory::

  python -m pip install .

Or, if you are doing development, you can do::

  python -m pip install --editable .

This requires a working C compiler on your machine as well as the other build requirements such as cython, setuptools and numpy.


python 3 compatibility
----------------------
The package is now testsed to be compatible with python 3.9+ (as of 0.86). It is likely to work with early versions of python 3.5-3.7 and might be recompilable with python 2.7.

The distinction between bytes and strings is now clear. For clarity all the
cython and C code uses bytes only. The python code deals with decoding and
encoding to either ascii or UTF-8 (for annotations) as described in the spec. In
addition, I will accept UTF-8 on reading though it is outside of spec.

Functions and properties with an 'underscore b' (_b) deal with bytes
representation, while unadorned python functions return native python strings or
numbers.

The goal is such that one can always get full access to the raw C functions and
bytes from python, but provide pleasant to use python interfaces via the reader
and writer classes.

Related Projects
----------------
* `pyedflib is a fork of this project with some nice work and documentation <https://github.com/holgern/pyedflib>`_.
* Robert Oostenveld wrote `bids-standard/pyedf <https://github.com/bids-standard/pyedf>`_, which is a pure python implementation of the standard.
* Teuniz wrote his own python library as well at https://gitlab.com/Teuniz/EDFlib-Python

Change list
-----------
- 2024-12-16 0.86 series with switch to memory views, numpy 2.0 compatibilty + packaging
           This version passes tests but with the switch is more a beta

- 2020-05-11 0.82 fix missing edf.pxi file in MANIFEST.in
- 2020-05-11 0.81 transition to github given sunsetting of mercurial support on bithbucket
- 2018-10-08 created mirror of code on github at https://github.com/cleemesser/python-edf
- 2018-10-08 added wraps for writing shorts, bump edflib version to 116
- 2018-02-15 noted that edflib.h not included in source package added to extension file list for 0.74
- 2017-03-22 added bitbucket-piplines.yml and got integration tests running
- 2017-03-22 update properties to modern (python 3) syntax in _edflib. Make distinction clear. Add tests.
- 2017-03 tweaks to api, python 3 working: will try for dual compatible code python 2.7 + python 3.5+ support
- 2015-06 update to edflib 1.11

packaging
---------

Install/Packing Status:

  pip install edflib  # works to install edflib 0.84.1 from source distribution

- windows install worked

To upload source dist to pypi::

  python -m build
  twine  check <package or wheel paths>    # make sure the text renders
  twine upload  <package or wheel paths>   # upload source dist

Wheels are generated on github, via .github/workflows/build_wheels.yml, but need
to be manually uploaded at this point.

To source distribution upload to test pypi::

  twine upload --verbose --repository testpypi <package or wheel paths>

To test the upload to test.pypi::

   pip install --extra-index-url https://test.pypi.org/simple/ --no-deps edflib


Todo:
-----
::
   - [ ] fix examples to be compatible with changes in api
   - [x] basic tests with py.test
   - [ ] test opening two files at once
   - [/] test, tests, tests !!!
   - [x] inital port to python 3 (tested with 3.5+)
   - [ ] add new functions from version 1.10 of edflibX
   - [x] 0.86 update cython interface to use typed memory views. This will be required for cython 3.0
   - [ ] set up continuous build/integration if possible -
         - [x] done on bitbucket for py 3.5 but not yet for github
         - [/] 0.89.2 targetting cibuildwheel
   - [x] incorporate edflib code for utf-8 and short (int16) vs int (int32) digital writes
   - [ ] test edflib code for utf-8 and short (int16) vs int (int32) digital writes
   - [x] create mirror on github
   - [/] investigate manylinux solution to wheels. [PEP 513](https://www.python.org/dev/peps/pep-0513/) and
   - [x] fix python packaging problems so that pip installs work again
         - progress: as of 0.84 have sdist installs working on linux
         - as of 0.86 have pip install builds working on linux, mac, windows
   - [x] added numpy 2.0.x compat with 0.86.x
