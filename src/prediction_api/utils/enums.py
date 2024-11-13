import os
from pathlib import Path

DEFAULT_ENDPOINT = os.environ.get("DEFAULT_ENDPOINT", "http://localhost:8082/")

ROOT_DIR = Path(__file__).parent.parent.parent

PRODUCTION_MODEL_ID = os.environ.get("PRODUCTION_MODEL_ID", "squak_squak_squak")
