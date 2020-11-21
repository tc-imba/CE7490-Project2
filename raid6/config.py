import json
from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "raid6"

    host: str = "127.0.0.1"
    base_port: int = 10000
    port: int = 10000
    debug: bool = False
    random: bool = False

    server_id: int = 0
    primary: int = 6
    parity: int = 2

    data_dir: str = "/var/data/raid6"


@lru_cache()
def get_settings():
    _settings = Settings()
    try:
        d = json.load(open('.settings.json'))
        for key, value in d.items():
            if key in _settings.__fields__:
                if value:
                    _settings.__setattr__(key, value)
    except:
        pass
    return _settings


settings = get_settings()
