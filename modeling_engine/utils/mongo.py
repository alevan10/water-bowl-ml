import os
from contextlib import contextmanager

from pymongo import MongoClient
from pymongo.database import Database


@contextmanager
def connect_to_mongo() -> Database:
    mongo_uri_string = f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}{os.environ.get('MONGO_URL')}"
    mongodb_client = MongoClient(mongo_uri_string)
    database = mongodb_client[os.environ.get("MONGO_DATABASE")]
    yield database
