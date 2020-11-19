# distutils: language = c++

cdef extern from "RSCode.cpp":
    pass

cdef extern from "RSCode.h":
    cdef cppclass RSCode:
        RSCode(unsigned char n, unsigned char k) except +
        void encode(size_t size, unsigned char *raw, unsigned char *parity)
        void decode(size_t size, unsigned char *rows, unsigned char *encoded, unsigned char *decoded)

cdef class PyRSCode:
    cdef RSCode *thisptr
    def __cinit__(self, unsigned char n, unsigned char k):
        self.thisptr = new RSCode(n, k)
    def __dealloc__(self):
        del self.thisptr
    def encode(self, size, raw, parity):
        self.thisptr.encode(size, raw, parity)
    def decode(self, size, rows, encoded, decoded):
        self.thisptr.decode(size, rows, encoded, decoded)

