"""Vercel build: collect static files, then migrate when a database URL is set."""

import os
import subprocess
import sys


def main():
    subprocess.check_call([sys.executable, "manage.py", "collectstatic", "--noinput"])
    if os.getenv("DATABASE_URL", "").strip():
        subprocess.check_call([sys.executable, "manage.py", "migrate", "--noinput"])
    else:
        print("DATABASE_URL is not set; skipping migrate.")


if __name__ == "__main__":
    main()
