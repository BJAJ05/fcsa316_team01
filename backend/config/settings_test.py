"""
Settings used by pytest (selected in pyproject.toml).

If backend/.env exists, its values are used, so tests run on your PostgreSQL.
On a machine without .env it falls back to SQLite and a throwaway secret key, so
`pip install -r requirements-dev.txt && pytest` works with no other setup.
Variables already set in the environment win over both: the GitHub Actions CI
(.github/workflows/ci.yml) sets DB_* so the tests run on its PostgreSQL service.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
# At least 32 bytes: the key also signs JWTs, and PyJWT warns about shorter HMAC keys.
os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-insecure-key-not-a-secret-0123456789")
os.environ.setdefault("DB_ENGINE", "sqlite")

# Django convention: test settings = all base settings, with the env defaults above.
# The import must come after os.environ is set, and it re-exports every setting.
# pylint: disable-next=wildcard-import,unused-wildcard-import,wrong-import-position
from config.settings import *  # noqa: E402, F401, F403
