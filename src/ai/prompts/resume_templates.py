"""Resume generation prompt templates with context injection."""

from typing import Dict


def get_resume_prompt(
    style: str,
    user_data: Dict,
    job_title: str,
    job_description: str = None,
    additional_instructions: str = None,
) -> str:
    """Get resume generation prompt based on style and context.

    Args:
        style: Resume style (modern, classic, executive, creative)
        user_data: User profile data including contact, experience, education, skills
        job_title: Target job title for resume optimization
        job_description: Optional job description for tailoring
        additional_instructions: Optional additional customization instructions

    Returns:
        str: Complete prompt for resume generation
    """
    contact_info = user_data.get("contact_info", {})
    work_experience = user_data.get("work_experience", [])
    education = user_data.get("education", [])
    skills = user_data.get("skills", [])

    base_context = f"""Generate a professional resume for the following candidate:

CONTACT INFORMATION:
Name: {contact_info.get('name', 'N/A')}
Email: {contact_info.get('email', 'N/A')}
Phone: {contact_info.get('phone', 'N/A')}
Location: {contact_info.get('location', 'N/A')}

TARGET JOB TITLE: {job_title}

WORK EXPERIENCE:
{_format_work_experience(work_experience)}

EDUCATION:
{_format_education(education)}

SKILLS:
{_format_skills(skills)}
"""

    if job_description:
        base_context += f"""
JOB DESCRIPTION FOR TAILORING:
{job_description}

Please tailor the resume to highlight relevant experience and skills that match this job description.
"""

    style_instructions = _get_style_instructions(style)
    base_context += f"\n{style_instructions}"

    if additional_instructions:
        base_context += f"""
ADDITIONAL REQUIREMENTS:
{additional_instructions}
"""

    base_context += """
OUTPUT FORMAT:
- Provide the resume in clean, well-formatted text
- Use appropriate sections and headers
- Keep it concise and impactful
- Focus on achievements and measurable results
- Use action verbs and industry-appropriate terminology
"""

    return base_context


def _format_work_experience(experience_list: list) -> str:
    """Format work experience for prompt.

    Args:
        experience_list: List of work experience entries

    Returns:
        str: Formatted work experience text
    """
    if not experience_list:
        return "No work experience provided"

    formatted = []
    for exp in experience_list:
        entry = f"- {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}"
        if exp.get('start_date'):
            entry += f" ({exp.get('start_date')} - {exp.get('end_date', 'Present')})"
        if exp.get('description'):
            entry += f"\n  {exp.get('description')}"
        formatted.append(entry)

    return "\n".join(formatted)


def _format_education(education_list: list) -> str:
    """Format education for prompt.

    Args:
        education_list: List of education entries

    Returns:
        str: Formatted education text
    """
    if not education_list:
        return "No education provided"

    formatted = []
    for edu in education_list:
        entry = f"- {edu.get('degree', 'N/A')} in {edu.get('field', 'N/A')}"
        entry += f" from {edu.get('institution', 'N/A')}"
        if edu.get('graduation_date'):
            entry += f" ({edu.get('graduation_date')})"
        formatted.append(entry)

    return "\n".join(formatted)


def _format_skills(skills_list: list) -> str:
    """Format skills for prompt.

    Args:
        skills_list: List of skills

    Returns:
        str: Formatted skills text
    """
    if not skills_list:
        return "No skills provided"

    return ", ".join(skills_list)


def _get_style_instructions(style: str) -> str:
    """Get style-specific instructions for resume generation.

    Args:
        style: Resume style (modern, classic, executive, creative)

    Returns:
        str: Style-specific instructions
    """
    style_templates = {
        "modern": """
STYLE: Modern
- Use a clean, contemporary format with clear visual hierarchy
- Emphasize technical skills and quantifiable achievements
- Include relevant keywords for applicant tracking systems (ATS)
- Keep language professional but conversational
- Focus on impact and results with specific metrics
""",
        "classic": """
STYLE: Classic
- Use a traditional, conservative format
- Emphasize career progression and stability
- Use formal, professional language throughout
- Focus on responsibilities and achievements
- Maintain chronological order with clear dates
""",
        "executive": """
STYLE: Executive
- Use a sophisticated, high-level format
- Emphasize leadership, strategy, and business impact
- Focus on organizational achievements and bottom-line results
- Include executive summary or professional profile
- Highlight board experience, P&L responsibility, and team leadership
""",
        "creative": """
STYLE: Creative
- Use an innovative format that showcases personality
- Emphasize creative projects, portfolio work, and unique achievements
- Balance creativity with professionalism
- Highlight diverse skills and cross-functional experience
- Include relevant creative tools and methodologies
""",
    }

    return style_templates.get(
        style,
        style_templates["modern"],
    )
