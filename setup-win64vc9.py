from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("edf", ["edf.pyx", "edflib.c"],
                         library_dirs=['.'],
                         include_dirs=[
            r"c:/Python26/Lib/site-packages/numpy/core/include"])
               ]

setup(
  name = 'edf module',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
