"""Pydantic models for AI service requests and responses."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ResumeGenerationRequest(BaseModel):
    """Request model for resume generation.

    Attributes:
        user_data: User profile data including contact, experience, education, skills
        job_title: Target job title for resume optimization
        job_description: Job description for tailoring resume content
        style: Resume style (modern, classic, executive, creative)
        additional_instructions: Optional additional customization instructions
    """

    user_data: Dict[str, any] = Field(
        ...,
        description="User profile data including contact, experience, education, skills",
    )
    job_title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Target job title",
    )
    job_description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Job description for tailoring resume",
    )
    style: str = Field(
        default="modern",
        description="Resume style (modern, classic, executive, creative)",
    )
    additional_instructions: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional customization instructions",
    )

    @field_validator("style")
    @classmethod
    def validate_style(cls, v: str) -> str:
        """Validate resume style.

        Args:
            v: Style value to validate

        Returns:
            str: Validated style value

        Raises:
            ValueError: If style is not in allowed values
        """
        allowed_styles = ["modern", "classic", "executive", "creative"]
        if v not in allowed_styles:
            raise ValueError(f"Style must be one of: {', '.join(allowed_styles)}")
        return v


class CoverLetterGenerationRequest(BaseModel):
    """Request model for cover letter generation.

    Attributes:
        user_data: User profile data including contact, experience, education
        job_title: Target job title for the cover letter
        company_name: Name of the company
        job_description: Job description to reference in the letter
        tone: Cover letter tone (formal, conversational, enthusiastic)
        additional_context: Optional additional context about company or role
    """

    user_data: Dict[str, any] = Field(
        ...,
        description="User profile data",
    )
    job_title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Target job title",
    )
    company_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Company name",
    )
    job_description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Job description",
    )
    tone: str = Field(
        default="formal",
        description="Cover letter tone (formal, conversational, enthusiastic)",
    )
    additional_context: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional context about company or role",
    )

    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: str) -> str:
        """Validate cover letter tone.

        Args:
            v: Tone value to validate

        Returns:
            str: Validated tone value

        Raises:
            ValueError: If tone is not in allowed values
        """
        allowed_tones = ["formal", "conversational", "enthusiastic"]
        if v not in allowed_tones:
            raise ValueError(f"Tone must be one of: {', '.join(allowed_tones)}")
        return v


class TokenUsage(BaseModel):
    """Model for tracking token usage in AI requests.

    Attributes:
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        total_tokens: Total tokens used
    """

    prompt_tokens: int = Field(
        ...,
        ge=0,
        description="Number of tokens in the prompt",
    )
    completion_tokens: int = Field(
        ...,
        ge=0,
        description="Number of tokens in the completion",
    )
    total_tokens: int = Field(
        ...,
        ge=0,
        description="Total tokens used",
    )


class CostCalculation(BaseModel):
    """Model for AI cost calculation.

    Attributes:
        prompt_cost: Cost for prompt tokens in USD
        completion_cost: Cost for completion tokens in USD
        total_cost: Total cost in USD
        model: Model used for generation
    """

    prompt_cost: float = Field(
        ...,
        ge=0.0,
        description="Cost for prompt tokens in USD",
    )
    completion_cost: float = Field(
        ...,
        ge=0.0,
        description="Cost for completion tokens in USD",
    )
    total_cost: float = Field(
        ...,
        ge=0.0,
        description="Total cost in USD",
    )
    model: str = Field(
        ...,
        description="Model used for generation",
    )


class AIGenerationResponse(BaseModel):
    """Response model for AI generation operations.

    Attributes:
        generation_id: Unique identifier for this generation
        content: Generated content
        token_usage: Token usage information
        cost: Cost calculation
        model_used: Model used for generation
        generation_type: Type of generation (resume or cover_letter)
    """

    generation_id: str = Field(
        ...,
        description="Unique identifier for this generation",
    )
    content: str = Field(
        ...,
        description="Generated content",
    )
    token_usage: TokenUsage = Field(
        ...,
        description="Token usage information",
    )
    cost: CostCalculation = Field(
        ...,
        description="Cost calculation",
    )
    model_used: str = Field(
        ...,
        description="Model used for generation",
    )
    generation_type: str = Field(
        ...,
        description="Type of generation (resume or cover_letter)",
    )
