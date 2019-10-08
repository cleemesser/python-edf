CC = gcc
CFLAGS = -O2 -Wall -Wextra -Wshadow -Wformat-nonliteral -Wformat-security -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE
LDLIBS = -lm

programs = sine_generator sweep_generator test_edflib test_generator

all: $(programs)

$(programs): edflib.o

clean:
	$(RM) *.o $(programs) *.[be]df
