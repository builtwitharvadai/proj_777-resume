"""Conversation export service for PDF and JSON generation."""

import io
import json
import logging
from datetime import datetime
from typing import Dict, List
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus.tables import Table, TableStyle
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models.conversation import Conversation
from src.database.models.message import Message

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting conversations to various formats.

    Supports PDF and JSON export with proper formatting and metadata.
    """

    async def export_to_pdf(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        user_id: str,
    ) -> bytes:
        """Export conversation to PDF format.

        Args:
            db: Database session
            conversation_id: Conversation ID to export
            user_id: User ID for authorization

        Returns:
            PDF file as bytes

        Raises:
            ValueError: If conversation not found or unauthorized
        """
        try:
            logger.info(
                "Exporting conversation to PDF",
                extra={
                    "conversation_id": str(conversation_id),
                    "user_id": user_id,
                },
            )

            # Fetch conversation with messages
            query = (
                select(Conversation)
                .options(selectinload(Conversation.messages))
                .where(Conversation.id == str(conversation_id))
                .where(Conversation.user_id == user_id)
            )
            result = await db.execute(query)
            conversation = result.scalar_one_or_none()

            if not conversation:
                raise ValueError(
                    f"Conversation {conversation_id} not found or unauthorized"
                )

            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=inch,
                leftMargin=inch,
                topMargin=inch,
                bottomMargin=inch,
            )

            # Build PDF content
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1e3a8a"),
                spaceAfter=30,
            )

            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#3b82f6"),
                spaceAfter=12,
            )

            meta_style = ParagraphStyle(
                "MetaStyle",
                parent=styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#6b7280"),
                spaceAfter=20,
            )

            user_style = ParagraphStyle(
                "UserMessage",
                parent=styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#1f2937"),
                leftIndent=10,
                rightIndent=10,
                spaceAfter=8,
            )

            ai_style = ParagraphStyle(
                "AIMessage",
                parent=styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#374151"),
                leftIndent=10,
                rightIndent=10,
                spaceAfter=8,
                backColor=colors.HexColor("#f3f4f6"),
            )

            # Title
            story.append(Paragraph(conversation.title, title_style))
            story.append(Spacer(1, 12))

            # Metadata
            metadata_text = f"""
            <b>Category:</b> {conversation.category.value}<br/>
            <b>Created:</b> {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <b>Messages:</b> {len(conversation.messages)}<br/>
            <b>Exported:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            """
            story.append(Paragraph(metadata_text, meta_style))
            story.append(Spacer(1, 20))

            # Messages
            for idx, message in enumerate(
                sorted(conversation.messages, key=lambda m: m.created_at), 1
            ):
                # Message header
                sender = "You" if message.sender_type.value == "user" else "AI Assistant"
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                header_text = f"<b>{sender}</b> - {timestamp}"

                story.append(Paragraph(header_text, heading_style))

                # Message content
                content_style = user_style if message.sender_type.value == "user" else ai_style
                # Escape HTML special characters in content
                safe_content = (
                    message.content.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "<br/>")
                )
                story.append(Paragraph(safe_content, content_style))
                story.append(Spacer(1, 16))

                # Add page break after every 5 messages to prevent very long pages
                if idx % 5 == 0 and idx < len(conversation.messages):
                    story.append(PageBreak())

            # Build PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(
                "Conversation exported to PDF successfully",
                extra={
                    "conversation_id": str(conversation_id),
                    "user_id": user_id,
                    "pdf_size": len(pdf_bytes),
                },
            )

            return pdf_bytes

        except ValueError:
            raise
        except Exception as exc:
            logger.error(
                "Failed to export conversation to PDF",
                extra={
                    "conversation_id": str(conversation_id),
                    "user_id": user_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

    async def export_to_json(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        user_id: str,
    ) -> Dict:
        """Export conversation to JSON format.

        Args:
            db: Database session
            conversation_id: Conversation ID to export
            user_id: User ID for authorization

        Returns:
            Conversation data as dictionary

        Raises:
            ValueError: If conversation not found or unauthorized
        """
        try:
            logger.info(
                "Exporting conversation to JSON",
                extra={
                    "conversation_id": str(conversation_id),
                    "user_id": user_id,
                },
            )

            # Fetch conversation with messages
            query = (
                select(Conversation)
                .options(selectinload(Conversation.messages))
                .where(Conversation.id == str(conversation_id))
                .where(Conversation.user_id == user_id)
            )
            result = await db.execute(query)
            conversation = result.scalar_one_or_none()

            if not conversation:
                raise ValueError(
                    f"Conversation {conversation_id} not found or unauthorized"
                )

            # Build JSON structure
            export_data = {
                "id": str(conversation.id),
                "user_id": conversation.user_id,
                "title": conversation.title,
                "category": conversation.category.value,
                "tags": conversation.tags,
                "is_active": conversation.is_active,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "last_message_at": (
                    conversation.last_message_at.isoformat()
                    if conversation.last_message_at
                    else None
                ),
                "exported_at": datetime.utcnow().isoformat(),
                "messages": [
                    {
                        "id": str(message.id),
                        "conversation_id": str(message.conversation_id),
                        "sender_type": message.sender_type.value,
                        "content": message.content,
                        "metadata": message.metadata,
                        "created_at": message.created_at.isoformat(),
                        "updated_at": message.updated_at.isoformat(),
                    }
                    for message in sorted(
                        conversation.messages, key=lambda m: m.created_at
                    )
                ],
            }

            logger.info(
                "Conversation exported to JSON successfully",
                extra={
                    "conversation_id": str(conversation_id),
                    "user_id": user_id,
                    "message_count": len(export_data["messages"]),
                },
            )

            return export_data

        except ValueError:
            raise
        except Exception as exc:
            logger.error(
                "Failed to export conversation to JSON",
                extra={
                    "conversation_id": str(conversation_id),
                    "user_id": user_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

    async def export_multiple_conversations(
        self,
        db: AsyncSession,
        conversation_ids: List[UUID],
        user_id: str,
        format: str = "json",
    ) -> bytes:
        """Export multiple conversations in specified format.

        Args:
            db: Database session
            conversation_ids: List of conversation IDs to export
            user_id: User ID for authorization
            format: Export format ('json' or 'pdf')

        Returns:
            Exported data as bytes

        Raises:
            ValueError: If format is invalid or conversations not found
        """
        try:
            logger.info(
                "Exporting multiple conversations",
                extra={
                    "conversation_count": len(conversation_ids),
                    "user_id": user_id,
                    "format": format,
                },
            )

            if format == "json":
                # Export all conversations to JSON
                conversations_data = []
                for conversation_id in conversation_ids:
                    try:
                        conv_data = await self.export_to_json(
                            db, conversation_id, user_id
                        )
                        conversations_data.append(conv_data)
                    except ValueError as exc:
                        logger.warning(
                            "Skipping conversation in bulk export",
                            extra={
                                "conversation_id": str(conversation_id),
                                "error": str(exc),
                            },
                        )
                        continue

                # Create combined JSON
                export_data = {
                    "export_type": "bulk",
                    "format": "json",
                    "exported_at": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "conversation_count": len(conversations_data),
                    "conversations": conversations_data,
                }

                json_bytes = json.dumps(export_data, indent=2, ensure_ascii=False).encode(
                    "utf-8"
                )

                logger.info(
                    "Multiple conversations exported to JSON successfully",
                    extra={
                        "user_id": user_id,
                        "exported_count": len(conversations_data),
                        "json_size": len(json_bytes),
                    },
                )

                return json_bytes

            elif format == "pdf":
                # For PDF, we'll create a single PDF with all conversations
                raise NotImplementedError(
                    "Bulk PDF export is not yet implemented. "
                    "Please export conversations individually as PDF."
                )
            else:
                raise ValueError(f"Unsupported export format: {format}")

        except (ValueError, NotImplementedError):
            raise
        except Exception as exc:
            logger.error(
                "Failed to export multiple conversations",
                extra={
                    "conversation_count": len(conversation_ids),
                    "user_id": user_id,
                    "format": format,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise
