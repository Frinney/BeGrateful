import asyncio
import uvicorn

from app import asgi_app
from data.tables import init_db


if __name__ == '__main__':
    asyncio.run(init_db())

    uvicorn.run(asgi_app, host = "127.0.0.1", port = 5000)
