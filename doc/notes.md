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

### new pep 517 to create builds of sdist and wheel 
pip install build
python -m build

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



### Poetry thoughts

https://stackoverflow.com/questions/63679315/how-to-use-cython-with-poetry

[tool.poetry]
...
build = 'build.py'

[build-system]
requires = ["poetry>=0.12", "cython"]
build-backend = "poetry.masonry.api"

```
import os

# See if Cython is installed
try:
    from Cython.Build import cythonize
# Do nothing if Cython is not available
except ImportError:
    # Got to provide this function. Otherwise, poetry will fail
    def build(setup_kwargs):
        pass
# Cython is installed. Compile
else:
    from setuptools import Extension
    from setuptools.dist import Distribution
    from distutils.command.build_ext import build_ext

    # This function will be executed in setup.py:
    def build(setup_kwargs):
        # The file you want to compile
        extensions = [
            "mylibrary/myfile.py"
        ]

        # gcc arguments hack: enable optimizations
        os.environ['CFLAGS'] = '-O3'

        # Build
        setup_kwargs.update({
            'ext_modules': cythonize(
                extensions,
                language_level=3,
                compiler_directives={'linetrace': True},
            ),
            'cmdclass': {'build_ext': build_ext}
        })
```
