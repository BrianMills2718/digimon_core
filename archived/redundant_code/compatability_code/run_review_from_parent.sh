#!/bin/bash
# Run Gemini review from parent directory

echo "Running Gemini review from parent directory..."
cd ..
python external_tools/gemini-review-tool/gemini_review.py --config main-project-verification-review.yaml