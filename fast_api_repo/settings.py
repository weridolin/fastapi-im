from pydantic import BaseConfig,BaseSettings,RedisDsn,PostgresDsn,AmqpDsn
from functools import lru_cache

class AppSettings(BaseSettings):

    EMAIL_PWD:str
    REDIS_DSN: RedisDsn
    PG_DSN: PostgresDsn
    # AMQP_DSN: AmqpDsn
    JWT_KEY:str
    JWT_EXPIRE_TIME:int
    JWT_ALGORITHM:str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()
