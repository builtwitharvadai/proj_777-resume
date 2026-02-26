"""NLP-based information extraction for structured data from documents."""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class InformationExtractor:
    """Extract structured information using regex patterns and NLP.

    Extracts contact information, work experience, education, and skills
    from document text using pattern matching and optional spaCy NER.
    """

    # Regex patterns for contact information
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    PHONE_PATTERN = re.compile(
        r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}"
    )
    URL_PATTERN = re.compile(
        r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)"  # noqa: E501
    )

    # Section headers for resume parsing
    EXPERIENCE_HEADERS = [
        "experience",
        "work experience",
        "employment",
        "professional experience",
        "work history",
    ]
    EDUCATION_HEADERS = [
        "education",
        "academic background",
        "qualifications",
        "academic history",
    ]
    SKILLS_HEADERS = ["skills", "technical skills", "competencies", "expertise"]

    def __init__(self, use_spacy: bool = False) -> None:
        """Initialize information extractor.

        Args:
            use_spacy: Whether to use spaCy for NER (optional enhancement)
        """
        self.use_spacy = use_spacy
        self.nlp = None

        if use_spacy:
            try:
                import spacy

                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    logger.info("spaCy NER model loaded successfully")
                except OSError:
                    logger.warning(
                        "spaCy model 'en_core_web_sm' not found, "
                        "using regex-only extraction"
                    )
                    self.use_spacy = False
            except ImportError:
                logger.warning("spaCy not installed, using regex-only extraction")
                self.use_spacy = False

    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information from text.

        Args:
            text: Document text content

        Returns:
            Dict containing emails, phones, urls, and optionally name
        """
        logger.info("Extracting contact information")

        contact_info: Dict[str, Any] = {
            "emails": [],
            "phones": [],
            "urls": [],
            "name": None,
        }

        try:
            # Extract emails
            emails = self.EMAIL_PATTERN.findall(text)
            contact_info["emails"] = list(set(emails))  # Remove duplicates

            # Extract phone numbers
            phones = self.PHONE_PATTERN.findall(text)
            # Join tuples from regex groups
            contact_info["phones"] = [
                "".join(phone).strip() for phone in phones if any(phone)
            ]
            contact_info["phones"] = list(set(contact_info["phones"]))

            # Extract URLs
            urls = self.URL_PATTERN.findall(text)
            contact_info["urls"] = list(set(urls))

            # Extract name using spaCy if available
            if self.use_spacy and self.nlp:
                name = self._extract_name_with_spacy(text)
                contact_info["name"] = name

            logger.info(
                f"Extracted contact info: {len(contact_info['emails'])} emails, "
                f"{len(contact_info['phones'])} phones, "
                f"{len(contact_info['urls'])} URLs"
            )

        except Exception as e:
            logger.error(f"Error extracting contact information: {str(e)}", exc_info=True)  # noqa: E501

        return contact_info

    def extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from text.

        Args:
            text: Document text content

        Returns:
            List of dictionaries containing work experience entries
        """
        logger.info("Extracting work experience")

        experiences: List[Dict[str, Any]] = []

        try:
            # Find experience section
            experience_section = self._extract_section(text, self.EXPERIENCE_HEADERS)

            if not experience_section:
                logger.info("No work experience section found")
                return experiences

            # Split into entries (simple heuristic: split by year patterns)
            year_pattern = re.compile(r"\b(19|20)\d{2}\b")
            lines = experience_section.split("\n")

            current_entry: Dict[str, Any] = {}
            for line in lines:
                line = line.strip()
                if not line:
                    if current_entry:
                        experiences.append(current_entry)
                        current_entry = {}
                    continue

                # Check if line contains a year (potential date range)
                if year_pattern.search(line):
                    if current_entry:
                        experiences.append(current_entry)
                    current_entry = {"text": line, "years": year_pattern.findall(line)}
                elif current_entry:
                    current_entry["text"] = current_entry.get("text", "") + " " + line

            # Add last entry
            if current_entry:
                experiences.append(current_entry)

            logger.info(f"Extracted {len(experiences)} work experience entries")

        except Exception as e:
            logger.error(f"Error extracting work experience: {str(e)}", exc_info=True)

        return experiences

    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information from text.

        Args:
            text: Document text content

        Returns:
            List of dictionaries containing education entries
        """
        logger.info("Extracting education information")

        education: List[Dict[str, Any]] = []

        try:
            # Find education section
            education_section = self._extract_section(text, self.EDUCATION_HEADERS)

            if not education_section:
                logger.info("No education section found")
                return education

            # Common degree patterns
            degree_pattern = re.compile(
                r"\b(Bachelor|Master|PhD|Ph\.D\.|Doctorate|Associate|B\.S\.|B\.A\.|M\.S\.|M\.A\.)[^\n]*",  # noqa: E501
                re.IGNORECASE,
            )

            # Find degrees
            degrees = degree_pattern.findall(education_section)
            for degree in degrees:
                # Extract years if present
                year_pattern = re.compile(r"\b(19|20)\d{2}\b")
                years = year_pattern.findall(degree)

                education.append({"degree": degree.strip(), "years": years})

            logger.info(f"Extracted {len(education)} education entries")

        except Exception as e:
            logger.error(f"Error extracting education: {str(e)}", exc_info=True)

        return education

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text.

        Args:
            text: Document text content

        Returns:
            List of identified skills
        """
        logger.info("Extracting skills")

        skills: List[str] = []

        try:
            # Find skills section
            skills_section = self._extract_section(text, self.SKILLS_HEADERS)

            if not skills_section:
                logger.info("No skills section found, using full text")
                skills_section = text

            # Common skill indicators and delimiters
            # Split by common delimiters
            potential_skills = re.split(r"[,;\n•·\-\*]", skills_section)

            # Clean and filter skills
            for skill in potential_skills:
                skill = skill.strip()
                # Filter out empty strings and very long entries (likely not skills)
                if skill and 2 < len(skill) < 50:
                    # Remove common section headers
                    if not any(
                        header in skill.lower()
                        for header in self.SKILLS_HEADERS
                        + self.EXPERIENCE_HEADERS
                        + self.EDUCATION_HEADERS
                    ):
                        skills.append(skill)

            # Remove duplicates while preserving order
            seen = set()
            unique_skills = []
            for skill in skills:
                skill_lower = skill.lower()
                if skill_lower not in seen:
                    seen.add(skill_lower)
                    unique_skills.append(skill)

            logger.info(f"Extracted {len(unique_skills)} skills")

            return unique_skills

        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}", exc_info=True)
            return []

    def _extract_section(
        self, text: str, headers: List[str]
    ) -> Optional[str]:
        """Extract text section by header.

        Args:
            text: Full document text
            headers: List of possible section headers

        Returns:
            Section text or None if not found
        """
        text_lower = text.lower()

        for header in headers:
            # Find header position
            header_pos = text_lower.find(header.lower())
            if header_pos == -1:
                continue

            # Find start of section (after header line)
            start_pos = text.find("\n", header_pos)
            if start_pos == -1:
                continue

            # Find next section header (approximate)
            next_section_pos = len(text)
            for next_header in (
                self.EXPERIENCE_HEADERS + self.EDUCATION_HEADERS + self.SKILLS_HEADERS
            ):
                if next_header == header:
                    continue
                pos = text_lower.find(next_header.lower(), start_pos)
                if pos != -1 and pos < next_section_pos:
                    next_section_pos = pos

            section = text[start_pos:next_section_pos].strip()
            return section

        return None

    def _extract_name_with_spacy(self, text: str) -> Optional[str]:
        """Extract person name using spaCy NER.

        Args:
            text: Document text

        Returns:
            Extracted name or None
        """
        if not self.nlp:
            return None

        try:
            # Process first few lines where name usually appears
            first_lines = "\n".join(text.split("\n")[:5])
            doc = self.nlp(first_lines)

            # Find PERSON entities
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text

        except Exception as e:
            logger.warning(f"Error extracting name with spaCy: {str(e)}")

        return None
