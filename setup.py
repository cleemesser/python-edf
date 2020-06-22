import setuptools

from distutils.core import setup
from distutils.extension import Extension
#from Cython.Distutils import build_ext
from Cython.Build import cythonize

import sys
import numpy


if sys.platform == 'win32':
    # could just import numpy and use that as base library
    include_dirs = ['src', numpy.get_include()]
    #defines = ['_CRT_SECURE_NO_WARNINGS', '_LARGEFILE64_SOURCE', '_LARGEFILE_SOURCE']
    defines = [('_CRT_SECURE_NO_WARNINGS', None),
               ('_LARGEFILE64_SOURCE', None), ('_LARGEFILE_SOURCE', None)]
elif sys.platform == 'win64':
    # could just import numpy and use that as base library
    include_dirs = ['src', numpy.get_include()]
    defines = [('_CRT_SECURE_NO_WARNINGS', None),
               ('_LARGEFILE64_SOURCE', None), ('_LARGEFILE_SOURCE', None)]
else:  # 'linux' or 'darwin'
    defines = [('_LARGEFILE64_SOURCE', None), ('_LARGEFILE_SOURCE', None)]
    include_dirs = ['src', 'edflib', numpy.get_include()]

# ext_modules_edf = [Extension("edf", ["edf.pyx", "edflib.c"],
#                          library_dirs=['.'],
#                          include_dirs=include_dirs,
#                          )]

ext_modules_edflib = Extension(
    "edflib._edflib", ["edflib/_edflib.pyx", "src/edflib.c"],
    library_dirs=['src'],
    include_dirs=include_dirs,
    define_macros=defines,
    # extra_compile_args = ['-O2'  ],
    #extra_compile_args = ['-g'],
    # libraries=['m']
    # extra_link_args =
    # export_symbols  #only useful on windows
    # depends =
)



setup(
    name='edflib',
    version='0.83',
    description="""python edflib is a python package ot allow access to European Data Format files (EDF for short). This is a standard for biological signals such as EEG, evoked potentials and EMG.  This module wraps Teunis van Beelen's edflib.""",
    author="""Chris Lee-Messer""",
    url=r"https://github.com/cleemesser/python-edf",
    download_url=r"https://github.com/cleemesser/python-edf/releases",
    # cmdclass={'build_ext': build_ext},
    ext_modules=cythonize([ext_modules_edflib]),
    packages=["edflib"],   # setuptools.find_packages()
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Development Status :: 4 - Beta'],
    # package_data={}
    # data_files=[],
    # scripts = [],  # python_requires='>=3.5' or include  2.7?
    install_requires = ['numpy'],
)
