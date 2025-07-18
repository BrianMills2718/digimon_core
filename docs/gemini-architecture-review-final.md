02:06:00 |     INFO | gemini_review | Initializing Gemini Code Reviewer
02:06:00 |     INFO | gemini_review | Using API key from environment variable
02:06:00 |     INFO | gemini_review | API key obtained successfully
02:06:00 |     INFO | gemini_review | Using model: gemini-2.5-flash
🤖 Using model: gemini-2.5-flash
🔄 Fallback model: gemini-2.5-flash
02:06:00 |     INFO | gemini_review | Rate limiter initialized
02:06:00 |     INFO | gemini_review | Cache disabled
🚫 Cache disabled

🚀 Starting Gemini Code Review for: /home/brian/Digimons/docs/architecture

📦 Running repomix on /home/brian/Digimons/docs/architecture...
🧹 Removing empty lines
🗜️  Compressing code
🔢 Using token encoding: gemini-pro
✅ Repomix completed successfully
📖 Reading repomix output from repomix-output.xml...
📊 File size: 0.75 MB
🤖 Sending to Gemini for analysis...
✅ Analysis complete

❌ Error during review: name 'config' is not defined
🧹 Cleaned up temporary files

❌ Unexpected fatal error: name 'config' is not defined
02:07:01 |    ERROR | gemini_review | Unexpected fatal error occurred
Traceback (most recent call last):
  File "/home/brian/Digimons/gemini-review-tool/gemini_review.py", line 1259, in main
    reviewer.review(
  File "/home/brian/Digimons/gemini-review-tool/gemini_review.py", line 928, in review
    output_file = config.output_file if config else "gemini-review.md"
NameError: name 'config' is not defined
