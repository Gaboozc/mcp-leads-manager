"""Settings shared by the Flask API and the MCP server.

Both processes must point to the same database and use the same timezone,
otherwise "today" and the data they see would drift apart.
"""

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'leads.db'}")
APP_TZ = os.environ.get("APP_TZ", "America/New_York")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me-in-production-32b")
JWT_HOURS = int(os.environ.get("JWT_HOURS", "8"))

TEST_USER_EMAIL = "operator@school.test"
TEST_USER_PASSWORD = "demo1234"
TEST_USER_NAME = "Operator"

# Which user is recorded as the author of attempts logged from the MCP server
# (stdio has no login, so the operator is configured by environment).
OPERATOR_EMAIL = os.environ.get("OPERATOR_EMAIL", TEST_USER_EMAIL)
