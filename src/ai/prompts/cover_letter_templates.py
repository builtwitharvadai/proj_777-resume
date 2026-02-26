"""Cover letter generation prompt templates with personalization."""

from typing import Dict


def get_cover_letter_prompt(
    tone: str,
    user_data: Dict,
    job_title: str,
    company_name: str,
    job_description: str,
    additional_context: str = None,
) -> str:
    """Get cover letter generation prompt based on tone and context.

    Args:
        tone: Cover letter tone (formal, conversational, enthusiastic)
        user_data: User profile data including contact, experience, education
        job_title: Target job title
        company_name: Name of the company
        job_description: Job description to reference
        additional_context: Optional additional context about company or role

    Returns:
        str: Complete prompt for cover letter generation
    """
    contact_info = user_data.get("contact_info", {})
    work_experience = user_data.get("work_experience", [])
    education = user_data.get("education", [])
    skills = user_data.get("skills", [])

    base_context = f"""Generate a professional cover letter for the following candidate:

CANDIDATE INFORMATION:
Name: {contact_info.get('name', 'N/A')}
Email: {contact_info.get('email', 'N/A')}
Phone: {contact_info.get('phone', 'N/A')}

TARGET POSITION: {job_title} at {company_name}

JOB DESCRIPTION:
{job_description}

CANDIDATE BACKGROUND:
Work Experience:
{_format_work_experience_summary(work_experience)}

Education:
{_format_education_summary(education)}

Key Skills:
{_format_skills_list(skills)}
"""

    if additional_context:
        base_context += f"""
ADDITIONAL CONTEXT:
{additional_context}
"""

    tone_instructions = _get_tone_instructions(tone)
    base_context += f"\n{tone_instructions}"

    base_context += """
COVER LETTER REQUIREMENTS:
- Address the hiring manager or use "Dear Hiring Manager"
- Open with a compelling introduction that captures attention
- Demonstrate knowledge of the company and why you're interested
- Highlight 2-3 most relevant experiences that match the job requirements
- Show genuine enthusiasm for the role and company
- Explain how your background makes you a strong fit
- Include specific examples and achievements with measurable results
- Close with a clear call to action
- Keep the letter to 3-4 paragraphs, approximately 300-400 words
- Use professional formatting with proper business letter structure

OUTPUT FORMAT:
Provide a complete, well-formatted cover letter ready to send. Include appropriate spacing and paragraph breaks.
"""

    return base_context


def _format_work_experience_summary(experience_list: list) -> str:
    """Format work experience summary for cover letter prompt.

    Args:
        experience_list: List of work experience entries

    Returns:
        str: Formatted work experience summary
    """
    if not experience_list:
        return "No relevant work experience provided"

    formatted = []
    for exp in experience_list:
        title = exp.get("title", "N/A")
        company = exp.get("company", "N/A")
        summary = f"- {title} at {company}"
        if exp.get("description"):
            summary += f": {exp.get('description')[:200]}"
        formatted.append(summary)

    return "\n".join(formatted[:3])


def _format_education_summary(education_list: list) -> str:
    """Format education summary for cover letter prompt.

    Args:
        education_list: List of education entries

    Returns:
        str: Formatted education summary
    """
    if not education_list:
        return "No education information provided"

    formatted = []
    for edu in education_list:
        degree = edu.get("degree", "N/A")
        field = edu.get("field", "N/A")
        institution = edu.get("institution", "N/A")
        summary = f"- {degree} in {field} from {institution}"
        formatted.append(summary)

    return "\n".join(formatted)


def _format_skills_list(skills_list: list) -> str:
    """Format skills list for cover letter prompt.

    Args:
        skills_list: List of skills

    Returns:
        str: Formatted skills list
    """
    if not skills_list:
        return "No skills information provided"

    return ", ".join(skills_list[:10])


def _get_tone_instructions(tone: str) -> str:
    """Get tone-specific instructions for cover letter generation.

    Args:
        tone: Cover letter tone (formal, conversational, enthusiastic)

    Returns:
        str: Tone-specific instructions
    """
    tone_templates = {
        "formal": """
TONE: Formal
- Use traditional business letter language and structure
- Maintain a professional and respectful tone throughout
- Use complete sentences and proper grammar
- Avoid contractions and casual language
- Express interest professionally without being overly effusive
- Use industry-standard terminology and formal expressions
""",
        "conversational": """
TONE: Conversational
- Write in a warm, personable style while maintaining professionalism
- Use natural language that sounds like a real conversation
- Show personality while staying appropriate for business context
- Use some contractions to create a friendly tone
- Balance professionalism with approachability
- Make it feel genuine and human, not template-driven
""",
        "enthusiastic": """
TONE: Enthusiastic
- Express genuine excitement about the opportunity
- Use dynamic, energetic language to convey passion
- Highlight eagerness to contribute to the company's success
- Show strong interest in the specific role and company mission
- Balance enthusiasm with professionalism - avoid being overly casual
- Use positive, action-oriented language throughout
- Convey confidence and motivation
""",
    }

    return tone_templates.get(
        tone,
        tone_templates["formal"],
    )
