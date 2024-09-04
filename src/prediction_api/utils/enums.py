import os
from pathlib import Path

DEFAULT_ENDPOINT = os.environ.get("DEFAULT_ENDPOINT", "http://localhost:8080/")

ROOT_DIR = Path(__file__).parent.parent.parent
MONGO_URL = os.environ.get("MONGO_URL", "localhost:27017")
MONGO_USER = os.environ.get("MONGO_USER", "robo_ruthie")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "robo_ruthie")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "test_waterbowl")
MODELS_COLLECTION = Path(os.environ.get("MODELS_DIR", "test_models"))

PRODUCTION_MODEL_ID = os.environ.get("PRODUCTION_MODEL_ID", "squak_squak_squak")
