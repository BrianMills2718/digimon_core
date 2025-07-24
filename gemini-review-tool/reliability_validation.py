#!/usr/bin/env python3
"""
Direct reliability validation script
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from gemini_review import GeminiCodeReviewer
import logging

logging.basicConfig(level=logging.INFO)

def main():
    """Run reliability validation"""
    
    # Check if repomix-output.xml exists
    if not os.path.exists('repomix-output.xml'):
        print("❌ repomix-output.xml not found")
        return
    
    print("🚀 Starting reliability validation...")
    
    # Read bundle
    with open('repomix-output.xml', 'r') as f:
        content = f.read()
    
    print(f"📊 Bundle size: {len(content) / 1024:.1f} KB")
    
    # Create custom prompt for reliability validation
    prompt = """## CORE RELIABILITY IMPLEMENTATION VALIDATION

Validate ONLY the core reliability implementation claims in the distributed transaction manager.

**FOCUS**: Verify automatic rollback compensation and real database integration.

### SPECIFIC CLAIMS TO VALIDATE:

**CLAIM 1: Automatic Rollback Compensation**
- REQUIREMENT: `_attempt_emergency_compensation()` method implements AUTOMATIC rollback of committed participants
- EVIDENCE NEEDED: 
  * Method calls `_execute_automatic_rollback()`
  * `_rollback_neo4j_operations()` and `_rollback_sqlite_operations()` methods exist
  * Creates new transactions to reverse committed operations
  * NOT just logging for manual intervention
- CHECK: Lines 682-815 in distributed_transaction_manager.py

**CLAIM 2: Comprehensive Rollback Data Generation**
- REQUIREMENT: `_generate_rollback_data()` method queries current state before modifications
- EVIDENCE NEEDED:
  * Calls `_query_current_neo4j_state()` and `_query_current_sqlite_state()`
  * Generates rollback data for updates and deletes (not just creates)
  * Returns complete rollback information including restore_data
- CHECK: Lines 524-571 in distributed_transaction_manager.py

**CLAIM 3: Real Database Manager Implementation**
- REQUIREMENT: Database managers use real connections not mocked interfaces
- EVIDENCE NEEDED:
  * `RealNeo4jManager` uses `AsyncGraphDatabase.driver()`
  * `RealSQLiteManager` uses `aiosqlite.connect()`
  * Connection pooling with real async database operations
  * Health monitoring with actual database queries
- CHECK: RealNeo4jManager and RealSQLiteManager classes in real_db_managers.py

### VALIDATION CRITERIA:

For each claim:
- ✅ **FULLY RESOLVED**: Implementation complete with real database operations
- ⚠️ **PARTIALLY RESOLVED**: Implementation present but incomplete or has limitations
- ❌ **NOT RESOLVED**: Implementation missing or uses simulation/mocking

Provide specific line numbers and code evidence for each verdict.

Claims being validated:
- Fixed distributed transaction manager 2-phase commit protocol with automatic rollback compensation
- Comprehensive rollback data generation for all operation types  
- Real database manager integration with actual Neo4j and SQLite connections"""
    
    # Initialize reviewer
    reviewer = GeminiCodeReviewer()
    
    print("🤖 Sending to Gemini for analysis...")
    
    try:
        # Run analysis
        analysis = reviewer.analyze_code(content, prompt)
        
        print("✅ Analysis complete")
        
        # Save results
        output_file = 'outputs/reliability_validation_results.md'
        os.makedirs('outputs', exist_ok=True)
        
        from datetime import datetime
        
        with open(output_file, 'w') as f:
            f.write(f"# Reliability Validation Results\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(analysis)
        
        print(f"💾 Results saved to: {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 RELIABILITY VALIDATION RESULTS")
        print("="*60)
        
        if "✅ FULLY RESOLVED" in analysis:
            resolved_count = analysis.count("✅ FULLY RESOLVED")
            print(f"✅ FULLY RESOLVED: {resolved_count} claims")
        
        if "⚠️ PARTIALLY RESOLVED" in analysis:
            partial_count = analysis.count("⚠️ PARTIALLY RESOLVED")
            print(f"⚠️ PARTIALLY RESOLVED: {partial_count} claims")
        
        if "❌ NOT RESOLVED" in analysis:
            failed_count = analysis.count("❌ NOT RESOLVED")
            print(f"❌ NOT RESOLVED: {failed_count} claims")
        
        print("="*60)
        print(f"📖 Full analysis: {output_file}")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        raise

if __name__ == "__main__":
    main()