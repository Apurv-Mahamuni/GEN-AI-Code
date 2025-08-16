from fastapi import FastAPI, UploadFile, Path
from .utils.file import save_to_disk
from .db.collections.files import file_collection, FileSchema   # type: ignore
from .queue.q import q
from .queue.workers import process_file
from bson import ObjectId
app = FastAPI()


@app.get("/")
def hello():
    return {"status": "healthy"}


@app.get("/{id}")
async def get_file_by_id(id: str = Path(..., description="ID of the file")):
    db_file = await file_collection.find_one({"_id": ObjectId(id)})

    return {
        "_id": str(db_file["_id"]),
        "name": db_file["name"],
        "status": db_file["status"],
        "result": db_file["result"] if "result" in db_file else None,
    }


@app.post("/upload")
async def upload_file(file: UploadFile):

    db_file = await file_collection.insert_one(
        document=FileSchema(
            name=file.filename,
            status="Saving"
        )
    )

    file_path = f"/mnt/uploads/{str(db_file.inserted_id)}/{file.filename}"

    await save_to_disk(file=await file.read(), path=file_path)
    
    q.enqueue(process_file, str(db_file.inserted_id), file_path)

    await file_collection.update_one({"_id": db_file.inserted_id}, {
        "$set": {
            "status": "queued"
        }
    })

    return {"File_id": str(db_file.inserted_id)}
