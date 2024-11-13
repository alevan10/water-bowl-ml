import logging
import os

import aiohttp
from fastapi import APIRouter
from utils.enums import PRODUCTION_MODEL_ID
from werkzeug.exceptions import NotFound

prediction_router = APIRouter()

logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG") == "true" else logging.INFO
)
logger = logging.getLogger(__name__)


@prediction_router.get("/health")
async def health_endpoint() -> str:
    return "pong"


@prediction_router.get("/modelId")
async def get_model_id():
    return {"modelId": PRODUCTION_MODEL_ID}


@prediction_router.get("/model")
async def get_model_info():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8080/info") as response:
            if response.status == 200:
                return await response.json()
    raise NotFound("Prediction server not healthy")
