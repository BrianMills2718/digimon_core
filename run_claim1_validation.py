#!/usr/bin/env python3
"""Run Claim 1 validation with focused repomix"""

import subprocess
import shutil
import os
import time

# Wait a bit for rate limit to reset
print("Waiting 35 seconds for rate limit reset...")
time.sleep(35)

# Copy our focused repomix to the gemini-review-tool
print("\nCopying focused repomix (16KB) to gemini-review-tool...")
shutil.copy("claim1-repomix.xml", "gemini-review-tool/repomix-output.xml")

# Run gemini validation without regenerating repomix
print("\nRunning Gemini validation on focused repomix...")
cmd = [
    "python", "gemini_review.py", 
    ".",  # Current directory (will be ignored since we have repomix-output.xml)
    "--config", "validation-claim1-simple.yaml",
    "--no-cache",
    "--keep-repomix"  # Don't regenerate repomix, use existing
]

# Change to gemini-review-tool directory
os.chdir("gemini-review-tool")

# Run the command
result = subprocess.run(cmd, capture_output=True, text=True)

print("\nSTDOUT:")
print(result.stdout)

if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)

print(f"\nReturn code: {result.returncode}")

# Check if review was created
review_dirs = [d for d in os.listdir("outputs") if d.startswith("2025")]
if review_dirs:
    latest_dir = max(review_dirs)
    review_file = f"outputs/{latest_dir}/reviews/gemini-review.md"
    if os.path.exists(review_file):
        print(f"\n✅ Review created: {review_file}")
        print("\nReview content:")
        with open(review_file, 'r') as f:
            print(f.read())