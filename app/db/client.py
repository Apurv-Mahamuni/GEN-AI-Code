from pymongo import AsyncMongoClient

mongoclient: AsyncMongoClient = AsyncMongoClient(
    "mongodb://admin:admin@mongo:27017")