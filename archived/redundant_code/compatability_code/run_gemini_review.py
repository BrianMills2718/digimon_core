#!/usr/bin/env python3
"""Run Gemini review with explicit .env loading."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from current directory
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Add the gemini review tool to path

# Now import and run
from gemini_review import main

if __name__ == "__main__":
    # Pass the config file argument
    sys.argv = ['gemini_review.py', '--config', '../external_tools/gemini-review-tool/verification-review.yaml']
    main()