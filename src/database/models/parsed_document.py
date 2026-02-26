"""Parsed document model for storing extracted content and structured data."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSON

from src.database.base import BaseModel


class ParsedDocument(BaseModel):
    """Parsed document model storing extracted text and structured data.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        document_id: Foreign key to documents table
        raw_text: Extracted raw text content from the document
        contact_info: JSON field containing extracted contact information
        work_experience: JSON field containing parsed work experience data
        education: JSON field containing education history
        skills: JSON field containing identified skills
        parsing_status: Status of parsing operation (pending, completed, failed)
        error_message: Error message if parsing failed
        parsed_at: Timestamp when parsing completed successfully
        created_at: Timestamp of record creation (inherited from BaseModel)
        updated_at: Timestamp of last update (inherited from BaseModel)
    """

    __tablename__ = "parsed_documents"

    document_id = Column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    raw_text = Column(
        Text,
        nullable=True,
    )

    contact_info = Column(
        JSON,
        nullable=True,
        default=dict,
    )

    work_experience = Column(
        JSON,
        nullable=True,
        default=list,
    )

    education = Column(
        JSON,
        nullable=True,
        default=list,
    )

    skills = Column(
        JSON,
        nullable=True,
        default=list,
    )

    parsing_status = Column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    parsed_at = Column(
        DateTime,
        nullable=True,
    )

    __table_args__ = (
        Index("ix_parsed_documents_document_id", "document_id"),
        Index("ix_parsed_documents_parsing_status", "parsing_status"),
        Index("ix_parsed_documents_parsed_at", "parsed_at"),
    )

    def __repr__(self) -> str:
        """String representation of ParsedDocument model.

        Returns:
            str: String representation showing document_id and parsing status
        """
        return (
            f"<ParsedDocument(id={self.id}, document_id={self.document_id}, "
            f"parsing_status={self.parsing_status})>"
        )
