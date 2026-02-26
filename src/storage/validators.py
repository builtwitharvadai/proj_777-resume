"""File validation utilities for type, size, and content checking."""

import logging
import magic
from typing import BinaryIO

from src.storage.exceptions import FileTooLargeException, UnsupportedFileTypeException

logger = logging.getLogger(__name__)

# Supported file formats with 10MB size limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
    "application/msword",  # DOC
    "text/plain",
}

MIME_TYPE_EXTENSIONS = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",  # noqa: E501
    "application/msword": ".doc",
    "text/plain": ".txt",
}


def validate_file_size(
    file: BinaryIO,
    filename: str,
    max_size: int = MAX_FILE_SIZE,
) -> int:
    """Validate file size against maximum allowed size.

    Args:
        file: File-like object to validate
        filename: Original filename for error messages
        max_size: Maximum allowed file size in bytes

    Returns:
        int: Actual file size in bytes

    Raises:
        FileTooLargeException: If file size exceeds max_size

    Example:
        with open("document.pdf", "rb") as f:
            size = validate_file_size(f, "document.pdf")
    """
    try:
        # Seek to end to get file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        logger.debug(
            "File size validation",
            extra={
                "filename": filename,
                "file_size": file_size,
                "max_size": max_size,
            },
        )

        if file_size > max_size:
            logger.warning(
                "File size exceeded limit",
                extra={
                    "filename": filename,
                    "file_size": file_size,
                    "max_size": max_size,
                },
            )
            raise FileTooLargeException(filename, file_size, max_size)

        return file_size

    except (OSError, IOError) as e:
        logger.error(
            "Error reading file size",
            extra={
                "filename": filename,
                "error": str(e),
            },
        )
        raise


def validate_file_type(file: BinaryIO, filename: str) -> str:
    """Validate file MIME type using python-magic.

    Args:
        file: File-like object to validate
        filename: Original filename for error messages

    Returns:
        str: Detected MIME type

    Raises:
        UnsupportedFileTypeException: If MIME type is not in ALLOWED_MIME_TYPES

    Example:
        with open("document.pdf", "rb") as f:
            mime_type = validate_file_type(f, "document.pdf")
    """
    try:
        # Read first 2048 bytes for MIME type detection
        file.seek(0)
        file_header = file.read(2048)
        file.seek(0)  # Reset to beginning

        # Detect MIME type using python-magic
        mime = magic.Magic(mime=True)
        detected_mime_type = mime.from_buffer(file_header)

        logger.debug(
            "File type detection",
            extra={
                "filename": filename,
                "detected_mime_type": detected_mime_type,
            },
        )

        if detected_mime_type not in ALLOWED_MIME_TYPES:
            logger.warning(
                "Unsupported file type",
                extra={
                    "filename": filename,
                    "detected_mime_type": detected_mime_type,
                    "allowed_types": list(ALLOWED_MIME_TYPES),
                },
            )
            raise UnsupportedFileTypeException(
                filename,
                detected_mime_type,
                list(ALLOWED_MIME_TYPES),
            )

        return detected_mime_type

    except (OSError, IOError) as e:
        logger.error(
            "Error detecting file type",
            extra={
                "filename": filename,
                "error": str(e),
            },
        )
        raise


def validate_file_content(file: BinaryIO, filename: str, mime_type: str) -> bool:
    """Validate file content integrity and structure.

    Performs additional content validation beyond MIME type checking,
    such as verifying file headers and basic structure.

    Args:
        file: File-like object to validate
        filename: Original filename for error messages
        mime_type: Already validated MIME type

    Returns:
        bool: True if file content is valid

    Raises:
        ValueError: If file content is corrupted or invalid

    Example:
        with open("document.pdf", "rb") as f:
            mime_type = validate_file_type(f, "document.pdf")
            is_valid = validate_file_content(f, "document.pdf", mime_type)
    """
    try:
        file.seek(0)

        # Check for empty file
        if file.tell() == 0 and not file.read(1):
            logger.warning(
                "Empty file detected",
                extra={
                    "filename": filename,
                    "mime_type": mime_type,
                },
            )
            raise ValueError(f"File '{filename}' is empty")

        file.seek(0)

        # Basic content validation based on MIME type
        if mime_type == "application/pdf":
            # PDF files should start with %PDF
            header = file.read(4)
            if header != b"%PDF":
                logger.warning(
                    "Invalid PDF header",
                    extra={
                        "filename": filename,
                        "header": header,
                    },
                )
                raise ValueError(f"File '{filename}' has invalid PDF structure")

        elif mime_type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ]:
            # DOCX/DOC files are ZIP-based or OLE-based
            header = file.read(4)
            # ZIP signature (DOCX) or OLE signature (DOC)
            if header not in [b"PK\x03\x04", b"\xd0\xcf\x11\xe0"]:
                logger.warning(
                    "Invalid Word document header",
                    extra={
                        "filename": filename,
                        "header": header,
                    },
                )
                raise ValueError(
                    f"File '{filename}' has invalid Word document structure"
                )

        file.seek(0)  # Reset to beginning

        logger.info(
            "File content validation passed",
            extra={
                "filename": filename,
                "mime_type": mime_type,
            },
        )

        return True

    except (OSError, IOError) as e:
        logger.error(
            "Error validating file content",
            extra={
                "filename": filename,
                "error": str(e),
            },
        )
        raise
