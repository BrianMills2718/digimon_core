📋 Using config file: /home/brian/Digimons/gemini-review.yaml
01:35:58 |     INFO | gemini_review | Initializing Gemini Code Reviewer
01:35:58 |     INFO | gemini_review | Using API key from environment variable
01:35:58 |     INFO | gemini_review | API key obtained successfully
01:35:58 |     INFO | gemini_review | Using model: gemini-2.5-flash
🤖 Using model: gemini-2.5-flash
🔄 Fallback model: gemini-2.5-flash
01:35:58 |     INFO | gemini_review | Rate limiter initialized
01:35:58 |     INFO | gemini_review | Cache disabled
🚫 Cache disabled

🚀 Starting Gemini Code Review for: /home/brian/Digimons/docs/architecture

📦 Running repomix on /home/brian/Digimons/docs/architecture...
🧹 Removing empty lines
🗜️  Compressing code
🔢 Using token encoding: gemini-pro
🚫 Ignoring patterns: *.pyc,__pycache__,.git,.venv,venv,node_modules,*.log,.pytest_cache,*.egg-info,build,dist,gemini-review*.md,repomix-output.*
✅ Repomix completed successfully
📖 Reading repomix output from repomix-output.xml...
📊 File size: 0.75 MB
🤖 Sending to Gemini for analysis...
01:37:01 |  WARNING | gemini_review.rate_limiter | Server error detected, reducing rate to 0.70
01:37:01 |    ERROR | gemini_review | Gemini API error with gemini-2.5-flash: 500 An internal error has occurred. Please retry or report in https://developers.generativeai.google/guide/troubleshooting
❌ Gemini API error with gemini-2.5-flash: 500 An internal error has occurred. Please retry or report in https://developers.generativeai.google/guide/troubleshooting
🔄 Retrying with fallback model: gemini-2.5-flash
✅ Analysis complete with fallback model: gemini-2.5-flash
💾 Saving results to gemini-review.md...
✅ Results saved to gemini-review.md
🧹 Cleaned up temporary files

✨ Code review complete!
