import logging
import os

import aiohttp
from fastapi import APIRouter
from models import PredictionRequest
from utils.enums import PREDICTION_ENDPOINT

prediction_router = APIRouter()

logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG") == "true" else logging.INFO
)
logger = logging.getLogger(__name__)


@prediction_router.get("/health")
async def health_endpoint() -> str:
    return "pong"


@prediction_router.get("/model")
async def get_model_info():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{PREDICTION_ENDPOINT}/info") as response:
            return await response.json()


@prediction_router.post("/predict")
async def predict(payload: PredictionRequest):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{PREDICTION_ENDPOINT}/predictions", json=payload.data
        ) as response:
            return await response.json()
