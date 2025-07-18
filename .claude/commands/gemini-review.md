Given a free-form description in $ARGUMENTS (e.g. "security audit", "verify these claims…", "focus on performance"), decide which `gemini_review.py` flags to use, build the command, run it, and summarise the result here.

Quick reference of useful flags you may combine:
• `--template <name>`        # one of security | performance | refactoring | enterprise
• `--claims "<text>"`        # multi-line success claims to verify
• `--docs <file>`            # repeat to add docs; omit for code-only
• `--prompt "<text>"`        # custom focus instructions
• `--config <file.yaml>`     # YAML config (default: gemini-review-tool/comprehensive-review.yaml)
• `--format markdown`        # use smaller markdown bundle if token limits hit

Steps:
1. Parse $ARGUMENTS and map to the flags above.
2. Run `python gemini-review-tool/gemini_review.py` with the chosen flags.
3. Return Gemini's findings.
4. If no `--config` is supplied, it falls back to `gemini-review-tool/comprehensive-review.yaml`, which runs a full-repo audit (ignores venv/build artifacts), injects core docs, includes current claims_of_success, and asks Gemini for a structured Critical/Major issue report.

Make sure to only include the files relevant to this review.
