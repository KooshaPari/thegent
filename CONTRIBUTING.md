# Contributing to thegent 🎩

Thank you for your interest in contributing to **thegent**! We welcome contributions of all kinds, including bug fixes, new features, documentation improvements, and bug reports.

## 📋 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive community. Please report any issues to the maintainers.

## 🛠️ Development Setup

We use `uv` for lightning-fast dependency management and `task` as a task runner.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kooshapari/thegent.git
   cd thegent
   ```

2. **Install dependencies:**
   ```bash
   uv sync --extra dev
   ```

3. **Install high-performance shims:**
   ```bash
   thegent install-shims
   ```

4. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

## 🧪 Running Tests & Quality Checks

We maintain strict quality standards to ensure agentic reliability.

- **Run all tests:**
  ```bash
  task test
  ```
- **Run specific test file:**
  ```bash
  uv run pytest tests/test_parser.py
  ```
- **Lint and format:**
  ```bash
  uv run ruff check .
  uv run ruff format .
  ```

## 📜 Coding Guidelines

- **Library-First**: Core logic should be accessible as a library, not just via CLI.
- **Performance**: Use Rust for hot paths (see `crates/`).
- **Test-Driven**: All new features and bug fixes MUST include corresponding tests.
- **Governance**: Reference any relevant Functional Requirements (FRs) or Architecture Decision Records (ADRs) in your PR.

## 🚀 Pull Request Process

1. **Create a branch**: `git checkout -b feature/your-feature-name`
2. **Commit changes**: Ensure clear, descriptive commit messages.
3. **Push to GitHub**: Open a PR against the `main` branch.
4. **Automated CI**: Your PR must pass all CI checks (linting, tests, multi-arch builds).
5. **Review**: Maintainers will review your PR and provide feedback.

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---
Happy coding!
