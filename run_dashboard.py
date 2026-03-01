"""Launcher for the Streamlit dashboard — ensures the project root is on sys.path."""

import sys
from pathlib import Path

# Add project root to path so `from app.xxx import ...` works
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Re-export the dashboard module so streamlit picks it up
from app.dashboard import *  # noqa: F401, F403, E402
