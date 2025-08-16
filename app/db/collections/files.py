from typing import TypedDict, Optional
from pydantic import Field
from pymongo.asynchronous.collection import AsyncCollection
from ..db import database


class FileSchema(TypedDict):
    name: str = Field(..., description="Name of file")
    status: str = Field(..., description="Status of the file")
    result: Optional[str] = Field(..., description="Result from AI")


COLLECTION_NAME = "files"
file_collection: AsyncCollection = database[COLLECTION_NAME]