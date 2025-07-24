#!/usr/bin/env python3
"""
Rapid analysis of Paul Davis notes to extract key insights quickly
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import re
from collections import Counter

class RapidDavisAnalyzer:
    """
    Quick analysis of Paul Davis papers to understand key themes and methods
    """
    
    def __init__(self):
        self.notes_dir = Path("/home/brian/projects/Digimons/paul_davis_notes")
        self.results = {}
    
    def extract_file_overview(self, file_path: Path) -> Dict:
        """Quick overview of a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            return {"error": str(e)}
        
        # Basic stats
        word_count = len(text.split())
        char_count = len(text)
        line_count = text.count('\n')
        
        # Extract key terms related to methodology
        methodology_terms = [
            'bayesian', 'uncertainty', 'probability', 'confidence', 'validation',
            'model', 'simulation', 'assessment', 'evaluation', 'framework',
            'methodology', 'approach', 'technique', 'algorithm', 'analysis',
            'evidence', 'reasoning', 'inference', 'prediction', 'forecast'
        ]
        
        # Count methodology term occurrences
        text_lower = text.lower()
        term_counts = {term: text_lower.count(term) for term in methodology_terms}
        significant_terms = {k: v for k, v in term_counts.items() if v > 5}
        
        # Extract section headers (rough heuristic)
        headers = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if (len(line) > 10 and len(line) < 100 and 
                (line.isupper() or 
                 re.match(r'^[A-Z].*[A-Z].*', line) or
                 re.match(r'^\d+\.?\s+[A-Z]', line))):
                headers.append(line[:80])
        
        # Extract first few paragraphs for context
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
        sample_content = paragraphs[:3] if paragraphs else ["No substantial paragraphs found"]
        
        # Look for explicit methodology sections
        methodology_sections = []
        text_sections = text.split('\n\n')
        for i, section in enumerate(text_sections):
            if any(term in section.lower() for term in ['method', 'approach', 'framework', 'technique']):
                if len(section) > 200:  # Substantial section
                    methodology_sections.append({
                        "section_number": i,
                        "preview": section[:300] + "..." if len(section) > 300 else section,
                        "relevance_score": sum(term_counts[term] for term in methodology_terms if term in section.lower())
                    })
        
        return {
            "filename": file_path.name,
            "size_kb": char_count / 1024,
            "word_count": word_count,
            "line_count": line_count,
            "significant_methodology_terms": significant_terms,
            "estimated_sections": len(headers),
            "sample_headers": headers[:10],
            "sample_content": sample_content,
            "methodology_sections": sorted(methodology_sections, key=lambda x: x["relevance_score"], reverse=True)[:5],
            "file_type_assessment": self._assess_file_type(text, significant_terms)
        }
    
    def _assess_file_type(self, text: str, term_counts: Dict) -> str:
        """Assess what type of document this appears to be"""
        
        # Check for academic paper indicators
        academic_indicators = ['abstract', 'introduction', 'methodology', 'conclusion', 'references', 'bibliography']
        academic_score = sum(1 for indicator in academic_indicators if indicator in text.lower())
        
        # Check for technical/implementation indicators  
        tech_indicators = ['algorithm', 'implementation', 'code', 'system', 'software', 'framework']
        tech_score = sum(term_counts.get(indicator, 0) for indicator in tech_indicators)
        
        # Check for research/theoretical indicators
        theory_indicators = ['theory', 'hypothesis', 'framework', 'model', 'concept']
        theory_score = sum(term_counts.get(indicator, 0) for indicator in theory_indicators)
        
        if academic_score >= 3:
            return "Academic Paper"
        elif tech_score > 20:
            return "Technical Implementation Guide"
        elif theory_score > 15:
            return "Theoretical Framework"
        elif 'simulation' in text.lower() and term_counts.get('model', 0) > 10:
            return "Simulation/Modeling Document"
        else:
            return "General Research Document"
    
    def analyze_collection(self) -> Dict:
        """Analyze entire Paul Davis collection rapidly"""
        
        print("🚀 Rapid Analysis of Paul Davis Notes Collection")
        print("=" * 60)
        
        txt_files = list(self.notes_dir.glob("*.txt"))
        txt_files.sort(key=lambda x: x.stat().st_size)  # Smallest first
        
        collection_results = {
            "analysis_timestamp": time.time(),
            "total_files": len(txt_files),
            "files": {},
            "collection_summary": {}
        }
        
        total_words = 0
        all_terms = Counter()
        file_types = Counter()
        
        print(f"Found {len(txt_files)} files to analyze\n")
        
        for file_path in txt_files:
            print(f"📄 Analyzing: {file_path.name} ({file_path.stat().st_size/1024:.1f} KB)")
            
            file_result = self.extract_file_overview(file_path)
            collection_results["files"][file_path.name] = file_result
            
            if "error" not in file_result:
                total_words += file_result["word_count"]
                all_terms.update(file_result["significant_methodology_terms"])
                file_types[file_result["file_type_assessment"]] += 1
                
                print(f"   Type: {file_result['file_type_assessment']}")
                print(f"   Words: {file_result['word_count']:,}")
                print(f"   Key terms: {', '.join(list(file_result['significant_methodology_terms'].keys())[:5])}")
                print(f"   Methodology sections: {len(file_result['methodology_sections'])}")
                print()
        
        # Collection-level insights
        collection_results["collection_summary"] = {
            "total_words": total_words,
            "file_types": dict(file_types),
            "top_methodology_terms": dict(all_terms.most_common(20)),
            "largest_files": [
                {
                    "name": name,
                    "size_kb": data["size_kb"],
                    "type": data["file_type_assessment"]
                }
                for name, data in collection_results["files"].items()
                if "error" not in data
            ]
        }
        
        # Sort largest files
        collection_results["collection_summary"]["largest_files"].sort(
            key=lambda x: x["size_kb"], reverse=True
        )
        
        return collection_results
    
    def generate_insights_report(self, results: Dict) -> str:
        """Generate readable insights report"""
        
        report = f"""# Paul Davis Notes - Rapid Analysis Report

## Collection Overview

**Total Files**: {results['total_files']}  
**Total Content**: {results['collection_summary']['total_words']:,} words

### File Types Distribution
"""
        
        for file_type, count in results['collection_summary']['file_types'].items():
            report += f"- **{file_type}**: {count} files\n"
        
        report += f"""
### Top Methodology Terms Across Collection
"""
        
        top_terms = results['collection_summary']['top_methodology_terms']
        for term, count in list(top_terms.items())[:10]:
            report += f"- **{term}**: {count} occurrences\n"
        
        report += f"""
## File-by-File Analysis

"""
        
        # Sort files by methodology relevance
        files_with_relevance = []
        for filename, data in results['files'].items():
            if "error" not in data:
                relevance_score = sum(data.get('significant_methodology_terms', {}).values())
                files_with_relevance.append((filename, data, relevance_score))
        
        files_with_relevance.sort(key=lambda x: x[2], reverse=True)
        
        for filename, data, relevance_score in files_with_relevance:
            report += f"""### {filename}
**Type**: {data['file_type_assessment']}  
**Size**: {data['size_kb']:.1f} KB, {data['word_count']:,} words  
**Methodology Relevance**: {relevance_score} term occurrences  

**Key Terms**: {', '.join(data['significant_methodology_terms'].keys())}

**Sample Content**:
> {data['sample_content'][0][:200]}...

"""
            
            if data['methodology_sections']:
                report += "**Top Methodology Sections**:\n"
                for section in data['methodology_sections'][:2]:
                    report += f"- Section {section['section_number']}: {section['preview'][:150]}...\n"
            
            report += "\n---\n\n"
        
        return report
    
    def identify_priority_files(self, results: Dict) -> List[str]:
        """Identify which files are most relevant for uncertainty methodology"""
        
        priority_files = []
        
        for filename, data in results['files'].items():
            if "error" in data:
                continue
            
            # Score files based on multiple factors
            methodology_score = sum(data.get('significant_methodology_terms', {}).values())
            uncertainty_terms = data.get('significant_methodology_terms', {}).get('uncertainty', 0)
            bayesian_terms = data.get('significant_methodology_terms', {}).get('bayesian', 0)
            validation_terms = data.get('significant_methodology_terms', {}).get('validation', 0)
            
            total_score = (methodology_score + 
                          uncertainty_terms * 5 +  # Weight uncertainty highly
                          bayesian_terms * 5 +     # Weight Bayesian highly
                          validation_terms * 3)    # Weight validation moderately
            
            priority_files.append((filename, total_score, data['file_type_assessment']))
        
        # Sort by relevance score
        priority_files.sort(key=lambda x: x[1], reverse=True)
        
        return priority_files

def main():
    """Run rapid analysis"""
    
    analyzer = RapidDavisAnalyzer()
    
    # Quick analysis
    results = analyzer.analyze_collection()
    
    # Generate report
    report = analyzer.generate_insights_report(results)
    
    # Identify priorities
    priority_files = analyzer.identify_priority_files(results)
    
    # Save results
    output_dir = Path("/home/brian/projects/Digimons/uncertainty_stress_test/analysis")
    
    # Save full results
    with open(output_dir / "paul_davis_rapid_analysis.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save readable report
    with open(output_dir / "paul_davis_insights_report.md", "w") as f:
        f.write(report)
    
    # Save priority ranking
    priority_report = "# Priority Files for Deep Analysis\n\n"
    for i, (filename, score, file_type) in enumerate(priority_files, 1):
        priority_report += f"{i}. **{filename}** (Score: {score:.0f}, Type: {file_type})\n"
    
    with open(output_dir / "paul_davis_priority_files.md", "w") as f:
        f.write(priority_report)
    
    print("\n✅ Rapid Analysis Complete!")
    print(f"📊 Results saved to paul_davis_rapid_analysis.json")
    print(f"📝 Report saved to paul_davis_insights_report.md") 
    print(f"🎯 Priority files saved to paul_davis_priority_files.md")
    
    print(f"\n🔍 Top 3 Most Relevant Files:")
    for i, (filename, score, file_type) in enumerate(priority_files[:3], 1):
        print(f"   {i}. {filename} (Score: {score:.0f}, {file_type})")
    
    return results, priority_files

if __name__ == "__main__":
    results, priorities = main()