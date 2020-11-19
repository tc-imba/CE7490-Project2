import hashlib
import time
import math

from pydantic import BaseModel
from raid6.config import settings
from raid6.cpp.pyrscode import PyRSCode


class FilePiece(BaseModel):
    file_path: str
    n: int
    k: int
    size: int
    piece_size: int
    piece_id: int
    timestamp: int
    checksum: bytes
    buffer: bytes


def init_coder() -> PyRSCode:
    global __coder
    nodes = settings.primary + settings.replica
    __coder = PyRSCode(nodes, settings.primary)
    return __coder


def encode_data(file_path, buffer):
    # initialization
    m = hashlib.sha1()
    m.update(buffer)
    checksum = m.digest()
    timestamp = int(round(time.time() * 1000))
    n = settings.primary + settings.replica
    k = settings.primary

    # align buffer to multiple of k bytes
    size = len(buffer)
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
            file_path=file_path, n=n, k=k, size=size, piece_size=piece_size, piece_id=i,
            timestamp=timestamp, checksum=checksum, buffer=piece_buffer,
        )
        pieces.append(piece)
    return pieces


def get_coder() -> PyRSCode:
    global __coder
    if __coder is None:
        __coder = init_coder()
    assert __coder is not None
    return __coder


__coder = None
