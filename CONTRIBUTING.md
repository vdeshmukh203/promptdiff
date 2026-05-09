# Contributing to promptdiff

Thank you for your interest in contributing!  All contributions — bug reports,
feature requests, documentation improvements, and code — are welcome.

## Getting started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install the development dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. Create a branch for your change:

   ```bash
   git checkout -b my-feature
   ```

## Running the tests

```bash
pytest
```

For coverage:

```bash
pytest --cov=promptdiff --cov-report=term-missing
```

## Code style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- All public functions must have NumPy-style docstrings.
- Keep the library dependency-free (standard library only).
- Add or update tests for any changed behaviour.

## Submitting changes

1. Ensure all tests pass.
2. Open a pull request against the `main` branch with a clear description of
   what the change does and why.
3. Reference any related issues in the PR description.

## Reporting bugs

Please open an issue at
<https://github.com/vdeshmukh203/promptdiff/issues> and include:

- Python version and operating system
- A minimal reproducible example
- The actual vs. expected output

## Code of conduct

Please be respectful and constructive in all interactions.
