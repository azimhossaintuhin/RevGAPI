import os 
from fastapi import UploadFile , HTTPException , status
from pathlib import Path
from decouple import config

UPLOAD_FOLDER = config("UPLOAD_FOLDER")


BASE_DIR = Path(__file__).parent.parent
IMAGE_UPLOAD_FOLDER = BASE_DIR / UPLOAD_FOLDER


ALLOWED_IMAGE_CONTENT_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024 # 5MB




def get_file_size(file: UploadFile) -> int:
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    return size

def validate_image_extension(file:UploadFile) -> bool:
    try:
        if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image content type")
        if get_file_size(file) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image size is too large")
        return True
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    


def save_image( folder:str ,name:str ,file:UploadFile) -> str:
    try:
        validate_image_extension(file)
        ext = file.filename.split(".")[-1]
        folder_path = os.path.join(IMAGE_UPLOAD_FOLDER, folder)
        os.makedirs(folder_path, exist_ok=True)
        file_name = f"{name}.{ext}"
        file_path = os.path.join(folder_path, file_name)
        print(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        return f"/{UPLOAD_FOLDER}/{folder}/{file_name}"
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
