import os
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)


def upload_file(file_obj, folder: str):
    # file_obj is Django UploadedFile
    res = cloudinary.uploader.upload(
        file_obj,
        folder=folder,
        resource_type="raw",  # important for PDFs
    )
    return {
        "public_id": res["public_id"],
        "url": res["secure_url"],
    }
