Obvious Changes Needed & Solutions

1. Inconsistent Overall System Status Reporting

    Problem: PROJECT_STATUS.md states "✅ FULLY FUNCTIONAL" at the top, but immediately contradicts this with "⚠️ PARTIALLY FUNCTIONAL" for Phase 2 and "⚠️ NOT INTEGRATED" for Phase 3. README.md and CLAUDE.md align more with the detailed partial functionality.
    Obvious Change: The high-level "Overall System Status" in PROJECT_STATUS.md is misleading and inconsistent with the detailed breakdown and other core documentation.
    Solution:
        Edit PROJECT_STATUS.md: Change the "Overall System Status" at the beginning of the document from "✅ FULLY FUNCTIONAL" to "⚠️ PARTIALLY FUNCTIONAL" or "⚠️ INTEGRATION IN PROGRESS" to accurately reflect the state of Phase 2 and Phase 3 integration. Ensure consistency with the more detailed phase-by-phase status descriptions within the same document and with README.md and CLAUDE.md.
        Action: Locate PROJECT_STATUS.md and modify the first line for "Overall System Status."

2. Ambiguity and Redundancy in Tool Counting

    Problem: While TOOL_COUNT_CLARIFICATION.md attempts to standardize tool counts, the presence of "571 capabilities" in CAPABILITY_AUDIT_FINAL_RESULTS.md and "29 MCP tools" in CAPABILITY_REGISTRY.md alongside "13 core tools" and "33 total available tools" (13 core + 20 MCP) can be confusing.
    Obvious Change: Consolidate and clarify the "tool" terminology and counting methodology across all relevant documents to avoid ambiguity.
    Solution:
        Consolidate TOOL_COUNT_CLARIFICATION.md into docs/current/SPECIFICATIONS.md: Merge the detailed explanation from TOOL_COUNT_CLARIFICATION.md into a dedicated "Tooling" or "Capabilities Overview" section within docs/core/SPECIFICATIONS.md.
        Standardize Terminology: Clearly define "Tool," "Capability," and "MCP Tool" in docs/core/SPECIFICATIONS.md. Always use these defined terms consistently throughout the documentation.
        Update README.md and PROJECT_STATUS.md: Refer to the definitive section in docs/core/SPECIFICATIONS.md for detailed tool counts, ensuring they only state the most relevant, high-level numbers (e.g., "13 Core GraphRAG Tools; 33 total tools including MCP server tools. For a full breakdown of capabilities and tools, see the Specifications document.").
        Action: Review TOOL_COUNT_CLARIFICATION.md, docs/core/SPECIFICATIONS.md, CAPABILITY_AUDIT_FINAL_RESULTS.md, and CAPABILITY_REGISTRY.md for consistent language and consolidate. Update README.md and PROJECT_STATUS.md to reference the single source of truth.

3. Unresolved "pdf_path vs document_paths" API Inconsistency

    Problem: docs/current/API_STANDARDIZATION_FRAMEWORK.md explicitly notes that "pdf_path vs document_paths signature variations remain" despite the current_step fix. This indicates an active API inconsistency.
    Obvious Change: This is a documented technical debt that needs to be addressed in the codebase and then updated in the documentation.
    Solution:
        Code Refactoring: Identify all instances where pdf_path and document_paths are used inconsistently across src/ files (e.g., src/core/workflow_state_service.py, src/core/phase_adapters.py, src/tools/phase1/t01_pdf_loader.py, src/tools/phase3/t301_multi_document_fusion.py). Standardize on a single, clear parameter name (e.g., document_paths) that can handle both single and multiple document inputs (e.g., a list of paths).
        Update API Contracts: Modify src/core/api_contracts.py to reflect the standardized parameter name and type.
        Update Documentation: After code changes, update docs/current/API_STANDARDIZATION_FRAMEWORK.md and PROJECT_STATUS.md to reflect that this inconsistency is "✅ FIXED."
        Action: Search the codebase for pdf_path and document_paths usage, choose one standard, refactor, and then update related documentation.

4. Contradictory Integration Test Status

    Problem: PROJECT_STATUS.md claims "✅ INTEGRATION WORKING - P1→P2→P3 pipeline fully functional," while docs/current/INTEGRATION_TESTING_GAP_ANALYSIS.md calls it a "⚠️ CRITICAL GAP" due to missing and partial tests.
    Obvious Change: The "INTEGRATION WORKING" claim in PROJECT_STATUS.md is directly contradicted by the detailed analysis in INTEGRATION_TESTING_GAP_ANALYSIS.md. This requires either more robust testing or a more honest status update.
    Solution:
        Prioritize Integration Testing: Address the "MISSING Phase Transition Tests" and "PARTIAL Service Integration Tests" detailed in docs/current/INTEGRATION_TESTING_GAP_ANALYSIS.md.
        Update PROJECT_STATUS.md: Until truly comprehensive integration tests pass reliably for the full P1→P2→P3 pipeline, the "Functional Integration Tests" status in PROJECT_STATUS.md should be downgraded to "⚠️ PARTIALLY WORKING" or similar, with a direct reference to INTEGRATION_TESTING_GAP_ANALYSIS.md for details.
        Action: Review and improve the integration tests (tests/integration/test_full_pipeline_integration.py, etc.) and then update PROJECT_STATUS.md to reflect the actual integration status and testing coverage.

By addressing these points, the repository's documentation will become significantly more consistent, accurate, and trustworthy, reflecting the true state of the project.