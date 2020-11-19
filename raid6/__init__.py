from fastapi import FastAPI
import pbr.version

from raid6.config import settings
from raid6.data import init_coder, get_coder


def get_version():
    return str(pbr.version.VersionInfo('raid6'))


app = FastAPI(
    title=settings.app_name,
    version=get_version(),
    description='sid: %d' % settings.server_id
)

from uvicorn.config import logger


@app.on_event("startup")
async def startup_event():
    logger.info(settings)
    assert settings.primary > 0
    assert settings.replica >= 0
    assert 0 <= settings.server_id < settings.primary + settings.replica
    settings.port = settings.server_id + 10000
    init_coder()
    logger.info(get_coder())



import raid6.apis
