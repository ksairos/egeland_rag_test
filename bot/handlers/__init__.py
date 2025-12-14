"""Import all routers and add them to routers_list."""

from .chat import chat_router
from .image import image_router
from .audio import audio_router

routers_list = [
    image_router,
    audio_router,
    chat_router,  # всегда в конце
]

__all__ = [
    "routers_list",
]
