import os
from pathlib import Path

DEFAULT_ENDPOINT = os.environ.get("DEFAULT_ENDPOINT", "http://localhost:8082")
PREDICTION_ENDPOINT = os.environ.get("PREDICTION_ENDPOINT", "http://localhost:8080")

ROOT_DIR = Path(__file__).parent.parent.parent
