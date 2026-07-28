# Coding Rules

## Python Environment

Always use a project-local virtual environment. Before running any Python command (tests, scripts, CLI):

1. If `.venv/` does not exist in the project root, create it: `python3 -m venv .venv`
2. Activate it: `source .venv/bin/activate`
3. Install dependencies if needed: `pip install -r requirements.txt` (when the file exists)

Never use the system Python or a venv from a parent/sibling directory.
