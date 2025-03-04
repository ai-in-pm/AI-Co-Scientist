#!/usr/bin/env python
# Script to run the Streamlit UI for AI Co-Scientist

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Run the Streamlit app directly
import streamlit.web.cli as stcli
import click

if __name__ == "__main__":
    print("Starting AI Co-Scientist UI...")
    # Run the Streamlit app
    sys.argv = ["streamlit", "run", str(project_root / "src" / "ui" / "streamlit_app.py")]
    sys.exit(stcli.main())
