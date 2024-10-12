import os

from flask import Flask
from asgiref.wsgi import WsgiToAsgi
from werkzeug.middleware.proxy_fix import ProxyFix

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB:   str

    SECRET_KEY: SecretStr


    @property
    def get_postegres_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file = os.path.join(os.path.dirname(__file__), ".env"),
        env_file_encoding = "utf-8"
    )


settings = Config()

app = Flask(__name__, template_folder = 'pages')
app.secret_key = settings.SECRET_KEY.get_secret_value()
app.wsgi_app = ProxyFix(app.wsgi_app)
asgi_app = WsgiToAsgi(app)
