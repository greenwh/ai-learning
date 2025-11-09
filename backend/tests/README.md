# Backend Tests

Simple testing setup for the AI Learning System backend.

## Quick Start

From the `backend` directory:

```bash
# Run setup and tests in one command
bash setup_and_test.sh
```

## Scripts

### `setup_and_test.sh` (in backend directory)
Complete setup and test script that:
1. Checks Python installation
2. Creates/activates virtual environment
3. Installs dependencies
4. Sets up database
5. Runs quick smoke tests

**Usage:**
```bash
cd backend
bash setup_and_test.sh
```

### `quick_start.sh` (in backend/tests directory)
Fast smoke tests to verify backend is working:
- Python syntax check
- Import validation (database, learning engine, AI providers)
- API health check

**Usage:**
```bash
cd backend
bash tests/quick_start.sh
```

Or from tests directory:
```bash
cd backend/tests
bash quick_start.sh
```

## Important: PYTHONPATH

The scripts automatically set `PYTHONPATH` to fix import issues. If running Python commands manually, set it first:

```bash
export PYTHONPATH="$(dirname $(pwd)):$PYTHONPATH"
```

This allows imports like `from backend.database.models import User` to work correctly.

## Running Full Tests

If you have pytest tests, run them with:

```bash
cd backend
export PYTHONPATH="$(dirname $(pwd)):$PYTHONPATH"
pytest tests/ -v
```

## Troubleshooting

### ModuleNotFoundError: No module named 'backend'

Make sure PYTHONPATH is set correctly. The scripts do this automatically, but if running Python directly:

```bash
export PYTHONPATH="/path/to/ai-learning:$PYTHONPATH"
```

### Virtual environment not activated

Activate it:
```bash
source venv/bin/activate
```
