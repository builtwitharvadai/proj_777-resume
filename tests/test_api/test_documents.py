"""Integration tests for document API endpoints."""

import io
from datetime import datetime
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.database.models.document import Document
from src.main import create_app
from src.storage.exceptions import (
    FileTooLargeException,
    UnsupportedFileTypeException,
    VirusDetectedException,
)


@pytest.fixture
def app() -> Any:
    """Create test application instance.

    Returns:
        FastAPI application instance
    """
    return create_app()


@pytest.fixture
def client(app: Any) -> TestClient:
    """Create test client.

    Args:
        app: FastAPI application instance

    Returns:
        Test client instance
    """
    return TestClient(app)


@pytest.fixture
def mock_auth_user() -> Dict[str, Any]:
    """Mock authenticated user data.

    Returns:
        Dict with user information
    """
    return {
        "id": str(uuid4()),
        "email": "test@example.com",
        "email_verified": True,
    }


@pytest.fixture
def mock_document() -> Document:
    """Create mock document instance.

    Returns:
        Mock document object
    """
    doc = Document(
        user_id=str(uuid4()),
        filename="test-file.pdf",
        original_filename="resume.pdf",
        file_size=102400,
        mime_type="application/pdf",
        s3_key="users/test-user/documents/test-file.pdf",
        upload_date=datetime.utcnow(),
        virus_scan_status="clean",
        virus_scan_date=datetime.utcnow(),
        is_processed=False,
    )
    doc.id = uuid4()
    doc.created_at = datetime.utcnow()
    doc.updated_at = datetime.utcnow()
    return doc


class TestUploadEndpoint:
    """Tests for document upload endpoint."""

    @patch("src.api.documents.get_current_user")
    @patch("src.api.documents.get_document_service")
    def test_upload_success(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_auth_user: Dict[str, Any],
        mock_document: Document,
    ) -> None:
        """Test successful document upload.

        Args:
            mock_get_service: Mock document service
            mock_get_user: Mock user dependency
            client: Test client
            mock_auth_user: Mock user data
            mock_document: Mock document
        """
        # Setup mocks
        mock_user = MagicMock()
        mock_user.id = mock_auth_user["id"]
        mock_get_user.return_value = mock_user

        mock_service = MagicMock()
        mock_service.upload_document = AsyncMock(return_value=mock_document)
        mock_get_service.return_value = mock_service

        # Create test file
        file_content = b"%PDF-1.4 test content"
        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}

        # Make request
        response = client.post("/api/documents/upload", files=files)

        # Assertions
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["original_filename"] == "resume.pdf"
        assert data["file_size"] == 102400
        assert data["virus_scan_status"] == "clean"
        assert data["message"] == "Document uploaded successfully"

    @patch("src.api.documents.get_current_user")
    @patch("src.api.documents.get_document_service")
    def test_upload_file_too_large(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_auth_user: Dict[str, Any],
    ) -> None:
        """Test upload with file too large error.

        Args:
            mock_get_service: Mock document service
            mock_get_user: Mock user dependency
            client: Test client
            mock_auth_user: Mock user data
        """
        # Setup mocks
        mock_user = MagicMock()
        mock_user.id = mock_auth_user["id"]
        mock_get_user.return_value = mock_user

        mock_service = MagicMock()
        mock_service.upload_document = AsyncMock(
            side_effect=FileTooLargeException("test.pdf", 20000000, 10000000)
        )
        mock_get_service.return_value = mock_service

        # Create test file
        file_content = b"%PDF-1.4 test content"
        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}

        # Make request
        response = client.post("/api/documents/upload", files=files)

        # Assertions
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert "detail" in response.json()

    @patch("src.api.documents.get_current_user")
    @patch("src.api.documents.get_document_service")
    def test_upload_unsupported_file_type(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_auth_user: Dict[str, Any],
    ) -> None:
        """Test upload with unsupported file type.

        Args:
            mock_get_service: Mock document service
            mock_get_user: Mock user dependency
            client: Test client
            mock_auth_user: Mock user data
        """
        # Setup mocks
        mock_user = MagicMock()
        mock_user.id = mock_auth_user["id"]
        mock_get_user.return_value = mock_user

        mock_service = MagicMock()
        mock_service.upload_document = AsyncMock(
            side_effect=UnsupportedFileTypeException(
                "test.exe", "application/x-executable", []
            )
        )
        mock_get_service.return_value = mock_service

        # Create test file
        file_content = b"MZ test content"
        files = {"file": ("test.exe", io.BytesIO(file_content), "application/octet-stream")}

        # Make request
        response = client.post("/api/documents/upload", files=files)

        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()

    @patch("src.api.documents.get_current_user")
    @patch("src.api.documents.get_document_service")
    def test_upload_virus_detected(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_auth_user: Dict[str, Any],
    ) -> None:
        """Test upload with virus detected.

        Args:
            mock_get_service: Mock document service
            mock_get_user: Mock user dependency
            client: Test client
            mock_auth_user: Mock user data
        """
        # Setup mocks
        mock_user = MagicMock()
        mock_user.id = mock_auth_user["id"]
        mock_get_user.return_value = mock_user

        mock_service = MagicMock()
        mock_service.upload_document = AsyncMock(
            side_effect=VirusDetectedException("test.pdf", "EICAR-Test-File")
        )
        mock_get_service.return_value = mock_service

        # Create test file
        file_content = b"%PDF-1.4 test content"
        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}

        # Make request
        response = client.post("/api/documents/upload", files=files)

        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()

    def test_upload_without_authentication(self, client: TestClient) -> None:
        """Test upload without authentication.

        Args:
            client: Test client
        """
        # Create test file
        file_content = b"%PDF-1.4 test content"
        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}

        # Make request
        response = client.post("/api/documents/upload", files=files)

        # Assertions
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListEndpoint:
    """Tests for document list endpoint."""

    @patch("src.api.documents.get_current_user")
    @patch("src.api.documents.get_document_service")
    @patch("src.api.documents.get_db")
    def test_list_documents_success(
        self,
        mock_get_db: Any,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_auth_user: Dict[str, Any],
        mock_document: Document,
    ) -> None:
        """Test successful document list retrieval.

        Args:
            mock_get_db: Mock database dependency
            mock_get_service: Mock document service
            mock_get_user: Mock user dependency
            client: Test client
            mock_auth_user: Mock user data
            mock_document: Mock document
        """
        # Setup mocks
        mock_user = MagicMock()
        mock_user.id = mock_auth_user["id"]
        mock_get_user.return_value = mock_user

        mock_service = MagicMock()
        mock_service.list_user_documents = AsyncMock(return_value=[mock_document])
        mock_get_service.return_value = mock_service

        mock_db_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db.return_value = mock_db_session

        # Make request
        response = client.get("/api/documents/")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "documents" in data
        assert "pagination" in data
        assert len(data["documents"]) == 1
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["total"] == 1

    @patch("src.api.documents.get_current_user")
    @patch("src.api.documents.get_document_service")
    @patch("src.api.documents.get_db")
    def test_list_documents_with_pagination(
        self,
        mock_get_db: Any,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_auth_user: Dict[str, Any],
    ) -> None:
        """Test document list with pagination parameters.

        Args:
            mock_get_db: Mock database dependency
            mock_get_service: Mock document service
            mock_get_user: Mock user dependency
            client: Test client
            mock_auth_user: Mock user data
        """
        # Setup mocks
        mock_user = MagicMock()
        mock_user.id = mock_auth_user["id"]
        mock_get_user.return_value = mock_user

        mock_service = MagicMock()
        mock_service.list_user_documents = AsyncMock(return_value=[])
        mock_get_service.return_value = mock_service

        mock_db_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db.return_value = mock_db_session

        # Make request with pagination
        response = client.get("/api/documents/?page=2&size=5")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["size"] == 5

    def test_list_documents_without_authentication(self, client: TestClient) -> None:
        """Test list without authentication.

        Args:
            client: Test client
        """
        # Make request
        response = client.get("/api/documents/")

        # Assertions
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteEndpoint:
    """Tests for document delete endpoint."""

    @patch("src.api.documents.get_current_user")
    @patch("src.api.documents.get_document_service")
    def test_delete_document_success(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_auth_user: Dict[str, Any],
    ) -> None:
        """Test successful document deletion.

        Args:
            mock_get_service: Mock document service
            mock_get_user: Mock user dependency
            client: Test client
            mock_auth_user: Mock user data
        """
        # Setup mocks
        mock_user = MagicMock()
        mock_user.id = mock_auth_user["id"]
        mock_get_user.return_value = mock_user

        mock_service = MagicMock()
        mock_service.delete_document = AsyncMock(return_value=True)
        mock_get_service.return_value = mock_service

        document_id = str(uuid4())

        # Make request
        response = client.delete(f"/api/documents/{document_id}")

        # Assertions
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @patch("src.api.documents.get_current_user")
    @patch("src.api.documents.get_document_service")
    def test_delete_document_not_found(
        self,
        mock_get_service: Any,
        mock_get_user: Any,
        client: TestClient,
        mock_auth_user: Dict[str, Any],
    ) -> None:
        """Test delete with document not found.

        Args:
            mock_get_service: Mock document service
            mock_get_user: Mock user dependency
            client: Test client
            mock_auth_user: Mock user data
        """
        # Setup mocks
        mock_user = MagicMock()
        mock_user.id = mock_auth_user["id"]
        mock_get_user.return_value = mock_user

        mock_service = MagicMock()
        mock_service.delete_document = AsyncMock(
            side_effect=ValueError("Document not found")
        )
        mock_get_service.return_value = mock_service

        document_id = str(uuid4())

        # Make request
        response = client.delete(f"/api/documents/{document_id}")

        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()

    def test_delete_document_without_authentication(self, client: TestClient) -> None:
        """Test delete without authentication.

        Args:
            client: Test client
        """
        document_id = str(uuid4())

        # Make request
        response = client.delete(f"/api/documents/{document_id}")

        # Assertions
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
