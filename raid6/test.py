import secrets
from pprint import pprint
from raid6.pyfinite.rs_code import RSCode
from raid6.pyfinite.genericmatrix import GenericMatrix
from raid6.pyfinite.ffield import FField
import numpy
import time
from raid6.cpp.pyrscode import PyRSCode
import pickle
import math

from raid6.data import encode_data, generate_file, decode_data


# file_path = '/a/b'
# buffer = secrets.token_bytes(1024)
# print(buffer)

# file = generate_file(file_path, buffer)
# pieces = encode_data(file)
# pprint(pieces)
#
# decoded_file = decode_data(pieces)


# n = 9
# k = 6
#
# cppcoder = PyRSCode(n, k)
# raw = bytes([41, 35, 190, 132, 225, 108])
# parity = bytes(n - k)
#
#
# cppcoder.encode(1, raw, parity)
# pprint(raw)
# pprint(parity)
# encoded = raw + parity
# # for i in range(n):
# #     print(encoded[i])
#
# rows = bytes([0, 1, 2, 3, 4, 6])
# temp = []
# for i in rows:
#     temp.append(encoded[i])
# temp = bytes(temp)
# decoded = bytes(k)
#
# cppcoder.decode(1, rows, temp, decoded)
#
# pprint(temp)
# pprint(decoded)

# for i in range(k):
#     print(decoded[i])


#

def test_pyfinite(n, k, raw, times):
    coder = RSCode(n=n, k=k, log2FieldSize=8, shouldUseLUT=1)

    size = len(raw)
    piece_size = math.ceil(size / k)
    encoded = []

    start = time.time()
    for i in range(piece_size):
        buffer = raw[i * k:(i + 1) * k]
        if len(buffer) < k:
            buffer += bytes(k - len(buffer))
        encoded += coder.Encode(buffer)
    end = time.time()
    time_encode = (end - start) * 1e9

    rows = list(range(n))
    rows = rows[-k:]

    start = time.time()
    coder.PrepareDecoder(rows)
    decoded = []
    for i in range(piece_size):
        decoded += coder.Decode(encoded[i * k:(i + 1) * k])
    end = time.time()
    time_decode = (end - start) * 1e9

    print('pyfinite,%d,%d,%d,%d,%d,%d' % (size, n, k, times, time_encode, time_decode))


small_raw = secrets.token_bytes(1024)
middle_raw = secrets.token_bytes(1024 * 1024)
for n in [8, 128]:
    for i in range(1, 9):
        k = n // 8 * i
        test_pyfinite(n, k, small_raw, 10)
        test_pyfinite(n, k, middle_raw, 10)

#
# data = coder.encoderMatrix.MakeSimilarMatrix(size=(k, 1000000), fillMode='z')
# for i in range(k):
#     data.SetRow(i, [i] * 1000000)
#
# # pprint(data)
# # print(len(data))
#
# encoded = coder.encoderMatrix * data

# for i in range(1000):
#     encoded = coder.Encode(data)
#
# pprint(encoded)
#
# print(len(encoded))

FIELD = FField(8, useLUT=1)


# print(FIELD.lut.divLUT)
#
#
# with open('LUT.h', 'w') as f:
#     f.write('#ifndef LUT_H\n')
#     f.write('#define LUT_H\n\n')
#     f.write('const static unsigned char GF8_LUT_MUL[256][256] = {\n')
#     for row in FIELD.lut.mulLUT:
#         f.write('    {')
#         for i, item in enumerate(row):
#             f.write('%3d, ' % item)
#             if i % 16 == 15 and i != len(row) - 1:
#                 f.write('\n     ')
#         f.write('},\n')
#     f.write('};\n\n')
#
#     f.write('const static unsigned char GF8_LUT_DIV[256][256] = {\n')
#     for row in FIELD.lut.divLUT:
#         f.write('    {')
#         for i, item in enumerate(row):
#             if item == 'NaN':
#                 item = 0
#             f.write('%3d, ' % item)
#             if i % 16 == 15 and i != len(row) - 1:
#                 f.write('\n     ')
#         f.write('},\n')
#
#     f.write('};\n\n')
#     f.write('#endif\n')


class GF8(object):
    def __init__(self, number):
        self.number = number

    def __add__(self, x):
        return self.number ^ x.number

    def __mul__(self, x):
        return FIELD.lut.mulLUT[self.number][x]

    def __sub__(self, x):
        return self.number ^ x.number

    def __div__(self, x):
        return FIELD.lut.divLUT[self.number][x]

    def __repr__(self):
        return str(self.number)

# a = numpy.array([GF8(numpy.random.randint(4)) for i in range(18)]).reshape(3, 6)
# b = numpy.array([GF8(numpy.random.randint(4)) for i in range(18)]).reshape(3, 6)
#
# print(a)
# print(b)
#
# print(a * b)

# m = 1000000
# data = numpy.zeros((k, m), dtype=GF8)
#
# start = time.time()
# print('start')
# encoderMatrix = numpy.zeros((n, k), dtype=GF8)
# for i in range(0, k):
#     encoderMatrix[i, i] = GF8(1)
# for i in range(k, n):
#     for j in range(0, k):
#         x = i - k + 1
#         y = j + (n - k) + 1
#         encoderMatrix[i, j] = GF8(FIELD.Inverse(FIELD.Add(x, y)))
#
# print(encoderMatrix[3:9])
# a = numpy.linalg.inv(encoderMatrix[3:9])
# print(a)
#
# encoded = numpy.matmul(encoderMatrix, data, dtype=GF8)
# print(encoded)
# end = time.time()
# print(end - start)

# encoderMatrix = numpy.linalg.inv(encoderMatrix.transpose()).transpose()
# print(encoderMatrix)
