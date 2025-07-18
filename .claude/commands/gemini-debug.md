Given a free-form bug description in $ARGUMENTS (e.g. "fix crash on startup", "resolve memory leak in pipeline", "debug why output is empty"), decide which `gemini_review.py` flags to use to focus the review on this bug, build the command, run it, and summarise the result here.

Quick reference of useful flags you may combine:
• `--prompt "<text>"`        # custom focus instructions (use the bug description)
• `--template debug`          # if you have a debug-focused template/config
• `--config <file.yaml>`      # YAML config (default: gemini-review-tool/focused-debug-review.yaml if available)
• `--include <pattern>`       # restrict to relevant files if possible
• `--format markdown`         # use smaller markdown bundle if token limits hit

Steps:
1. Parse $ARGUMENTS and map to the flags above (use --prompt to pass the bug description).
2. Run `python gemini-review-tool/gemini_review.py` with the chosen flags.
3. Return Gemini's findings and any suggested fixes.
4. If no `--config` is supplied, it falls back to `gemini-review-tool/focused-debug-review.yaml` if available, or a default config.

Before building the command, ensure `GEMINI_MODEL` is set to `gemini-1.5-flash` (export it if needed) so the review runs with the lighter, faster model. 