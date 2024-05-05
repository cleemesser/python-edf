
When building packages, it is possible to get the following error 
```
Traceback (most recent call last):
  File "/home/clee/bin/edf2eeghdf.py", line 41, in <module>
    import edflib # have several choices for reading edf, this is my library version 0.76 and 0.8 work
  File "/home/clee/.conda/envs/pyt181/lib/python3.8/site-packages/edflib/__init__.py", line 4, in <module>
    from .edfwriter import EdfWriter
  File "/home/clee/.conda/envs/pyt181/lib/python3.8/site-packages/edflib/edfwriter.py", line 6, in <module>
    from . import _edflib
  File "edflib/_edflib.pyx", line 1, in init edflib._edflib
ValueError: numpy.ndarray size changed, may indicate binary incompatibility. Expected 96 from C header, got 80 from PyObject
```

https://stackoverflow.com/questions/66060487/valueerror-numpy-ndarray-size-changed-may-indicate-binary-incompatibility-exp

it sounds like this occurs with new features of pip which builds with a more recent version of pip than what is installed in an environment


can try installing with pip with --no-binary OR --no-build-isolation
