"""Classic resume template with traditional professional format."""

import logging
from typing import Any, Dict

from src.generation.templates.base_template import BaseResumeTemplate

logger = logging.getLogger(__name__)


class ClassicResumeTemplate(BaseResumeTemplate):
    """Classic resume template with traditional professional format.

    Features:
    - Traditional, conservative layout
    - Chronological format
    - Professional appearance
    - ATS-friendly structure
    """

    def __init__(self):
        """Initialize classic resume template."""
        super().__init__(template_name="classic")
        logger.info("ClassicResumeTemplate initialized")

    def render_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render resume content using classic template formatting.

        Args:
            content_data: Dictionary containing resume data sections

        Returns:
            Dict[str, Any]: Rendered content with classic styling

        Raises:
            ValueError: If required content fields are missing
        """
        logger.info(
            "Rendering classic template content",
            extra={"sections": list(content_data.keys())},
        )

        # Validate data before rendering
        self.validate_data(content_data)

        rendered = {
            "template": "classic",
            "sections": [],
            "styling": self._get_classic_styling(),
        }

        # Render contact information (traditional header)
        if "contact_info" in content_data:
            rendered["sections"].append(
                self._render_contact_section(content_data["contact_info"])
            )

        # Render professional summary/objective
        if "professional_summary" in content_data and content_data["professional_summary"]:
            rendered["sections"].append(
                self.format_section("professional_summary", content_data["professional_summary"])
            )

        # Render work experience (chronological - most important in classic format)
        if "work_experience" in content_data and content_data["work_experience"]:
            rendered["sections"].append(
                self._render_work_experience_section(content_data["work_experience"])
            )

        # Render education
        if "education" in content_data and content_data["education"]:
            rendered["sections"].append(
                self._render_education_section(content_data["education"])
            )

        # Render skills
        if "skills" in content_data and content_data["skills"]:
            rendered["sections"].append(
                self._render_skills_section(content_data["skills"])
            )

        # Render certifications
        if "certifications" in content_data and content_data["certifications"]:
            rendered["sections"].append(
                self.format_section("certifications", content_data["certifications"])
            )

        # Render projects
        if "projects" in content_data and content_data["projects"]:
            rendered["sections"].append(
                self.format_section("projects", content_data["projects"])
            )

        # Render languages
        if "languages" in content_data and content_data["languages"]:
            rendered["sections"].append(
                self.format_section("languages", content_data["languages"])
            )

        logger.info(
            "Classic template content rendered successfully",
            extra={"section_count": len(rendered["sections"])},
        )
        return rendered

    def _render_contact_section(self, contact_info: Dict[str, Any]) -> Dict[str, Any]:
        """Render contact information with traditional centered layout.

        Args:
            contact_info: Contact information data

        Returns:
            Dict[str, Any]: Formatted contact section
        """
        return {
            "name": "contact_info",
            "content": contact_info,
            "visible": True,
            "layout": "classic_centered_header",
        }

    def _render_work_experience_section(self, work_experience: list) -> Dict[str, Any]:
        """Render work experience in chronological format.

        Args:
            work_experience: List of work experience entries

        Returns:
            Dict[str, Any]: Formatted work experience section
        """
        return {
            "name": "work_experience",
            "content": work_experience,
            "visible": True,
            "layout": "chronological",
            "reverse_chronological": True,
        }

    def _render_education_section(self, education: list) -> Dict[str, Any]:
        """Render education section with traditional layout.

        Args:
            education: List of education entries

        Returns:
            Dict[str, Any]: Formatted education section
        """
        return {
            "name": "education",
            "content": education,
            "visible": True,
            "layout": "traditional",
            "reverse_chronological": True,
        }

    def _render_skills_section(self, skills: Any) -> Dict[str, Any]:
        """Render skills section with traditional list format.

        Args:
            skills: Skills data (list or dict)

        Returns:
            Dict[str, Any]: Formatted skills section
        """
        return {
            "name": "skills",
            "content": skills,
            "visible": True,
            "layout": "bulleted_list",
        }

    def _get_classic_styling(self) -> Dict[str, Any]:
        """Get classic template styling configuration.

        Returns:
            Dict[str, Any]: Styling configuration
        """
        return {
            "font_family": "Times New Roman",
            "font_size_header": 14,
            "font_size_body": 11,
            "font_size_section_title": 12,
            "color_primary": "#000000",
            "color_secondary": "#000000",
            "color_text": "#000000",
            "spacing_section": 10,
            "spacing_paragraph": 5,
            "margins": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
            "ats_friendly": True,
            "conservative": True,
        }
