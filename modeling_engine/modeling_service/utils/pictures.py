import random
from pathlib import Path
from typing import Any

import shortuuid
import tensorflow as tf


def manipulate_images(image: tf.Tensor) -> list[tf.Tensor]:
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


def save_images(
    directory: Path, filename_prefix: str, images: list[tf.Tensor]
) -> list[Path]:
    saved_images = []
    for image in images:
        filename = f"{filename_prefix}_{shortuuid.uuid()}.jpeg"
        output_file = directory.joinpath(filename)
        saved_images.append(output_file)
        new_jpg = tf.image.encode_jpeg(image, format="grayscale", quality=100)
        tf.io.write_file(filename=str(output_file), contents=new_jpg)
    return saved_images


def create_training_pictures(
    raw_picture_path: Path,
    directory: Path,
    picture_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    raw_jpeg = tf.io.read_file(str(raw_picture_path))
    water_image = tf.image.decode_jpeg(raw_jpeg)
    water_training_images = manipulate_images(water_image)
    saved_images = save_images(directory, "water", water_training_images)
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
