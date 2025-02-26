from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from utils.image_processing import resize_image


from model.model_datastore import model

app = FastAPI()

db = model()
  
@app.on_event("startup")
def startup_event():
    db.create_image_mappings()

@app.get("/{category}/{name}/{width}/{height}/")
def get_placeholder_image(category: str, name: str, width: int, height: int):
    image_path = db.get_image_path(category, name)
    
    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    resized_image = resize_image(image_path, width, height)
    return FileResponse(resized_image, media_type="image/jpeg")
