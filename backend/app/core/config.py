from pydantic_settings import BaseSettings , SettingsConfigDict
from functools import lru_cache

# lrucache store the env requenst in it and give it directly from the cache instead if reading it every time from here.

class AppConfig(BaseSettings):
    app_name: str = "Evalops"
    app_env: str = "development"
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    REDIS_URL: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def getAppConfig():
    return AppConfig()