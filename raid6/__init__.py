from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from aiohttp import ClientSession

from raid6.config import settings
from raid6.data import init_coder, get_coder


app = FastAPI(
    title=settings.app_name,
)

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
    return RedirectResponse(url='/docs')
