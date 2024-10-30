import zipfile
from pathlib import Path
from zipfile import ZipFile

import pytest
from tempfile import TemporaryDirectory
from aioresponses import aioresponses

from modeling_engine.modeling_service.dataset_service import DatasetRetriever

@pytest.fixture
def mock_aiohttp():
    with aioresponses() as m:
        yield m


@pytest.fixture
def temp_dir():
    with TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_dataset(temp_dir):
    dataset_dir = temp_dir / "dataset"
    dataset_dir.mkdir()
    for i in range(10):
        with open(dataset_dir / f"test_{i}.jpg", "w") as f:
            f.write("test")
    yield dataset_dir


@pytest.fixture
def test_dataset_zip_file(temp_dir, test_dataset):
    with ZipFile(temp_dir / "dataset.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for file in test_dataset.glob("*.jpg"):
            z.write(file, arcname=file.name)
    yield temp_dir / "dataset.zip"


@pytest.fixture
def mock_file_response(mock_aiohttp, test_dataset_zip_file):
    mock_aiohttp.get(
        "http://localhost:8000/batch-pictures/?pictureType=water_bowl",
        body=test_dataset_zip_file.read_bytes(),
        status=200,
    )

@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_file_response")
async def test_get_dataset(mock_aiohttp, test_dataset):
    with TemporaryDirectory() as tmp_dir:
        dataset_retriever = DatasetRetriever()
        dataset = await dataset_retriever.get_dataset(Path(tmp_dir))
        with ZipFile(dataset, "r") as z:
            zipfile_filenames = [file.filename for file in z.filelist]
        existing_files = [file.name for file in test_dataset.glob("*.jpg")]
        assert len(zipfile_filenames) == len(existing_files)
        assert existing_files == zipfile_filenames
