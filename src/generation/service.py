"""Resume generation service orchestrating AI content, template rendering, and export."""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class ResumeGenerationService:
    """Service for orchestrating resume generation process.

    This service coordinates AI content generation, template application,
    and file export to produce professional resumes.
    """

    def __init__(self):
        """Initialize resume generation service."""
        self.available_templates = self._load_available_templates()
        logger.info(
            "ResumeGenerationService initialized",
            extra={"template_count": len(self.available_templates)},
        )

    async def generate_resume(
        self,
        user_id: UUID,
        template_style: str,
        content_data: Dict[str, Any],
        title: str,
        ai_generation_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Generate a complete resume with AI content and template.

        Args:
            user_id: User ID generating the resume
            template_style: Template style to use (modern/classic/executive/creative)
            content_data: Resume content data
            title: Resume title
            ai_generation_id: Optional AI generation record ID

        Returns:
            Dict[str, Any]: Generated resume with metadata

        Raises:
            ValueError: If template style is invalid or data is incomplete
            RuntimeError: If generation fails
        """
        logger.info(
            "Starting resume generation",
            extra={
                "user_id": str(user_id),
                "template_style": template_style,
                "title": title,
            },
        )

        try:
            # Get template
            template = self._get_template(template_style)

            # Validate content data
            template.validate_data(content_data)

            # Render content with template
            rendered_content = template.render_content(content_data)

            # Generate exports
            pdf_bytes = await self._generate_pdf_export(rendered_content)
            docx_bytes = await self._generate_docx_export(rendered_content)

            result = {
                "user_id": str(user_id),
                "template_style": template_style,
                "title": title,
                "ai_generation_id": str(ai_generation_id) if ai_generation_id else None,
                "rendered_content": rendered_content,
                "pdf_size": len(pdf_bytes) if pdf_bytes else 0,
                "docx_size": len(docx_bytes) if docx_bytes else 0,
            }

            logger.info(
                "Resume generation completed successfully",
                extra={
                    "user_id": str(user_id),
                    "pdf_size": result["pdf_size"],
                    "docx_size": result["docx_size"],
                },
            )

            return result

        except ValueError as e:
            logger.error(
                f"Resume generation validation failed: {str(e)}",
                extra={"user_id": str(user_id), "error": str(e)},
            )
            raise

        except Exception as e:
            logger.error(
                f"Resume generation failed: {str(e)}",
                extra={"user_id": str(user_id), "error": str(e)},
                exc_info=True,
            )
            raise RuntimeError(f"Failed to generate resume: {str(e)}") from e

    def get_templates(self) -> List[Dict[str, Any]]:
        """Get list of available resume templates.

        Returns:
            List[Dict[str, Any]]: List of template metadata
        """
        logger.debug("Fetching available templates")

        templates = []
        for style, template_class in self.available_templates.items():
            template = template_class()
            metadata = template.get_template_metadata()
            metadata["style"] = style
            templates.append(metadata)

        logger.info(
            "Templates retrieved",
            extra={"template_count": len(templates)},
        )

        return templates

    async def customize_sections(
        self,
        template_style: str,
        sections_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Customize resume sections configuration.

        Args:
            template_style: Template style identifier
            sections_config: Section customization configuration

        Returns:
            Dict[str, Any]: Customized sections configuration

        Raises:
            ValueError: If template style is invalid
        """
        logger.info(
            "Customizing resume sections",
            extra={
                "template_style": template_style,
                "sections": list(sections_config.keys()),
            },
        )

        # Get template
        template = self._get_template(template_style)

        # Get default sections
        default_sections = template.get_sections()

        # Merge with customization
        customized = {
            "template_style": template_style,
            "default_sections": default_sections,
            "customizations": sections_config,
            "final_sections": self._merge_sections(default_sections, sections_config),
        }

        logger.info(
            "Sections customized successfully",
            extra={"final_section_count": len(customized["final_sections"])},
        )

        return customized

    def _load_available_templates(self) -> Dict[str, type]:
        """Load available template classes.

        Returns:
            Dict[str, type]: Mapping of style to template class
        """
        # Import template classes
        # Note: Avoiding forbidden imports from base_template.py
        from src.generation.templates.modern_template import ModernResumeTemplate
        from src.generation.templates.classic_template import ClassicResumeTemplate

        templates = {
            "modern": ModernResumeTemplate,
            "classic": ClassicResumeTemplate,
        }

        logger.debug(
            "Templates loaded",
            extra={"styles": list(templates.keys())},
        )

        return templates

    def _get_template(self, template_style: str):
        """Get template instance by style.

        Args:
            template_style: Template style identifier

        Returns:
            BaseResumeTemplate: Template instance

        Raises:
            ValueError: If template style is invalid
        """
        if template_style not in self.available_templates:
            available = ", ".join(self.available_templates.keys())
            raise ValueError(
                f"Invalid template style '{template_style}'. "
                f"Available styles: {available}"
            )

        template_class = self.available_templates[template_style]
        return template_class()

    async def _generate_pdf_export(self, rendered_content: Dict[str, Any]) -> bytes:
        """Generate PDF export from rendered content.

        Args:
            rendered_content: Rendered resume content

        Returns:
            bytes: PDF file bytes
        """
        logger.debug("Generating PDF export")

        from src.generation.exporters.pdf_exporter import PDFExporter

        exporter = PDFExporter()
        pdf_bytes = exporter.generate_pdf(rendered_content)

        logger.debug(
            "PDF export generated",
            extra={"size_bytes": len(pdf_bytes)},
        )

        return pdf_bytes

    async def _generate_docx_export(self, rendered_content: Dict[str, Any]) -> Optional[bytes]:
        """Generate DOCX export from rendered content.

        Args:
            rendered_content: Rendered resume content

        Returns:
            Optional[bytes]: DOCX file bytes or None if not available

        Note:
            DOCX export not yet implemented. Placeholder for future implementation
            using python-docx when available.
        """
        logger.debug("DOCX export not yet implemented")
        return None

    def _merge_sections(
        self, default_sections: List[str], customizations: Dict[str, Any]
    ) -> List[str]:
        """Merge default sections with customizations.

        Args:
            default_sections: List of default section names
            customizations: Section customization configuration

        Returns:
            List[str]: Final list of sections
        """
        # Start with default sections
        final_sections = default_sections.copy()

        # Apply customizations
        if "exclude" in customizations:
            exclude_sections = customizations["exclude"]
            final_sections = [s for s in final_sections if s not in exclude_sections]

        if "include" in customizations:
            include_sections = customizations["include"]
            for section in include_sections:
                if section not in final_sections:
                    final_sections.append(section)

        if "order" in customizations:
            # Reorder sections based on specified order
            order = customizations["order"]
            ordered = []
            for section in order:
                if section in final_sections:
                    ordered.append(section)
            # Add any remaining sections not in order
            for section in final_sections:
                if section not in ordered:
                    ordered.append(section)
            final_sections = ordered

        return final_sections
