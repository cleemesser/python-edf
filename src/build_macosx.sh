#!/bin/sh
gcc -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE main.c edflib.c -Wall -O2 -lm -o test_edflib
gcc -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE sine.c edflib.c -Wall -O2 -lm -o sine
gcc -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE test_generator.c edflib.c -Wall -O2 -lm -o testgenerator
gcc -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE sweep.c edflib.c -Wall -O2 -lm -o sweep
