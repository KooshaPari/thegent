# Contributing to thegent

Thank you for your interest in contributing to **thegent**! We welcome contributions of all kinds, including bug fixes, new features, documentation improvements, and bug reports.

## 🛠️ Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kooshapari/thegent.git
   cd thegent
   ```

2. **Install dependencies:**
   We use `uv` for dependency management.
   ```bash
   uv sync --extra dev
   ```

3. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

## 🧪 Running Tests

```bash
task test
```

## 📜 Coding Guidelines

- We use `ruff` for linting and formatting.
- Ensure all new code has unit tests.
- Reference any relevant Functional Requirements (FRs) in your test docstrings.

## 🚀 Pull Request Process

1. Create a new branch for your feature or bug fix.
2. Ensure all tests pass and linters are happy.
3. Submit a Pull Request with a clear description of your changes.
4. Your PR will be reviewed and merged once it meets our quality standards.

## ⚖️ License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE).
