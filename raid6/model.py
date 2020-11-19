import base64
import os
import pickle

import aiofile
import aiohttp
from uvicorn.config import logger

from raid6 import get_session
from raid6.config import settings


def get_filename(file_path):
    return base64.b32encode(file_path.encode('utf-8')).decode('ascii')


async def write_file_block_in_fs(file_path, func):
    filename = get_filename(file_path)
    logger.info('%s: writeblock in server %d', file_path, settings.server_id)
    file_path = os.path.join(settings.data_dir, filename)
    async with aiofile.async_open(file_path, 'wb') as f:
        await f.write(await func())


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
            async def __get_buffer():
                return buffer

            await write_file_block_in_fs(file_path, __get_buffer)
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
