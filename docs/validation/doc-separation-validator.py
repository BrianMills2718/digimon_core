#!/usr/bin/env python3
"""
Documentation Separation Validator

This script validates that documentation follows the proper separation principles:
- Architecture docs contain NO implementation status
- Planning docs contain current status and implementation details
- All docs reference the roadmap for current status
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class DocSeparationValidator:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.violations = []
        
    def validate_all(self) -> Dict[str, List[str]]:
        """Run all validation checks"""
        results = {
            "architecture_violations": [],
            "planning_violations": [],
            "reference_violations": [],
            "template_violations": []
        }
        
        # Check architecture documents
        for arch_file in self.docs_root.rglob("architecture/*.md"):
            violations = self.validate_architecture_doc(arch_file)
            results["architecture_violations"].extend(violations)
            
        # Check planning documents
        for plan_file in self.docs_root.rglob("planning/*.md"):
            violations = self.validate_planning_doc(plan_file)
            results["planning_violations"].extend(violations)
            
        # Check for roadmap references
        for doc_file in self.docs_root.rglob("*.md"):
            violations = self.validate_roadmap_reference(doc_file)
            results["reference_violations"].extend(violations)
            
        # Check template usage
        for doc_file in self.docs_root.rglob("*.md"):
            violations = self.validate_template_usage(doc_file)
            results["template_violations"].extend(violations)
            
        return results
    
    def validate_architecture_doc(self, file_path: Path) -> List[str]:
        """Check that architecture docs don't contain implementation status"""
        violations = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for implementation status indicators
        status_patterns = [
            r"Status:\s*(Implemented|Complete|In Progress|Pending|Not Started)",
            r"Current Implementation:",
            r"Integration Gap:",
            r"Next Step:",
            r"Progress:",
            r"Completion:",
            r"Currently:",
            r"Currently implemented",
            r"Not yet implemented",
            r"Implementation status"
        ]
        
        for pattern in status_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Contains implementation status: {pattern}")
                
        # Check for file paths (often indicate current implementation)
        file_path_patterns = [
            r"`/src/",
            r"`src/",
            r"Location:",
            r"File:",
            r"Path:"
        ]
        
        for pattern in file_path_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Contains file paths (implementation detail): {pattern}")
                
        return violations
    
    def validate_planning_doc(self, file_path: Path) -> List[str]:
        """Check that planning docs contain proper status information"""
        violations = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Planning docs should contain status information
        required_patterns = [
            r"Status:",
            r"Current",
            r"Progress",
            r"Implementation"
        ]
        
        has_status = any(re.search(pattern, content, re.IGNORECASE) 
                        for pattern in required_patterns)
        
        if not has_status and "roadmap" not in file_path.name.lower():
            violations.append("Planning document should contain status information")
            
        return violations
    
    def validate_roadmap_reference(self, file_path: Path) -> List[str]:
        """Check that documents reference the roadmap for current status"""
        violations = []
        
        # Skip the roadmap itself and templates
        if "roadmap" in file_path.name.lower() or "template" in file_path.name.lower():
            return violations
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for roadmap references
        roadmap_patterns = [
            r"roadmap\.md",
            r"planning/roadmap",
            r"current status",
            r"project status"
        ]
        
        has_roadmap_ref = any(re.search(pattern, content, re.IGNORECASE) 
                             for pattern in roadmap_patterns)
        
        if not has_roadmap_ref and "claude" not in file_path.name.lower():
            violations.append("Document should reference roadmap for current status")
            
        return violations
    
    def validate_template_usage(self, file_path: Path) -> List[str]:
        """Check that documents follow template structure"""
        violations = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for document type header
        if not re.search(r"Document Type:", content):
            violations.append("Missing document type header")
            
        # Check for purpose statement
        if not re.search(r"Purpose:", content):
            violations.append("Missing purpose statement")
            
        return violations
    
    def generate_report(self, results: Dict[str, List[str]]) -> str:
        """Generate a validation report"""
        report = "# Documentation Separation Validation Report\n\n"
        
        total_violations = sum(len(violations) for violations in results.values())
        
        if total_violations == 0:
            report += "✅ **All validation checks passed!**\n\n"
            report += "Documentation follows proper separation principles.\n"
        else:
            report += f"⚠️ **Found {total_violations} violations**\n\n"
            
            for category, violations in results.items():
                if violations:
                    report += f"## {category.replace('_', ' ').title()}\n"
                    for violation in violations:
                        report += f"- {violation}\n"
                    report += "\n"
                    
        return report

def main():
    """Run the validation and generate report"""
    validator = DocSeparationValidator()
    results = validator.validate_all()
    report = validator.generate_report(results)
    
    # Write report
    report_path = Path("docs/validation/validation-report.md")
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(report)
    
    # Exit with error code if violations found
    total_violations = sum(len(violations) for violations in results.values())
    if total_violations > 0:
        exit(1)

if __name__ == "__main__":
    main() 