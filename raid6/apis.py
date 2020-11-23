import os
import asyncio
import time
import tempfile
import pickle

import aiofile
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from fastapi import File, UploadFile, BackgroundTasks
from uvicorn.config import logger

from raid6 import app
from raid6.config import settings
from raid6.data import generate_file, decode_data, File as Raid6File
from raid6.model import receive_file_block, write_file_block_in_fs, read_file_block_from_fs, \
    get_filename, process_file, remove_file, delete_file_block_in_fs


def delete_temp_file(filename: str):
    try:
        os.remove(filename)
    except:
        pass


async def rebuild_redundancy(file: Raid6File, piece_map):
    rebuild_flag = False
    for server_id in piece_map:
        if server_id < 0:
            rebuild_flag = True
            break
    if not rebuild_flag:
        return
    logger.info('%s: rebuild redundancy', file.path)
    await process_file(file, piece_map)


async def rebuild_redundancy_all():
    for f in os.listdir(settings.data_dir):
        tasks = []
        async with aiofile.async_open(os.path.join(settings.data_dir, f), 'rb') as fp:
            buffer = await fp.read()
            piece = pickle.loads(buffer)
            file_path = piece.path
            for i in range(settings.primary + settings.parity):
                tasks.append(receive_file_block(i, file_path))
            pieces = await asyncio.gather(*tasks)
            file, piece_map = decode_data(pieces)
            await rebuild_redundancy(file, piece_map)


@app.get('/read/{file_path:path}')
async def read_file(file_path: str, background_tasks: BackgroundTasks, stats: bool = False):
    try:
        tasks = []
        start = time.time()
        for i in range(settings.primary + settings.parity):
            tasks.append(receive_file_block(i, file_path))
        pieces = await asyncio.gather(*tasks)
        transfer_time = time.time() - start
        start = time.time()
        file, piece_map = decode_data(pieces)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        async with aiofile.async_open(temp_file.name, 'wb') as f:
            await f.write(file.buffer)
        decode_time = time.time() - start
        background_tasks.add_task(delete_temp_file, temp_file.name)
        background_tasks.add_task(rebuild_redundancy, file, piece_map)
        if stats:
            return {
                'delay': [transfer_time, decode_time]
            }
        else:
            return FileResponse(temp_file.name, media_type='application/octet-stream')

    except Exception as e:
        logger.exception(e)
        raise HTTPException(400, str(e))


@app.post('/write/{file_path:path}')
async def write_file(file_path: str, file: UploadFile = File(...)):
    try:
        logger.info('write: %s', file_path)
        buffer = await file.read()
        file = generate_file(file_path, buffer)
        piece_map = [-1] * (settings.primary + settings.parity)
        result, delay = await process_file(file, piece_map)
        received_count = sum(result)
        return {
            'success': received_count >= settings.primary,
            'result': result,
            'delay': delay
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(400, str(e))


@app.get('/delete/{file_path:path}')
async def delete_file(file_path: str):
    try:
        logger.info('delete: %s', file_path)
        start = time.time()
        result = await remove_file(file_path)
        deleted_count = sum(result)
        return {
            'success': deleted_count == settings.primary + settings.parity,
            'result': result,
            'delay': time.time() - start
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(400, str(e))


@app.get('/readblock/{file_path:path}', response_class=FileResponse)
async def read_file_block(file_path: str):
    try:
        filename = get_filename(file_path)
        logger.info('%s: readblock from server %d', file_path, settings.server_id)
        file_path = os.path.join(settings.data_dir, filename)
        # buffer = await read_file_block_from_fs(file_path)
        # stream = io.BytesIO(buffer)
        return FileResponse(file_path, media_type='application/octet-stream')
    except Exception as e:
        logger.exception(e)
        raise HTTPException(400, str(e))


write_file_block_lock = asyncio.Lock()


@app.post('/writeblock/{file_path:path}')
async def write_file_block(file_path: str, request: Request):
    try:
        async with write_file_block_lock:
            new_buffer = await request.body()
            new_piece = pickle.loads(new_buffer)
            replace = True
            try:
                old_buffer = await read_file_block_from_fs(file_path)
                old_piece = pickle.loads(old_buffer)
                if new_piece.timestamp < old_piece.timestamp:
                    replace = False
            except:
                pass
            if replace:
                await write_file_block_in_fs(file_path, new_buffer)
            else:
                logger.error('%s failed: writeblock into server %d, received file has smaller timestamp',
                             file_path, settings.server_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(400, str(e))


@app.get('/deleteblock/{file_path:path}')
async def delete_file_block(file_path: str, timestamp: int):
    try:
        async with write_file_block_lock:
            result = await delete_file_block_in_fs(file_path, timestamp)
            return {
                'result': result
            }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(400, str(e))


rebuild_server_lock = asyncio.Lock()


@app.get('/rebuild')
async def rebuild_server(background_tasks: BackgroundTasks):
    if rebuild_server_lock.locked():
        raise HTTPException(400, 'already rebuilding server')
    background_tasks.add_task(rebuild_redundancy_all)
    return {
        'success': True
    }
