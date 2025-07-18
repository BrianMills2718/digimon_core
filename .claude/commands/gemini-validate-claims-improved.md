Set up and run a Gemini validation to verify my implementation claims. Follow these steps precisely:

1. **CLEAR CACHE FIRST**
   ```bash
   python gemini-review-tool/gemini_review.py --clear-cache
   ```

2. **CREATE FOCUSED CONFIG**
   Create a new validation config file `gemini-review-tool/validation-[timestamp].yaml` with:
   - **project_name**: Specific to what you're validating (e.g., "CLAUDE.md Issue X Validation")
   - **include_patterns**: ONLY the specific files containing the implementations being claimed
   - **custom_prompt**: Clear validation objective with specific criteria for each claim
   - **claims_of_success**: Map each claim to specific file locations and expected behavior

3. **VALIDATION CRITERIA**
   For each claim, verify:
   - **Implementation Present**: Does the method/feature exist in the specified file?
   - **Functionality Complete**: Is it fully implemented (not a stub/placeholder)?
   - **Requirements Met**: Does it satisfy the specific requirements mentioned?

4. **RUN VALIDATION**
   ```bash
   python gemini-review-tool/gemini_review.py --config gemini-review-tool/validation-[timestamp].yaml --no-cache
   ```

5. **REPORT RESULTS**
   Provide Gemini's verdict for each claim:
   - ✅ FULLY RESOLVED
   - ⚠️ PARTIALLY RESOLVED  
   - ❌ NOT RESOLVED

**CRITICAL**: Only include files directly related to the claims. Exclude Evidence.md, logs, and unrelated code to avoid confusion.

**SUCCESS INDICATORS**:
- Gemini references specific line numbers from your included files
- Analysis directly addresses each claim individually
- Verdict uses the exact claim names from your config
- File paths mentioned match your include patterns

**FAILURE INDICATORS**:
- Gemini analyzes different issues than claimed
- Generic analysis without specific file/line references
- Mentions files not in your include patterns
- Verdict doesn't address your specific claims