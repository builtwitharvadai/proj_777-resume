"""Unit tests for database models."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.base import Base
from src.database.models.user import User


@pytest.fixture(scope="function")
def test_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a database session for testing."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


class TestUserModel:
    """Test cases for the User model."""

    def test_user_creation(self, test_session):
        """Test creating a user with valid data."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            email_verified=False,
        )
        test_session.add(user)
        test_session.commit()

        # Verify user was created
        assert user.id is not None
        assert len(user.id) == 36
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.email_verified is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_id_is_uuid(self, test_session):
        """Test that user ID is a valid UUID."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
        )
        test_session.add(user)
        test_session.commit()

        # Verify ID is a valid UUID
        try:
            uuid.UUID(user.id)
        except ValueError:
            pytest.fail("User ID is not a valid UUID")

    def test_user_email_unique_constraint(self, test_session):
        """Test that email must be unique."""
        user1 = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
        )
        test_session.add(user1)
        test_session.commit()

        # Attempt to create another user with the same email
        user2 = User(
            email="test@example.com",
            hashed_password="different_password",
        )
        test_session.add(user2)

        with pytest.raises(IntegrityError):
            test_session.commit()

    def test_user_email_not_null(self, test_session):
        """Test that email field cannot be null."""
        user = User(
            email=None,
            hashed_password="hashed_password_123",
        )
        test_session.add(user)

        with pytest.raises(IntegrityError):
            test_session.commit()

    def test_user_hashed_password_not_null(self, test_session):
        """Test that hashed_password field cannot be null."""
        user = User(
            email="test@example.com",
            hashed_password=None,
        )
        test_session.add(user)

        with pytest.raises(IntegrityError):
            test_session.commit()

    def test_user_email_verified_default(self, test_session):
        """Test that email_verified defaults to False."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
        )
        test_session.add(user)
        test_session.commit()

        assert user.email_verified is False

    def test_user_timestamps_auto_set(self, test_session):
        """Test that created_at and updated_at are automatically set."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
        )

        before_creation = datetime.utcnow()
        test_session.add(user)
        test_session.commit()
        after_creation = datetime.utcnow()

        assert before_creation <= user.created_at <= after_creation
        assert before_creation <= user.updated_at <= after_creation
        assert user.created_at == user.updated_at

    def test_user_updated_at_changes_on_update(self, test_session):
        """Test that updated_at changes when user is updated."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
        )
        test_session.add(user)
        test_session.commit()

        original_updated_at = user.updated_at

        # Update the user
        user.email_verified = True
        test_session.commit()

        assert user.updated_at >= original_updated_at

    def test_user_to_dict(self, test_session):
        """Test serialization to dictionary."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            email_verified=True,
        )
        test_session.add(user)
        test_session.commit()

        user_dict = user.to_dict()

        assert user_dict["id"] == user.id
        assert user_dict["email"] == "test@example.com"
        assert user_dict["hashed_password"] == "hashed_password_123"
        assert user_dict["email_verified"] is True
        assert isinstance(user_dict["created_at"], str)
        assert isinstance(user_dict["updated_at"], str)

    def test_user_to_dict_exclude_fields(self, test_session):
        """Test serialization with excluded fields."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
        )
        test_session.add(user)
        test_session.commit()

        user_dict = user.to_dict(exclude={"hashed_password"})

        assert "hashed_password" not in user_dict
        assert "email" in user_dict

    def test_user_update_from_dict(self, test_session):
        """Test updating user from dictionary."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            email_verified=False,
        )
        test_session.add(user)
        test_session.commit()

        user.update_from_dict({"email_verified": True})
        test_session.commit()

        assert user.email_verified is True

    def test_user_update_from_dict_ignores_id(self, test_session):
        """Test that update_from_dict ignores id field."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
        )
        test_session.add(user)
        test_session.commit()

        original_id = user.id
        user.update_from_dict({"id": "new-id-should-be-ignored"})
        test_session.commit()

        assert user.id == original_id

    def test_user_repr(self, test_session):
        """Test string representation of User."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            email_verified=True,
        )
        test_session.add(user)
        test_session.commit()

        repr_str = repr(user)

        assert "User" in repr_str
        assert user.id in repr_str
        assert "test@example.com" in repr_str
        assert "email_verified=True" in repr_str

    def test_user_query_by_email(self, test_session):
        """Test querying user by email."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
        )
        test_session.add(user)
        test_session.commit()

        # Query by email
        result = test_session.execute(
            select(User).where(User.email == "test@example.com")
        )
        found_user = result.scalar_one()

        assert found_user.id == user.id
        assert found_user.email == "test@example.com"

    def test_user_email_verified_index(self, test_session):
        """Test that composite index on email and email_verified exists."""
        # Create multiple users
        users = [
            User(
                email=f"user{i}@example.com",
                hashed_password="password",
                email_verified=(i % 2 == 0),
            )
            for i in range(5)
        ]
        test_session.add_all(users)
        test_session.commit()

        # Query using the indexed fields
        result = test_session.execute(
            select(User).where(
                User.email.like("%@example.com"),
                User.email_verified == True,  # noqa: E712
            )
        )
        verified_users = result.scalars().all()

        assert len(verified_users) == 3
        for user in verified_users:
            assert user.email_verified is True
