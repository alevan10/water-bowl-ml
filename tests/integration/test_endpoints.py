import base64
import os
from io import BytesIO

import aiohttp
import pandas as pd
import pytest
from PIL import Image


@pytest.fixture
def api_endpoint():
    yield os.environ.get("API_ENDPOINT", "http://localhost:8082")


@pytest.fixture
def prediction_payload(test_water_bowl_picture_file):
    image = Image.open(test_water_bowl_picture_file)
    img_bytes = BytesIO()
    image.save(img_bytes, "jpeg", quality=90)
    image_base64 = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
    df = pd.DataFrame(
        {
            "filename": [image_base64],
        }
    )
    yield df.to_dict(orient="records")


@pytest.mark.asyncio
async def test_health_endpoint(api_endpoint):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_endpoint}/health") as response:
            assert response.status == 200
            assert await response.json() == "pong"


@pytest.mark.asyncio
async def test_prediction_endpoint(api_endpoint, prediction_payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{api_endpoint}/predict", json={"data": prediction_payload}
        ) as response:
            assert response.status == 200
            response_json = await response.json()
            assert isinstance(response_json["data"][0]["prediction"], float)
