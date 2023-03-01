from typing import List, Optional

from pydantic import BaseSettings, Field, SecretStr


class Settings(BaseSettings):
    TOKEN: SecretStr = Field(..., env="BOT_TOKEN")
    ADMINS: List[int] = []
    LOGLEVEL: Optional[str] = "DEBUG"
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: str
    REDIS_PASSWORD: SecretStr
    REDIS_DB: int
    GOOGLE_TOKEN: SecretStr

    class Config:
        env_file = ".env", "stack.env"
        env_file_encoding = "utf-8"
