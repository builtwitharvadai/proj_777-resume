"""Full-text search service using PostgreSQL search capabilities."""

import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.conversation import Conversation
from src.database.models.message import Message

logger = logging.getLogger(__name__)


class SearchService:
    """Service for full-text search operations on Q&A messages.

    Uses PostgreSQL tsvector and tsquery for full-text search with
    ranking and highlighting capabilities.
    """

    async def search_messages(
        self,
        db: AsyncSession,
        user_id: str,
        query: str,
        conversation_id: Optional[UUID] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[List[Dict], int]:
        """Search messages using PostgreSQL full-text search.

        Args:
            db: Database session
            user_id: User ID to filter messages
            query: Search query text
            conversation_id: Optional conversation ID to limit search
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            Tuple of (list of message dicts with ranking, total count)
        """
        try:
            logger.info(
                "Searching messages",
                extra={
                    "user_id": user_id,
                    "query": query,
                    "conversation_id": str(conversation_id) if conversation_id else None,
                    "limit": limit,
                    "offset": offset,
                },
            )

            # Build base query with conversation join for user filtering
            base_query = (
                select(Message)
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(Conversation.user_id == user_id)
            )

            # Add conversation filter if provided
            if conversation_id:
                base_query = base_query.where(Message.conversation_id == str(conversation_id))

            # Create tsquery from search query
            tsquery = func.plainto_tsquery("english", query)

            # Add full-text search filter
            search_query = base_query.where(Message.search_vector.op("@@")(tsquery))

            # Get total count
            count_query = select(func.count()).select_from(search_query.subquery())
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0

            # Add ranking and ordering
            rank = func.ts_rank(Message.search_vector, tsquery).label("rank")
            search_query = search_query.add_columns(rank).order_by(rank.desc(), Message.created_at.desc())

            # Apply pagination
            search_query = search_query.offset(offset).limit(limit)

            # Execute search
            result = await db.execute(search_query)
            rows = result.all()

            # Build results with ranking and highlighted content
            messages = []
            for message, rank_score in rows:
                message_dict = {
                    "id": str(message.id),
                    "conversation_id": str(message.conversation_id),
                    "sender_type": message.sender_type.value,
                    "content": message.content,
                    "metadata": message.metadata,
                    "created_at": message.created_at.isoformat(),
                    "rank": float(rank_score) if rank_score else 0.0,
                    "highlighted_content": await self.highlight_matches(
                        db, message.content, query
                    ),
                }
                messages.append(message_dict)

            logger.info(
                "Messages searched successfully",
                extra={
                    "user_id": user_id,
                    "total": total,
                    "returned": len(messages),
                },
            )

            return messages, total

        except Exception as exc:
            logger.error(
                "Failed to search messages",
                extra={
                    "user_id": user_id,
                    "query": query,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

    async def rank_results(
        self,
        db: AsyncSession,
        messages: List[Message],
        query: str,
    ) -> List[Tuple[Message, float]]:
        """Rank search results by relevance.

        Args:
            db: Database session
            messages: List of messages to rank
            query: Search query text

        Returns:
            List of (message, rank_score) tuples sorted by rank
        """
        try:
            logger.debug(
                "Ranking search results",
                extra={
                    "message_count": len(messages),
                    "query": query,
                },
            )

            # Create tsquery from search query
            tsquery = func.plainto_tsquery("english", query)

            # Calculate ranks for all messages
            ranked_messages = []
            for message in messages:
                # Calculate rank score
                rank_query = select(
                    func.ts_rank(Message.search_vector, tsquery)
                ).where(Message.id == message.id)
                result = await db.execute(rank_query)
                rank_score = result.scalar() or 0.0

                ranked_messages.append((message, float(rank_score)))

            # Sort by rank score descending
            ranked_messages.sort(key=lambda x: x[1], reverse=True)

            logger.debug(
                "Results ranked successfully",
                extra={
                    "ranked_count": len(ranked_messages),
                },
            )

            return ranked_messages

        except Exception as exc:
            logger.error(
                "Failed to rank results",
                extra={
                    "message_count": len(messages),
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

    async def highlight_matches(
        self,
        db: AsyncSession,
        content: str,
        query: str,
    ) -> str:
        """Highlight search term matches in content.

        Args:
            db: Database session
            content: Text content to highlight
            query: Search query text

        Returns:
            Content with search terms highlighted
        """
        try:
            # Create tsquery from search query
            tsquery_func = func.plainto_tsquery("english", query)

            # Use ts_headline to highlight matches
            headline_query = select(
                func.ts_headline(
                    "english",
                    content,
                    tsquery_func,
                    "StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=25",
                )
            )

            result = await db.execute(headline_query)
            highlighted = result.scalar()

            return highlighted or content

        except Exception as exc:
            logger.warning(
                "Failed to highlight matches, returning original content",
                extra={
                    "error": str(exc),
                },
            )
            # Return original content if highlighting fails
            return content
