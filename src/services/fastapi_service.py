from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import os
from utils.image_processing import resize_image
from utils.paragraph_processing import generate_paragraphs
from utils.file_utils import get_downloadable_file_response, save_file
from utils.html_utils import generate_html_page, generate_download_page
from model.model_datastore import model
from utils.helpers import cleanup_old_files
from contextlib import asynccontextmanager
import asyncio



db = model()  

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles FastAPI startup & shutdown events."""
    
    db.create_image_mappings()
    print("Image mappings created successfully.")

    # Start cleanup scheduler in the background
    task = asyncio.create_task(cleanup_scheduler())

    yield  

    task.cancel()  

async def cleanup_scheduler():
    """Runs cleanup every 1 hour asynchronously."""
    while True:
        cleanup_old_files("static/downloads", "html")  
        await asyncio.sleep(3600)  

app = FastAPI(lifespan=lifespan)  




@app.get("/{category}/{name}/{width}/{height}/")
def get_placeholder_image(category: str, name: str, width: int, height: int):
    image_path = db.get_image_path(category, name)
    
    if not image_path or not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    resized_image = resize_image(image_path, width, height)
    return FileResponse(resized_image, media_type="image/jpeg")

@app.get("/paragraphs")
def get_paragraphs(
    type: str = Query("lorem"),
    length: str = Query("medium"),
    count: int = Query(3),
    format: str = Query("json")
):
    """FastAPI Endpoint for Placeholder Paragraphs in JSON, HTML, or Downloadable HTML."""
    paragraphs = generate_paragraphs(type, length, count)


    paragraph_styles = {
        ".p1": "text-align: left; font-size: 18px; line-height: 1.6; margin-bottom: 16px; padding: 10px; background: #f8f8f8; border-left: 5px solid #007BFF; border-radius: 4px;",
        ".p2": "text-align: left; font-size: 18px; line-height: 1.6; margin-bottom: 16px; padding: 10px; background: #f0f0f0; border-left: 5px solid #555; border-radius: 4px;",
    }

    if format == "json":
        return JSONResponse(content={"paragraphs": paragraphs}, media_type="application/json")

    html_content = "".join([
        f'<p class="p{(i % 2) + 1}">{paragraph}</p>' for i, paragraph in enumerate(paragraphs)
    ])

    if format == "html":
        return HTMLResponse(content=generate_html_page("Generated Paragraphs", html_content, paragraph_styles))

    if format == "paragraph_download":
    
        file_path = save_file(content=generate_html_page("Generated Paragraphs", html_content, paragraph_styles),file_extension="html", folder="static/downloads")

        return HTMLResponse(content=generate_download_page("Your Generated Paragraphs HTML", file_path, "generated_paragraphs.html", paragraph_styles))


@app.get("/download_file")
def download_file(file: str):
    """Serve any generated file for download with correct MIME type."""
    return get_downloadable_file_response(file)