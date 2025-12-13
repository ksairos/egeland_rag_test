import base64

from fastapi import UploadFile


async def encode_image(image_file: UploadFile) -> str | None:
    """Кодирует картинку в base64"""
    if not image_file:
        return None
    image_bytes = image_file.file.read()
    return base64.b64encode(image_bytes).decode('utf-8')