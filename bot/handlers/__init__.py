"""Import all routers and add them to routers_list."""

from .chat import chat_router

routers_list = [
    chat_router,  # всегда в конце
]

__all__ = [
    "routers_list",
]
