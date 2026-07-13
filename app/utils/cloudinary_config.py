import cloudinary
import cloudinary.uploader
import os
from fastapi import UploadFile

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_image_to_cloudinary(file: UploadFile, folder: str = "dropbox") -> str:
    """
    Uploads an image to Cloudinary and returns the secure URL.
    """
    try:
        result = cloudinary.uploader.upload(file.file, folder=folder)
        return result.get("secure_url")
    except Exception as e:
        raise Exception(f"Failed to upload image to Cloudinary: {str(e)}")
