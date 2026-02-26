# Resume

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourorg/resume)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen)](https://github.com/yourorg/resume)
[![Coverage](https://img.shields.io/badge/coverage-80%25-green)](https://github.com/yourorg/resume)

An intelligent resume and cover letter generation application that helps users create professional documents based on their uploaded materials and conversational interactions.

## Features

- **Resume Generation**: AI-powered resume creation tailored to user profiles
- **Cover Letter Writing**: Generate customized cover letters based on job requirements
- **Document Upload**: Upload CVs, portfolios, and other supporting documents
- **Q&A System**: Ask questions and get contextual answers about your documents
- **Conversation History**: Track and review past questions and answers
- **User Management**: Secure registration and authentication system

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Virtual environment tool (venv or virtualenv)

### Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourorg/resume.git
cd resume
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
alembic upgrade head
```

## Development Setup

### Running the Application

Start the development server:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

### Running Tests

Run the full test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=src --cov-report=html
```

Run specific test categories:
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m "not slow"    # Skip slow tests
```

### Code Formatting

Format code with Black:
```bash
black src tests
```

Check code style with Flake8:
```bash
flake8 src tests
```

Run security checks with Bandit:
```bash
bandit -r src
```

Run type checking with mypy:
```bash
mypy src
```

### Code Quality Standards

- Maintain minimum 80% test coverage
- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write docstrings for all public modules, classes, and functions
- Ensure all tests pass before committing

## Project Structure

```
resume/
├── src/                # Application source code
│   └── __init__.py
├── tests/              # Test suite
│   ├── __init__.py
│   └── conftest.py
├── .gitignore          # Git ignore patterns
├── .env.example        # Environment variables template
├── pyproject.toml      # Project configuration
└── README.md           # Project documentation
```

## Contributing

1. Create a feature branch from `main`
2. Make your changes following code quality standards
3. Write or update tests for your changes
4. Ensure all tests pass and coverage is maintained
5. Format code with Black and check with Flake8
6. Submit a pull request with a clear description

### Development Workflow

1. Pick an issue or create a new one
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit changes with descriptive messages
4. Push to your branch and create a pull request
5. Address review comments if any
6. Merge after approval

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.
