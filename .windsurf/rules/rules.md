---
trigger: model_decision
---

# Shameless - Development Rules & Guidelines

## Code Standards

### Python Style Guide
- Follow PEP 8 strictly
- Use Black for code formatting (line length: 100)
- Use isort for import sorting
- Type hints are mandatory for all functions
- Docstrings required (Google style)

### Naming Conventions
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore()`

### Import Order
1. Standard library imports
2. Third-party imports
3. Local application imports
4. Use absolute imports, avoid relative imports in production code

## Project Structure Rules

### Directory Organization
- Each module must have `__init__.py`
- Keep related functionality together
- Max file length: 500 lines (refactor if exceeded)
- One class per file (exceptions for small helper classes)

### Data Management
- Raw data goes to `data/raw/` (never modify)
- Processed data goes to `data/processed/`
- Models saved in `data/models/` with versioning
- Never commit large data files (use .gitignore)

### Notebooks
- Clear naming: `YYYY-MM-DD_purpose_description.ipynb`
- Include markdown cells explaining each section
- Restart kernel and run all cells before committing
- Extract production code to modules (notebooks for exploration only)

## Git Workflow

### Commit Messages
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
- `feat(scraper): add Twitter rate limit handling`
- `fix(model): resolve null value handling in preprocessing`
- `docs(readme): update installation instructions`

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `fix/*`: Bug fixes
- `experiment/*`: ML experiments (can be messy)

### Pull Requests
- Descriptive title and description
- Reference related issues
- Include tests for new features
- Update documentation
- Ensure CI passes

## Testing Requirements

### Coverage Standards
- Minimum 80% code coverage
- 100% coverage for critical paths (data loss, security)
- Unit tests for all business logic
- Integration tests for API endpoints

### Testing Structure
```python
# tests/test_module.py
import pytest

class TestClassName:
    def test_specific_behavior(self):
        # Arrange
        # Act
        # Assert
        pass
```

### Fixtures
- Use pytest fixtures for common setup
- Keep fixtures in `conftest.py`
- Mock external API calls

## ML/Data Science Rules

### Experimentation
- Log all experiments with MLflow
- Document hyperparameters
- Save experiment results
- Version control datasets (DVC)

### Model Development
- Always split: train (70%), validation (15%), test (15%)
- Use cross-validation for small datasets
- Set random seeds for reproducibility
- Baseline model first, then iterate

### Model Deployment
- Model versioning mandatory
- A/B testing before full rollout
- Monitor model drift
- Fallback mechanism if model fails

### Data Processing
```python
# Good: Reusable pipeline
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression())
])

# Bad: Hardcoded preprocessing
data = (data - data.mean()) / data.std()  # Not reusable
```

## Scraping Ethics & Rules

### Rate Limiting
- Respect robots.txt
- Implement exponential backoff
- Max 1 request/second default
- User-Agent header required

### Data Collection
- Only collect publicly available data
- Respect user privacy
- Anonymize personal information
- Store minimal required data

### Error Handling
- Graceful degradation
- Comprehensive logging
- Retry logic with limits
- Alert on critical failures

## Security Rules

### API Keys & Secrets
- Never commit secrets to Git
- Use `.env` files (in `.gitignore`)
- Use environment variables in production
- Rotate keys regularly

### Data Security
- Encrypt sensitive data at rest
- Use HTTPS for all API calls
- Sanitize all user inputs
- Regular security audits

### Dependencies
- Pin dependency versions
- Regular security updates
- Use `pip-audit` for vulnerability scanning
- Review dependencies before adding

## Performance Guidelines

### Code Optimization
- Profile before optimizing
- Use appropriate data structures
- Vectorize operations (NumPy/Pandas)
- Cache expensive computations

### Database Queries
- Use indexes appropriately
- Avoid N+1 queries
- Batch operations when possible
- Connection pooling

### API Performance
- Implement caching (Redis)
- Use pagination for large responses
- Async operations for I/O
- Monitor response times

## Documentation Requirements

### Code Documentation
- Module-level docstring in all `.py` files
- Class docstring explaining purpose
- Function docstring with Args, Returns, Raises
- Complex logic needs inline comments

### Example Docstring
```python
def analyze_sentiment(text: str, model_version: str = "v1") -> dict:
    """
    Analyzes the sentiment of the given text.
    
    Args:
        text: The text to analyze
        model_version: Version of the model to use (default: "v1")
    
    Returns:
        Dictionary containing:
            - sentiment: "positive", "negative", or "neutral"
            - confidence: Float between 0 and 1
            - scores: Dict of all sentiment scores
    
    Raises:
        ValueError: If text is empty
        ModelNotFoundError: If model_version doesn't exist
    
    Example:
        >>> analyze_sentiment("I love this!")
        {'sentiment': 'positive', 'confidence': 0.95, ...}
    """
    pass
```

### Project Documentation
- README.md with setup instructions
- API documentation (OpenAPI/Swagger)
- Architecture diagrams
- Changelog for releases

## Logging Standards

### Log Levels
- **DEBUG**: Detailed diagnostic info
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical issues

### Logging Format
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### What to Log
- Application start/stop
- Configuration changes
- API requests/responses
- Errors and exceptions (with stack trace)
- Performance metrics
- Model predictions (sampling)

## Dependencies Management

### Requirements Files
- `requirements.txt`: Production dependencies (pinned versions)
- `requirements-dev.txt`: Development dependencies
- `requirements-test.txt`: Testing dependencies

### Version Pinning
```txt
# Good: Specific versions
pandas==2.0.3
numpy==1.24.3

# Acceptable: Compatible release
scikit-learn~=1.3.0

# Avoid: Unpinned
# requests  # Bad!
```

## CI/CD Pipeline

### Pre-commit Checks
- Linting (flake8, mypy)
- Formatting (black, isort)
- Tests (pytest)
- Security scan (bandit)

### CI Requirements
- All tests must pass
- Code coverage ≥80%
- No linting errors
- Documentation builds successfully

### Deployment
- Automated to staging on merge to develop
- Manual approval for production
- Rollback plan required
- Health checks post-deployment

## Environment Setup

### Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

### Environment Variables
```bash
# .env.example (commit this)
TWITTER_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost/db
MODEL_PATH=/path/to/models

# .env (DO NOT commit)
TWITTER_API_KEY=actual_secret_key
```

## Code Review Checklist

- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Error handling adequate
- [ ] Performance considered
- [ ] Security reviewed
- [ ] Backwards compatible (if applicable)

## Emergency Procedures

### Production Issues
1. Assess severity
2. Check monitoring/logs
3. Rollback if critical
4. Fix and test
5. Deploy fix
6. Post-mortem

### Data Loss Prevention
- Regular backups (automated)
- Backup verification
- Restore testing
- Incident documentation

## Contact & Resources

- **Project Lead**: [TBD]
- **Documentation**: `/docs`
- **Issue Tracker**: GitHub Issues
- **Chat**: [TBD]
- **Wiki**: [TBD]
