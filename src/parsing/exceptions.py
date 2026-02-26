"""Custom exceptions for document parsing operations."""


class ParsingException(Exception):
    """Base exception for parsing-related errors.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
    """

    def __init__(self, message: str, error_code: str = "PARSING_ERROR") -> None:
        """Initialize parsing exception.

        Args:
            message: Error message describing what went wrong
            error_code: Unique error code for categorization
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class UnsupportedFormatException(ParsingException):
    """Exception raised when document format is not supported.

    This exception is raised when attempting to parse a document
    with a format that is not supported by the parsing service.
    """

    def __init__(self, filename: str, mime_type: str) -> None:
        """Initialize unsupported format exception.

        Args:
            filename: Name of the file
            mime_type: MIME type of the file
        """
        message = (
            f"Document format '{mime_type}' for file '{filename}' "
            f"is not supported for parsing"
        )
        super().__init__(message, error_code="UNSUPPORTED_FORMAT")
        self.filename = filename
        self.mime_type = mime_type


class CorruptedFileException(ParsingException):
    """Exception raised when document file is corrupted.

    This exception is raised when the document file cannot be read
    or parsed due to corruption or invalid structure.
    """

    def __init__(self, filename: str, details: str = None) -> None:
        """Initialize corrupted file exception.

        Args:
            filename: Name of the file
            details: Additional details about the corruption
        """
        detail_info = f": {details}" if details else ""
        message = f"Document file '{filename}' is corrupted or invalid{detail_info}"
        super().__init__(message, error_code="CORRUPTED_FILE")
        self.filename = filename
        self.details = details


class ExtractionFailedException(ParsingException):
    """Exception raised when content extraction fails.

    This exception is raised when the extraction of text or structured
    data from a document fails unexpectedly during parsing.
    """

    def __init__(
        self, filename: str, extraction_type: str, details: str = None
    ) -> None:
        """Initialize extraction failed exception.

        Args:
            filename: Name of the file
            extraction_type: Type of extraction that failed (e.g., 'text', 'metadata')
            details: Additional details about the failure
        """
        detail_info = f": {details}" if details else ""
        message = (
            f"Failed to extract {extraction_type} from document "
            f"'{filename}'{detail_info}"
        )
        super().__init__(message, error_code="EXTRACTION_FAILED")
        self.filename = filename
        self.extraction_type = extraction_type
        self.details = details
