# Contributing to JobApplicationAgent

Thank you for considering contributing to JobApplicationAgent! This document provides guidelines and information for contributors.

## 🎯 Project Vision

JobApplicationAgent aims to democratize job application automation through affordable AI technology. We focus on:
- **Accessibility**: Low-cost AI solutions for job seekers
- **Privacy**: Local data storage and user control
- **Intelligence**: Smart field matching and response generation
- **Ease of Use**: Simple setup and intuitive interfaces

## 🤝 How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Reports** - Help us identify and fix issues
2. **Feature Requests** - Suggest new functionality
3. **Code Contributions** - Submit bug fixes and new features
4. **Documentation** - Improve guides, comments, and examples
5. **Testing** - Add test cases and improve coverage
6. **AI Provider Integration** - Add support for new AI services

### Getting Started

1. **Fork the Repository**
   ```bash
   git clone https://github.com/sanketmuchhala/JobApplicationAgent.git
   cd JobApplicationAgent
   ```

2. **Set Up Development Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run Tests**
   ```bash
   python -m pytest test_basic.py -v --asyncio-mode=auto
   ```

4. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number
   ```

## 📝 Development Guidelines

### Code Style

- **Python Version**: 3.9+
- **Formatting**: Follow PEP 8 style guidelines
- **Type Hints**: Use type annotations for function parameters and return values
- **Documentation**: Add docstrings for all public functions and classes

### Code Organization

```
src/
├── models/          # Pydantic data models
├── services/        # Business logic and AI integrations
├── utils/          # Utility functions and helpers
└── server.py       # Main MCP server implementation
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`

### Testing Guidelines

1. **Write Tests**: All new features should include tests
2. **Test Location**: Place tests in the same directory or `tests/` folder
3. **Test Naming**: `test_feature_name.py`
4. **Async Tests**: Use `pytest-asyncio` for async functionality

```python
import pytest

@pytest.mark.asyncio
async def test_your_feature():
    # Your test implementation
    assert True
```

### Documentation

- **Code Comments**: Explain complex logic and business rules
- **Docstrings**: Use Google-style docstrings
- **README Updates**: Update documentation for new features
- **Examples**: Provide usage examples for new functionality

```python
def analyze_form(html_content: str, job_context: dict = None) -> AnalysisResult:
    """
    Analyze a job application form to extract field structure and requirements.
    
    Args:
        html_content: The HTML content of the job form
        job_context: Optional job context information
        
    Returns:
        AnalysisResult containing extracted fields and metadata
        
    Raises:
        ValidationError: If HTML content is invalid
    """
```

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - Operating System
   - Python version
   - Package versions (`pip list`)

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected behavior
   - Actual behavior

3. **Error Messages**
   - Full stack traces
   - Log outputs
   - Configuration details (without API keys)

4. **Additional Context**
   - Sample forms or data (if relevant)
   - Screenshots (if applicable)

### Feature Requests

For feature requests, please describe:

1. **Problem Statement** - What need does this address?
2. **Proposed Solution** - How should it work?
3. **Alternatives** - Any alternative approaches considered?
4. **Additional Context** - Use cases, mockups, examples

## 🔧 Pull Request Process

### Before Submitting

1. **Update Documentation** - Update README, docstrings, and comments
2. **Add Tests** - Ensure new functionality is tested
3. **Run Tests** - All tests should pass
4. **Check Style** - Follow coding standards
5. **Update Changelog** - Add entry for your changes (if applicable)

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### Review Process

1. **Automated Checks** - CI/CD will run tests and checks
2. **Code Review** - Maintainers will review your code
3. **Feedback** - Address any requested changes
4. **Approval** - Once approved, changes will be merged

## 🔒 Security Considerations

### API Keys and Secrets

- **Never commit API keys** to the repository
- **Use environment variables** for sensitive configuration
- **Update .gitignore** to exclude sensitive files
- **Test with dummy keys** when possible

### Data Privacy

- **Local Storage** - Keep user data local by default
- **Encryption** - Encrypt sensitive data at rest
- **Minimal Data** - Only collect necessary information
- **Clear Policies** - Document data usage clearly

## 🚀 Adding New AI Providers

To add support for a new AI provider:

1. **Create Provider Class**
   ```python
   from src.services.ai_service import AIService
   
   class NewProviderService(AIService):
       async def test_connection(self) -> bool:
           # Implementation
           pass
           
       async def generate_completion(self, prompt: str) -> str:
           # Implementation
           pass
   ```

2. **Add Configuration**
   - Update `AIProviderType` enum
   - Add provider config to `ai_providers.json`
   - Update environment variable handling

3. **Write Tests**
   ```python
   @pytest.mark.asyncio
   async def test_new_provider_connection():
       provider = NewProviderService(config)
       assert await provider.test_connection()
   ```

4. **Update Documentation**
   - Add setup instructions
   - Include pricing information
   - Provide configuration examples

## 📊 Performance Guidelines

### Efficiency Considerations

- **Minimize API Calls** - Use caching and batch processing
- **Optimize Prompts** - Keep prompts concise but effective
- **Handle Rate Limits** - Implement proper retry logic
- **Monitor Costs** - Track token usage and costs

### Scalability

- **Async Operations** - Use async/await for I/O operations
- **Error Handling** - Implement robust error recovery
- **Resource Management** - Clean up resources properly
- **Configuration** - Make settings configurable

## 🌟 Recognition

Contributors will be recognized in:

- **README.md** - Contributors section
- **Release Notes** - Major contribution acknowledgments
- **GitHub** - Contributor graphs and statistics

## 📞 Getting Help

If you need help with contributing:

1. **Check Documentation** - README, SETUP_GUIDE, and code comments
2. **Search Issues** - Look for similar questions or problems
3. **Join Discussions** - Use GitHub Discussions for questions
4. **Contact Maintainers** - Tag @sanketmuchhala for urgent matters

## 🎉 Thank You!

Every contribution makes JobApplicationAgent better for job seekers worldwide. Whether it's a bug fix, new feature, or documentation improvement, your effort helps others achieve their career goals.

Together, we're making job applications more intelligent, efficient, and accessible for everyone.

---

**Happy Contributing!** 🚀

*Questions? Feedback? Reach out through GitHub Issues or Discussions.*