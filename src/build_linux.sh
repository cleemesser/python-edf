#!/bin/sh
# gcc main.c edflib.c -Wall -s -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -o test_edflib
#
#
# gcc sine.c edflib.c -Wall -s -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o sine
#
#
# gcc test_generator.c edflib.c -Wall -s -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o testgenerator
#
#
# gcc sweep.c edflib.c -Wall -s -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o sweep





gcc main.c edflib.c -Wall -g -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -o test_edflib


gcc sine.c edflib.c -Wall -g -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o sine


gcc test_generator.c edflib.c -Wall -g -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o testgenerator


gcc sweep.c edflib.c -Wall -g -o2 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -lm -o sweep

