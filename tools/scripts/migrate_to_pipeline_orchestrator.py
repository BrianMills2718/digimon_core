#!/usr/bin/env python3
"""Migrate all files from old workflow classes to PipelineOrchestrator"""

import os
import re
from pathlib import Path

def migrate_file(file_path):
    """Migrate a single file to use PipelineOrchestrator"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace old imports
        content = re.sub(
            r'from\s+src\.tools\.phase1\.vertical_slice_workflow\s+import\s+VerticalSliceWorkflow',
            'from src.core.pipeline_orchestrator import PipelineOrchestrator',
            content
        )
        
        content = re.sub(
            r'from\s+src\.tools\.phase2\.enhanced_vertical_slice_workflow\s+import\s+EnhancedVerticalSliceWorkflow',
            'from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel',
            content
        )
        
        content = re.sub(
            r'from\s+src\.tools\.phase3\.basic_multi_document_workflow\s+import\s+BasicMultiDocumentWorkflow',
            '# Phase 3 now uses PipelineOrchestrator with Phase.PHASE3',
            content
        )
        
        # Replace instantiation patterns
        content = re.sub(
            r'(\w+)\s*=\s*VerticalSliceWorkflow\(\)',
            r'\1_config = create_unified_workflow_config(phase=Phase.PHASE1, optimization_level=OptimizationLevel.STANDARD)\n\1 = PipelineOrchestrator(\1_config)',
            content
        )
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Migrated: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error migrating {file_path}: {e}")
        return False

def main():
    """Migrate all files using old workflow classes"""
    migrated_count = 0
    
    # Find files with old workflow imports
    for py_file in Path('.').rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if any(old_class in content for old_class in [
                    'VerticalSliceWorkflow', 
                    'EnhancedVerticalSliceWorkflow', 
                    'BasicMultiDocumentWorkflow'
                ]):
                    if migrate_file(py_file):
                        migrated_count += 1
        except Exception as e:
            print(f"Error checking {py_file}: {e}")
    
    print(f"\nMigrated {migrated_count} files")
    
    # Verify migration
    remaining_files = []
    for py_file in Path('.').rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if any(old_class in content for old_class in [
                    'VerticalSliceWorkflow', 
                    'EnhancedVerticalSliceWorkflow', 
                    'BasicMultiDocumentWorkflow'
                ]):
                    remaining_files.append(str(py_file))
        except:
            continue
    
    if remaining_files:
        print(f"\nWARNING: {len(remaining_files)} files still use old workflow classes:")
        for f in remaining_files[:10]:
            print(f"  {f}")
    else:
        print("\n✅ ALL files migrated to PipelineOrchestrator")

if __name__ == "__main__":
    main()