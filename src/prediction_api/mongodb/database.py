import os

from pymongo import MongoClient


async def get_db():
    mongo_uri_string = f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}{os.environ.get('MONGO_URL')}"
    mongodb_client = MongoClient(mongo_uri_string)
    database = mongodb_client[os.environ.get("MONGO_DATABASE")]
    try:
        yield database
    finally:
        await mongodb_client.close()
