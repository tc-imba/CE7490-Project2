from aiohttp import ClientSession
import asyncio
import random
import numpy as np


async def run(file_size, file_num):
    upload_delays = []
    download_delays = []
    async with ClientSession() as session:
        for i in range(file_num):
            file_path = '%s-%d' % (file_size, i)
            server_id = np.random.randint(0, 7)
            port = 11000 + server_id
            url = 'http://127.0.0.1:%d/write/%s' % (port, file_path)
            buffer = np.random.bytes(file_size)
            files = {'file': buffer}
            async with session.post(url, data=files) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data['delay']:
                        upload_delays.append(data['delay'])
        for i in range(file_num):
            file_path = '%s-%d' % (file_size, i)
            server_id = np.random.randint(0, 7)
            port = 11000 + server_id
            url = 'http://127.0.0.1:%d/read/%s?stats=true' % (port, file_path)
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data['delay']:
                        download_delays.append(data['delay'])

    upload_delay = np.average(upload_delays, 0)
    download_delay = np.average(download_delays, 0)

    print('%d,%f,%f,%f,%f' % (file_size, upload_delay[0], upload_delay[1], download_delay[0], download_delay[1]))

    # print(upload_delay)
    # print(download_delay)


async def main():
    # await run(file_size=1024, file_num=100)
    await run(file_size=1024 * 10, file_num=100)
    await run(file_size=1024 * 100, file_num=100)
    # await run(file_size=1024 * 1024, file_num=50)
    # await run(file_size=1024 * 1024 * 10, file_num=20)
    # await run(file_size=1024 * 1024 * 100, file_num=10)


if __name__ == '__main__':
    asyncio.run(main())
