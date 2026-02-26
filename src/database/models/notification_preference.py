"""NotificationPreference model for user notification settings."""

from sqlalchemy import Boolean, Column, ForeignKey, Index, JSON, String

from src.database.base import BaseModel


class NotificationPreference(BaseModel):
    """NotificationPreference model for storing user notification preferences.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        user_id: Foreign key to users table
        email_enabled: Flag for email notifications
        in_app_enabled: Flag for in-app notifications
        digest_frequency: Frequency for digest emails (daily/weekly/never)
        categories: JSON field for notification categories
        created_at: Timestamp of creation (inherited from BaseModel)
        updated_at: Timestamp of last update (inherited from BaseModel)
    """

    __tablename__ = "notification_preferences"

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    email_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    in_app_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    digest_frequency = Column(
        String(20),
        default="daily",
        nullable=False,
    )

    categories = Column(
        JSON,
        default=dict,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_notification_preferences_user_id", "user_id", unique=True),
    )

    def __repr__(self) -> str:
        """String representation of NotificationPreference model.

        Returns:
            str: String representation showing user_id and enabled flags
        """
        return (
            f"<NotificationPreference(id={self.id}, user_id={self.user_id}, "
            f"email_enabled={self.email_enabled}, "
            f"in_app_enabled={self.in_app_enabled}, "
            f"digest_frequency={self.digest_frequency})>"
        )
