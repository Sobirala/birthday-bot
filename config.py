from pydantic import BaseSettings, SecretStr, Field


class Settings(BaseSettings):
    TOKEN: SecretStr = Field(..., env="BOT_TOKEN")
    ADMINS: list[int]
    LOGLEVEL: str = "DEBUG"
    MONGO_URL: SecretStr
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: str
    REDIS_PASSWORD: SecretStr
    REDIS_DB: int
    GOOGLE_TOKEN: SecretStr

    class Config:
        env_file = "stack.env"
        env_file_encoding = "utf-8"
