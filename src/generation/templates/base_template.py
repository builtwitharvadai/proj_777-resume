"""Base template class defining common resume structure and methods."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class BaseResumeTemplate(ABC):
    """Abstract base class for resume templates.

    This class defines the common structure and methods that all resume
    templates must implement. Each template extends this base to provide
    specific styling and layout.
    """

    def __init__(self, template_name: str):
        """Initialize base resume template.

        Args:
            template_name: Name identifier for the template
        """
        self.template_name = template_name
        self.sections = self.get_sections()
        logger.info(
            f"Initialized {self.__class__.__name__}",
            extra={"template_name": template_name},
        )

    @abstractmethod
    def render_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render resume content using template-specific formatting.

        Args:
            content_data: Dictionary containing resume data sections

        Returns:
            Dict[str, Any]: Rendered content ready for export

        Raises:
            ValueError: If required content fields are missing
        """
        pass

    def get_sections(self) -> List[str]:
        """Get available resume sections for this template.

        Returns:
            List[str]: List of section identifiers
        """
        return [
            "contact_info",
            "professional_summary",
            "work_experience",
            "education",
            "skills",
            "certifications",
            "projects",
            "languages",
        ]

    def validate_data(self, content_data: Dict[str, Any]) -> bool:
        """Validate resume data against template requirements.

        Args:
            content_data: Dictionary containing resume data to validate

        Returns:
            bool: True if data is valid

        Raises:
            ValueError: If required fields are missing or invalid
        """
        logger.debug(
            "Validating resume data",
            extra={
                "template_name": self.template_name,
                "data_keys": list(content_data.keys()),
            },
        )

        # Validate required sections
        required_sections = ["contact_info"]
        for section in required_sections:
            if section not in content_data or not content_data[section]:
                error_msg = f"Required section '{section}' is missing or empty"
                logger.error(
                    error_msg,
                    extra={"template_name": self.template_name, "section": section},
                )
                raise ValueError(error_msg)

        # Validate contact_info structure
        contact_info = content_data["contact_info"]
        required_contact_fields = ["name"]
        for field in required_contact_fields:
            if field not in contact_info or not contact_info[field]:
                error_msg = f"Required contact field '{field}' is missing or empty"
                logger.error(
                    error_msg,
                    extra={"template_name": self.template_name, "field": field},
                )
                raise ValueError(error_msg)

        # Validate optional sections have correct structure
        if "work_experience" in content_data and content_data["work_experience"]:
            if not isinstance(content_data["work_experience"], list):
                raise ValueError("work_experience must be a list")

        if "education" in content_data and content_data["education"]:
            if not isinstance(content_data["education"], list):
                raise ValueError("education must be a list")

        if "skills" in content_data and content_data["skills"]:
            if not isinstance(content_data["skills"], (list, dict)):
                raise ValueError("skills must be a list or dictionary")

        logger.info(
            "Resume data validation successful",
            extra={"template_name": self.template_name},
        )
        return True

    def format_section(
        self, section_name: str, section_data: Any
    ) -> Dict[str, Any]:
        """Format a specific section for rendering.

        Args:
            section_name: Name of the section
            section_data: Data for the section

        Returns:
            Dict[str, Any]: Formatted section data
        """
        if not section_data:
            return {"name": section_name, "content": None, "visible": False}

        return {
            "name": section_name,
            "content": section_data,
            "visible": True,
        }

    def get_template_metadata(self) -> Dict[str, Any]:
        """Get template metadata and configuration.

        Returns:
            Dict[str, Any]: Template metadata
        """
        return {
            "name": self.template_name,
            "class": self.__class__.__name__,
            "sections": self.sections,
            "ats_friendly": True,
        }
