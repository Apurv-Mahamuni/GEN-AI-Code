from ..db.collections.files import file_collection
from bson import ObjectId
import os
from pdf2image import convert_from_path
import base64
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
load_dotenv()
gemini_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=gemini_key)

model = genai.GenerativeModel('gemini-2.5-flash')


def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def process_file(id: str, file_path: str):
    await file_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "Processing"
        }
    })
    print("I have to process the file with id ", id)
    
    await file_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "Converting to images"
        }
    })
    
    # Step 1 : Convert the PDF to
    pages = convert_from_path(file_path)
    images = []
    
    for i, page in enumerate(pages):
        image_save_path = f"/mnt/uploads/images/{id}/image-{i}.jpg"
        os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
        page.save(image_save_path, 'JPEG')
        images.append(image_save_path)
    
    await file_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "Converting to images successful"
        }
    })
    
    img = Image.open(images[0])
    
    response = model.generate_content([
        "Based on the Resume Given , Roast the resume:",
        img
    ])
    
    await file_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "Processed",
            "result": response.text
        }
    })

    print(response.text)