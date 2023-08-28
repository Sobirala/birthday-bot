from typing import List, Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TOKEN: SecretStr
    ADMINS: List[int] = [1568892912]
    LOGLEVEL: Optional[str] = "DEBUG"
    DONATE_LINK: str = "https://www.buymeacoffee.com/kulunchick"

    USE_WEBHOOK: bool = False
    WEB_SERVER_HOST: str = "127.0.0.1"
    WEB_SERVER_PORT: int = 8080
    WEBHOOK_PATH: str = "/webhook"
    WEBHOOK_SECRET: str = "my-secret"
    BASE_WEBHOOK_URL: Optional[str] = None

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

    model_config = SettingsConfigDict(
        env_file=('stack.env', '.env'),
        extra="ignore"
    )


settings = Settings()
