# def _manipulate_images(self, image: Tensor) -> list[Tensor]:
    #     inverted_image = tf.image.flip_left_right(image)
    #     rotated_1 = tf.image.rot90(image)
    #     rotated_2 = tf.image.rot90(rotated_1)
    #     rotated_3 = tf.image.rot90(rotated_2)
    #     inv_rotated_1 = tf.image.rot90(inverted_image)
    #     inv_rotated_2 = tf.image.rot90(inv_rotated_1)
    #     inv_rotated_3 = tf.image.rot90(inv_rotated_2)
    #     return [image, rotated_1, rotated_2, rotated_3, inverted_image, inv_rotated_1, inv_rotated_2, inv_rotated_3]

    # def _save_images(self, directory: Path, filename_prefix: str, images: list[Tensor]) -> None:
    #     for image in images:
    #         filename = f"{filename_prefix}_{shortuuid.uuid()}.jpeg"
    #         output_file = directory.joinpath(filename)
    #         new_jpg = tf.image.encode_jpeg(image, format="grayscale", quality=100)
    #         tf.io.write_file(filename=str(output_file), contents=new_jpg)

    # async def _create_training_pictures(self, raw_picture_path: Path):
    #     async with aiofiles.open(raw_picture_path, 'rb') as raw_image:
    #         read_image = await raw_image.read()
    #     food_image = tf.image.decode_and_crop_jpeg(contents=read_image, crop_window=FOOD_BOWL_CROP_WINDOW, channels=1)
    #     water_image = tf.image.decode_and_crop_jpeg(contents=read_image, crop_window=WATER_BOWL_CROP_WINDOW, channels=1)
    #     food_training_images = self._manipulate_images(food_image)
    #     water_training_images = self._manipulate_images(water_image)
    #     new_dir = PICTURES_DIR.joinpath(raw_picture_path.stem)
    #     new_dir.mkdir()
    #     self._save_images(new_dir, "food", food_training_images)
    #     self._save_images(new_dir, "water", water_training_images)
    #     shutil.make_archive(base_name=raw_picture_path.stem, format="tar", root_dir=PICTURES_DIR.joinpath(""), base_dir=new_dir)

    # FOOD_BOWL_CROP_WINDOW = [
#     350,
#     550,
#     500,
#     500,
# ]  # [crop_y, crop_x, crop_height, crop_width]
# WATER_BOWL_CROP_WINDOW = [
#     700,
#     1300,
#     500,
#     500,
# ]  # [crop_y, crop_x, crop_height, crop_width]


from pathlib import Path
import tensorflow as tf
import tensorflow_addons as tfa

root_dir = Path(__file__).parent
raw_picture_path = root_dir.joinpath("tests", "test_data", "waterbowl-test.jpg")
output_file = root_dir.joinpath("output_file.jpg")


def decode_shit():
    with open(raw_picture_path, "rb") as raw_image:
        read_image = raw_image.read()
    decoded_image = tf.image.decode_and_crop_jpeg(
        contents=read_image, crop_window=[350, 450, 1000, 1400], channels=1
    )
    new_jpg = tf.image.encode_jpeg(decoded_image, format="grayscale", quality=100)
    tf.io.write_file(filename=output_file.name, contents=new_jpg)


if __name__ == "__main__":
    decode_shit()
