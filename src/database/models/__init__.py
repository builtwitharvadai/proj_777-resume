"""Database models package.

Import all models here for Alembic auto-generation to detect them.
"""

from src.database.base import Base, BaseModel
from src.database.models.user import User
from src.database.models.conversation import Conversation
from src.database.models.message import Message
from src.database.models.message_rating import MessageRating

__all__ = ["Base", "BaseModel", "User", "Conversation", "Message", "MessageRating"]
