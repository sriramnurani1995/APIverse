import os
import uuid
from fastapi.responses import FileResponse

# Function to determine MIME type based on file extension
def get_mime_type(file_extension: str):
    """Returns the correct MIME type based on file extension."""
    mime_types = {
        "html": "text/html",
        "json": "application/json",
        "txt": "text/plain",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "pdf": "application/pdf",
    }
    return mime_types.get(file_extension, "application/octet-stream")  # Default fallback

# Save any file with correct extension
def save_file(content: str, file_extension: str, folder: str):
    """Saves given content as a uniquely named file and returns its path."""
    os.makedirs(folder, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(folder, unique_filename)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    return file_path

# Serve any file with the correct MIME type
def get_downloadable_file_response(file_path: str):
    """Returns a FastAPI FileResponse with the correct MIME type based on file extension."""
    file_extension = file_path.split('.')[-1]
    mime_type = get_mime_type(file_extension)

    return FileResponse(
        file_path,
        filename=os.path.basename(file_path),
        media_type=mime_type,  # Uses correct MIME type for response
        headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"}
    )
