import os
import asyncio
import random
import tempfile
import pickle

import aiofile
from fastapi.requests import Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.exceptions import HTTPException
from fastapi import File, UploadFile, BackgroundTasks
from uvicorn.config import logger

from raid6 import app
from raid6.config import settings
from raid6.data import generate_file, encode_data, decode_data, File as Raid6File
from raid6.model import send_file_block, receive_file_block, write_file_block_in_fs, read_file_block_from_fs, \
    get_filename, process_file


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



@app.get('/read/{file_path:path}', response_class=FileResponse)
async def read_file(file_path: str, background_tasks: BackgroundTasks):
    try:
        tasks = []
        for i in range(settings.primary + settings.parity):
            tasks.append(receive_file_block(i, file_path))
        pieces = await asyncio.gather(*tasks)
        file, piece_map = decode_data(pieces)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        async with aiofile.async_open(temp_file.name, 'wb') as f:
            await f.write(file.buffer)
        background_tasks.add_task(delete_temp_file, temp_file.name)
        background_tasks.add_task(rebuild_redundancy, file, piece_map)
        return FileResponse(temp_file.name, media_type='application/octet-stream')

    except Exception as e:
        raise HTTPException(400, str(e))


@app.post('/write/{file_path:path}')
async def write_file(file_path: str, file: UploadFile = File(...)):
    try:
        logger.info('write: %s', file_path)
        buffer = await file.read()
        file = generate_file(file_path, buffer)
        piece_map = [-1] * (settings.primary + settings.parity)
        result = await process_file(file, piece_map)
        received_count = sum(result)
        return {
            'success': received_count >= settings.primary,
            'result': result
        }
    except Exception as e:
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
        raise HTTPException(400, str(e))
