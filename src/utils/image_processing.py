from PIL import Image
import os
import time

CACHE_DIR = "cache/" 

def clear_cache_on_restart():
    """Deletes all cached images on restart to match updated mappings."""
    if os.path.exists(CACHE_DIR):
        
        for file in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, file)
            if os.path.isfile(file_path):
                print(f"Removing cached file: {file_path}")
                os.remove(file_path)


def resize_image(image_path: str, width: int, height: int) -> str:
    """Resizes an image and caches it."""
    os.makedirs(CACHE_DIR, exist_ok=True) 
    cached_path = os.path.join(CACHE_DIR, f"{width}x{height}_{os.path.basename(image_path)}")

    if os.path.exists(cached_path):
        return cached_path  

    img = Image.open(image_path)
    img = img.resize((width, height))
    img.save(cached_path, "JPEG")  

    return cached_path


clear_cache_on_restart()

