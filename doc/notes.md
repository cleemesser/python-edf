So far
------
- edflib.[ch] compile. Thank you Teunis!
- start doing tests from cpython, can open sample 
- create list of constants in edf.pxi
- use gccxml and xml2cython to get an initial template for _edflib.pxd
  * looks like most functions and structs are wrapped
- got compilation going with direct linkage of edflib.o under windows 7 + VC9
  (see setup-win64.py)


- it is possible to build python 2.7 extensions with setupegg.py develop and MS compiler free release for python2.7  on windows (autodetected!) 2016-05

How to distribute
-----------------
- see https://packaging.python.org/
# binary wheels build
python setup.py bdist_wheel

# upload using twine
- first setup ~/.pypirc correctly

# as of 2018-09-30 still using legacy upload

# test upload
twine upload -r testpypi dist/*

# if looks ok then upload to real pypi
twine upload -r legacypypi dist/*

Then to test (example for 0.84.1.alpha9 version uploaded to test.pypi.org)
```
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/pypi edflib==0.84.1a9
```
0.84.0
- does not work on windows, can't find numpy includes (my ubuntu has system numpy instaled?)


### Newer versions of how to distribute source dist. sdist

2022
https://stackoverflow.com/questions/19919905/how-to-bootstrap-numpy-installation-in-setup-py

```
from setuptools import dist
dist.Distribution().fetch_build_eggs(['Cython>=0.15.1', 'numpy>=1.10'])
```

To do
-----
- start on low-level interface to functions
- probably will start with a single buffer, allocated and reallocated as needed to pass the data in as physical measurements via numpy array
- will leave open lower level interface to underlying data
- accessors for patient information
