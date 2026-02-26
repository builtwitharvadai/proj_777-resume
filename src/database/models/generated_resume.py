"""Generated resume tracking model with version history."""

import logging
from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON

from src.database.base import BaseModel

logger = logging.getLogger(__name__)


class GeneratedResume(BaseModel):
    """Generated resume model for tracking resume generation and versions.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        user_id: Foreign key to users table
        template_id: Foreign key to resume_templates table
        ai_generation_id: Foreign key to ai_generations table (optional)
        title: Resume title or name
        content_data: JSON field containing resume content
        pdf_s3_key: S3 key for generated PDF file
        docx_s3_key: S3 key for generated DOCX file
        version: Version number for this resume
        is_active: Flag indicating if this is the active version
        created_at: Timestamp of creation (inherited from BaseModel)
        updated_at: Timestamp of last update (inherited from BaseModel)
    """

    __tablename__ = "generated_resumes"

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    template_id = Column(
        String(36),
        ForeignKey("resume_templates.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    ai_generation_id = Column(
        String(36),
        ForeignKey("ai_generations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    content_data = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    pdf_s3_key = Column(
        String(500),
        nullable=True,
    )

    docx_s3_key = Column(
        String(500),
        nullable=True,
    )

    version = Column(
        Integer,
        nullable=False,
        default=1,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index("ix_generated_resumes_user_id_created_at", "user_id", "created_at"),
        Index("ix_generated_resumes_user_id_is_active", "user_id", "is_active"),
        Index("ix_generated_resumes_template_id", "template_id"),
        Index("ix_generated_resumes_ai_generation_id", "ai_generation_id"),
    )

    def __repr__(self) -> str:
        """String representation of GeneratedResume model.

        Returns:
            str: String representation showing title and version
        """
        return (
            f"<GeneratedResume(id={self.id}, user_id={self.user_id}, "
            f"title={self.title}, version={self.version}, is_active={self.is_active})>"
        )
