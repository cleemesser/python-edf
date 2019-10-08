CC=gcc
CFLAGS=-Wall -fPIC -O -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE
LIBS=-lm
LDFLAGS= -fPIC

quick:	edflib/_edflib.pyx
	cython edflib/_edflib.pyx


edf:
	python setup.py build_ext --inplace

library:	edflib.o 
	gcc -shared -fPIC -o libedf.so edflib.o $(LIBS)	
# gcc main.c edflib.c -Wall -s -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -o test_edflib
#
#
# gcc sine.c edflib.c -Wall -s -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o sine
#
#
testgenerator:	
	gcc test_generator.c edflib.c -Wall -s -O2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o testgenerator
#
#
# gcc sweep.c edflib.c -Wall -s -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o sweep





# gcc main.c edflib.c -Wall -g -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -o test_edflib


# gcc sine.c edflib.c -Wall -g -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o sine


# gcc test_generator.c edflib.c -Wall -g -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o testgenerator


# gcc sweep.c edflib.c -Wall -g -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o sweep

