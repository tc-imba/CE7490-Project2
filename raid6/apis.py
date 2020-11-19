import os
import asyncio
import random
import tempfile

import aiofile
from fastapi.requests import Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.exceptions import HTTPException
from fastapi import File, UploadFile, BackgroundTasks
from uvicorn.config import logger

from raid6 import app
from raid6.config import settings
from raid6.data import generate_file, encode_data, decode_data
from raid6.model import send_file_block, receive_file_block, write_file_block_in_fs, get_filename


def delete_temp_file(filename: str):
    try:
        os.remove(filename)
    except:
        pass


@app.get('/read/{file_path:path}', response_class=FileResponse)
async def read_file(file_path: str, background_tasks: BackgroundTasks):
    try:
        tasks = []
        for i in range(settings.primary + settings.replica):
            tasks.append(receive_file_block(i, file_path))
        result = await asyncio.gather(*tasks)
        pieces = list(filter(lambda x: x is not None, result))
        file = decode_data(pieces)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        async with aiofile.async_open(temp_file.name, 'wb') as f:
            await f.write(file.buffer)
        background_tasks.add_task(delete_temp_file, temp_file.name)
        return FileResponse(temp_file.name, media_type='application/octet-stream')

    except Exception as e:
        raise HTTPException(400, str(e))


@app.post('/write/{file_path:path}')
async def write_file(file_path: str, file: UploadFile = File(...)):
    try:
        logger.info('write: %s', file_path)
        buffer = await file.read()
        file = generate_file(file_path, buffer)
        pieces = encode_data(file)
        tasks = []
        servers = list(range(len(pieces)))
        random.shuffle(servers)
        for i, piece in enumerate(pieces):
            tasks.append(send_file_block(servers[i], file_path, piece))
        result = await asyncio.gather(*tasks)
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


@app.post('/writeblock/{file_path:path}')
async def write_file_block(file_path: str, request: Request):
    try:
        await write_file_block_in_fs(file_path, request.body)
    except Exception as e:
        raise HTTPException(400, str(e))
