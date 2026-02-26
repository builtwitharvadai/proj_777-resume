"""Document storage service orchestrating upload, validation, and metadata management."""  # noqa: E501

import logging
import uuid
from datetime import datetime
from typing import BinaryIO, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.document import Document
from src.storage.exceptions import VirusDetectedException
from src.storage.s3_client import S3Client
from src.storage.validators import validate_file_content, validate_file_size, validate_file_type  # noqa: E501
from src.storage.virus_scanner import ClamAVScanner

logger = logging.getLogger(__name__)


class DocumentStorageService:
    """Service for document upload, storage, and metadata management.

    Orchestrates file validation, virus scanning, S3 upload, and
    database operations for document management.

    Attributes:
        s3_client: S3 client for file storage operations
        virus_scanner: ClamAV scanner for virus detection
    """

    def __init__(
        self,
        s3_client: S3Client,
        virus_scanner: ClamAVScanner = None,
    ) -> None:
        """Initialize document storage service.

        Args:
            s3_client: Configured S3 client for file operations
            virus_scanner: Optional ClamAV scanner (if None, virus scanning is skipped)  # noqa: E501
        """
        self.s3_client = s3_client
        self.virus_scanner = virus_scanner

        logger.info(
            "Document storage service initialized",
            extra={
                "virus_scanning_enabled": virus_scanner is not None,
            },
        )

    async def upload_document(
        self,
        file: BinaryIO,
        filename: str,
        user_id: str,
        db: AsyncSession,
    ) -> Document:
        """Upload document with validation, scanning, and storage.

        Args:
            file: File-like object to upload
            filename: Original filename
            user_id: User ID who owns the document
            db: Database session for metadata storage

        Returns:
            Document: Created document record

        Raises:
            FileTooLargeException: If file exceeds size limit
            UnsupportedFileTypeException: If file type is not allowed
            VirusDetectedException: If virus is detected in file
            S3OperationException: If S3 upload fails

        Example:
            service = DocumentStorageService(s3_client, virus_scanner)
            with open("resume.pdf", "rb") as f:
                document = await service.upload_document(
                    f, "resume.pdf", user_id, db
                )
        """
        logger.info(
            "Starting document upload",
            extra={
                "filename": filename,
                "user_id": user_id,
            },
        )

        try:
            # Step 1: Validate file size
            file_size = validate_file_size(file, filename)

            logger.debug(
                "File size validated",
                extra={
                    "filename": filename,
                    "file_size": file_size,
                },
            )

            # Step 2: Validate file type
            mime_type = validate_file_type(file, filename)

            logger.debug(
                "File type validated",
                extra={
                    "filename": filename,
                    "mime_type": mime_type,
                },
            )

            # Step 3: Validate file content
            validate_file_content(file, filename, mime_type)

            logger.debug(
                "File content validated",
                extra={
                    "filename": filename,
                },
            )

            # Step 4: Virus scan (if scanner is configured)
            virus_scan_status = "pending"
            virus_scan_date = None

            if self.virus_scanner:
                try:
                    is_clean, scan_result = self.virus_scanner.scan_file(
                        file, filename
                    )

                    if not is_clean:
                        logger.warning(
                            "Virus detected in uploaded file",
                            extra={
                                "filename": filename,
                                "user_id": user_id,
                                "virus_name": scan_result,
                            },
                        )
                        raise VirusDetectedException(filename, scan_result)

                    virus_scan_status = "clean"
                    virus_scan_date = datetime.utcnow()

                    logger.info(
                        "Virus scan completed - file clean",
                        extra={
                            "filename": filename,
                            "user_id": user_id,
                        },
                    )

                except (ConnectionError, TimeoutError) as e:
                    logger.warning(
                        "Virus scanner unavailable, proceeding without scan",
                        extra={
                            "filename": filename,
                            "user_id": user_id,
                            "error": str(e),
                        },
                    )
                    virus_scan_status = "pending"

            # Step 5: Generate unique S3 key
            file_ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
            unique_filename = f"{uuid.uuid4()}.{file_ext}" if file_ext else str(uuid.uuid4())  # noqa: E501
            s3_key = f"users/{user_id}/documents/{unique_filename}"

            logger.debug(
                "Generated S3 key",
                extra={
                    "filename": filename,
                    "s3_key": s3_key,
                },
            )

            # Step 6: Upload to S3
            self.s3_client.upload_file(
                file,
                s3_key,
                mime_type,
                metadata={
                    "original_filename": filename,
                    "user_id": user_id,
                },
            )

            logger.info(
                "File uploaded to S3",
                extra={
                    "filename": filename,
                    "s3_key": s3_key,
                    "user_id": user_id,
                },
            )

            # Step 7: Create database record
            document = Document(
                user_id=user_id,
                filename=unique_filename,
                original_filename=filename,
                file_size=file_size,
                mime_type=mime_type,
                s3_key=s3_key,
                upload_date=datetime.utcnow(),
                virus_scan_status=virus_scan_status,
                virus_scan_date=virus_scan_date,
                is_processed=False,
            )

            db.add(document)
            await db.commit()
            await db.refresh(document)

            logger.info(
                "Document record created",
                extra={
                    "document_id": document.id,
                    "filename": filename,
                    "user_id": user_id,
                },
            )

            return document

        except Exception as e:
            logger.error(
                "Document upload failed",
                extra={
                    "filename": filename,
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise

    async def get_document(
        self,
        document_id: str,
        user_id: str,
        db: AsyncSession,
    ) -> Optional[Document]:
        """Get document by ID for specific user.

        Args:
            document_id: Document ID to retrieve
            user_id: User ID who owns the document
            db: Database session

        Returns:
            Optional[Document]: Document record if found, None otherwise

        Example:
            service = DocumentStorageService(s3_client)
            document = await service.get_document(doc_id, user_id, db)
        """
        try:
            result = await db.execute(
                select(Document).where(
                    Document.id == document_id,
                    Document.user_id == user_id,
                )
            )
            document = result.scalar_one_or_none()

            if document:
                logger.debug(
                    "Document retrieved",
                    extra={
                        "document_id": document_id,
                        "user_id": user_id,
                    },
                )
            else:
                logger.warning(
                    "Document not found",
                    extra={
                        "document_id": document_id,
                        "user_id": user_id,
                    },
                )

            return document

        except Exception as e:
            logger.error(
                "Failed to retrieve document",
                extra={
                    "document_id": document_id,
                    "user_id": user_id,
                    "error": str(e),
                },
            )
            raise

    async def delete_document(
        self,
        document_id: str,
        user_id: str,
        db: AsyncSession,
    ) -> bool:
        """Delete document from S3 and database.

        Args:
            document_id: Document ID to delete
            user_id: User ID who owns the document
            db: Database session

        Returns:
            bool: True if deletion successful

        Raises:
            ValueError: If document not found
            S3OperationException: If S3 deletion fails

        Example:
            service = DocumentStorageService(s3_client)
            success = await service.delete_document(doc_id, user_id, db)
        """
        try:
            logger.info(
                "Starting document deletion",
                extra={
                    "document_id": document_id,
                    "user_id": user_id,
                },
            )

            # Get document
            document = await self.get_document(document_id, user_id, db)

            if not document:
                logger.warning(
                    "Document not found for deletion",
                    extra={
                        "document_id": document_id,
                        "user_id": user_id,
                    },
                )
                raise ValueError(f"Document {document_id} not found")

            # Delete from S3
            self.s3_client.delete_file(document.s3_key)

            logger.info(
                "Document deleted from S3",
                extra={
                    "document_id": document_id,
                    "s3_key": document.s3_key,
                },
            )

            # Delete from database
            await db.delete(document)
            await db.commit()

            logger.info(
                "Document deleted successfully",
                extra={
                    "document_id": document_id,
                    "user_id": user_id,
                },
            )

            return True

        except Exception as e:
            logger.error(
                "Document deletion failed",
                extra={
                    "document_id": document_id,
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise

    async def list_user_documents(
        self,
        user_id: str,
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Document]:
        """List all documents for a user.

        Args:
            user_id: User ID to list documents for
            db: Database session
            limit: Maximum number of documents to return
            offset: Number of documents to skip

        Returns:
            List[Document]: List of document records

        Example:
            service = DocumentStorageService(s3_client)
            documents = await service.list_user_documents(user_id, db)
        """
        try:
            logger.debug(
                "Listing user documents",
                extra={
                    "user_id": user_id,
                    "limit": limit,
                    "offset": offset,
                },
            )

            result = await db.execute(
                select(Document)
                .where(Document.user_id == user_id)
                .order_by(Document.upload_date.desc())
                .limit(limit)
                .offset(offset)
            )

            documents = result.scalars().all()

            logger.info(
                "User documents retrieved",
                extra={
                    "user_id": user_id,
                    "count": len(documents),
                },
            )

            return list(documents)

        except Exception as e:
            logger.error(
                "Failed to list user documents",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                },
            )
            raise

    def get_document_download_url(
        self,
        document: Document,
        expiration: int = 3600,
    ) -> str:
        """Generate presigned URL for document download.

        Args:
            document: Document record
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Presigned URL for document download

        Example:
            service = DocumentStorageService(s3_client)
            url = service.get_document_download_url(document)
        """
        try:
            logger.debug(
                "Generating document download URL",
                extra={
                    "document_id": document.id,
                    "s3_key": document.s3_key,
                    "expiration": expiration,
                },
            )

            url = self.s3_client.generate_presigned_url(
                document.s3_key,
                expiration=expiration,
            )

            logger.info(
                "Download URL generated",
                extra={
                    "document_id": document.id,
                },
            )

            return url

        except Exception as e:
            logger.error(
                "Failed to generate download URL",
                extra={
                    "document_id": document.id,
                    "error": str(e),
                },
            )
            raise
