# Contributing to University Performance Analyzer

Thank you for your interest in contributing to the University Performance Analyzer! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the GitHub issue tracker to report bugs or request features
- Provide detailed information about the issue
- Include steps to reproduce the problem
- Attach relevant files or screenshots

### Suggesting Enhancements
- Use the GitHub issue tracker for feature requests
- Clearly describe the proposed enhancement
- Explain why it would be valuable
- Consider the impact on existing functionality

### Code Contributions
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 🛠️ Development Setup

### Prerequisites
- Python 3.11 or higher
- Git
- Docker (optional)

### Setup Instructions
1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/university-performance-analyzer.git
   cd university-performance-analyzer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-optional.txt  # For development tools
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 📝 Coding Standards

### Python Style Guide
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Maximum line length: 88 characters

### Type Hints
- Use type hints for all function parameters and return values
- Use `typing` module for complex types
- Use `Optional` for nullable values
- Use `Union` for multiple possible types

### Documentation
- Write comprehensive docstrings for all functions and classes
- Use Google-style docstrings
- Include examples in docstrings where helpful
- Update README.md for significant changes

### Example Code Style
```python
from typing import List, Optional, Dict, Any
import pandas as pd

def calculate_gpa(
    student_records: pd.DataFrame, 
    grade_scale: GradeScale
) -> pd.Series:
    """
    Calculate GPA for each student using credit-weighted average.
    
    Args:
        student_records: DataFrame with student course records
        grade_scale: GradeScale instance for grade conversion
        
    Returns:
        Series with GPA for each student
        
    Example:
        >>> df = pd.DataFrame({'Marks': [85, 90], 'CreditHours': [3, 3]})
        >>> gpa = calculate_gpa(df, grade_scale)
        >>> print(gpa)
    """
    # Implementation here
    pass
```

## 🧪 Testing

### Test Requirements
- Write tests for all new functionality
- Maintain test coverage above 80%
- Use descriptive test names
- Test edge cases and error conditions

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_grading.py

# Run specific test
pytest tests/test_grading.py::TestGradeScale::test_marks_to_grade
```

### Test Structure
```python
class TestFeatureName:
    """Test cases for feature functionality."""
    
    def test_feature_valid_input(self):
        """Test feature with valid input."""
        # Arrange
        input_data = create_test_data()
        expected_result = expected_output()
        
        # Act
        result = feature_function(input_data)
        
        # Assert
        assert result == expected_result
    
    def test_feature_edge_case(self):
        """Test feature with edge case input."""
        # Test implementation
        pass
    
    def test_feature_error_handling(self):
        """Test feature error handling."""
        with pytest.raises(ValueError, match="Expected error message"):
            feature_function(invalid_input)
```

## 🔍 Code Review Process

### Pull Request Guidelines
1. **Title**: Use clear, descriptive titles
2. **Description**: Explain what changes were made and why
3. **Tests**: Ensure all tests pass
4. **Documentation**: Update documentation as needed
5. **Size**: Keep PRs focused and reasonably sized

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or clearly documented)
- [ ] Performance implications considered
- [ ] Security implications considered

## 🚀 Release Process

### Version Numbering
We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number updated
- [ ] CHANGELOG.md updated
- [ ] Release notes prepared

## 📋 Issue Templates

### Bug Report
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g. Windows, macOS, Linux]
- Python version: [e.g. 3.11]
- Browser: [e.g. Chrome, Firefox]

**Additional context**
Any other context about the problem.
```

### Feature Request
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions.

**Additional context**
Add any other context or screenshots.
```

## 🤔 Questions and Support

### Getting Help
- Check existing issues and discussions
- Join our community discussions
- Contact the maintainers

### Community Guidelines
- Be respectful and inclusive
- Help others learn and grow
- Share knowledge and experiences
- Follow the code of conduct

## 📚 Resources

### Documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Documentation](https://plotly.com/python/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [isort Import Sorter](https://pycqa.github.io/isort/)
- [flake8 Linter](https://flake8.pycqa.org/)
- [mypy Type Checker](https://mypy.readthedocs.io/)

## 🎯 Contribution Areas

### High Priority
- Performance optimizations
- Additional chart types
- Enhanced PDF reports
- Database integration
- Authentication system

### Medium Priority
- Additional grade scales
- Export formats (Excel, JSON)
- Advanced filtering options
- Custom themes
- API endpoints

### Low Priority
- Documentation improvements
- Code refactoring
- Test coverage improvements
- UI/UX enhancements

## 📊 Project Statistics

- **Lines of Code**: ~5,000
- **Test Coverage**: >80%
- **Dependencies**: 6 core, 8 optional
- **Python Version**: 3.11+
- **License**: MIT

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation
- Community acknowledgments

Thank you for contributing to the University Performance Analyzer! 🎓
