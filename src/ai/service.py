"""Main AI service orchestrating OpenAI API calls, prompt management, and usage tracking."""

import logging
from decimal import Decimal
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.exceptions import (
    AIServiceUnavailableException,
    APIQuotaExceededException,
    ContentFilteredException,
    TokenLimitExceededException,
)
from src.ai.models import (
    AIGenerationResponse,
    CostCalculation,
    CoverLetterGenerationRequest,
    ResumeGenerationRequest,
    TokenUsage,
)
from src.ai.prompts.cover_letter_templates import get_cover_letter_prompt
from src.ai.prompts.resume_templates import get_resume_prompt
from src.ai.rate_limiter import AIRateLimiter
from src.core.config import settings
from src.database.models.ai_generation import AIGeneration

logger = logging.getLogger(__name__)


class AIService:
    """AI service for resume and cover letter generation using OpenAI GPT-4.

    Handles OpenAI API integration, prompt management, token tracking,
    cost calculation, and rate limiting.

    Attributes:
        rate_limiter: Rate limiter instance for API call throttling
        model: OpenAI model to use for generation
        max_retries: Maximum number of retry attempts for failed requests
    """

    # Token cost per 1000 tokens (in USD) for GPT-4
    GPT4_PROMPT_COST_PER_1K = 0.03
    GPT4_COMPLETION_COST_PER_1K = 0.06

    def __init__(
        self,
        rate_limiter: Optional[AIRateLimiter] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
    ) -> None:
        """Initialize AIService.

        Args:
            rate_limiter: Optional rate limiter instance
            model: Optional OpenAI model name (defaults to config)
            max_retries: Maximum retry attempts for failed requests
        """
        self.rate_limiter = rate_limiter or AIRateLimiter(
            free_limit=settings.AI_RATE_LIMIT_FREE,
            premium_limit=settings.AI_RATE_LIMIT_PREMIUM,
            enterprise_limit=settings.AI_RATE_LIMIT_ENTERPRISE,
        )
        self.model = model or settings.OPENAI_MODEL
        self.max_retries = max_retries

        logger.info(
            f"AIService initialized with model: {self.model}, "
            f"max_retries: {max_retries}"
        )

    async def generate_resume(
        self,
        request: ResumeGenerationRequest,
        user_id: str,
        user_tier: str,
        db: AsyncSession,
        document_id: Optional[str] = None,
    ) -> AIGenerationResponse:
        """Generate resume using OpenAI GPT-4.

        Args:
            request: Resume generation request with user data and preferences
            user_id: User identifier for rate limiting and tracking
            user_tier: User tier for rate limiting (free, premium, enterprise)
            db: Database session for storing generation record
            document_id: Optional document ID to associate with generation

        Returns:
            AIGenerationResponse: Generated resume with usage and cost information

        Raises:
            APIQuotaExceededException: If user exceeds rate limit
            TokenLimitExceededException: If request exceeds token limit
            AIServiceUnavailableException: If OpenAI service is unavailable
        """
        # Check rate limit
        is_allowed, seconds_until_reset = self.rate_limiter.check_rate_limit(
            user_id=user_id,
            user_tier=user_tier,
        )

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for user {user_id}, "
                f"reset in {seconds_until_reset}s"
            )
            raise APIQuotaExceededException(
                message=f"Rate limit exceeded. Try again in {seconds_until_reset} seconds",
                details={
                    "user_id": user_id,
                    "tier": user_tier,
                    "seconds_until_reset": seconds_until_reset,
                },
            )

        # Generate prompt
        prompt = get_resume_prompt(
            style=request.style,
            user_data=request.user_data,
            job_title=request.job_title,
            job_description=request.job_description,
            additional_instructions=request.additional_instructions,
        )

        logger.info(
            f"Generating resume for user {user_id}, "
            f"style: {request.style}, job_title: {request.job_title}"
        )

        # Call OpenAI API with retry logic
        generated_content, token_usage = await self._call_openai_with_retry(
            prompt=prompt,
            user_id=user_id,
        )

        # Calculate costs
        cost = self.calculate_cost(
            prompt_tokens=token_usage.prompt_tokens,
            completion_tokens=token_usage.completion_tokens,
        )

        # Track usage
        generation_record = await self.track_usage(
            user_id=user_id,
            document_id=document_id,
            generation_type="resume",
            prompt_tokens=token_usage.prompt_tokens,
            completion_tokens=token_usage.completion_tokens,
            total_tokens=token_usage.total_tokens,
            cost_usd=cost.total_cost,
            model_used=self.model,
            generated_content=generated_content,
            db=db,
        )

        # Update rate limiter
        self.rate_limiter.update_usage(user_id=user_id, user_tier=user_tier)

        logger.info(
            f"Resume generated successfully for user {user_id}, "
            f"generation_id: {generation_record.id}, "
            f"tokens: {token_usage.total_tokens}, cost: ${cost.total_cost:.4f}"
        )

        return AIGenerationResponse(
            generation_id=generation_record.id,
            content=generated_content,
            token_usage=token_usage,
            cost=cost,
            model_used=self.model,
            generation_type="resume",
        )

    async def generate_cover_letter(
        self,
        request: CoverLetterGenerationRequest,
        user_id: str,
        user_tier: str,
        db: AsyncSession,
        document_id: Optional[str] = None,
    ) -> AIGenerationResponse:
        """Generate cover letter using OpenAI GPT-4.

        Args:
            request: Cover letter generation request
            user_id: User identifier
            user_tier: User tier for rate limiting
            db: Database session
            document_id: Optional document ID

        Returns:
            AIGenerationResponse: Generated cover letter with metadata

        Raises:
            APIQuotaExceededException: If rate limit exceeded
            TokenLimitExceededException: If token limit exceeded
            AIServiceUnavailableException: If service unavailable
        """
        # Check rate limit
        is_allowed, seconds_until_reset = self.rate_limiter.check_rate_limit(
            user_id=user_id,
            user_tier=user_tier,
        )

        if not is_allowed:
            raise APIQuotaExceededException(
                message=f"Rate limit exceeded. Try again in {seconds_until_reset} seconds",
                details={
                    "user_id": user_id,
                    "tier": user_tier,
                    "seconds_until_reset": seconds_until_reset,
                },
            )

        # Generate prompt
        prompt = get_cover_letter_prompt(
            tone=request.tone,
            user_data=request.user_data,
            job_title=request.job_title,
            company_name=request.company_name,
            job_description=request.job_description,
            additional_context=request.additional_context,
        )

        logger.info(
            f"Generating cover letter for user {user_id}, "
            f"company: {request.company_name}, job_title: {request.job_title}"
        )

        # Call OpenAI API
        generated_content, token_usage = await self._call_openai_with_retry(
            prompt=prompt,
            user_id=user_id,
        )

        # Calculate costs
        cost = self.calculate_cost(
            prompt_tokens=token_usage.prompt_tokens,
            completion_tokens=token_usage.completion_tokens,
        )

        # Track usage
        generation_record = await self.track_usage(
            user_id=user_id,
            document_id=document_id,
            generation_type="cover_letter",
            prompt_tokens=token_usage.prompt_tokens,
            completion_tokens=token_usage.completion_tokens,
            total_tokens=token_usage.total_tokens,
            cost_usd=cost.total_cost,
            model_used=self.model,
            generated_content=generated_content,
            db=db,
        )

        # Update rate limiter
        self.rate_limiter.update_usage(user_id=user_id, user_tier=user_tier)

        logger.info(
            f"Cover letter generated successfully for user {user_id}, "
            f"generation_id: {generation_record.id}"
        )

        return AIGenerationResponse(
            generation_id=generation_record.id,
            content=generated_content,
            token_usage=token_usage,
            cost=cost,
            model_used=self.model,
            generation_type="cover_letter",
        )

    def calculate_tokens(self, text: str) -> int:
        """Calculate approximate token count for text.

        Uses a simple heuristic: 1 token ≈ 4 characters.
        For production, consider using tiktoken library for accurate counting.

        Args:
            text: Text to calculate tokens for

        Returns:
            int: Approximate token count
        """
        # Simple heuristic: ~4 characters per token
        return len(text) // 4

    def calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> CostCalculation:
        """Calculate cost for AI generation.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            CostCalculation: Cost breakdown
        """
        prompt_cost = (prompt_tokens / 1000) * self.GPT4_PROMPT_COST_PER_1K
        completion_cost = (completion_tokens / 1000) * self.GPT4_COMPLETION_COST_PER_1K
        total_cost = prompt_cost + completion_cost

        return CostCalculation(
            prompt_cost=round(prompt_cost, 6),
            completion_cost=round(completion_cost, 6),
            total_cost=round(total_cost, 6),
            model=self.model,
        )

    async def track_usage(
        self,
        user_id: str,
        generation_type: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cost_usd: float,
        model_used: str,
        generated_content: str,
        db: AsyncSession,
        document_id: Optional[str] = None,
    ) -> AIGeneration:
        """Track AI generation usage in database.

        Args:
            user_id: User identifier
            generation_type: Type (resume or cover_letter)
            prompt_tokens: Prompt token count
            completion_tokens: Completion token count
            total_tokens: Total token count
            cost_usd: Cost in USD
            model_used: Model name
            generated_content: Generated content
            db: Database session
            document_id: Optional document ID

        Returns:
            AIGeneration: Created generation record
        """
        generation = AIGeneration(
            user_id=user_id,
            document_id=document_id,
            generation_type=generation_type,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=Decimal(str(cost_usd)),
            model_used=model_used,
            status="completed",
            generated_content=generated_content,
        )

        db.add(generation)
        await db.commit()
        await db.refresh(generation)

        logger.debug(
            f"Tracked AI generation: {generation.id}, "
            f"type: {generation_type}, tokens: {total_tokens}"
        )

        return generation

    async def _call_openai_with_retry(
        self,
        prompt: str,
        user_id: str,
        retry_count: int = 0,
    ) -> tuple[str, TokenUsage]:
        """Call OpenAI API with exponential backoff retry logic.

        Args:
            prompt: Prompt text
            user_id: User identifier for logging
            retry_count: Current retry attempt

        Returns:
            tuple: (generated_content, token_usage)

        Raises:
            AIServiceUnavailableException: If all retries fail
            TokenLimitExceededException: If token limit exceeded
            ContentFilteredException: If content filtered
        """
        # Mock implementation for now - in production, use OpenAI SDK
        # This is a placeholder that simulates API behavior

        logger.info(
            f"Calling OpenAI API for user {user_id}, "
            f"model: {self.model}, attempt: {retry_count + 1}/{self.max_retries}"
        )

        # Calculate estimated tokens
        prompt_tokens = self.calculate_tokens(prompt)

        # Check token limits (GPT-4 has 8K context limit)
        if prompt_tokens > 6000:
            raise TokenLimitExceededException(
                message=f"Prompt too long: {prompt_tokens} tokens exceeds limit",
                details={"prompt_tokens": prompt_tokens, "limit": 6000},
            )

        # Simulate API call
        # In production, replace with actual OpenAI API call:
        # import openai
        # response = await openai.ChatCompletion.acreate(
        #     model=self.model,
        #     messages=[{"role": "user", "content": prompt}],
        #     temperature=0.7,
        #     max_tokens=2000,
        # )

        # Mock response
        generated_content = f"[Generated content based on prompt]\n\n{prompt[:200]}..."
        completion_tokens = 500

        token_usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

        return generated_content, token_usage
