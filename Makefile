CC = clang
CFLAGS = -std=c99 -Wall -pedantic -gdwarf-4  # Added -g for debug symbols
LDFLAGS = -L. -lhclib  # Link with the shared library in the current directory

all: _hclib.so

_hclib.so: hclib_wrap.o libhclib.so
	$(CC) $(CFLAGS) -shared hclib_wrap.o -L. -L/usr/lib/python3.11 -lpython3.11 -lhclib -o _hclib.so

hclib_wrap.o: hclib_wrap.c
	$(CC) $(CFLAGS) -c hclib_wrap.c -I/usr/include/python3.11/ -fPIC -o hclib_wrap.o

hclib_wrap.c hclib.py: hclib.i
	swig -python hclib.i

libhclib.so: hclib.o
	$(CC) hclib.o -shared -o libhclib.so -lm

hclib.o: hclib.c hclib.h
	$(CC) $(CFLAGS) -c hclib.c -o hclib.o -fpic

clean:
	rm -f *.o *.so test
