"""Pydantic schemas for document API request and response models."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """Schema for document response.

    Attributes:
        id: Document unique identifier
        user_id: User who owns the document
        filename: Sanitized filename
        original_filename: Original filename from upload
        file_size: File size in bytes
        mime_type: MIME type of the file
        upload_date: Timestamp of upload
        virus_scan_status: Status of virus scan
        virus_scan_date: Optional timestamp of virus scan
        is_processed: Flag indicating if document is processed
        created_at: Timestamp of record creation
        updated_at: Timestamp of last update
    """

    id: UUID = Field(..., description="Document unique identifier")
    user_id: str = Field(..., description="User ID who owns the document")
    filename: str = Field(..., description="Sanitized filename")
    original_filename: str = Field(..., description="Original filename from upload")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    upload_date: datetime = Field(..., description="Timestamp of upload")
    virus_scan_status: str = Field(..., description="Virus scan status")
    virus_scan_date: Optional[datetime] = Field(
        None, description="Timestamp of virus scan"
    )
    is_processed: bool = Field(..., description="Document processing status")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response.

    Attributes:
        id: Document unique identifier
        filename: Sanitized filename
        original_filename: Original filename from upload
        file_size: File size in bytes
        mime_type: MIME type of the file
        upload_date: Timestamp of upload
        virus_scan_status: Status of virus scan
        message: Success message
    """

    id: UUID = Field(..., description="Document unique identifier")
    filename: str = Field(..., description="Sanitized filename")
    original_filename: str = Field(..., description="Original filename from upload")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    upload_date: datetime = Field(..., description="Timestamp of upload")
    virus_scan_status: str = Field(..., description="Virus scan status")
    message: str = Field(
        default="Document uploaded successfully", description="Success message"
    )


class PaginationMetadata(BaseModel):
    """Schema for pagination metadata.

    Attributes:
        page: Current page number (1-indexed)
        size: Number of items per page
        total: Total number of items
    """

    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, le=100, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")


class DocumentListResponse(BaseModel):
    """Schema for paginated document list response.

    Attributes:
        documents: List of document responses
        pagination: Pagination metadata
    """

    documents: List[DocumentResponse] = Field(..., description="List of documents")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")
