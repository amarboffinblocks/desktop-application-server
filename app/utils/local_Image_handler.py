import os
from fastapi import UploadFile
from typing import List
import aiofiles
import logging

logger = logging.getLogger(__name__)

async def save_single_image(folder_path: str, sub_folder:str, filename: str, file: UploadFile) -> str:
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, sub_folder)
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Failed to save image {filename}: {e}")
        raise
    return file_path




async def save_gallery_images(folder_path: str, files: List[UploadFile]) -> List[str]:
    os.makedirs(folder_path, exist_ok=True)
    paths = []
    for file in files:
        path = os.path.join(folder_path, "gallery")
        try:
            async with aiofiles.open(path, "wb") as f:
                while chunk := await file.read(1024 * 1024):
                    await f.write(chunk)
        except Exception as e:
            logger.error(f"Failed to save image {file.filename}: {e}")
            raise
        paths.append(path)
    return paths

def delete_file(path: str) -> None:
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            logger.error(f"Failed to delete file {path}: {e}")
