import base64


def encode_image(image_bytes: bytes) -> str:
    """Кодирует картинку в base64"""
    return base64.b64encode(image_bytes).decode("utf-8")
