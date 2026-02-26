"""Modern resume template with contemporary design and layout."""

import logging
from typing import Any, Dict

from src.generation.templates.base_template import BaseResumeTemplate

logger = logging.getLogger(__name__)


class ModernResumeTemplate(BaseResumeTemplate):
    """Modern resume template with contemporary design.

    Features:
    - Clean, modern layout
    - Emphasis on skills and achievements
    - ATS-friendly structure
    - Professional appearance with contemporary styling
    """

    def __init__(self):
        """Initialize modern resume template."""
        super().__init__(template_name="modern")
        logger.info("ModernResumeTemplate initialized")

    def render_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render resume content using modern template formatting.

        Args:
            content_data: Dictionary containing resume data sections

        Returns:
            Dict[str, Any]: Rendered content with modern styling

        Raises:
            ValueError: If required content fields are missing
        """
        logger.info(
            "Rendering modern template content",
            extra={"sections": list(content_data.keys())},
        )

        # Validate data before rendering
        self.validate_data(content_data)

        rendered = {
            "template": "modern",
            "sections": [],
            "styling": self._get_modern_styling(),
        }

        # Render contact information (always first)
        if "contact_info" in content_data:
            rendered["sections"].append(
                self._render_contact_section(content_data["contact_info"])
            )

        # Render professional summary
        if "professional_summary" in content_data and content_data["professional_summary"]:
            rendered["sections"].append(
                self.format_section("professional_summary", content_data["professional_summary"])
            )

        # Render skills prominently (modern templates emphasize skills)
        if "skills" in content_data and content_data["skills"]:
            rendered["sections"].append(
                self._render_skills_section(content_data["skills"])
            )

        # Render work experience
        if "work_experience" in content_data and content_data["work_experience"]:
            rendered["sections"].append(
                self._render_work_experience_section(content_data["work_experience"])
            )

        # Render education
        if "education" in content_data and content_data["education"]:
            rendered["sections"].append(
                self._render_education_section(content_data["education"])
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
            "Modern template content rendered successfully",
            extra={"section_count": len(rendered["sections"])},
        )
        return rendered

    def _render_contact_section(self, contact_info: Dict[str, Any]) -> Dict[str, Any]:
        """Render contact information with modern styling.

        Args:
            contact_info: Contact information data

        Returns:
            Dict[str, Any]: Formatted contact section
        """
        return {
            "name": "contact_info",
            "content": contact_info,
            "visible": True,
            "layout": "modern_header",
        }

    def _render_skills_section(self, skills: Any) -> Dict[str, Any]:
        """Render skills section with modern categorization.

        Args:
            skills: Skills data (list or dict)

        Returns:
            Dict[str, Any]: Formatted skills section
        """
        return {
            "name": "skills",
            "content": skills,
            "visible": True,
            "layout": "skills_grid",
            "highlight": True,
        }

    def _render_work_experience_section(self, work_experience: list) -> Dict[str, Any]:
        """Render work experience with achievement focus.

        Args:
            work_experience: List of work experience entries

        Returns:
            Dict[str, Any]: Formatted work experience section
        """
        return {
            "name": "work_experience",
            "content": work_experience,
            "visible": True,
            "layout": "achievement_focused",
        }

    def _render_education_section(self, education: list) -> Dict[str, Any]:
        """Render education section with modern layout.

        Args:
            education: List of education entries

        Returns:
            Dict[str, Any]: Formatted education section
        """
        return {
            "name": "education",
            "content": education,
            "visible": True,
            "layout": "modern_timeline",
        }

    def _get_modern_styling(self) -> Dict[str, Any]:
        """Get modern template styling configuration.

        Returns:
            Dict[str, Any]: Styling configuration
        """
        return {
            "font_family": "Helvetica",
            "font_size_header": 16,
            "font_size_body": 11,
            "font_size_section_title": 13,
            "color_primary": "#2C3E50",
            "color_secondary": "#3498DB",
            "color_text": "#34495E",
            "spacing_section": 12,
            "spacing_paragraph": 6,
            "margins": {"top": 0.75, "bottom": 0.75, "left": 0.75, "right": 0.75},
            "ats_friendly": True,
        }
