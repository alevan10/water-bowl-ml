import random
import shutil
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Optional

import aiofiles
import pandas as pd
import shortuuid
import tensorflow as tf
from aiohttp import ClientResponse, ClientSession

from modeling_engine.utils.enums import DATASET_ENDPOINT, PictureType


class DatasetRetriever:
    def __init__(self, endpoint: str = DATASET_ENDPOINT):
        if endpoint.endswith("/"):
            endpoint = endpoint.rstrip("/")
        self.base_endpoint = endpoint

    @asynccontextmanager
    async def _make_request(self, method: str, url: str, **kwargs) -> ClientResponse:
        async with ClientSession() as session:
            async with session.request(method=method, url=url, **kwargs) as resp:
                yield resp

    async def get_dataset(
        self,
        dataset_directory: Path,
        picture_type: PictureType = PictureType.WATER_BOWL,
        picture_class: Optional[bool] = None,
    ) -> Path:
        params = {"pictureType": picture_type}
        if picture_class is not None:
            params.update({"pictureClass": picture_class})
        async with self._make_request(
            method="GET",
            url=f"{self.base_endpoint}/batch-pictures/",
            params=params,
            ssl=False,
        ) as resp:
            if not resp.ok:
                raise Exception(f"Request failed with status {resp.status}")
            pictures_collection = Path(f"{dataset_directory}/dataset.zip")
            async with aiofiles.open(pictures_collection, "wb") as zip_file:
                await zip_file.write(await resp.read())
        return pictures_collection

    def _manipulate_images(self, image: tf.Tensor) -> list[tf.Tensor]:
        inverted_image = tf.image.flip_left_right(image)
        rotated_1 = tf.image.rot90(image)
        rotated_2 = tf.image.rot90(rotated_1)
        rotated_3 = tf.image.rot90(rotated_2)
        inv_rotated_1 = tf.image.rot90(inverted_image)
        inv_rotated_2 = tf.image.rot90(inv_rotated_1)
        inv_rotated_3 = tf.image.rot90(inv_rotated_2)
        images_list = [
            image,
            rotated_1,
            rotated_2,
            rotated_3,
            inverted_image,
            inv_rotated_1,
            inv_rotated_2,
            inv_rotated_3,
        ]
        modified_images = []
        for image in images_list:
            random_adjustment = random.randrange(30, 60)
            random_adjustment = (random_adjustment * -1) / 100
            modified_images.append(tf.image.adjust_brightness(image, random_adjustment))
        return images_list

    def _save_images(
        self, directory: Path, filename_prefix: str, images: list[tf.Tensor]
    ) -> list[Path]:
        saved_images = []
        for image in images:
            filename = f"{filename_prefix}_{shortuuid.uuid()}.jpeg"
            output_file = directory.joinpath(filename)
            saved_images.append(output_file)
            new_jpg = tf.image.encode_jpeg(image, format="grayscale", quality=100)
            tf.io.write_file(filename=str(output_file), contents=new_jpg)
        return saved_images

    def _create_training_pictures(
        self,
        raw_picture_path: Path,
        directory: Path,
        picture_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        raw_jpeg = tf.io.read_file(str(raw_picture_path))
        water_image = tf.image.decode_jpeg(raw_jpeg)
        water_training_images = self._manipulate_images(water_image)
        saved_images = self._save_images(directory, "water", water_training_images)
        image_data = next(
            data
            for data in picture_data
            if raw_picture_path.name in data["waterbowl_picture"]
        )
        base_data = {
            "water_in_bowl": image_data["water_in_bowl"],
            "cat_at_bowl": image_data["cat_at_bowl"],
        }
        updated_image_data = []
        for image in saved_images:
            image_data = {
                **base_data,
                "filename": f"{raw_picture_path.parent.name}/{image.name}",
            }
            updated_image_data.append(image_data)
        return updated_image_data

    @asynccontextmanager
    async def generate_training_dataset(
        self,
        download_dataset: bool = True,
        picture_directory: Optional[Path] = None,
        file_copy_location: Optional[Path] = None,
    ) -> Path:
        if picture_directory and download_dataset:
            raise ValueError(
                "Cannot download dataset and use existing picture directory"
            )
        with TemporaryDirectory() as tmp_dir:
            if download_dataset and not picture_directory:
                picture_directory = Path(f"{tmp_dir}/dataset")
                picture_directory.mkdir(exist_ok=True)
                dataset_file = await self.get_dataset(picture_directory)
                shutil.unpack_archive(dataset_file, picture_directory)
            tmp_path = Path(tmp_dir)
            csv_file = next(picture_directory.glob("*.csv"))
            csv_df = pd.read_csv(csv_file)
            picture_data = csv_df.to_dict("records")
            updated_picture_data = []
            for directory in picture_directory.glob("*"):
                if directory.is_dir():
                    class_path = tmp_path.joinpath(directory.name)
                    class_path.mkdir()
                    for file in directory.glob("*.jpeg"):
                        updated_rows = self._create_training_pictures(
                            file, class_path, picture_data
                        )
                        updated_picture_data.extend(updated_rows)
            dataset_csv_file = tmp_path.joinpath("picture_data.csv")
            updated_csv_df = pd.DataFrame(updated_picture_data)
            updated_csv_df.to_csv(dataset_csv_file, index=False)
            if file_copy_location:
                dataset_dir = file_copy_location.joinpath("modeling_dataset")
                dataset_dir.mkdir(exist_ok=True)
                shutil.copytree(tmp_path, dataset_dir, dirs_exist_ok=True)
            if download_dataset:
                shutil.rmtree(picture_directory)
            dataset_path = tmp_path.joinpath("dataset.zip")
            with zipfile.ZipFile(dataset_path, "w") as zip_file:
                for file in tmp_path.glob("**/*"):
                    if not file.name.endswith(".zip"):
                        zip_file.write(file, arcname=file.relative_to(tmp_path))
            yield dataset_path
