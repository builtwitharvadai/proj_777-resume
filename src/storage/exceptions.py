"""Custom exceptions for storage operations."""


class StorageException(Exception):
    """Base exception for storage-related errors.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
    """

    def __init__(self, message: str, error_code: str = "STORAGE_ERROR") -> None:
        """Initialize storage exception.

        Args:
            message: Error message describing what went wrong
            error_code: Unique error code for categorization
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class VirusDetectedException(StorageException):
    """Exception raised when virus is detected in uploaded file.

    This exception is raised after virus scanning detects malware
    in an uploaded file. The file should be quarantined or deleted.
    """

    def __init__(self, filename: str, virus_name: str = None) -> None:
        """Initialize virus detected exception.

        Args:
            filename: Name of the infected file
            virus_name: Name of the detected virus (if available)
        """
        virus_info = f" ({virus_name})" if virus_name else ""
        message = f"Virus detected in file: {filename}{virus_info}"
        super().__init__(message, error_code="VIRUS_DETECTED")
        self.filename = filename
        self.virus_name = virus_name


class FileTooLargeException(StorageException):
    """Exception raised when uploaded file exceeds size limit.

    This exception is raised during file validation when the file
    size exceeds the configured maximum allowed size.
    """

    def __init__(self, filename: str, file_size: int, max_size: int) -> None:
        """Initialize file too large exception.

        Args:
            filename: Name of the file
            file_size: Actual file size in bytes
            max_size: Maximum allowed file size in bytes
        """
        message = (
            f"File '{filename}' size {file_size} bytes exceeds "
            f"maximum allowed size of {max_size} bytes"
        )
        super().__init__(message, error_code="FILE_TOO_LARGE")
        self.filename = filename
        self.file_size = file_size
        self.max_size = max_size


class UnsupportedFileTypeException(StorageException):
    """Exception raised when uploaded file type is not supported.

    This exception is raised during file validation when the file
    MIME type is not in the list of allowed file types.
    """

    def __init__(self, filename: str, mime_type: str, allowed_types: list) -> None:
        """Initialize unsupported file type exception.

        Args:
            filename: Name of the file
            mime_type: Detected MIME type of the file
            allowed_types: List of allowed MIME types
        """
        allowed_str = ", ".join(allowed_types)
        message = (
            f"File '{filename}' type '{mime_type}' is not supported. "
            f"Allowed types: {allowed_str}"
        )
        super().__init__(message, error_code="UNSUPPORTED_FILE_TYPE")
        self.filename = filename
        self.mime_type = mime_type
        self.allowed_types = allowed_types


class S3OperationException(StorageException):
    """Exception raised when S3 operations fail.

    This exception is raised when operations like upload, download,
    or delete fail on S3. It wraps the underlying error for debugging.
    """

    def __init__(self, operation: str, details: str, original_error: Exception = None) -> None:  # noqa: E501
        """Initialize S3 operation exception.

        Args:
            operation: Name of the S3 operation that failed
            details: Additional details about the failure
            original_error: Original exception that caused this error
        """
        message = f"S3 operation '{operation}' failed: {details}"
        super().__init__(message, error_code="S3_OPERATION_FAILED")
        self.operation = operation
        self.details = details
        self.original_error = original_error
