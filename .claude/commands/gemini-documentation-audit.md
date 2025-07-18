Run `python gemini-review-tool/gemini_review.py` with `--docs` pointing to each file you pass as $ARGUMENTS (or, if none, every `*.md` inside `docs/`), using `--config gemini-review-tool/comprehensive-review.yaml`; then append any doc-vs-code mismatches to `CLAUDE.md` under `### Documentation Fixes Needed` and list them here. 

Make sure to only include the files relevant to this review.

Note: If `comprehensive-review.yaml` does not exist, create it in the `gemini-review-tool/` directory or use an appropriate config file. 