"""Unit tests for Q&A database models."""

import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.base import Base
from src.database.models.user import User
from src.database.models.conversation import Conversation, ConversationCategory
from src.database.models.message import Message, SenderType
from src.database.models.message_rating import MessageRating


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a test database session."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def sample_user(test_session):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_123",
        email_verified=True,
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def sample_conversation(test_session, sample_user):
    """Create a sample conversation for testing."""
    conversation = Conversation(
        user_id=sample_user.id,
        title="Help with resume formatting",
        category=ConversationCategory.RESUME_HELP,
        tags=["resume", "formatting", "tips"],
        is_active=True,
    )
    test_session.add(conversation)
    test_session.commit()
    test_session.refresh(conversation)
    return conversation


@pytest.fixture(scope="function")
def sample_message(test_session, sample_conversation):
    """Create a sample message for testing."""
    message = Message(
        conversation_id=sample_conversation.id,
        sender_type=SenderType.USER,
        content="How do I format my resume for a tech job?",
        metadata={"context": "initial_question"},
    )
    test_session.add(message)
    test_session.commit()
    test_session.refresh(message)
    return message


class TestConversationModel:
    """Test cases for Conversation model."""

    def test_conversation_creation(self, test_session, sample_user):
        """Test creating a new conversation."""
        conversation = Conversation(
            user_id=sample_user.id,
            title="Career advice needed",
            category=ConversationCategory.CAREER_ADVICE,
            tags=["career", "guidance"],
            is_active=True,
        )

        test_session.add(conversation)
        test_session.commit()
        test_session.refresh(conversation)

        assert conversation.id is not None
        assert conversation.user_id == sample_user.id
        assert conversation.title == "Career advice needed"
        assert conversation.category == ConversationCategory.CAREER_ADVICE
        assert conversation.tags == ["career", "guidance"]
        assert conversation.is_active is True
        assert conversation.created_at is not None
        assert conversation.updated_at is not None
        assert conversation.last_message_at is None

    def test_conversation_id_is_uuid(self, test_session, sample_conversation):
        """Test that conversation ID is a valid UUID."""
        try:
            uuid.UUID(sample_conversation.id)
        except ValueError:
            pytest.fail("Conversation ID is not a valid UUID")

    def test_conversation_category_enum(self, test_session, sample_user):
        """Test all conversation category enum values."""
        categories = [
            ConversationCategory.RESUME_HELP,
            ConversationCategory.CAREER_ADVICE,
            ConversationCategory.INTERVIEW_PREP,
            ConversationCategory.JOB_SEARCH,
        ]

        for category in categories:
            conversation = Conversation(
                user_id=sample_user.id,
                title=f"Test {category.value}",
                category=category,
                tags=[],
                is_active=True,
            )
            test_session.add(conversation)
            test_session.commit()
            test_session.refresh(conversation)

            assert conversation.category == category

    def test_conversation_tags_json_array(self, test_session, sample_user):
        """Test that tags are stored as JSON array."""
        tags = ["tag1", "tag2", "tag3"]
        conversation = Conversation(
            user_id=sample_user.id,
            title="Tagged conversation",
            category=ConversationCategory.JOB_SEARCH,
            tags=tags,
            is_active=True,
        )

        test_session.add(conversation)
        test_session.commit()
        test_session.refresh(conversation)

        assert conversation.tags == tags
        assert isinstance(conversation.tags, list)

    def test_conversation_default_tags_empty_list(self, test_session, sample_user):
        """Test that tags default to empty list."""
        conversation = Conversation(
            user_id=sample_user.id,
            title="No tags",
            category=ConversationCategory.RESUME_HELP,
            is_active=True,
        )

        test_session.add(conversation)
        test_session.commit()
        test_session.refresh(conversation)

        assert conversation.tags == []

    def test_conversation_is_active_default_true(self, test_session, sample_user):
        """Test that is_active defaults to True."""
        conversation = Conversation(
            user_id=sample_user.id,
            title="Active by default",
            category=ConversationCategory.CAREER_ADVICE,
            tags=[],
        )

        test_session.add(conversation)
        test_session.commit()
        test_session.refresh(conversation)

        assert conversation.is_active is True

    def test_conversation_user_relationship(self, test_session, sample_conversation):
        """Test conversation-user relationship."""
        assert sample_conversation.user is not None
        assert sample_conversation.user.email == "test@example.com"

    def test_conversation_last_message_at_update(self, test_session, sample_user):
        """Test updating last_message_at timestamp."""
        conversation = Conversation(
            user_id=sample_user.id,
            title="Test timestamp",
            category=ConversationCategory.RESUME_HELP,
            tags=[],
            is_active=True,
        )

        test_session.add(conversation)
        test_session.commit()
        test_session.refresh(conversation)

        assert conversation.last_message_at is None

        timestamp = datetime.utcnow()
        conversation.last_message_at = timestamp
        test_session.commit()
        test_session.refresh(conversation)

        assert conversation.last_message_at is not None
        assert abs((conversation.last_message_at - timestamp).total_seconds()) < 1

    def test_conversation_repr(self, test_session, sample_conversation):
        """Test conversation string representation."""
        repr_str = repr(sample_conversation)
        assert "Conversation" in repr_str
        assert sample_conversation.id in repr_str
        assert sample_conversation.title in repr_str
        assert "resume_help" in repr_str


class TestMessageModel:
    """Test cases for Message model."""

    def test_message_creation(self, test_session, sample_conversation):
        """Test creating a new message."""
        message = Message(
            conversation_id=sample_conversation.id,
            sender_type=SenderType.AI,
            content="Here are some tips for resume formatting...",
            metadata={"model": "gpt-4", "tokens": 150},
        )

        test_session.add(message)
        test_session.commit()
        test_session.refresh(message)

        assert message.id is not None
        assert message.conversation_id == sample_conversation.id
        assert message.sender_type == SenderType.AI
        assert "tips for resume formatting" in message.content
        assert message.metadata == {"model": "gpt-4", "tokens": 150}
        assert message.created_at is not None
        assert message.updated_at is not None

    def test_message_id_is_uuid(self, test_session, sample_message):
        """Test that message ID is a valid UUID."""
        try:
            uuid.UUID(sample_message.id)
        except ValueError:
            pytest.fail("Message ID is not a valid UUID")

    def test_message_sender_type_enum(self, test_session, sample_conversation):
        """Test both sender type enum values."""
        user_message = Message(
            conversation_id=sample_conversation.id,
            sender_type=SenderType.USER,
            content="User question",
            metadata={},
        )

        ai_message = Message(
            conversation_id=sample_conversation.id,
            sender_type=SenderType.AI,
            content="AI response",
            metadata={},
        )

        test_session.add(user_message)
        test_session.add(ai_message)
        test_session.commit()
        test_session.refresh(user_message)
        test_session.refresh(ai_message)

        assert user_message.sender_type == SenderType.USER
        assert ai_message.sender_type == SenderType.AI

    def test_message_content_text_field(self, test_session, sample_conversation):
        """Test that content can store long text."""
        long_content = "A" * 10000
        message = Message(
            conversation_id=sample_conversation.id,
            sender_type=SenderType.USER,
            content=long_content,
            metadata={},
        )

        test_session.add(message)
        test_session.commit()
        test_session.refresh(message)

        assert message.content == long_content
        assert len(message.content) == 10000

    def test_message_metadata_json_field(self, test_session, sample_conversation):
        """Test that metadata is stored as JSON."""
        metadata = {
            "model": "gpt-4",
            "temperature": 0.7,
            "tokens": 200,
            "tags": ["helpful", "detailed"],
        }
        message = Message(
            conversation_id=sample_conversation.id,
            sender_type=SenderType.AI,
            content="Response with metadata",
            metadata=metadata,
        )

        test_session.add(message)
        test_session.commit()
        test_session.refresh(message)

        assert message.metadata == metadata
        assert isinstance(message.metadata, dict)

    def test_message_default_metadata_empty_dict(self, test_session, sample_conversation):
        """Test that metadata defaults to empty dict."""
        message = Message(
            conversation_id=sample_conversation.id,
            sender_type=SenderType.USER,
            content="No metadata",
        )

        test_session.add(message)
        test_session.commit()
        test_session.refresh(message)

        assert message.metadata == {}

    def test_message_conversation_relationship(self, test_session, sample_message):
        """Test message-conversation relationship."""
        assert sample_message.conversation is not None
        assert sample_message.conversation.title == "Help with resume formatting"

    def test_message_threading(self, test_session, sample_conversation):
        """Test multiple messages in a conversation thread."""
        messages = []
        for i in range(5):
            sender = SenderType.USER if i % 2 == 0 else SenderType.AI
            message = Message(
                conversation_id=sample_conversation.id,
                sender_type=sender,
                content=f"Message {i}",
                metadata={},
            )
            test_session.add(message)
            messages.append(message)

        test_session.commit()

        conversation_messages = (
            test_session.query(Message)
            .filter(Message.conversation_id == sample_conversation.id)
            .order_by(Message.created_at)
            .all()
        )

        assert len(conversation_messages) == 5
        for i, msg in enumerate(conversation_messages):
            assert msg.content == f"Message {i}"

    def test_message_repr(self, test_session, sample_message):
        """Test message string representation."""
        repr_str = repr(sample_message)
        assert "Message" in repr_str
        assert sample_message.id in repr_str
        assert "user" in repr_str

    def test_message_repr_with_long_content(self, test_session, sample_conversation):
        """Test message repr truncates long content."""
        long_content = "A" * 100
        message = Message(
            conversation_id=sample_conversation.id,
            sender_type=SenderType.USER,
            content=long_content,
            metadata={},
        )

        test_session.add(message)
        test_session.commit()
        test_session.refresh(message)

        repr_str = repr(message)
        assert "..." in repr_str
        assert len(repr_str) < 200


class TestMessageRatingModel:
    """Test cases for MessageRating model."""

    def test_message_rating_creation(self, test_session, sample_message, sample_user):
        """Test creating a new message rating."""
        rating = MessageRating(
            message_id=sample_message.id,
            user_id=sample_user.id,
            rating=5,
            feedback_text="Very helpful response!",
            helpful=True,
        )

        test_session.add(rating)
        test_session.commit()
        test_session.refresh(rating)

        assert rating.id is not None
        assert rating.message_id == sample_message.id
        assert rating.user_id == sample_user.id
        assert rating.rating == 5
        assert rating.feedback_text == "Very helpful response!"
        assert rating.helpful is True
        assert rating.created_at is not None
        assert rating.updated_at is not None

    def test_message_rating_id_is_uuid(self, test_session, sample_message, sample_user):
        """Test that rating ID is a valid UUID."""
        rating = MessageRating(
            message_id=sample_message.id,
            user_id=sample_user.id,
            rating=4,
            helpful=True,
        )

        test_session.add(rating)
        test_session.commit()
        test_session.refresh(rating)

        try:
            uuid.UUID(rating.id)
        except ValueError:
            pytest.fail("MessageRating ID is not a valid UUID")

    def test_message_rating_valid_range(self, test_session, sample_message, sample_user):
        """Test rating values from 1 to 5."""
        for rating_value in range(1, 6):
            rating = MessageRating(
                message_id=sample_message.id,
                user_id=sample_user.id,
                rating=rating_value,
                helpful=True,
            )
            test_session.add(rating)
            test_session.commit()
            test_session.refresh(rating)

            assert rating.rating == rating_value

            # Clean up for next iteration
            test_session.delete(rating)
            test_session.commit()

    def test_message_rating_optional_feedback_text(
        self, test_session, sample_message, sample_user
    ):
        """Test that feedback_text is optional."""
        rating = MessageRating(
            message_id=sample_message.id,
            user_id=sample_user.id,
            rating=3,
            helpful=False,
        )

        test_session.add(rating)
        test_session.commit()
        test_session.refresh(rating)

        assert rating.feedback_text is None

    def test_message_rating_default_helpful_false(
        self, test_session, sample_message, sample_user
    ):
        """Test that helpful defaults to False."""
        rating = MessageRating(
            message_id=sample_message.id,
            user_id=sample_user.id,
            rating=3,
        )

        test_session.add(rating)
        test_session.commit()
        test_session.refresh(rating)

        assert rating.helpful is False

    def test_message_rating_unique_constraint(
        self, test_session, sample_message, sample_user
    ):
        """Test unique constraint on message_id + user_id."""
        rating1 = MessageRating(
            message_id=sample_message.id,
            user_id=sample_user.id,
            rating=5,
            helpful=True,
        )

        test_session.add(rating1)
        test_session.commit()

        rating2 = MessageRating(
            message_id=sample_message.id,
            user_id=sample_user.id,
            rating=3,
            helpful=False,
        )

        test_session.add(rating2)

        with pytest.raises(IntegrityError):
            test_session.commit()

    def test_message_rating_message_relationship(
        self, test_session, sample_message, sample_user
    ):
        """Test message rating-message relationship."""
        rating = MessageRating(
            message_id=sample_message.id,
            user_id=sample_user.id,
            rating=5,
            helpful=True,
        )

        test_session.add(rating)
        test_session.commit()
        test_session.refresh(rating)

        assert rating.message is not None
        assert rating.message.id == sample_message.id

    def test_message_rating_user_relationship(
        self, test_session, sample_message, sample_user
    ):
        """Test message rating-user relationship."""
        rating = MessageRating(
            message_id=sample_message.id,
            user_id=sample_user.id,
            rating=4,
            helpful=True,
        )

        test_session.add(rating)
        test_session.commit()
        test_session.refresh(rating)

        assert rating.user is not None
        assert rating.user.email == sample_user.email

    def test_message_rating_repr(self, test_session, sample_message, sample_user):
        """Test message rating string representation."""
        rating = MessageRating(
            message_id=sample_message.id,
            user_id=sample_user.id,
            rating=5,
            helpful=True,
        )

        test_session.add(rating)
        test_session.commit()
        test_session.refresh(rating)

        repr_str = repr(rating)
        assert "MessageRating" in repr_str
        assert rating.id in repr_str
        assert "5" in repr_str
        assert "True" in repr_str


class TestModelRelationships:
    """Test cases for relationships between models."""

    def test_user_to_conversations(self, test_session, sample_user):
        """Test user can have multiple conversations."""
        conv1 = Conversation(
            user_id=sample_user.id,
            title="Conversation 1",
            category=ConversationCategory.RESUME_HELP,
            tags=[],
            is_active=True,
        )

        conv2 = Conversation(
            user_id=sample_user.id,
            title="Conversation 2",
            category=ConversationCategory.CAREER_ADVICE,
            tags=[],
            is_active=True,
        )

        test_session.add(conv1)
        test_session.add(conv2)
        test_session.commit()

        user_conversations = (
            test_session.query(Conversation)
            .filter(Conversation.user_id == sample_user.id)
            .all()
        )

        assert len(user_conversations) == 2

    def test_conversation_to_messages(self, test_session, sample_conversation):
        """Test conversation can have multiple messages."""
        msg1 = Message(
            conversation_id=sample_conversation.id,
            sender_type=SenderType.USER,
            content="First message",
            metadata={},
        )

        msg2 = Message(
            conversation_id=sample_conversation.id,
            sender_type=SenderType.AI,
            content="Second message",
            metadata={},
        )

        msg3 = Message(
            conversation_id=sample_conversation.id,
            sender_type=SenderType.USER,
            content="Third message",
            metadata={},
        )

        test_session.add(msg1)
        test_session.add(msg2)
        test_session.add(msg3)
        test_session.commit()

        conversation_messages = (
            test_session.query(Message)
            .filter(Message.conversation_id == sample_conversation.id)
            .all()
        )

        assert len(conversation_messages) == 3

    def test_message_to_ratings(self, test_session, sample_message, sample_user):
        """Test message can have ratings."""
        rating = MessageRating(
            message_id=sample_message.id,
            user_id=sample_user.id,
            rating=5,
            helpful=True,
        )

        test_session.add(rating)
        test_session.commit()

        message_ratings = (
            test_session.query(MessageRating)
            .filter(MessageRating.message_id == sample_message.id)
            .all()
        )

        assert len(message_ratings) == 1
        assert message_ratings[0].rating == 5


class TestModelConstraintsAndEdgeCases:
    """Test cases for constraints and edge cases."""

    def test_conversation_without_user_fails(self, test_session):
        """Test that conversation requires valid user_id."""
        conversation = Conversation(
            user_id="non-existent-user-id",
            title="Test",
            category=ConversationCategory.RESUME_HELP,
            tags=[],
            is_active=True,
        )

        test_session.add(conversation)

        with pytest.raises(IntegrityError):
            test_session.commit()

    def test_message_without_conversation_fails(self, test_session):
        """Test that message requires valid conversation_id."""
        message = Message(
            conversation_id="non-existent-conversation-id",
            sender_type=SenderType.USER,
            content="Test message",
            metadata={},
        )

        test_session.add(message)

        with pytest.raises(IntegrityError):
            test_session.commit()

    def test_empty_conversation_title(self, test_session, sample_user):
        """Test conversation with empty title."""
        conversation = Conversation(
            user_id=sample_user.id,
            title="",
            category=ConversationCategory.JOB_SEARCH,
            tags=[],
            is_active=True,
        )

        test_session.add(conversation)
        test_session.commit()
        test_session.refresh(conversation)

        assert conversation.title == ""

    def test_empty_message_content(self, test_session, sample_conversation):
        """Test message with empty content."""
        message = Message(
            conversation_id=sample_conversation.id,
            sender_type=SenderType.USER,
            content="",
            metadata={},
        )

        test_session.add(message)
        test_session.commit()
        test_session.refresh(message)

        assert message.content == ""

    def test_message_rating_updated_at_changes(
        self, test_session, sample_message, sample_user
    ):
        """Test that updated_at changes when rating is updated."""
        rating = MessageRating(
            message_id=sample_message.id,
            user_id=sample_user.id,
            rating=3,
            helpful=False,
        )

        test_session.add(rating)
        test_session.commit()
        test_session.refresh(rating)

        original_updated_at = rating.updated_at

        # Update rating
        rating.rating = 5
        rating.helpful = True
        test_session.commit()
        test_session.refresh(rating)

        assert rating.updated_at > original_updated_at
