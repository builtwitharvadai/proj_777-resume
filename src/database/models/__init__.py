"""Database models package.

Import all models here for Alembic auto-generation to detect them.
"""

from src.database.base import Base, BaseModel
from src.database.models.user import User

__all__ = ["Base", "BaseModel", "User"]
