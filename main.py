import asyncio
import sys

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api import api_router

origins = [
    '*'
]


class EventAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def run_server():
    uvicorn.run("main:get_application", reload=True, host='0.0.0.0', port=8000)


def get_application():
    app = EventAPI()
    app.include_router(api_router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


if __name__ == "__main__":
    command = sys.argv[1]
    if command == 'insert_values':
        from seeds.seeder import insert_value
        asyncio.run(insert_value())
    if command == 'runserver':
        run_server()
