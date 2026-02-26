"""Base extractor class defining interface for document parsing."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, BinaryIO

from src.parsing.exceptions import ExtractionFailedException

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Abstract base class for document text and data extractors.

    This class defines the common interface that all document extractors
    must implement. Subclasses should implement specific extraction logic
    for different file formats (PDF, DOCX, TXT, etc.).
    """

    def __init__(self, filename: str) -> None:
        """Initialize the base extractor.

        Args:
            filename: Name of the file being extracted
        """
        self.filename = filename
        logger.debug(f"Initialized {self.__class__.__name__} for file: {filename}")

    @abstractmethod
    def extract_text(self, file_obj: BinaryIO) -> str:
        """Extract raw text content from document.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            str: Extracted raw text content

        Raises:
            ExtractionFailedException: If text extraction fails
            CorruptedFileException: If file is corrupted or invalid
        """
        pass

    @abstractmethod
    def extract_structured_data(self, file_obj: BinaryIO) -> Dict[str, Any]:
        """Extract structured metadata and data from document.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            Dict[str, Any]: Dictionary containing extracted structured data
                such as metadata, formatting information, tables, etc.

        Raises:
            ExtractionFailedException: If structured data extraction fails
            CorruptedFileException: If file is corrupted or invalid
        """
        pass

    def validate_file(self, file_obj: BinaryIO) -> bool:
        """Validate that the file can be processed by this extractor.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            bool: True if file is valid for this extractor

        Raises:
            CorruptedFileException: If file validation fails
        """
        # Default implementation - subclasses can override for specific validation
        if not file_obj:
            logger.error(f"Invalid file object for {self.filename}")
            return False

        try:
            # Check if file is readable
            current_pos = file_obj.tell()
            file_obj.seek(0, 2)  # Seek to end
            file_size = file_obj.tell()
            file_obj.seek(current_pos)  # Reset position

            if file_size == 0:
                logger.warning(f"File {self.filename} is empty")
                return False

            return True
        except Exception as e:
            logger.error(
                f"File validation failed for {self.filename}: {str(e)}",
                exc_info=True,
            )
            return False

    def __repr__(self) -> str:
        """String representation of the extractor.

        Returns:
            str: String representation showing class name and filename
        """
        return f"<{self.__class__.__name__}(filename={self.filename})>"
