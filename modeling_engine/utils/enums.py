import os
from enum import StrEnum
from pathlib import Path

PREDICTION_ENDPOINT = os.environ.get("PREDICTION_ENDPOINT", "http://localhost:8080/")
DATASET_ENDPOINT = os.environ.get("DATASET_ENDPOINT", "http://localhost:8000/")

ROOT_DIR = Path(__file__).parent.parent.parent
MONGO_URL = os.environ.get("MONGO_URL", "localhost:27017")
MONGO_USER = os.environ.get("MONGO_USER", "robo_ruthie")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "robo_ruthie")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "test_waterbowl")
MODELS_COLLECTION = Path(os.environ.get("MODELS_DIR", "test_models"))

DATAROBOT_API_TOKEN = os.environ.get(
    "DATAROBOT_API_TOKEN",
    "NjVkYTBiMzFmNzQ5NTVjMTA4NTM4ZmZhOnVyOUh4VGtvSWlkNmt4RWY4UUkySjhVOVNCY00vWENqREs4Vi9oelUzeHc9",
)
DATAROBOT_API_ENDPOINT = os.environ.get(
    "DATAROBOT_API_ENDPOINT", "https://app.datarobot.com/api/v2"
)
WATERBOWL_DATASET_ID = "65cedf1140521904352531a6"
FORCE_DATASET_CREATION = os.environ.get("FORCE_DATASET_CREATION", False)
FORCE_REDEPLOY = os.environ.get("FORCE_REDEPLOY", False)
OVERRIDE_PULL_PREDICTION_SERVER_IMAGE = os.environ.get(
    "OVERRIDE_PULL_PREDICTION_SERVER_IMAGE", False
)

MODEL_PACKAGE_STORAGE_LOCATION = Path(
    os.environ.get("MODEL_PACKAGE_STORAGE_LOCATION", "model_packages")
)


class PictureType(StrEnum):
    WATER_BOWL = "water_bowl"
    FOOD_BOWL = "food_bowl"
