#!/usr/bin/env python3
"""
Generate Comprehensive Documentation for External Review
Concatenates all relevant documentation in logical order
"""

import os
from pathlib import Path
from datetime import datetime

def read_file_safe(filepath):
    """Safely read a file, return empty string if not found"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"[FILE NOT FOUND: {filepath}]"
    except Exception as e:
        return f"[ERROR READING {filepath}: {e}]"

def generate_comprehensive_documentation():
    """Generate single comprehensive document for external review"""
    
    base_dir = Path("/home/brian/projects/Digimons/uncertainty_stress_test")
    
    # Document structure in logical presentation order
    document_sections = [
        {
            "title": "EXECUTIVE SUMMARY",
            "files": [
                ("IMPLEMENTATION_REPORT.md", "Project Overview and Implementation Status")
            ]
        },
        {
            "title": "VALIDATION RESULTS", 
            "files": [
                ("VALIDATION_STATUS_REPORT.md", "Comprehensive Validation Analysis")
            ]
        },
        {
            "title": "MATHEMATICAL FOUNDATIONS",
            "files": [
                ("docs/UNCERTAINTY_IMPLEMENTATION_SPECIFICATION.md", "Complete Mathematical Specifications"),
                ("docs/METHODOLOGICAL_JUSTIFICATIONS.md", "Justification for All Mathematical Choices")
            ]
        },
        {
            "title": "CORE IMPLEMENTATION",
            "files": [
                ("core_services/uncertainty_engine.py", "Main Uncertainty Processing Engine"),
                ("core_services/bayesian_aggregation_service.py", "Bayesian Evidence Aggregation Service"),
                ("core_services/cerqual_assessor.py", "CERQual Assessment Framework")
            ]
        },
        {
            "title": "VALIDATION FRAMEWORK",
            "files": [
                ("validation/ground_truth_validator.py", "Ground Truth Validation System"),
                ("validation/bias_analyzer.py", "Comprehensive Bias Analysis Framework"),
                ("validation/comprehensive_uncertainty_test.py", "Full Integration Test Suite")
            ]
        },
        {
            "title": "TEST RESULTS AND VALIDATION DATA",
            "files": [
                ("validation/basic_test_results.json", "Basic Functionality Test Results"),
                ("validation/ground_truth_validation_results.json", "Ground Truth Test Results"),
                ("validation/bias_analysis_results.json", "Bias Analysis Results")
            ]
        }
    ]
    
    # Generate comprehensive document
    comprehensive_doc = f"""# KGAS Uncertainty Framework - Comprehensive Documentation for External Review

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Version**: 1.0  
**Status**: Ready for External Evaluation  

---

## 📋 TABLE OF CONTENTS

"""
    
    # Generate table of contents
    for i, section in enumerate(document_sections, 1):
        comprehensive_doc += f"{i}. **{section['title']}**\n"
        for j, (filename, description) in enumerate(section['files'], 1):
            comprehensive_doc += f"   {i}.{j} {description}\n"
        comprehensive_doc += "\n"
    
    comprehensive_doc += "---\n\n"
    
    # Add each section
    for section_num, section in enumerate(document_sections, 1):
        comprehensive_doc += f"# {section_num}. {section['title']}\n\n"
        
        for file_num, (filename, description) in enumerate(section['files'], 1):
            filepath = base_dir / filename
            
            comprehensive_doc += f"## {section_num}.{file_num} {description}\n\n"
            comprehensive_doc += f"**Source File**: `{filename}`\n\n"
            
            # Read and include file content
            file_content = read_file_safe(filepath)
            
            # Add appropriate code blocks based on file type
            if filename.endswith('.py'):
                comprehensive_doc += f"```python\n{file_content}\n```\n\n"
            elif filename.endswith('.md'):
                comprehensive_doc += f"{file_content}\n\n"
            elif filename.endswith('.json'):
                comprehensive_doc += f"```json\n{file_content}\n```\n\n"
            else:
                comprehensive_doc += f"```\n{file_content}\n```\n\n"
            
            comprehensive_doc += "---\n\n"
    
    # Add appendices
    comprehensive_doc += f"""# APPENDICES

## A. DIRECTORY STRUCTURE

```
{base_dir.name}/
├── core_services/           # Main uncertainty processing services
│   ├── uncertainty_engine.py
│   ├── bayesian_aggregation_service.py
│   └── cerqual_assessor.py
├── docs/                    # Technical documentation
│   ├── UNCERTAINTY_IMPLEMENTATION_SPECIFICATION.md
│   └── METHODOLOGICAL_JUSTIFICATIONS.md
├── validation/              # Validation and testing framework
│   ├── ground_truth_validator.py
│   ├── bias_analyzer.py
│   ├── comprehensive_uncertainty_test.py
│   └── [test results].json
├── IMPLEMENTATION_REPORT.md
├── VALIDATION_STATUS_REPORT.md
└── run_basic_test.py
```

## B. QUICK START GUIDE

### Prerequisites
```bash
pip install numpy aiohttp python-dateutil
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage
```python
from core_services.uncertainty_engine import UncertaintyEngine

engine = UncertaintyEngine()
confidence = await engine.assess_initial_confidence(
    text="Your research text here",
    claim="The claim to assess", 
    domain="research_domain"
)
print(f"Confidence: {{confidence.get_overall_confidence():.3f}}")
```

### Run Validation Tests
```bash
# Basic functionality test
python run_basic_test.py

# Ground truth validation
python validation/ground_truth_validator.py

# Bias analysis
python validation/bias_analyzer.py

# Full integration test
python validation/comprehensive_uncertainty_test.py
```

## C. EXTERNAL EVALUATION CHECKLIST

### For Technical Reviewers:
- [ ] Mathematical framework soundness (Section 3)
- [ ] Implementation quality and error handling (Section 4)
- [ ] Validation methodology and results (Section 2, 5)
- [ ] Bias analysis and mitigation (Section 2, 5)
- [ ] Reproducibility and determinism (Section 4)

### For Domain Experts:
- [ ] CERQual framework implementation (Section 3.2, 4.3)
- [ ] Bayesian methodology correctness (Section 3.1, 4.2)
- [ ] Academic applicability and usefulness (Section 1, 2)
- [ ] Comparison with existing methods (Section 3.2)
- [ ] Practical deployment considerations (Section 1)

### For Methodology Experts:
- [ ] Ground truth validation approach (Section 5.1)
- [ ] Statistical significance of results (Section 6)
- [ ] Calibration and accuracy assessment (Section 2, 6)
- [ ] Bias detection methodology (Section 5.2)
- [ ] Error propagation analysis (Section 3.2)

## D. KNOWN LIMITATIONS AND FUTURE WORK

### Current Limitations:
1. **Validation Scale**: Tested on 6 ground truth cases (pilot scale)
2. **Expert Validation**: No formal expert comparison study conducted
3. **Domain Coverage**: Primarily tested on academic research texts
4. **API Dependency**: Requires external LLM API for operation
5. **Computational Cost**: ~$0.10-0.50 per comprehensive analysis

### Recommended Future Work:
1. **Expanded Validation**: 100+ ground truth cases across domains
2. **Expert Comparison Study**: Systematic comparison with domain experts
3. **Calibration Study**: Longitudinal study of prediction accuracy
4. **Domain Specialization**: Field-specific confidence models
5. **Offline Operation**: Local model integration for independence

### Technical Debt:
1. **Error Handling**: Could be more comprehensive for edge cases
2. **Caching**: Basic implementation, could be optimized
3. **Monitoring**: Production monitoring system not implemented
4. **Documentation**: API documentation could be more comprehensive

## E. CONTACT AND SUPPORT

**Development Team**: KGAS Development Team  
**Documentation Version**: 1.0  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}  
**Repository**: /home/brian/projects/Digimons/uncertainty_stress_test  

For questions about this documentation or the uncertainty framework:
1. Review the implementation code (Section 4)
2. Check validation results (Section 6) 
3. Examine mathematical specifications (Section 3)
4. Run test suite for verification

---

**End of Comprehensive Documentation**  
**Total Sections**: {len(document_sections)}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return comprehensive_doc

def main():
    """Generate and save comprehensive documentation"""
    
    print("📄 Generating Comprehensive Documentation for External Review")
    print("=" * 70)
    
    # Generate documentation
    print("🔄 Reading and concatenating documentation files...")
    comprehensive_doc = generate_comprehensive_documentation()
    
    # Save to file
    output_path = Path("/home/brian/projects/Digimons/uncertainty_stress_test/COMPREHENSIVE_EXTERNAL_REVIEW_DOCUMENTATION.md")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(comprehensive_doc)
    
    # Calculate statistics
    line_count = comprehensive_doc.count('\n')
    word_count = len(comprehensive_doc.split())
    char_count = len(comprehensive_doc)
    
    print("✅ Documentation generation complete!")
    print(f"📊 Statistics:")
    print(f"   - Lines: {line_count:,}")
    print(f"   - Words: {word_count:,}")
    print(f"   - Characters: {char_count:,}")
    print(f"   - File size: {char_count/1024:.1f} KB")
    
    print(f"\n📁 Output saved to:")
    print(f"   {output_path}")
    
    print(f"\n🎯 Ready for External Review!")
    print("This comprehensive document contains:")
    print("   ✅ Complete mathematical specifications")
    print("   ✅ Full implementation code") 
    print("   ✅ Validation results and analysis")
    print("   ✅ Bias analysis framework")
    print("   ✅ Test results and performance data")
    print("   ✅ Methodological justifications")
    
    # Generate summary for reviewer
    print(f"\n📋 For the External Reviewer:")
    print("   1. Start with Section 1 (Executive Summary)")
    print("   2. Review Section 2 (Validation Results)")
    print("   3. Examine Section 3 (Mathematical Foundations)")
    print("   4. Evaluate Section 4 (Implementation Quality)")
    print("   5. Assess Section 5 (Validation Framework)")
    print("   6. Check Section 6 (Test Results)")
    print("   7. Use Appendix C (Evaluation Checklist)")
    
    return output_path

if __name__ == "__main__":
    output_file = main()
    print(f"\n🚀 Documentation ready: {output_file}")