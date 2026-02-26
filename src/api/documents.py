"""Document management API endpoints."""

import logging
from typing import Any, Dict
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.rate_limit import UPLOAD_RATE_LIMIT, limiter
from src.api.schemas.documents import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
    PaginationMetadata,
)
from src.auth.dependencies import get_current_user
from src.database.connection import get_db
from src.database.models.user import User
from src.storage.exceptions import (
    FileTooLargeException,
    StorageException,
    UnsupportedFileTypeException,
    VirusDetectedException,
)
from src.storage.s3_client import S3Client
from src.storage.service import DocumentStorageService
from src.storage.virus_scanner import ClamAVScanner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents")


def get_document_service() -> DocumentStorageService:
    """Dependency to provide document storage service.

    Returns:
        DocumentStorageService: Configured document storage service
    """
    s3_client = S3Client()
    virus_scanner = ClamAVScanner()
    return DocumentStorageService(s3_client, virus_scanner)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description="Upload a document file with validation, virus scanning, and storage",
    responses={
        201: {
            "description": "Document uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "filename": "abc123.pdf",
                        "original_filename": "resume.pdf",
                        "file_size": 102400,
                        "mime_type": "application/pdf",
                        "upload_date": "2026-02-26T12:00:00Z",
                        "virus_scan_status": "clean",
                        "message": "Document uploaded successfully",
                    }
                }
            },
        },
        400: {"description": "Invalid file type or file too large"},
        401: {"description": "Authentication required"},
        413: {"description": "File too large"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(UPLOAD_RATE_LIMIT)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentStorageService = Depends(get_document_service),
) -> DocumentUploadResponse:
    """Upload a document file.

    Args:
        file: Uploaded file
        current_user: Authenticated user
        db: Database session
        service: Document storage service

    Returns:
        DocumentUploadResponse: Upload result with document metadata

    Raises:
        HTTPException: On validation or upload failure
    """
    logger.info(
        "Document upload requested",
        extra={
            "user_id": current_user.id,
            "filename": file.filename,
            "content_type": file.content_type,
        },
    )

    try:
        document = await service.upload_document(
            file.file,
            file.filename or "unknown",
            str(current_user.id),
            db,
        )

        logger.info(
            "Document uploaded successfully",
            extra={
                "document_id": document.id,
                "user_id": current_user.id,
                "filename": file.filename,
            },
        )

        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_size=document.file_size,
            mime_type=document.mime_type,
            upload_date=document.upload_date,
            virus_scan_status=document.virus_scan_status,
        )

    except FileTooLargeException as e:
        logger.warning(
            "File too large",
            extra={
                "user_id": current_user.id,
                "filename": file.filename,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        )

    except UnsupportedFileTypeException as e:
        logger.warning(
            "Unsupported file type",
            extra={
                "user_id": current_user.id,
                "filename": file.filename,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except VirusDetectedException as e:
        logger.error(
            "Virus detected in uploaded file",
            extra={
                "user_id": current_user.id,
                "filename": file.filename,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except StorageException as e:
        logger.error(
            "Storage operation failed",
            extra={
                "user_id": current_user.id,
                "filename": file.filename,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document. Please try again later.",
        )

    except Exception as e:
        logger.error(
            "Unexpected error during document upload",
            extra={
                "user_id": current_user.id,
                "filename": file.filename,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during upload",
        )


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="List user documents",
    description="Get a paginated list of documents for the authenticated user",
    responses={
        200: {
            "description": "List of documents with pagination",
            "content": {
                "application/json": {
                    "example": {
                        "documents": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "user_id": "user-123",
                                "filename": "abc123.pdf",
                                "original_filename": "resume.pdf",
                                "file_size": 102400,
                                "mime_type": "application/pdf",
                                "upload_date": "2026-02-26T12:00:00Z",
                                "virus_scan_status": "clean",
                                "virus_scan_date": "2026-02-26T12:00:10Z",
                                "is_processed": False,
                                "created_at": "2026-02-26T12:00:00Z",
                                "updated_at": "2026-02-26T12:00:10Z",
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "size": 10,
                            "total": 1,
                        },
                    }
                }
            },
        },
        401: {"description": "Authentication required"},
    },
)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentStorageService = Depends(get_document_service),
) -> DocumentListResponse:
    """List documents for the authenticated user.

    Args:
        page: Page number (1-indexed)
        size: Items per page
        current_user: Authenticated user
        db: Database session
        service: Document storage service

    Returns:
        DocumentListResponse: Paginated list of documents
    """
    logger.info(
        "Document list requested",
        extra={
            "user_id": current_user.id,
            "page": page,
            "size": size,
        },
    )

    try:
        offset = (page - 1) * size

        documents = await service.list_user_documents(
            str(current_user.id),
            db,
            limit=size,
            offset=offset,
        )

        # Get total count for pagination
        from sqlalchemy import func, select

        from src.database.models.document import Document

        count_result = await db.execute(
            select(func.count()).select_from(Document).where(Document.user_id == str(current_user.id))
        )
        total = count_result.scalar() or 0

        logger.info(
            "Document list retrieved",
            extra={
                "user_id": current_user.id,
                "count": len(documents),
                "total": total,
            },
        )

        return DocumentListResponse(
            documents=[DocumentResponse.model_validate(doc) for doc in documents],
            pagination=PaginationMetadata(
                page=page,
                size=size,
                total=total,
            ),
        )

    except Exception as e:
        logger.error(
            "Failed to list documents",
            extra={
                "user_id": current_user.id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents",
        )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
    description="Delete a document by ID. Only the owner can delete their documents.",
    responses={
        204: {"description": "Document deleted successfully"},
        401: {"description": "Authentication required"},
        404: {"description": "Document not found"},
    },
)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: DocumentStorageService = Depends(get_document_service),
) -> None:
    """Delete a document.

    Args:
        document_id: Document ID to delete
        current_user: Authenticated user
        db: Database session
        service: Document storage service

    Raises:
        HTTPException: If document not found or deletion fails
    """
    logger.info(
        "Document deletion requested",
        extra={
            "user_id": current_user.id,
            "document_id": str(document_id),
        },
    )

    try:
        await service.delete_document(
            str(document_id),
            str(current_user.id),
            db,
        )

        logger.info(
            "Document deleted successfully",
            extra={
                "user_id": current_user.id,
                "document_id": str(document_id),
            },
        )

    except ValueError as e:
        logger.warning(
            "Document not found for deletion",
            extra={
                "user_id": current_user.id,
                "document_id": str(document_id),
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    except Exception as e:
        logger.error(
            "Failed to delete document",
            extra={
                "user_id": current_user.id,
                "document_id": str(document_id),
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document",
        )
