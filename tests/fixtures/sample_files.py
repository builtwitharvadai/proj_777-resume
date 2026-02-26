"""Test fixtures for sample document files."""

import io
from typing import BinaryIO, Tuple

import pytest


@pytest.fixture
def sample_pdf_file() -> Tuple[BinaryIO, str, str, int]:
    """Create a sample PDF file for testing.

    Returns:
        Tuple containing:
            - File-like object with PDF content
            - Filename
            - MIME type
            - File size in bytes
    """
    # Minimal valid PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Resume) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000214 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
306
%%EOF
"""
    file_obj = io.BytesIO(pdf_content)
    filename = "test_resume.pdf"
    mime_type = "application/pdf"
    file_size = len(pdf_content)

    return file_obj, filename, mime_type, file_size


@pytest.fixture
def sample_docx_file() -> Tuple[BinaryIO, str, str, int]:
    """Create a sample DOCX file for testing.

    Returns:
        Tuple containing:
            - File-like object with DOCX content
            - Filename
            - MIME type
            - File size in bytes
    """
    # Minimal DOCX file structure (ZIP-based)
    # This is a simplified mock that starts with ZIP signature
    docx_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"
    docx_content += b"\x00" * 20  # Simplified ZIP header
    docx_content += b"[Content_Types].xml"
    docx_content += b"\x00" * 50
    docx_content += b"word/document.xml"
    docx_content += b"\x00" * 100
    docx_content += b"<w:document><w:body><w:p><w:r><w:t>Test Resume Content</w:t></w:r></w:p></w:body></w:document>"
    docx_content += b"\x00" * 50

    file_obj = io.BytesIO(docx_content)
    filename = "test_resume.docx"
    mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    file_size = len(docx_content)

    return file_obj, filename, mime_type, file_size


@pytest.fixture
def sample_txt_file() -> Tuple[BinaryIO, str, str, int]:
    """Create a sample TXT file for testing.

    Returns:
        Tuple containing:
            - File-like object with TXT content
            - Filename
            - MIME type
            - File size in bytes
    """
    txt_content = b"""John Doe
Software Engineer

Summary:
Experienced software engineer with 5+ years of expertise in Python,
FastAPI, and cloud technologies. Proven track record of building
scalable web applications and RESTful APIs.

Experience:
Senior Software Engineer - Tech Company (2020-Present)
- Developed microservices architecture using FastAPI
- Implemented CI/CD pipelines with GitHub Actions
- Reduced API response time by 40%

Software Engineer - Startup Inc (2018-2020)
- Built RESTful APIs with Python and Django
- Collaborated with frontend team on React integration
- Mentored junior developers

Education:
B.S. Computer Science - University (2018)

Skills:
Python, FastAPI, Django, PostgreSQL, Docker, Kubernetes, AWS,
Git, REST APIs, Microservices, CI/CD, Testing, Agile
"""
    file_obj = io.BytesIO(txt_content)
    filename = "test_resume.txt"
    mime_type = "text/plain"
    file_size = len(txt_content)

    return file_obj, filename, mime_type, file_size


@pytest.fixture
def sample_large_file() -> Tuple[BinaryIO, str, str, int]:
    """Create a large file that exceeds size limit for testing.

    Returns:
        Tuple containing:
            - File-like object with large content
            - Filename
            - MIME type
            - File size in bytes
    """
    # Create a file larger than 10MB (default limit)
    large_content = b"%PDF-1.4\n" + (b"0" * (11 * 1024 * 1024))
    file_obj = io.BytesIO(large_content)
    filename = "large_file.pdf"
    mime_type = "application/pdf"
    file_size = len(large_content)

    return file_obj, filename, mime_type, file_size


@pytest.fixture
def sample_invalid_file() -> Tuple[BinaryIO, str, str, int]:
    """Create an invalid file with unsupported type for testing.

    Returns:
        Tuple containing:
            - File-like object with invalid content
            - Filename
            - MIME type
            - File size in bytes
    """
    # Executable file signature
    invalid_content = b"MZ\x90\x00\x03\x00\x00\x00"
    invalid_content += b"\x00" * 100
    file_obj = io.BytesIO(invalid_content)
    filename = "malicious.exe"
    mime_type = "application/x-executable"
    file_size = len(invalid_content)

    return file_obj, filename, mime_type, file_size


@pytest.fixture
def sample_corrupted_pdf() -> Tuple[BinaryIO, str, str, int]:
    """Create a corrupted PDF file for testing.

    Returns:
        Tuple containing:
            - File-like object with corrupted PDF content
            - Filename
            - MIME type
            - File size in bytes
    """
    # Invalid PDF without proper header
    corrupted_content = b"NOT A PDF FILE\n"
    corrupted_content += b"Some random content that looks like PDF but isn't"
    corrupted_content += b"\x00" * 100

    file_obj = io.BytesIO(corrupted_content)
    filename = "corrupted.pdf"
    mime_type = "application/pdf"
    file_size = len(corrupted_content)

    return file_obj, filename, mime_type, file_size


@pytest.fixture
def sample_empty_file() -> Tuple[BinaryIO, str, str, int]:
    """Create an empty file for testing.

    Returns:
        Tuple containing:
            - File-like object with no content
            - Filename
            - MIME type
            - File size in bytes
    """
    file_obj = io.BytesIO(b"")
    filename = "empty.pdf"
    mime_type = "application/pdf"
    file_size = 0

    return file_obj, filename, mime_type, file_size


@pytest.fixture
def sample_doc_file() -> Tuple[BinaryIO, str, str, int]:
    """Create a sample DOC file (legacy Word format) for testing.

    Returns:
        Tuple containing:
            - File-like object with DOC content
            - Filename
            - MIME type
            - File size in bytes
    """
    # OLE (Object Linking and Embedding) file signature for DOC
    doc_content = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
    doc_content += b"\x00" * 20
    doc_content += b"Microsoft Word Document"
    doc_content += b"\x00" * 100
    doc_content += b"Test resume content in legacy Word format"
    doc_content += b"\x00" * 200

    file_obj = io.BytesIO(doc_content)
    filename = "test_resume.doc"
    mime_type = "application/msword"
    file_size = len(doc_content)

    return file_obj, filename, mime_type, file_size


def create_test_file(
    content: bytes, filename: str, mime_type: str
) -> Tuple[BinaryIO, str, str, int]:
    """Create a custom test file with specified content.

    Args:
        content: File content as bytes
        filename: Name of the file
        mime_type: MIME type of the file

    Returns:
        Tuple containing:
            - File-like object with content
            - Filename
            - MIME type
            - File size in bytes

    Example:
        file_obj, name, mime, size = create_test_file(
            b"%PDF-1.4 content",
            "custom.pdf",
            "application/pdf"
        )
    """
    file_obj = io.BytesIO(content)
    file_size = len(content)
    return file_obj, filename, mime_type, file_size
