"""Resume template model for storing template configurations and styles."""

import logging
from sqlalchemy import Boolean, Column, Index, String
from sqlalchemy.dialects.postgresql import JSON

from src.database.base import BaseModel

logger = logging.getLogger(__name__)


class ResumeTemplate(BaseModel):
    """Resume template model for storing template configurations and styles.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        name: Template name (e.g., "Modern Professional")
        style: Template style identifier (modern/classic/executive/creative)
        template_data: JSON field containing template configuration
        sections_config: JSON field containing sections configuration
        is_active: Flag indicating if template is active and available
        created_at: Timestamp of creation (inherited from BaseModel)
        updated_at: Timestamp of last update (inherited from BaseModel)
    """

    __tablename__ = "resume_templates"

    name = Column(
        String(255),
        nullable=False,
        index=True,
    )

    style = Column(
        String(50),
        nullable=False,
        index=True,
    )

    template_data = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    sections_config = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index("ix_resume_templates_style_active", "style", "is_active"),
        Index("ix_resume_templates_name", "name"),
    )

    def __repr__(self) -> str:
        """String representation of ResumeTemplate model.

        Returns:
            str: String representation showing name and style
        """
        return (
            f"<ResumeTemplate(id={self.id}, name={self.name}, "
            f"style={self.style}, is_active={self.is_active})>"
        )
