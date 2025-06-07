"""
This file contains the function for building the database URL.
It is used to build the database URL from environment variables or defaults.
"""

import os

from dotenv import load_dotenv


def build_database_url():
    """
    Build a PostgreSQL database connection URL from environment variables or defaults.

    Returns:
        str: The database connection URL

    Environment variables used:
        DATABASE_URL: If set, this value is used directly
        DB_USER: Database username (default: "dbuser")
        DB_PASSWORD_FILE: Path to file containing database password (default: "/run/secrets/pg_password")
        DB_HOST: Database host (default: "postgres")
        DB_PORT: Database port (default: "5432")
        DB_NAME: Database name (default: "projectdb")

    Raises:
        RuntimeError: If the password file cannot be read
    """
    # First try to load variables from .env file
    load_dotenv()

    # Check if DATABASE_URL is already set
    db_url = os.environ.get("DATABASE_URL")

    # If no DATABASE_URL, build URL from components and password file
    if not db_url:
        user = os.environ.get("DB_USER", "dbuser")
        password_file = os.environ.get("DB_PASSWORD_FILE", "/run/secrets/pg_password")
        host = os.environ.get("DB_HOST", "postgres")
        port = os.environ.get("DB_PORT", "5432")
        dbname = os.environ.get("DB_NAME", "projectdb")

        try:
            with open(password_file) as f:
                password = f.read().strip()
        except Exception as e:
            raise RuntimeError(f"Failed to read DB password file: {e}")

        db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    return db_url
