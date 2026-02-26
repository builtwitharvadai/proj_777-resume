"""Plain text file extractor with encoding detection."""

import logging
from typing import Any, Dict, BinaryIO, List

from src.parsing.extractors.base import BaseExtractor
from src.parsing.exceptions import ExtractionFailedException

logger = logging.getLogger(__name__)


class TXTExtractor(BaseExtractor):
    """Plain text extractor with automatic encoding detection.

    Uses chardet for encoding detection to handle various text encodings
    (UTF-8, Latin-1, ASCII, etc.) and preserves line structure.
    """

    # Common encodings to try if chardet fails
    FALLBACK_ENCODINGS = ["utf-8", "latin-1", "cp1252", "ascii", "iso-8859-1"]

    def extract_text(self, file_obj: BinaryIO) -> str:
        """Extract text content from plain text file.

        Detects encoding automatically and handles various text encodings.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            str: Extracted text content

        Raises:
            ExtractionFailedException: If text extraction fails
        """
        logger.info(f"Extracting text from TXT file: {self.filename}")

        try:
            file_obj.seek(0)
            raw_content = file_obj.read()

            if not raw_content:
                logger.warning(f"File {self.filename} is empty")
                return ""

            # Detect encoding
            encoding = self._detect_encoding(raw_content)
            logger.debug(f"Detected encoding for {self.filename}: {encoding}")

            # Decode content
            try:
                text = raw_content.decode(encoding)
            except (UnicodeDecodeError, LookupError) as e:
                logger.warning(
                    f"Failed to decode {self.filename} with detected encoding "
                    f"{encoding}: {str(e)}, trying fallback encodings"
                )
                text = self._decode_with_fallback(raw_content)

            logger.info(
                f"Successfully extracted {len(text)} characters from {self.filename}"
            )

            return text

        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.filename}: {str(e)}",
                exc_info=True,
            )
            raise ExtractionFailedException(self.filename, "text", str(e))

    def extract_structured_data(self, file_obj: BinaryIO) -> Dict[str, Any]:
        """Extract structured information from text file.

        Args:
            file_obj: File object opened in binary mode

        Returns:
            Dict containing encoding, line count, and line structure info

        Raises:
            ExtractionFailedException: If structured data extraction fails
        """
        logger.info(f"Extracting structured data from TXT file: {self.filename}")

        structured_data: Dict[str, Any] = {
            "encoding": "unknown",
            "line_count": 0,
            "empty_line_count": 0,
            "character_count": 0,
            "word_count": 0,
        }

        try:
            file_obj.seek(0)
            raw_content = file_obj.read()

            if not raw_content:
                logger.info(f"File {self.filename} is empty")
                return structured_data

            # Detect and store encoding
            encoding = self._detect_encoding(raw_content)
            structured_data["encoding"] = encoding

            # Decode content
            try:
                text = raw_content.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                text = self._decode_with_fallback(raw_content)
                # Update encoding to what was actually used
                structured_data["encoding"] = "fallback"

            # Extract line structure
            lines = text.splitlines()
            structured_data["line_count"] = len(lines)
            structured_data["empty_line_count"] = sum(
                1 for line in lines if not line.strip()
            )

            # Character and word count
            structured_data["character_count"] = len(text)
            structured_data["word_count"] = len(text.split())

            logger.info(
                f"Extracted structured data from {self.filename}: "
                f"{structured_data['line_count']} lines, "
                f"{structured_data['word_count']} words, "
                f"encoding: {structured_data['encoding']}"
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

    def _detect_encoding(self, raw_content: bytes) -> str:
        """Detect file encoding using chardet.

        Args:
            raw_content: Raw bytes content

        Returns:
            str: Detected encoding name
        """
        try:
            import chardet

            result = chardet.detect(raw_content)
            encoding = result.get("encoding")
            confidence = result.get("confidence", 0)

            if encoding and confidence > 0.7:
                logger.debug(
                    f"chardet detected encoding {encoding} "
                    f"with confidence {confidence}"
                )
                return encoding.lower()
            else:
                logger.debug(
                    f"chardet confidence too low ({confidence}), "
                    f"defaulting to utf-8"
                )
                return "utf-8"

        except ImportError:
            logger.warning(
                "chardet library not installed, defaulting to utf-8 encoding"
            )
            return "utf-8"
        except Exception as e:
            logger.warning(
                f"Error detecting encoding for {self.filename}: {str(e)}, "
                f"defaulting to utf-8"
            )
            return "utf-8"

    def _decode_with_fallback(self, raw_content: bytes) -> str:
        """Try multiple encodings to decode content.

        Args:
            raw_content: Raw bytes content

        Returns:
            str: Decoded text content

        Raises:
            ExtractionFailedException: If all encoding attempts fail
        """
        last_error = None

        for encoding in self.FALLBACK_ENCODINGS:
            try:
                text = raw_content.decode(encoding)
                logger.info(
                    f"Successfully decoded {self.filename} using fallback "
                    f"encoding: {encoding}"
                )
                return text
            except (UnicodeDecodeError, LookupError) as e:
                logger.debug(
                    f"Failed to decode {self.filename} with {encoding}: {str(e)}"
                )
                last_error = e
                continue

        # If all encodings fail, try with errors='replace'
        try:
            text = raw_content.decode("utf-8", errors="replace")
            logger.warning(
                f"Decoded {self.filename} with errors='replace', "
                f"some characters may be lost"
            )
            return text
        except Exception as e:
            logger.error(
                f"All decoding attempts failed for {self.filename}: {str(e)}"
            )
            raise ExtractionFailedException(
                self.filename,
                "text",
                f"Failed to decode with any encoding. Last error: {last_error}",
            )
