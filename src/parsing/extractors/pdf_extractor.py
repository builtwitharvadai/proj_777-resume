"""PDF document extractor using PyPDF2 and pdfplumber."""

import logging
from typing import Any, Dict, BinaryIO, List

from src.parsing.extractors.base import BaseExtractor
from src.parsing.exceptions import (
    CorruptedFileException,
    ExtractionFailedException,
)

logger = logging.getLogger(__name__)


class PDFExtractor(BaseExtractor):
    """PDF extractor using PyPDF2 with pdfplumber fallback.

    Extracts text content and structured data from PDF documents.
    Handles password-protected PDFs, table extraction, and metadata.
    """

    def __init__(self, filename: str, password: str = None) -> None:
        """Initialize PDF extractor.

        Args:
            filename: Name of the PDF file
            password: Optional password for encrypted PDFs
        """
        super().__init__(filename)
        self.password = password

    def extract_text(self, file_obj: BinaryIO) -> str:
        """Extract text content from PDF file.

        Uses PyPDF2 as primary extraction method and pdfplumber as fallback.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            str: Extracted text content

        Raises:
            CorruptedFileException: If PDF is corrupted
            ExtractionFailedException: If text extraction fails
        """
        logger.info(f"Extracting text from PDF: {self.filename}")

        try:
            # Try PyPDF2 first
            text = self._extract_with_pypdf2(file_obj)
            if text and len(text.strip()) > 0:
                logger.info(
                    f"Successfully extracted {len(text)} characters "
                    f"from {self.filename} using PyPDF2"
                )
                return text
        except Exception as e:
            logger.warning(
                f"PyPDF2 extraction failed for {self.filename}: {str(e)}, "
                f"trying pdfplumber fallback"
            )

        # Fallback to pdfplumber
        try:
            file_obj.seek(0)
            text = self._extract_with_pdfplumber(file_obj)
            if text:
                logger.info(
                    f"Successfully extracted {len(text)} characters "
                    f"from {self.filename} using pdfplumber"
                )
                return text
        except Exception as e:
            logger.error(
                f"Pdfplumber extraction also failed for {self.filename}: {str(e)}",
                exc_info=True,
            )

        raise ExtractionFailedException(
            self.filename,
            "text",
            "Both PyPDF2 and pdfplumber extraction methods failed",
        )

    def extract_structured_data(self, file_obj: BinaryIO) -> Dict[str, Any]:
        """Extract structured metadata and data from PDF.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            Dict containing metadata, page count, tables, etc.

        Raises:
            ExtractionFailedException: If structured data extraction fails
        """
        logger.info(f"Extracting structured data from PDF: {self.filename}")

        structured_data: Dict[str, Any] = {
            "metadata": {},
            "page_count": 0,
            "tables": [],
            "is_encrypted": False,
        }

        try:
            # Extract metadata using PyPDF2
            metadata = self._extract_metadata_pypdf2(file_obj)
            structured_data["metadata"] = metadata
            structured_data["is_encrypted"] = metadata.get("encrypted", False)

            # Extract tables using pdfplumber
            file_obj.seek(0)
            tables = self._extract_tables_pdfplumber(file_obj)
            structured_data["tables"] = tables

            # Get page count
            file_obj.seek(0)
            page_count = self._get_page_count(file_obj)
            structured_data["page_count"] = page_count

            logger.info(
                f"Extracted structured data from {self.filename}: "
                f"{page_count} pages, {len(tables)} tables"
            )

            return structured_data

        except Exception as e:
            logger.error(
                f"Failed to extract structured data from {self.filename}: {str(e)}",
                exc_info=True,
            )
            raise ExtractionFailedException(
                self.filename, "structured_data", str(e)
            )

    def _extract_with_pypdf2(self, file_obj: BinaryIO) -> str:
        """Extract text using PyPDF2.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            str: Extracted text

        Raises:
            Exception: If extraction fails
        """
        try:
            import PyPDF2
        except ImportError:
            logger.error("PyPDF2 library not installed")
            raise ExtractionFailedException(
                self.filename, "text", "PyPDF2 library not available"
            )

        try:
            file_obj.seek(0)
            pdf_reader = PyPDF2.PdfReader(file_obj)

            # Handle encrypted PDFs
            if pdf_reader.is_encrypted:
                if self.password:
                    pdf_reader.decrypt(self.password)
                else:
                    logger.warning(f"PDF {self.filename} is encrypted, no password provided")  # noqa: E501

            text_parts: List[str] = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(
                        f"Failed to extract page {page_num} from {self.filename}: {str(e)}"  # noqa: E501
                    )

            return "\n".join(text_parts)

        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"PDF read error for {self.filename}: {str(e)}")
            raise CorruptedFileException(
                self.filename, f"PDF read error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"PyPDF2 extraction error for {self.filename}: {str(e)}")
            raise

    def _extract_with_pdfplumber(self, file_obj: BinaryIO) -> str:
        """Extract text using pdfplumber as fallback.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            str: Extracted text

        Raises:
            Exception: If extraction fails
        """
        try:
            import pdfplumber
        except ImportError:
            logger.error("pdfplumber library not installed")
            raise ExtractionFailedException(
                self.filename, "text", "pdfplumber library not available"
            )

        try:
            file_obj.seek(0)
            text_parts: List[str] = []

            with pdfplumber.open(file_obj) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    except Exception as e:
                        logger.warning(
                            f"Failed to extract page {page_num} from {self.filename}: {str(e)}"  # noqa: E501
                        )

            return "\n".join(text_parts)

        except Exception as e:
            logger.error(f"pdfplumber extraction error for {self.filename}: {str(e)}")  # noqa: E501
            raise

    def _extract_metadata_pypdf2(self, file_obj: BinaryIO) -> Dict[str, Any]:
        """Extract metadata using PyPDF2.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            Dict containing PDF metadata
        """
        try:
            import PyPDF2

            file_obj.seek(0)
            pdf_reader = PyPDF2.PdfReader(file_obj)

            metadata: Dict[str, Any] = {}

            if pdf_reader.metadata:
                for key, value in pdf_reader.metadata.items():
                    # Remove leading slash from metadata keys
                    clean_key = key.lstrip("/") if isinstance(key, str) else str(key)
                    metadata[clean_key] = str(value) if value else None

            metadata["encrypted"] = pdf_reader.is_encrypted
            metadata["page_count"] = len(pdf_reader.pages)

            return metadata

        except Exception as e:
            logger.warning(f"Failed to extract metadata from {self.filename}: {str(e)}")  # noqa: E501
            return {"encrypted": False, "page_count": 0}

    def _extract_tables_pdfplumber(self, file_obj: BinaryIO) -> List[Dict[str, Any]]:
        """Extract tables using pdfplumber.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            List of dictionaries containing table data
        """
        try:
            import pdfplumber

            file_obj.seek(0)
            tables_data: List[Dict[str, Any]] = []

            with pdfplumber.open(file_obj) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        tables = page.extract_tables()
                        if tables:
                            for table_idx, table in enumerate(tables):
                                tables_data.append(
                                    {
                                        "page": page_num + 1,
                                        "table_index": table_idx,
                                        "data": table,
                                        "row_count": len(table) if table else 0,
                                    }
                                )
                    except Exception as e:
                        logger.warning(
                            f"Failed to extract tables from page {page_num} "
                            f"of {self.filename}: {str(e)}"
                        )

            return tables_data

        except Exception as e:
            logger.warning(f"Failed to extract tables from {self.filename}: {str(e)}")  # noqa: E501
            return []

    def _get_page_count(self, file_obj: BinaryIO) -> int:
        """Get page count from PDF.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            int: Number of pages in the PDF
        """
        try:
            import PyPDF2

            file_obj.seek(0)
            pdf_reader = PyPDF2.PdfReader(file_obj)
            return len(pdf_reader.pages)

        except Exception as e:
            logger.warning(f"Failed to get page count from {self.filename}: {str(e)}")  # noqa: E501
            return 0
