import shutil
from pathlib import Path

import aiofiles
import datarobot as dr
from aiofiles.tempfile import TemporaryDirectory
from docker.errors import ImageNotFound, NotFound

import docker
from modeling_engine.utils.enums import DATAROBOT_API_ENDPOINT, DATAROBOT_API_TOKEN


async def download_prediction_server_image(tmp_dir: Path):
    image_file_name = "datarobot-prediction-server.tar.gz"
    image_file = tmp_dir.joinpath(image_file_name)
    if Path(__file__).parent.joinpath(image_file_name).exists():
        shutil.copy(Path(__file__).parent.joinpath(image_file_name), image_file)
    else:
        response = dr.Client(
            token=DATAROBOT_API_TOKEN, endpoint=DATAROBOT_API_ENDPOINT
        ).get(url="mlops/portablePredictionServerImage/")
        async with aiofiles.open(image_file, "wb") as out_file:
            await out_file.write(response.content)
    return image_file


async def ensure_prediction_server_image(override: bool = False):
    client = docker.DockerClient()
    client.login(
        username="levan.andrew.w@gmail.com", registry="http://levan.home:5000/v2"
    )
    try:
        if (
            not client.images.get_registry_data(
                name="levan.home:5000/datarobot/datarobot-portable-prediction-api"
            )
            or override
        ):
            raise ImageNotFound("datarobot prediction server not found in registry")
    except (ImageNotFound, NotFound):
        # Download datarobot-prediction-server image from DataRobot
        # Tag and push the image to the local registry
        async with TemporaryDirectory() as tmp_dir:
            if not any(
                image.tags[0]
                for image in client.images.list()
                if "datarobot" in image.tags[0]
            ):
                server_image_file = await download_prediction_server_image(
                    Path(tmp_dir)
                )
                with open(server_image_file, "rb") as image_file:
                    client.images.load(image_file)
            image_tag = next(
                image.tags[0]
                for image in client.images.list()
                if "datarobot" in image.tags[0]
            )
            image_version = image_tag.split(":")[-1]
            local_image = client.images.get(image_tag)
            local_image.tag(
                "levan.home:5000/datarobot/datarobot-portable-prediction-api",
                tag="latest",
            )
            local_image.tag(
                "levan.home:5000/datarobot/datarobot-portable-prediction-api",
                tag=image_version,
            )
            client.images.push(
                "levan.home:5000/datarobot/datarobot-portable-prediction-api:latest"
            )
            client.images.push(
                f"levan.home:5000/datarobot/datarobot-portable-prediction-api:{image_version}"
            )
