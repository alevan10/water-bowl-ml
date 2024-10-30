import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import datarobot as dr
from aiohttp import ClientSession
from bson import ObjectId
from modeling_service.datarobot_model import AsyncModel
from modeling_service.dataset_service import DatasetRetriever

from modeling_engine.utils.docker import ensure_prediction_server_image
from modeling_engine.utils.enums import (
    DATAROBOT_API_ENDPOINT,
    DATAROBOT_API_TOKEN,
    FORCE_DATASET_CREATION,
    FORCE_REDEPLOY,
    MODEL_PACKAGE_STORAGE_LOCATION,
    OVERRIDE_PULL_PREDICTION_SERVER_IMAGE,
    PREDICTION_ENDPOINT,
    WATERBOWL_DATASET_ID,
)
from modeling_engine.utils.mongo import connect_to_mongo

logger = logging.getLogger(__name__)


async def prep_docker_environment() -> None:
    # Download datarobot-prediction-server image from DataRobot
    # Tag and push the image to the local registry
    await ensure_prediction_server_image(override=OVERRIDE_PULL_PREDICTION_SERVER_IMAGE)


async def generate_dataset_version() -> tuple[dr.Dataset, str]:
    dr.Client(token=DATAROBOT_API_TOKEN, endpoint=DATAROBOT_API_ENDPOINT)
    dataset = dr.Dataset.get(WATERBOWL_DATASET_ID)
    creation_date = cast(datetime, dataset.created_at)
    if creation_date.date() != datetime.today().date() or FORCE_DATASET_CREATION:
        async with DatasetRetriever(
            endpoint="https://levan.home/api/waterbowl/v1"
        ).generate_training_dataset() as dataset_path:
            dataset = dr.Dataset.create_version_from_file(
                dataset_id=WATERBOWL_DATASET_ID, file_path=str(dataset_path)
            )
    if dataset.is_latest_version:
        latest_version = dataset.version_id
    else:
        dataset = dr.Dataset.get(WATERBOWL_DATASET_ID)
        latest_version = dataset.version_id
    return dataset, latest_version


async def train_model(
    dataset: dr.Dataset, dataset_version: str
) -> tuple[dr.Project, AsyncModel, dict[str, Any]]:
    logger.debug("Training model")
    project: dr.Project = dr.Project.create_from_dataset(
        dataset.id, dataset_version, project_name=f"Waterbowl Project {datetime.now()}"
    )

    logger.debug("New project ID: %s", project.id)
    project.analyze_and_model(
        "water_in_bowl", mode=dr.AUTOPILOT_MODE.FULL_AUTO, worker_count=-1
    )
    project.wait_for_autopilot()
    top_model: AsyncModel = AsyncModel.get(
        project=project.id, model_id=project.recommended_model().id
    )
    logger.debug("Top model ID: %s", project.id)

    model_file_name = f"model_{top_model.id}.mlpkg"
    model_information = {
        **await top_model.to_dict(),
        "modelFileName": model_file_name,
    }
    return project, top_model, model_information


async def get_production_model_id() -> str:
    async with ClientSession() as session:
        async with session.get(f"{PREDICTION_ENDPOINT}/modelId") as resp:
            model_id_payload = await resp.json()
            prod_model_id = model_id_payload.get("modelId")
            logger.debug("Production model ID: %s", prod_model_id)
            return prod_model_id


def new_model_better_than_prod(prod_model: dict, new_model: dict) -> bool:
    prod_metrics = prod_model.get("metrics", {})
    new_metrics = new_model.get("metrics", {})
    prod_better = []
    new_better = []
    if prod_metrics:
        for metric in new_metrics.keys():
            validation_diff = (
                new_metrics[metric]["validation"] - prod_metrics[metric]["validation"]
            )
            cross_validation_diff = (
                new_metrics[metric]["crossValidation"]
                - prod_metrics[metric]["crossValidation"]
            )
            if validation_diff > 0 or cross_validation_diff > 0:
                new_better.append(metric)
            else:
                prod_better.append(metric)
            logger.debug("Validation diff: %s", validation_diff)
            logger.debug("Cross validation diff: %s", cross_validation_diff)
        return len(new_better) > len(prod_better)
    return True


async def save_model_package_file(model: AsyncModel, filepath: str) -> Path:
    full_file_path = Path(MODEL_PACKAGE_STORAGE_LOCATION, filepath)
    await model.download_model_package_file(full_file_path)
    logger.debug("Model package saved to %s", str(full_file_path))
    return full_file_path


async def main():
    # Setup for the model training process
    logger.info("Starting model training process")
    await prep_docker_environment()
    logger.info("Generating dataset version")
    dataset, dataset_version = await generate_dataset_version()
    logger.info("Generated dataset version")
    logger.info("Training model")
    project, top_model, model_information = await train_model(dataset, dataset_version)
    logger.info("Model trained")
    # Get production modelId from prediction API
    logger.info("Getting production model ID")
    production_model_id = await get_production_model_id()

    # Generate artifact on model trained on new dataset
    with open("model_information.json", "w") as model_info_file:
        json.dump(model_information, model_info_file)

    # Compare model metrics to current model running in production
    with connect_to_mongo() as db:
        prod_model = db["model_registry"].find({"id": ObjectId(production_model_id)})
        if new_model_better_than_prod(prod_model, model_information) or FORCE_REDEPLOY:
            full_file_path = await save_model_package_file(
                top_model, model_information["modelFileName"]
            )
            logger.debug("Model package saved to %s", str(full_file_path))
            db["model_registry"].insert_one(model_information)

    # Clean up
    project.delete()

    # Next steps:
    # 1. Compare model metrics to current model running in production
    # 2. If model performs better, add new row to model registry
    # 3. Download the model
    # 4. Redeploy prediction container with new model


if __name__ == "__main__":
    asyncio.run(main())
