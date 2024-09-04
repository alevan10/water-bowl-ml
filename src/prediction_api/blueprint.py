import logging
import os

from fastapi import APIRouter
from utils.enums import PRODUCTION_MODEL_ID

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
