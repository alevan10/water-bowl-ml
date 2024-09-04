import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prediction_api.blueprint import prediction_router

default_origins = [
    "http://levan.home",
    "https://levan.home",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
]


def create_app() -> FastAPI:
    prediction_app = FastAPI()
    prediction_app.include_router(prediction_router)
    default_origins.extend(os.environ.get("ALLOWED_ORIGINS", []))
    prediction_app.add_middleware(
        CORSMiddleware,
        allow_origins=default_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return prediction_app


app = create_app()
