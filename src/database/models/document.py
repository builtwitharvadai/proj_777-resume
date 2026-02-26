"""Document model for file metadata and storage tracking."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String

from src.database.base import BaseModel


class Document(BaseModel):
    """Document model with metadata and relationships to user.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        user_id: Foreign key to users table
        filename: Sanitized filename used in storage
        original_filename: Original filename from upload
        file_size: File size in bytes
        mime_type: MIME type of the file
        s3_key: S3 object key for file location
        upload_date: Timestamp of successful upload
        virus_scan_status: Status of virus scan (pending, clean, infected)
        virus_scan_date: Timestamp of virus scan completion
        is_processed: Flag indicating if document processing is complete
        created_at: Timestamp of record creation (inherited from BaseModel)
        updated_at: Timestamp of last update (inherited from BaseModel)
    """

    __tablename__ = "documents"

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    filename = Column(
        String(255),
        nullable=False,
    )

    original_filename = Column(
        String(255),
        nullable=False,
    )

    file_size = Column(
        Integer,
        nullable=False,
    )

    mime_type = Column(
        String(100),
        nullable=False,
    )

    s3_key = Column(
        String(512),
        nullable=False,
        unique=True,
    )

    upload_date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    virus_scan_status = Column(
        String(20),
        default="pending",
        nullable=False,
    )

    virus_scan_date = Column(
        DateTime,
        nullable=True,
    )

    is_processed = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_documents_user_id_upload_date", "user_id", "upload_date"),
        Index("ix_documents_virus_scan_status", "virus_scan_status"),
        Index("ix_documents_is_processed", "is_processed"),
    )

    def __repr__(self) -> str:
        """String representation of Document model.

        Returns:
            str: String representation showing filename and user
        """
        return (
            f"<Document(id={self.id}, filename={self.filename}, "
            f"user_id={self.user_id}, virus_scan_status={self.virus_scan_status})>"
        )
