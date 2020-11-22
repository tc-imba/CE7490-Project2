import os
from fastapi import FastAPI
import pbr.version
from aiohttp import ClientSession

from raid6.config import settings
from raid6.data import init_coder, get_coder


# def get_version():
#     return str(pbr.version.VersionInfo('raid6'))


app = FastAPI(
    title=settings.app_name,
    # version=get_version(),
    description='sid: %d' % settings.server_id
)

from uvicorn.config import logger

__session : ClientSession = None


def get_session() -> ClientSession:
    global __session
    if __session is None:
        __session = ClientSession()
    return __session


@app.on_event("startup")
async def startup_event():
    global session
    logger.info(settings)
    assert settings.primary > 0
    assert settings.parity >= 0
    assert 0 <= settings.server_id < settings.primary + settings.parity
    settings.port = settings.server_id + settings.base_port
    init_coder()
    logger.info(get_coder())
    os.makedirs(settings.data_dir, exist_ok=True)
    get_session()


@app.on_event("shutdown")
def shutdown_event():
    if __session is not None:
        __session.close()



from raid6.apis import *


@app.get("/")
async def root():
    return {"message": "Hello World"}
