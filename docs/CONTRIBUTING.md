# Contributing to CircuitNet Enhanced

Thank you for your interest in contributing to CircuitNet Enhanced! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We pledge to:

- Be respectful and considerate
- Welcome diverse perspectives
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy toward others

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling or insulting/derogatory remarks
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Basic understanding of electronics and circuits (helpful but not required)

### First Time Contributors

If you're new to open source, here are some good first issues:
- Documentation improvements
- Adding examples
- Fixing typos
- Writing tests
- Adding component support

Look for issues labeled `good-first-issue` or `help-wanted`.

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/AI-Schematic-To-Breadboard.git
cd AI-Schematic-To-Breadboard
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Base dependencies
pip install -r requirements.txt

# Enhanced dependencies
pip install -r requirements-enhanced.txt

# Development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env and add your API keys (if needed for testing)
```

### 5. Extract Dataset (Optional)

```bash
cd dataset/
tar -xzvf circuit_dataset.tar.gz
cd ..
```

### 6. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

---

## How to Contribute

### Types of Contributions

#### 🐛 Bug Fixes
- Fix incorrect behavior
- Resolve crashes or errors
- Improve error messages

#### ✨ New Features
- Add new component types
- Improve algorithms
- Add export formats
- Enhance visualization

#### 📚 Documentation
- Improve README files
- Add code comments
- Create tutorials
- Update API docs

#### 🧪 Tests
- Add unit tests
- Improve test coverage
- Add integration tests
- Create test fixtures

#### 🎨 Design
- Improve UI/UX
- Enhance visualizations
- Create diagrams
- Design examples

---

## Code Style Guidelines

### Python Style

We follow **PEP 8** with some modifications:

#### General Rules
- Maximum line length: 100 characters
- Use 4 spaces for indentation (no tabs)
- Use double quotes for strings
- Add trailing commas in multi-line structures

#### Naming Conventions

```python
# Classes: PascalCase
class BreadboardLayout:
    pass

# Functions and methods: snake_case
def calculate_position(x, y):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_COMPONENTS = 100

# Private methods/attributes: leading underscore
def _internal_method(self):
    pass

# Type hints: Use them!
def process_component(component: Component) -> bool:
    pass
```

#### Docstrings

Use **Google-style docstrings**:

```python
def place_component(component: Component, position: Tuple[int, int]) -> bool:
    """Place a component at the specified position on the breadboard.

    Args:
        component: The component to place.
        position: Tuple of (row, column) coordinates.

    Returns:
        True if placement was successful, False otherwise.

    Raises:
        ValueError: If position is out of bounds.
        ComponentConflictError: If position is already occupied.

    Example:
        >>> layout = BreadboardLayout()
        >>> resistor = Resistor(value=220)
        >>> layout.place_component(resistor, (10, 5))
        True
    """
    pass
```

#### Type Hints

Always use type hints for function signatures:

```python
from typing import List, Dict, Optional, Tuple

def route_connection(
    start: Tuple[int, int],
    end: Tuple[int, int],
    avoid_positions: Optional[List[Tuple[int, int]]] = None
) -> List[Tuple[int, int]]:
    """Route a wire connection between two points."""
    pass
```

#### Imports

Organize imports in this order:
1. Standard library
2. Third-party packages
3. Local modules

```python
# Standard library
import os
import sys
from typing import List, Dict

# Third-party
import numpy as np
import matplotlib.pyplot as plt

# Local
from breadboard.layout_engine import BreadboardLayout
from breadboard.visualizer import BreadboardVisualizer
```

### Code Formatting

Use **Black** for automatic formatting:

```bash
# Format all Python files
black breadboard/ ai_enhancement/ integration/

# Check without modifying
black --check breadboard/
```

### Linting

Use **flake8** for linting:

```bash
# Run linter
flake8 breadboard/ ai_enhancement/ integration/

# With specific configuration
flake8 --max-line-length=100 --ignore=E203,W503 breadboard/
```

### Type Checking

Use **mypy** for static type checking:

```bash
# Run type checker
mypy breadboard/ ai_enhancement/ integration/
```

---

## Testing Guidelines

### Writing Tests

#### Test File Structure

```python
# tests/test_breadboard.py
import pytest
from breadboard.layout_engine import BreadboardLayout, Component

class TestBreadboardLayout:
    """Tests for BreadboardLayout class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.layout = BreadboardLayout()

    def test_initialization(self):
        """Test that layout initializes correctly."""
        assert self.layout.rows == 30
        assert self.layout.columns == 63

    def test_place_component_success(self):
        """Test successful component placement."""
        component = Component(type="resistor", value=220)
        result = self.layout.place_component(component, (10, 5))
        assert result is True
        assert component in self.layout.components

    def test_place_component_conflict(self):
        """Test that placing on occupied position fails."""
        component1 = Component(type="resistor", value=220)
        component2 = Component(type="resistor", value=330)
        
        self.layout.place_component(component1, (10, 5))
        
        with pytest.raises(ComponentConflictError):
            self.layout.place_component(component2, (10, 5))
```

#### Test Coverage Goals

- Minimum 80% code coverage
- 100% coverage for critical algorithms (placement, routing)
- Test edge cases and error conditions

#### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_breadboard.py

# Run with coverage
pytest --cov=breadboard --cov=ai_enhancement --cov=integration

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_breadboard.py::TestBreadboardLayout::test_initialization
```

#### Mocking External Dependencies

```python
import pytest
from unittest.mock import Mock, patch

@patch('ai_enhancement.gpt_vision.OpenAI')
def test_gpt_vision_api_call(mock_openai):
    """Test GPT-4 Vision API integration with mocked response."""
    mock_response = Mock()
    mock_response.choices[0].message.content = '{"components": []}'
    mock_openai.return_value.chat.completions.create.return_value = mock_response
    
    analyzer = SchematicAnalyzer(api_key="test_key")
    result = analyzer.analyze_schematic(test_image)
    
    assert result is not None
    assert 'components' in result
```

---

## Pull Request Process

### Before Submitting

1. **Update your branch**:
   ```bash
   git checkout main
   git pull origin main
   git checkout your-branch
   git rebase main
   ```

2. **Run tests**:
   ```bash
   pytest
   ```

3. **Run linters**:
   ```bash
   black breadboard/ ai_enhancement/ integration/
   flake8 breadboard/ ai_enhancement/ integration/
   ```

4. **Update documentation**:
   - Add docstrings to new functions/classes
   - Update relevant README files
   - Add examples if applicable

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: Add component placement algorithm"
   ```

### Commit Message Format

Follow the **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(breadboard): Add wire routing algorithm

Implement A* pathfinding for wire routing with Manhattan distance
heuristic. Includes conflict avoidance and optimization for minimal
crossings.

Closes #42
```

```
fix(visualizer): Correct component orientation rendering

Fixed issue where some components were rendered with incorrect
orientation on the breadboard.

Fixes #58
```

### Submitting Pull Request

1. **Push to your fork**:
   ```bash
   git push origin your-branch
   ```

2. **Create Pull Request**:
   - Go to GitHub and click "New Pull Request"
   - Select your branch
   - Fill out the PR template

3. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Code refactoring

   ## Testing
   - [ ] Tests pass locally
   - [ ] New tests added
   - [ ] Manual testing performed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No breaking changes
   - [ ] All tests pass
   ```

4. **Review Process**:
   - Address review comments
   - Push updates to the same branch
   - Request re-review when ready

5. **After Merge**:
   - Delete your branch
   - Update your local main branch

---

## Issue Reporting

### Before Creating an Issue

1. **Search existing issues**: Check if already reported
2. **Check documentation**: Ensure it's not a known limitation
3. **Verify bug**: Try to reproduce in a clean environment

### Bug Report Template

```markdown
**Describe the bug**
Clear and concise description of the bug.

**To Reproduce**
Steps to reproduce:
1. Load schematic '...'
2. Run conversion '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- Package versions: [from pip freeze]

**Additional context**
Any other relevant information.
```

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem.

**Describe the solution you'd like**
Clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Additional context**
Mockups, examples, or other relevant information.
```

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code contributions and reviews

### Getting Help

If you need help:
1. Check the documentation in `docs/`
2. Search existing issues
3. Ask in GitHub Discussions
4. Reach out to maintainers

### Recognition

We appreciate all contributions! Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

---

## Additional Resources

### Useful Links

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2)

### Learning Resources

- **Electronics Basics**: [All About Circuits](https://www.allaboutcircuits.com/)
- **Breadboard Tutorial**: [SparkFun Guide](https://learn.sparkfun.com/tutorials/how-to-use-a-breadboard)
- **Python Best Practices**: [Real Python](https://realpython.com/)

---

Thank you for contributing to CircuitNet Enhanced! 🎉

**Questions?** Open an issue or discussion on GitHub.

**Last Updated**: January 2026
