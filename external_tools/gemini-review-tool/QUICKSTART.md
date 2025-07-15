# Quick Start Guide

## 1. One-Time Setup (5 minutes)

```bash
# Copy this folder to your tools directory
cp -r gemini-review-tool ~/tools/

# Go to the tool directory
cd ~/tools/gemini-review-tool

# Run installer
./install.sh

# Add your Gemini API key
nano .env
# Add: GEMINI_API_KEY=your-actual-api-key
```

## 2. Review Any Project (1 minute)

```bash
# Option 1: Review current directory
cd /path/to/your/project
python ~/tools/gemini-review-tool/gemini_review.py

# Option 2: Review from anywhere
python ~/tools/gemini-review-tool/gemini_review.py /path/to/project
```

## 3. Common Use Cases

### Quick Security Check
```bash
python ~/tools/gemini-review-tool/gemini_review.py --template security
```

### Evaluate Specific Claims
```bash
python ~/tools/gemini-review-tool/gemini_review.py \
  --claims "This code is production-ready with 100% test coverage"
```

### Include Documentation
```bash
python ~/tools/gemini-review-tool/gemini_review.py \
  --docs README.md --docs docs/API.md
```

### Create Project Config
```bash
cd /your/project
python ~/tools/gemini-review-tool/gemini_review.py --init
# Edit .gemini-review.yaml to customize
```

## 4. Tips

- Use `--format markdown` for large codebases
- Add ignore patterns to focus the review
- Keep documentation files included for context
- Use templates as starting points

## Need Help?

Run: `python ~/tools/gemini-review-tool/gemini_review.py --help`