# Contributing to LLM Reliability Lab

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/llm-reliability-lab.git
   cd llm-reliability-lab
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the stack:
   ```bash
   docker compose up --build -d
   ```

## Code Style

- **Python**: Follow PEP 8 guidelines
- **Linting**: We use `ruff` for linting
- **Type hints**: Preferred but not required

## Testing

Run the test suite before submitting:
```bash
PYTHONPATH=. pytest tests/ -v
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure nothing is broken
5. Commit with a descriptive message
6. Push to your fork
7. Open a Pull Request

## What to Contribute

- Bug fixes
- Documentation improvements
- New chaos engineering scenarios
- Dashboard enhancements
- Test coverage improvements

## Questions?

Open an issue for discussion before starting major changes.
