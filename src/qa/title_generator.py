"""Automatic conversation title generation from first question."""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class TitleGenerator:
    """Generate concise conversation titles from user questions.

    Uses NLP techniques and heuristics to create descriptive titles
    from user questions, with fallback titles and length limits.

    Attributes:
        max_title_length: Maximum length for generated titles
        min_title_length: Minimum length for generated titles
    """

    # Common question words to remove from titles
    QUESTION_WORDS = {
        "how",
        "what",
        "when",
        "where",
        "why",
        "who",
        "which",
        "can",
        "could",
        "should",
        "would",
        "do",
        "does",
        "is",
        "are",
        "was",
        "were",
    }

    # Common stopwords to remove
    STOPWORDS = {
        "a",
        "an",
        "the",
        "this",
        "that",
        "these",
        "those",
        "i",
        "me",
        "my",
        "you",
        "your",
        "to",
        "from",
        "for",
        "about",
        "with",
        "in",
        "on",
        "at",
    }

    def __init__(
        self,
        max_title_length: int = 100,
        min_title_length: int = 10,
    ) -> None:
        """Initialize TitleGenerator.

        Args:
            max_title_length: Maximum length for generated titles
            min_title_length: Minimum length for generated titles
        """
        self.max_title_length = max_title_length
        self.min_title_length = min_title_length

        logger.info(
            f"TitleGenerator initialized with max_length: {max_title_length}, "
            f"min_length: {min_title_length}"
        )

    def generate_title(self, question: str, category: Optional[str] = None) -> str:
        """Generate a concise, descriptive title from user question.

        Uses NLP techniques to extract key phrases and create
        a meaningful title. Falls back to default titles if
        extraction fails.

        Args:
            question: User's question text
            category: Optional conversation category

        Returns:
            str: Generated conversation title
        """
        logger.debug(f"Generating title from question: {question[:100]}...")

        # Clean and normalize the question
        cleaned = self._clean_question(question)

        if not cleaned:
            logger.warning("Question cleaning resulted in empty string, using fallback")
            return self._get_fallback_title(category)

        # Extract key phrases
        title = self._extract_key_phrases(cleaned)

        # Apply length limits
        title = self._apply_length_limits(title)

        # Validate title quality
        if not self._is_valid_title(title):
            logger.warning(f"Generated title quality check failed: {title}")
            return self._get_fallback_title(category)

        # Capitalize properly
        title = self._capitalize_title(title)

        logger.info(f"Generated title: {title}")
        return title

    def _clean_question(self, question: str) -> str:
        """Clean and normalize question text.

        Removes extra whitespace, special characters, and normalizes text.

        Args:
            question: Raw question text

        Returns:
            str: Cleaned question text
        """
        # Remove extra whitespace
        cleaned = " ".join(question.split())

        # Remove question marks and other punctuation at the end
        cleaned = re.sub(r"[?!.]+$", "", cleaned)

        # Remove special characters but keep essential punctuation
        cleaned = re.sub(r"[^\w\s\-,']", "", cleaned)

        return cleaned.strip()

    def _extract_key_phrases(self, question: str) -> str:
        """Extract key phrases from question to form title.

        Removes question words and stopwords, keeping meaningful content.

        Args:
            question: Cleaned question text

        Returns:
            str: Extracted key phrases
        """
        words = question.lower().split()

        # Remove leading question words
        while words and words[0] in self.QUESTION_WORDS:
            words.pop(0)

        # Remove stopwords but keep phrase structure
        filtered_words = []
        for word in words:
            # Keep word if it's not a stopword or if it's critical for meaning
            if word not in self.STOPWORDS or len(word) > 4:
                filtered_words.append(word)

        # If we removed too many words, use original
        if len(filtered_words) < 2:
            filtered_words = words

        # Join back into phrase
        key_phrase = " ".join(filtered_words)

        # If phrase is too short, try to extract noun phrases
        if len(key_phrase) < self.min_title_length:
            key_phrase = self._extract_noun_phrase(question)

        return key_phrase

    def _extract_noun_phrase(self, question: str) -> str:
        """Extract main noun phrase from question.

        Simple heuristic-based noun phrase extraction.

        Args:
            question: Question text

        Returns:
            str: Extracted noun phrase or original question
        """
        # Look for common patterns
        patterns = [
            r"(?:help with|assistance with|advice on|tips for|info about)\s+(.+)",
            r"(?:how to|ways to|steps to)\s+(.+)",
            r"(?:best|good|effective)\s+(.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                return match.group(1).strip()

        # Default: return question as-is
        return question

    def _apply_length_limits(self, title: str) -> str:
        """Apply length limits to title.

        Truncates long titles and ensures minimum length.

        Args:
            title: Title text

        Returns:
            str: Length-adjusted title
        """
        # Truncate if too long
        if len(title) > self.max_title_length:
            # Try to truncate at word boundary
            truncated = title[: self.max_title_length].rsplit(" ", 1)[0]
            if len(truncated) >= self.min_title_length:
                logger.debug(
                    f"Title truncated from {len(title)} to {len(truncated)} chars"
                )
                return truncated + "..."
            # If truncation too aggressive, just cut at limit
            return title[: self.max_title_length] + "..."

        return title

    def _is_valid_title(self, title: str) -> bool:
        """Validate title quality.

        Checks if title meets minimum requirements for meaningfulness.

        Args:
            title: Generated title

        Returns:
            bool: True if title is valid
        """
        # Check minimum length
        if len(title) < self.min_title_length:
            return False

        # Check that title has meaningful content (not just stopwords)
        words = title.lower().split()
        meaningful_words = [w for w in words if w not in self.STOPWORDS]

        if len(meaningful_words) < 2:
            return False

        # Check that title isn't just numbers or special characters
        if not re.search(r"[a-zA-Z]{3,}", title):
            return False

        return True

    def _capitalize_title(self, title: str) -> str:
        """Apply proper capitalization to title.

        Uses title case with exceptions for common lowercase words.

        Args:
            title: Title text

        Returns:
            str: Properly capitalized title
        """
        # Words that should remain lowercase in title case
        lowercase_words = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with"}

        words = title.split()
        capitalized = []

        for i, word in enumerate(words):
            # Always capitalize first and last word
            if i == 0 or i == len(words) - 1:
                capitalized.append(word.capitalize())
            # Keep lowercase words lowercase if not first/last
            elif word.lower() in lowercase_words:
                capitalized.append(word.lower())
            # Capitalize all other words
            else:
                capitalized.append(word.capitalize())

        return " ".join(capitalized)

    def _get_fallback_title(self, category: Optional[str] = None) -> str:
        """Get fallback title when generation fails.

        Provides category-specific fallback titles.

        Args:
            category: Optional conversation category

        Returns:
            str: Fallback title
        """
        fallback_titles = {
            "resume_help": "Resume Help Conversation",
            "career_advice": "Career Advice Discussion",
            "interview_prep": "Interview Preparation",
            "job_search": "Job Search Assistance",
        }

        if category and category in fallback_titles:
            return fallback_titles[category]

        return "New Conversation"
