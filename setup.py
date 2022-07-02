import setuptools

# from distutils.core import setup
# from distutils.extension import Extension
from setuptools import setup
from setuptools import Extension
from setuptools import dist

# preload numpy to find headers
try:
    import numpy
except:
    dist.Distribution().fetch_build_eggs(["numpy"])

# can remove the dependency here since setuptools 18.0
# from Cython.Distutils import build_ext
# from Cython.Build import cythonize

import sys

if sys.platform in ["win32", "win64"]:
    # could just import numpy and use that as base library
    include_dirs = ["src",  numpy.get_include()]
    defines = [
        ("_CRT_SECURE_NO_WARNINGS", None),
        ("_LARGEFILE64_SOURCE", None),
        ("_LARGEFILE_SOURCE", None),
    ]
else:  # 'linux' or 'darwin'
    defines = [("_LARGEFILE64_SOURCE", None), ("_LARGEFILE_SOURCE", None)]
    include_dirs = ["src", "edflib", numpy.get_include()]

# trying doing this without re-cythoning things
# ext_modules_edf = [Extension("edf", ["edf.pyx", "edflib.c"],
#                          library_dirs=['.'],
#                          include_dirs=include_dirs,
#                          )]

ext_modules_edflib = Extension(
    "edflib._edflib",
    ["edflib/_edflib.c", "src/edflib.c"],
    library_dirs=["src"],
    include_dirs=include_dirs,
    define_macros=defines,
    # extra_compile_args = ['-O2'  ],
    # extra_compile_args = ['-g'],
    # libraries=['m']
    # extra_link_args =
    # export_symbols  #only useful on windows
    # depends =
)


setup(
    name="edflib",
    version="0.84.1",
    setup_requires=["setuptools", 'numpy'], # developmnet requires: 'cython>=0.29.30,<3.0'],
    install_requires=["numpy", "future"],
    description="""python edflib is a python package ot allow access to European Data Format files (EDF for short). This is a standard for biological signals such as EEG, evoked potentials and EMG.  This module wraps Teunis van Beelen's edflib.""",
    author="""Chris Lee-Messer""",
    url=r"https://github.com/cleemesser/python-edf",
    download_url=r"https://github.com/cleemesser/python-edf/releases",
    # cmdclass={'build_ext': build_ext},
    # ext_modules=cythonize([ext_modules_edflib]), # removed cythonize
    ext_modules=[ext_modules_edflib], 
    #packages=["edflib"],  # setuptools.find_packages()
    packages=setuptools.find_packages(exclude=['test']),
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Development Status :: 4 - Beta",
    ],
    # package_data={}
    # data_files=[],
    # scripts = [],  # python_requires='>=3.5' or include  2.7?
    zip_safe=False,
)
