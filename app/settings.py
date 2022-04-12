from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    ELASTICSEARCH_HOSTS: List[str] | str
    ELASTICSEARCH_TIME_OUT: int = 30
    ELASTICSEARCH_MAX_RETRIES: int = 10
    ELASTICSEARCH_RETRY_ON_TIME_OUT = True

    class Config:
        case_sensitive = True


settings = Settings()
