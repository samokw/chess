CC = clang
CFLAGS = -std=c99 -Wall -pedantic -gdwarf-4 -fPIC
LDFLAGS =

# Use python3-config to get the correct flags
PYTHON_INCLUDE_DIR := $(shell python3-config --includes)
PYTHON_CFLAGS := $(shell python3-config --cflags)
PYTHON_LDFLAGS := $(shell python3-config --ldflags)


all: _hclib.so

_hclib.so: hclib_wrap.o libhclib.so
	$(CC) $(CFLAGS) -shared hclib_wrap.o -L. -lhclib -o _hclib.so -undefined dynamic_lookup

hclib_wrap.o: hclib_wrap.c
	$(CC) $(CFLAGS) -c hclib_wrap.c $(PYTHON_INCLUDE_DIR) -o hclib_wrap.o

hclib_wrap.c hclib.py: hclib.i
	swig -python hclib.i

libhclib.so: hclib.o
	$(CC) $(CFLAGS) hclib.o -shared -o libhclib.so -lm

hclib.o: hclib.c hclib.h
	$(CC) $(CFLAGS) -c hclib.c -o hclib.o

clean:
	rm -f *.o *.so hclib.py hclib_wrap.c