import base64
import os
import pickle
import asyncio
import random

import aiofile
import aiohttp
from uvicorn.config import logger

from raid6 import get_session
from raid6.config import settings
from raid6.data import encode_data


def get_filename(file_path):
    return base64.b32encode(file_path.encode('utf-8')).decode('ascii')


write_file_block_in_fs_lock = asyncio.Lock()


async def write_file_block_in_fs(file_path, buffer):
    async with write_file_block_in_fs_lock:
        filename = get_filename(file_path)
        logger.info('%s: writeblock into server %d', file_path, settings.server_id)
        file_path = os.path.join(settings.data_dir, filename)
        async with aiofile.async_open(file_path, 'wb') as f:
            await f.write(buffer)


async def read_file_block_from_fs(file_path):
    filename = get_filename(file_path)
    logger.info('%s: readblock from server %d', file_path, settings.server_id)
    file_path = os.path.join(settings.data_dir, filename)
    async with aiofile.async_open(file_path, 'rb') as f:
        return await f.read()


async def send_file_block(server_id, file_path, piece):
    try:
        buffer = pickle.dumps(piece)
        if server_id == settings.server_id:
            await write_file_block_in_fs(file_path, buffer)
            logger.info('%s: sendblock %d to server %d', file_path, piece.piece_id, server_id)
            return True
        else:
            port = settings.base_port + server_id
            url = 'http://%s:%d/writeblock/%s' % (settings.host, port, file_path)
            headers = {
                'content-type': 'application/octet-stream'
            }
            session = get_session()
            async with session.post(url, data=buffer, headers=headers) as resp:
                resp: aiohttp.ClientResponse
                if resp.status == 200:
                    logger.info('%s: sendblock %d to server %d', file_path, piece.piece_id, server_id)
                    return True
                else:
                    raise Exception(resp)
    except Exception as e:
        logger.error('%s failed: sendblock %d to server %d', file_path, piece.piece_id, server_id)
        # logger.exception(e)
    return False


async def receive_file_block(server_id, file_path):
    try:
        if server_id == settings.server_id:
            buffer = await read_file_block_from_fs(file_path)
            piece = pickle.loads(buffer)
            logger.info('%s: receiveblock %d from server %d', file_path, piece.piece_id, server_id)
            return piece
        else:
            port = settings.base_port + server_id
            url = 'http://%s:%d/readblock/%s' % (settings.host, port, file_path)
            session = get_session()
            async with session.get(url) as resp:
                resp: aiohttp.ClientResponse
                if resp.status == 200:
                    buffer = await resp.read()
                    piece = pickle.loads(buffer)
                    logger.info('%s: receiveblock %d from server %d', file_path, piece.piece_id, server_id)
                    return piece
                else:
                    raise Exception(resp)
    except Exception as e:
        logger.error('%s failed: receiveblock from server %d', file_path, server_id)
        # logger.exception(e)
    return None


async def process_file(file, piece_map):
    pieces = encode_data(file)
    n = len(pieces)
    assert len(piece_map) == n
    tasks = []
    servers = set(range(n))
    sending_pieces = []
    for piece_id, server_id in enumerate(piece_map):
        if server_id in servers:
            servers.remove(server_id)
        elif server_id < 0:
            sending_pieces.append(pieces[piece_id])
    servers = list(servers)
    assert len(servers) == len(sending_pieces)
    random.shuffle(servers)
    for i, piece in enumerate(sending_pieces):
        tasks.append(send_file_block(servers[i], file.path, piece))
    result = await asyncio.gather(*tasks)
    return result
