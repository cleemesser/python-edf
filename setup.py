import setuptools

# from distutils.core import setup
# from distutils.extension import Extension
from setuptools import setup
from setuptools import Extension


# preload numpy to find headers
import numpy
# try to rely upon pyproject.toml to specify these requirements


import sys

if sys.platform in ["win32", "win64"]:
    # could just import numpy and use that as base library
    include_dirs = ["src", numpy.get_include()]
    defines = [
        ("_CRT_SECURE_NO_WARNINGS", None),
        ("_LARGEFILE64_SOURCE", None),
        ("_LARGEFILE_SOURCE", None),
    ]
else:  # 'linux' or 'darwin'
    defines = [("_LARGEFILE64_SOURCE", None), ("_LARGEFILE_SOURCE", None)]
    include_dirs = ["src", "edflib", numpy.get_include()]

ext_modules_edflib = Extension(
    "edflib._edflib",  # name of module
    ["edflib/_edflib.c", "src/edflib.c"],  # source files
    library_dirs=["src"],  # where to find any files
    include_dirs=include_dirs,
    define_macros=defines + [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    # extra_compile_args = ['-O2'  ],
    # extra_compile_args = ['-g'],
    # libraries=['m']
    # extra_link_args =
    # export_symbols  #only useful on windows
    # depends =
)


setup(
    ext_modules=[ext_modules_edflib],
)
