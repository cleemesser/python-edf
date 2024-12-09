# -*- coding: utf-8 -*
from __future__ import division, print_function, absolute_import

# FIR filter design with Python and SciPy
# http://mpastell.com/2010/01/18/fir-with-scipy/
# Jan 18th, 2010 by Matti Pastell

# SciPy really has good capabilities for DSP, but the filter design
# functions lack good examples. A while back I wrote about IIR filter
# design with SciPy. Today I’m going to implement lowpass, highpass
# and bandpass example for FIR filters. We use the same functions
# (mfreqz and impz, shown in the end of this post as well) as in the
# previous post to get the frequency, phase, impulse and step
# responses. You can download this example along with the functions
# here FIR_design.py.

# To begin with we’ll import pylab and scipy.signal:
from pylab import *
import scipy.signal as signal

# Lowpass FIR filter

# Designing a lowpass FIR filter is very simple to do with SciPy, all you need to do is to define the window length, cut off frequency and the window:

n = 61
a = signal.firwin(n, cutoff=0.3, window="hamming")
# Frequency and phase response
mfreqz(a)
show()
# Impulse and step response
figure(2)
impz(a)
show()

# Which yields:
# <plot here>

# Highpass FIR Filter
# SciPy does not have a function for directly designing a highpass FIR
# filter, however it is fairly easy design a lowpass filter and use
# spectral inversion to convert it to highpass. See e.g Chp 16 of The
# Scientist and Engineer’s Guide to Digital Signal Processing for the
# theory, the last page has an example code.

n = 101
a = signal.firwin(n, cutoff=0.3, window="hanning")
# Spectral inversion
a = -a
a[n / 2] = a[n / 2] + 1
mfreqz(a)
show()


# 1. IIR filter design with Python and SciPy
# 2. Python in Sweave document
