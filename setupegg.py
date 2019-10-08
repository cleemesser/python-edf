import sys

if sys.version[0] >= 3:
    import setuptools
    pass
if sys.version[0] == 2:
    from setuptools import setup
    execfile('setup.py') # only works on python 2.x
