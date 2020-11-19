import hashlib
import time
import math
import pickle

from pydantic import BaseModel
from raid6.config import settings
from raid6.cpp.pyrscode import PyRSCode


class File(BaseModel):
    path: str
    size: int
    timestamp: int
    checksum: bytes
    buffer: bytes


class FilePiece(File):
    n: int
    k: int
    piece_size: int
    piece_id: int


def init_coder() -> PyRSCode:
    global __coder
    nodes = settings.primary + settings.replica
    __coder = PyRSCode(nodes, settings.primary)
    return __coder


def generate_file(path, buffer):
    # initialization
    m = hashlib.sha1()
    m.update(buffer)
    checksum = m.digest()
    timestamp = int(round(time.time() * 1000))
    size = len(buffer)
    return File(path=path, size=size, timestamp=timestamp, checksum=checksum, buffer=buffer)


def encode_data(file: File):
    # initialization
    n = settings.primary + settings.replica
    k = settings.primary

    # align buffer to multiple of k bytes
    size = file.size
    buffer = file.buffer

    piece_size = math.ceil(size / k)
    if size < piece_size * k:
        buffer += bytes(piece_size * k - size)

    parity_buffer = bytes(piece_size * (n - k))
    coder = get_coder()
    coder.encode(piece_size, buffer, parity_buffer)

    # generate file pieces
    pieces = []
    for i in range(n):
        if i < k:
            piece_buffer = buffer[i * piece_size:(i + 1) * piece_size]
        else:
            piece_buffer = parity_buffer[(i - k) * piece_size:(i - k + 1) * piece_size]
        assert len(piece_buffer) == piece_size
        piece = FilePiece(
            path=file.path, n=n, k=k, size=size, piece_size=piece_size, piece_id=i,
            timestamp=file.timestamp, checksum=file.checksum, buffer=piece_buffer,
        )
        pieces.append(piece)
    return pieces


def decode_data(pieces):
    # initialization
    n = settings.primary + settings.replica
    k = settings.primary

    # filter pieces with latest timestamp and correct checksum
    timestamp = 0
    checksum = ''
    piece_size = 0
    size = 0
    path = ''
    for piece in pieces:
        piece: FilePiece
        if piece.timestamp > timestamp:
            timestamp = piece.timestamp
            checksum = piece.checksum
            size = piece.size
            piece_size = piece.piece_size
            path = piece.path
    pieces = list(filter(lambda x: x.timestamp == timestamp and x.checksum == checksum and
                                   x.piece_size == piece_size and x.size == size and x.path == path and
                                   x.n == n and x.k == k, pieces))

    # make sure piece id is unique
    temp = []
    id_set = set()
    for piece in pieces:
        if piece.piece_id not in id_set:
            temp.append(piece)
            id_set.add(piece.piece_id)
    pieces = temp
    pieces.sort(key=lambda x: x.piece_id)

    if len(pieces) < k:
        raise ValueError('Too few available blocks')

    pieces = pieces[:k]
    rows = []
    buffer = bytes()
    for piece in pieces:
        rows.append(piece.piece_id)
        buffer += piece.buffer
    rows_buffer = bytes(rows)

    decoded_buffer = bytes(piece_size * k)
    coder = get_coder()
    coder.decode(piece_size, rows_buffer, buffer, decoded_buffer)
    decoded_buffer = decoded_buffer[0:size]

    m = hashlib.sha1()
    m.update(decoded_buffer)
    decoded_checksum = m.digest()

    if checksum != decoded_checksum:
        raise ValueError('Checksum not matched')

    return File(path=path, size=size, timestamp=timestamp, checksum=checksum, buffer=decoded_buffer)


def get_coder() -> PyRSCode:
    global __coder
    if __coder is None:
        __coder = init_coder()
    assert __coder is not None
    return __coder


__coder = None
