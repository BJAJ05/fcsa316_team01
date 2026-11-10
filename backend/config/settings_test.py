"""
Settings used by pytest (selected in pyproject.toml).

If backend/.env exists, its values are used, so tests run on your PostgreSQL.
On a machine without .env (for example a fresh CI runner) it falls back to SQLite
and a throwaway secret key, so `pip install -r requirements-dev.txt && pytest`
works with no other setup.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-insecure-key")
os.environ.setdefault("DB_ENGINE", "sqlite")

from config.settings import *  # noqa: E402, F401, F403
