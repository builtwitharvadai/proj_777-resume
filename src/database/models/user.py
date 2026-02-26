"""User model for authentication and user management."""

from sqlalchemy import Boolean, Column, Index, String

from src.database.base import BaseModel


class User(BaseModel):
    """User model with authentication fields.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        email: Unique email address for the user
        hashed_password: Hashed password for authentication
        email_verified: Flag indicating if email has been verified
        created_at: Timestamp of user creation (inherited from BaseModel)
        updated_at: Timestamp of last update (inherited from BaseModel)
    """

    __tablename__ = "users"

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password = Column(
        String(255),
        nullable=False,
    )

    email_verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_users_email_verified", "email", "email_verified"),
    )

    def __repr__(self) -> str:
        """String representation of User model.

        Returns:
            str: String representation showing email and verification status
        """
        return (
            f"<User(id={self.id}, email={self.email}, "
            f"email_verified={self.email_verified})>"
        )
