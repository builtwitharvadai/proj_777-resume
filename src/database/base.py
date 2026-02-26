"""Base model class with common fields and functionality."""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class BaseModel(Base):
    """Abstract base model with common fields for all models.

    Provides:
        - id: UUID primary key
        - created_at: Timestamp of creation
        - updated_at: Timestamp of last update
        - to_dict(): Serialization method
    """

    __abstract__ = True

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def to_dict(self, exclude: set = None) -> Dict[str, Any]:
        """Convert model instance to dictionary.

        Args:
            exclude: Set of field names to exclude from output

        Returns:
            Dict[str, Any]: Dictionary representation of the model

        Example:
            user = User(email="test@example.com")
            user_dict = user.to_dict(exclude={"hashed_password"})
        """
        if exclude is None:
            exclude = set()

        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)

                # Handle datetime serialization
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                else:
                    result[column.name] = value

        return result

    def update_from_dict(self, data: Dict[str, Any], exclude: set = None) -> None:
        """Update model fields from dictionary.

        Args:
            data: Dictionary with field values to update
            exclude: Set of field names to exclude from update

        Example:
            user = User.query.get(user_id)
            user.update_from_dict({"email": "new@example.com"})
        """
        if exclude is None:
            exclude = {"id", "created_at"}
        else:
            exclude = exclude | {"id", "created_at"}

        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                setattr(self, key, value)

        # Update timestamp
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        """String representation of the model.

        Returns:
            str: String representation showing class name and id
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
