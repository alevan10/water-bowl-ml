from typing import Any

from pydantic import BaseModel


class PredictionRequest(BaseModel):
    data: list[dict[str, Any]]
