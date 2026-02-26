"""Rate limiting service for AI API calls with user tier support."""

import logging
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AIRateLimiter:
    """Rate limiter for AI API calls with sliding window algorithm.

    Supports different rate limits per user tier (free, premium, enterprise).
    Uses in-memory storage for tracking usage windows.

    Attributes:
        limits: Dictionary mapping user tiers to their rate limits
        usage: Dictionary tracking usage per user
    """

    def __init__(
        self,
        free_limit: int = 10,
        premium_limit: int = 100,
        enterprise_limit: int = 1000,
        window_seconds: int = 3600,
    ) -> None:
        """Initialize AIRateLimiter.

        Args:
            free_limit: Rate limit for free tier users (requests per window)
            premium_limit: Rate limit for premium tier users
            enterprise_limit: Rate limit for enterprise tier users
            window_seconds: Time window in seconds for rate limiting
        """
        self.limits = {
            "free": free_limit,
            "premium": premium_limit,
            "enterprise": enterprise_limit,
        }
        self.window_seconds = window_seconds
        self.usage: Dict[str, list] = {}

        logger.info(
            f"AIRateLimiter initialized with limits: {self.limits}, "
            f"window: {window_seconds}s"
        )

    def check_rate_limit(
        self,
        user_id: str,
        user_tier: str = "free",
    ) -> tuple[bool, Optional[int]]:
        """Check if user can make an AI API request.

        Args:
            user_id: Unique identifier for the user
            user_tier: User tier (free, premium, enterprise)

        Returns:
            tuple: (is_allowed, seconds_until_reset)
                - is_allowed: True if request is allowed, False if rate limit exceeded
                - seconds_until_reset: None if allowed, otherwise seconds until limit resets
        """
        current_time = time.time()
        user_key = f"{user_id}:{user_tier}"

        # Get user's limit based on tier
        limit = self.limits.get(user_tier, self.limits["free"])

        # Initialize user's usage history if not exists
        if user_key not in self.usage:
            self.usage[user_key] = []

        # Remove timestamps outside the current window
        window_start = current_time - self.window_seconds
        self.usage[user_key] = [
            ts for ts in self.usage[user_key] if ts > window_start
        ]

        # Check if limit exceeded
        current_count = len(self.usage[user_key])

        if current_count >= limit:
            # Calculate time until oldest request expires
            oldest_timestamp = min(self.usage[user_key])
            seconds_until_reset = int(
                (oldest_timestamp + self.window_seconds) - current_time
            )

            logger.warning(
                f"Rate limit exceeded for user {user_id} (tier: {user_tier}). "
                f"Current: {current_count}, Limit: {limit}, "
                f"Reset in: {seconds_until_reset}s"
            )

            return False, seconds_until_reset

        logger.debug(
            f"Rate limit check passed for user {user_id} (tier: {user_tier}). "
            f"Current: {current_count}/{limit}"
        )

        return True, None

    def update_usage(
        self,
        user_id: str,
        user_tier: str = "free",
    ) -> None:
        """Update usage tracking after successful API request.

        Args:
            user_id: Unique identifier for the user
            user_tier: User tier (free, premium, enterprise)
        """
        current_time = time.time()
        user_key = f"{user_id}:{user_tier}"

        # Initialize if needed
        if user_key not in self.usage:
            self.usage[user_key] = []

        # Add current timestamp
        self.usage[user_key].append(current_time)

        logger.debug(
            f"Updated usage for user {user_id} (tier: {user_tier}). "
            f"Total requests in window: {len(self.usage[user_key])}"
        )

    def get_usage_stats(
        self,
        user_id: str,
        user_tier: str = "free",
    ) -> Dict[str, any]:
        """Get current usage statistics for a user.

        Args:
            user_id: Unique identifier for the user
            user_tier: User tier (free, premium, enterprise)

        Returns:
            Dict: Usage statistics including current count, limit, and remaining
        """
        current_time = time.time()
        user_key = f"{user_id}:{user_tier}"
        limit = self.limits.get(user_tier, self.limits["free"])

        if user_key not in self.usage:
            return {
                "user_id": user_id,
                "tier": user_tier,
                "current_count": 0,
                "limit": limit,
                "remaining": limit,
                "window_seconds": self.window_seconds,
            }

        # Clean up old timestamps
        window_start = current_time - self.window_seconds
        self.usage[user_key] = [
            ts for ts in self.usage[user_key] if ts > window_start
        ]

        current_count = len(self.usage[user_key])

        return {
            "user_id": user_id,
            "tier": user_tier,
            "current_count": current_count,
            "limit": limit,
            "remaining": max(0, limit - current_count),
            "window_seconds": self.window_seconds,
        }

    def reset_user_usage(
        self,
        user_id: str,
        user_tier: str = "free",
    ) -> None:
        """Reset usage tracking for a specific user.

        Args:
            user_id: Unique identifier for the user
            user_tier: User tier (free, premium, enterprise)
        """
        user_key = f"{user_id}:{user_tier}"

        if user_key in self.usage:
            del self.usage[user_key]
            logger.info(f"Reset usage for user {user_id} (tier: {user_tier})")
