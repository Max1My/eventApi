import os
import sys
from functools import lru_cache
from typing import TypeVar

import dotenv
import rootpath
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from passlib.context import CryptContext
from pydantic import PostgresDsn, field_validator, BaseModel
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.common.fastapi_jwt_auth import AuthJWT

TSettings = TypeVar("TSettings", bound=BaseSettings)
dotenv.load_dotenv()

ROOT_DIR = rootpath.detect()

ACCESS_TOKEN_EXPIRE_DAYS = os.getenv("ACCESS_TOKEN_EXPIRE_DAYS")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

DEBUG = os.getenv("DEBUG", False)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{ROOT_DIR}/.env",
        env_file_encoding="utf-8",
        env_prefix="app_",
    )

    debug: bool = True


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        env_prefix="postgres_",
        extra="allow",
    )

    scheme: str
    user: str
    password: str
    host: str
    port: str
    db: str
    url: PostgresDsn | None = None

    @field_validator("url")
    def get_postgres_dsn(
            cls,
            value: PostgresDsn | None,
            values: FieldValidationInfo,
    ) -> PostgresDsn:
        if value:
            return value
        return PostgresDsn(
            f"{values.data.get('scheme')}://"
            f"{values.data.get('user')}:"
            f"{values.data.get('password')}@"
            f"{values.data.get('host')}:"
            f"{values.data.get('port')}/"
            f"{values.data.get('db') if values.data.get('db') else 'postgres'}",
        )


@lru_cache
def get_settings(cls: type[TSettings]) -> TSettings:
    return cls()


logger.remove()
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS!UTC}</green> | "
    "<level>{level}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

logger.add(sys.stdout, format=log_format)
logger.add(
    "./logs/backend.log",
    format=log_format,
    rotation="10 MB",
    compression="zip",
    enqueue=True,
)


class JWTSettings(BaseModel):
    authjwt_secret_key: str = SECRET_KEY


@AuthJWT.load_config
def get_config():
    return JWTSettings()
