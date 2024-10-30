from unittest import mock

import pytest
import tensorflow as tf
from modeling_engine.modeling_service.utils.pictures import manipulate_images


@pytest.fixture
def test_picture(test_data_dir):
    yield test_data_dir.joinpath("water-bowl.jpeg")


@pytest.fixture
def test_tensor(test_picture):
    raw_jpeg = tf.io.read_file(str(test_picture))
    water_image = tf.image.decode_jpeg(raw_jpeg)
    yield water_image

@pytest.fixture
def expected_tensors(test_data_dir, test_picture):
    tensors_file = test_data_dir.joinpath("waterbowl_tensors.csv")
    if not tensors_file.exists():
        raw_jpeg = tf.io.read_file(str(test_picture))
        water_image = tf.image.decode_jpeg(raw_jpeg)
        water_training_images = manipulate_images(water_image)
        type_tensor = tf.constant(
            [str(tensor.dtype)[9:-2] for tensor in water_training_images])  # figures out the dtypes by itself
        serialized_tensor = tf.io.serialize_tensor(type_tensor)
        with tf.io.TFRecordWriter(str(tensors_file)) as writer:
            writer.write(serialized_tensor.numpy())
            for tensor in water_training_images:
                serialized_tensor = tf.io.serialize_tensor(tensor)
                writer.write(serialized_tensor.numpy())

    num_tensors = 8  # 8 manipulated images

    ret = []
    records = tf.data.TFRecordDataset(tensors_file)
    type_list = []
    for i, record in enumerate(records):
        if i % (num_tensors + 1) == 0:
            type_list = []
            type_list_tensor = tf.io.parse_tensor(record, tf.string)
            type_list = tf.Variable(type_list_tensor).numpy().tolist()
            type_list = [tf.dtypes.as_dtype(tp.decode()) for tp in type_list]
            type_list.insert(0, tf.string)  # 0th entry is always just the types
        else:
            ret.append(tf.io.parse_tensor(record, type_list[i % (num_tensors + 1)]))
    yield ret

def test_manipulate_images(test_tensor, expected_tensors):
    with mock.patch("modeling_engine.modeling_service.utils.pictures.tf.image.adjust_brightness") as mock_brightness:
        mock_brightness.return_value = lambda x, y: x
        images = manipulate_images(test_tensor)
        for expected, test in zip(expected_tensors, images):
            assert tf.reduce_all(tf.equal(expected, test))