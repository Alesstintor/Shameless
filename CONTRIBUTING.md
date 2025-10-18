# Contributing to Shameless

🎉 Thanks for your interest in contributing to Shameless! This project is part of **Hacktoberfest 2025**.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of NLP and sentiment analysis (helpful but not required)

### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/Shameless.git
cd Shameless

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
make install-dev
# or
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Copy environment file
cp .env.example .env
```

### Verify Setup

```bash
# Run tests
make test

# Run linters
make lint

# Format code
make format
```

## Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding tests

### 2. Make Your Changes

- Write clean, readable code
- Follow the coding standards (see below)
- Add tests for new features
- Update documentation as needed
- Keep commits atomic and focused

### 3. Test Your Changes

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_file.py -v

# Check coverage
pytest --cov --cov-report=html
```

### 4. Lint and Format

```bash
# Format code
make format

# Run linters
make lint

# Or manually
black Sentiment_Analyser/ --line-length=100
isort Sentiment_Analyser/ --profile=black
flake8 Sentiment_Analyser/
mypy Sentiment_Analyser/
```

### 5. Commit Your Changes

Follow the commit message guidelines (see below).

```bash
git add .
git commit -m "feat(scraper): add Reddit collector"
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Pull Request Process

### Before Submitting

- [ ] Code follows the style guide
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow guidelines
- [ ] No merge conflicts
- [ ] Pre-commit hooks pass

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Checklist
- [ ] Tests pass
- [ ] Code formatted
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. At least one maintainer must review and approve
2. All CI checks must pass
3. Any requested changes must be addressed
4. Once approved, maintainers will merge

## Coding Standards

### Python Style Guide

We follow **PEP 8** with these specifics:

- **Line length**: 100 characters
- **Formatter**: Black
- **Import sorting**: isort with Black profile
- **Type hints**: Required for all functions
- **Docstrings**: Google style, required for all public APIs

### Example

```python
from typing import List, Optional

from sentiment_analyser.models import TextPreprocessor


def analyze_texts(
    texts: List[str],
    model_name: str = "default",
    batch_size: int = 32
) -> List[dict]:
    """
    Analyze sentiment of multiple texts.
    
    Args:
        texts: List of texts to analyze
        model_name: Name of the model to use
        batch_size: Size of processing batches
        
    Returns:
        List of dictionaries containing sentiment results
        
    Raises:
        ValueError: If texts list is empty
        
    Example:
        >>> results = analyze_texts(["I love this!", "Terrible"])
        >>> print(results[0]['sentiment'])
        'positive'
    """
    if not texts:
        raise ValueError("Texts list cannot be empty")
    
    # Implementation here
    pass
```

### Type Hints

Always use type hints:

```python
# Good ✅
def process_data(data: List[dict]) -> pd.DataFrame:
    pass

# Bad ❌
def process_data(data):
    pass
```

### Docstrings

Use Google style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Short description of function.
    
    Longer description if needed, explaining what the function does,
    its purpose, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When and why this is raised
        
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

## Testing Guidelines

### Test Organization

```
tests/
├── __init__.py
├── test_scraper.py
├── test_preprocessor.py
├── test_analyzer.py
└── conftest.py  # Shared fixtures
```

### Writing Tests

Use pytest with AAA pattern (Arrange, Act, Assert):

```python
def test_feature_name():
    """Test that feature works correctly."""
    # Arrange
    preprocessor = TextPreprocessor(lowercase=True)
    text = "HELLO WORLD"
    
    # Act
    result = preprocessor.clean(text)
    
    # Assert
    assert result == "hello world"
```

### Test Coverage

- Minimum **80%** coverage for all PRs
- **100%** coverage for critical paths
- Use `pytest --cov` to check coverage

### Test Markers

```python
@pytest.mark.slow
def test_large_dataset():
    """Test with large dataset (takes time)."""
    pass

@pytest.mark.integration
def test_end_to_end():
    """Integration test."""
    pass
```

Run specific markers:
```bash
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests
```

## Commit Message Guidelines

We follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Code style (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring
- **test**: Adding tests
- **chore**: Maintenance tasks

### Scopes

- `scraper`: Data collection module
- `models`: ML models
- `preprocessing`: Text preprocessing
- `api`: API endpoints
- `cli`: Command-line interface
- `config`: Configuration
- `docs`: Documentation

### Examples

```bash
# Good commits ✅
feat(scraper): add Reddit data collector
fix(models): resolve null value handling in preprocessing
docs(readme): update installation instructions
test(preprocessor): add tests for URL extraction
refactor(storage): simplify DataStorage class

# Bad commits ❌
update code
fixed bug
WIP
```

### Commit Body

Add details when needed:

```
feat(scraper): add Reddit data collector

- Implements RedditCollector class
- Supports subreddit and user scraping
- Includes rate limiting
- Adds tests for new functionality

Closes #123
```

## Good First Issues

Looking for something to work on? Check out these areas:

### Easy (Good for beginners)
- 🟢 Add more unit tests
- 🟢 Improve documentation
- 🟢 Fix typos
- 🟢 Add examples to notebooks

### Medium
- 🟡 Add Reddit scraper
- 🟡 Implement new preprocessing options
- 🟡 Add visualization functions
- 🟡 Improve error handling

### Advanced
- 🔴 Fine-tune BERT models
- 🔴 Implement real-time processing
- 🔴 Add FastAPI endpoints
- 🔴 Multi-language support

## Documentation

### Code Documentation

- All public APIs must have docstrings
- Use clear, descriptive variable names
- Add comments for complex logic
- Update README for new features

### Architecture Documentation

Update `.windsurf/` files when making architectural changes:
- `architecture.md` - System design
- `context.md` - Project context
- `rules.md` - Development rules

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Email**: your.email@example.com

## Recognition

All contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Eligible for Hacktoberfest rewards (if participating)

---

**Thank you for contributing to Shameless! 🎉**
