"""Custom exceptions for AI operations and API failures."""


class AIException(Exception):
    """Base exception for AI service errors.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        error_code: str = "AI_ERROR",
        details: dict = None,
    ) -> None:
        """Initialize AIException.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the exception.

        Returns:
            str: Error message with error code
        """
        return f"[{self.error_code}] {self.message}"


class APIQuotaExceededException(AIException):
    """Exception raised when API quota is exceeded.

    Raised when the user has exceeded their API usage quota
    for the billing period.
    """

    def __init__(
        self,
        message: str = "API quota exceeded for the current billing period",
        details: dict = None,
    ) -> None:
        """Initialize APIQuotaExceededException.

        Args:
            message: Human-readable error message
            details: Additional error details including quota information
        """
        super().__init__(
            message=message,
            error_code="API_QUOTA_EXCEEDED",
            details=details,
        )


class ContentFilteredException(AIException):
    """Exception raised when content is filtered by AI provider.

    Raised when the AI provider's content filter blocks
    the request or response due to policy violations.
    """

    def __init__(
        self,
        message: str = "Content was filtered due to policy violations",
        details: dict = None,
    ) -> None:
        """Initialize ContentFilteredException.

        Args:
            message: Human-readable error message
            details: Additional error details including filter reason
        """
        super().__init__(
            message=message,
            error_code="CONTENT_FILTERED",
            details=details,
        )


class TokenLimitExceededException(AIException):
    """Exception raised when token limit is exceeded.

    Raised when the request exceeds the maximum token limit
    for the AI model being used.
    """

    def __init__(
        self,
        message: str = "Token limit exceeded for the selected model",
        details: dict = None,
    ) -> None:
        """Initialize TokenLimitExceededException.

        Args:
            message: Human-readable error message
            details: Additional error details including token counts
        """
        super().__init__(
            message=message,
            error_code="TOKEN_LIMIT_EXCEEDED",
            details=details,
        )


class AIServiceUnavailableException(AIException):
    """Exception raised when AI service is unavailable.

    Raised when the AI provider's service is temporarily unavailable
    or experiencing issues.
    """

    def __init__(
        self,
        message: str = "AI service is temporarily unavailable",
        details: dict = None,
    ) -> None:
        """Initialize AIServiceUnavailableException.

        Args:
            message: Human-readable error message
            details: Additional error details including retry information
        """
        super().__init__(
            message=message,
            error_code="AI_SERVICE_UNAVAILABLE",
            details=details,
        )
