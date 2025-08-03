#!/usr/bin/env python3
"""
Multi-Pass V12 Schema Extraction with Refinement
Implements iterative refinement to achieve higher quality scores

TDD Approach:
1. Test baseline single-pass extraction
2. Test multi-pass with algorithm refinement
3. Test quality validation pass
4. Compare final results with evidence
"""

import os
import json
import time
import asyncio
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

# Add universal model tester to path
sys.path.append(str(Path(__file__).parent / "universal_model_tester"))
from universal_model_client import UniversalModelClient

@dataclass
class PassResult:
    pass_number: int
    pass_type: str
    success: bool
    duration: float
    entity_count: int
    relation_count: int
    algorithm_count: int
    quality_score: float
    extraction_data: Dict[str, Any]
    improvements: List[str]
    error: Optional[str] = None

@dataclass
class MultiPassResult:
    theory_name: str
    total_passes: int
    total_duration: float
    final_quality: float
    quality_improvement: float
    algorithm_improvement: int
    passes: List[PassResult]
    success: bool

@dataclass
class TheoryTestCase:
    name: str
    paper_path: str
    theory_type: str
    description: str

class MultiPassExtractor:
    def __init__(self):
        self.client = UniversalModelClient()
    
    def load_paper(self, paper_path: str) -> str:
        """Load paper text, truncate if needed"""
        full_path = Path(__file__).parent / paper_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error loading {paper_path}: {e}")
            return ""
        
        # Truncate to manageable size
        if len(text) > 12000:
            text = text[:12000] + "\n\n[TRUNCATED FOR MULTI-PASS PROCESSING]"
        return text
    
    def get_pass1_prompt(self) -> str:
        """Pass 1: Broad extraction with winning component-specific prompt"""
        return """
You are a theory extraction specialist. Analyze this academic paper and extract:

1. THEORY NAME: Exact name from the paper
2. KEY ENTITIES: Main concepts/variables (preserve exact terminology)
3. KEY RELATIONS: How concepts connect (include direction and nature)
4. OPERATIONAL COMPONENTS (extract all that apply):
   a) FORMULAS: Mathematical equations or calculations
   b) PROCEDURES: Step-by-step processes or workflows
   c) RULES: Decision criteria or classification logic
   d) SEQUENCES: Ordered steps or phases
   e) FRAMEWORKS: Structured approaches or methods
   f) ALGORITHMS: Computational or logical procedures
5. THEORY PURPOSE: What questions this theory answers
6. THEORY TYPE: Classification (causal, taxonomic, procedural, mathematical, etc.)

Focus on precision and use the author's exact terminology throughout.
Examine the theory for any systematic approach or method it provides.
Rate your extraction quality from 1-10 based on completeness and fidelity.
"""
    
    def get_pass2_prompt(self, pass1_data: Dict[str, Any]) -> str:
        """Pass 2: Algorithm refinement based on theory type and initial extraction"""
        theory_type = pass1_data.get('theory_type_classification', '').lower()
        algorithm_count = len(pass1_data.get('algorithms', []))
        
        # Adaptive refinement based on theory type
        if 'mathematical' in theory_type:
            focus = "mathematical formulas, equations, calculations, and computational procedures"
        elif 'taxonomic' in theory_type:
            focus = "classification rules, categorization procedures, and systematic frameworks"
        elif 'procedural' in theory_type:
            focus = "step-by-step processes, workflows, and operational procedures"
        elif 'causal' in theory_type:
            focus = "causal mechanisms, decision processes, and logical sequences"
        else:
            focus = "any systematic methods, procedures, or operational elements"
        
        return f"""
REFINEMENT PASS: Algorithm and Procedure Detection

Previous extraction found {algorithm_count} algorithms/procedures. 
Theory type: {theory_type}

Re-examine the academic paper specifically looking for {focus}.

Search thoroughly for:
1. MISSED PROCEDURES: Any step-by-step processes you may have missed
2. IMPLICIT ALGORITHMS: Logical procedures described in text but not formally stated
3. DECISION FRAMEWORKS: How the theory guides choices or classifications
4. COMPUTATIONAL METHODS: Any calculations or systematic approaches
5. OPERATIONAL GUIDELINES: How to apply or use this theory in practice

Extract ONLY the algorithms/procedures/methods you find. Use this exact format:
- Name: [exact name from paper]
- Type: [mathematical/logical/procedural/classification]
- Description: [what it does]
- Steps/Formula: [detailed implementation]

Focus on finding systematic approaches the theory provides for DO-ing something.
Rate the completeness of your algorithm detection from 1-10.
"""
    
    def get_pass3_prompt(self, combined_data: Dict[str, Any]) -> str:
        """Pass 3: Quality validation and completeness check"""
        entity_count = len(combined_data.get('key_entities', []))
        relation_count = len(combined_data.get('key_relations', []))
        algorithm_count = len(combined_data.get('algorithms', []))
        
        return f"""
VALIDATION PASS: Quality Assessment and Completeness Check

Current extraction summary:
- Entities: {entity_count}
- Relations: {relation_count} 
- Algorithms/Procedures: {algorithm_count}

Perform a final quality validation:

1. COMPLETENESS CHECK: Are there any major theoretical components missing?
2. ACCURACY VERIFICATION: Are entity names and descriptions precise to the paper?
3. RELATIONSHIP VALIDATION: Are the connections between concepts correctly captured?
4. ALGORITHM ASSESSMENT: Are all procedural elements properly identified?
5. TERMINOLOGY FIDELITY: Is the author's exact language preserved?

Provide:
- QUALITY_SCORE: Rate overall extraction from 1-10
- MISSING_ELEMENTS: List any important components you notice are missing
- ACCURACY_ISSUES: Note any inaccuracies in terminology or descriptions
- COMPLETENESS_ASSESSMENT: Estimate what percentage of the theory is captured
- IMPROVEMENT_SUGGESTIONS: How could this extraction be enhanced?

Focus on identifying gaps and assessing extraction fidelity.
"""
    
    def create_schema(self, pass_type: str) -> Dict[str, Any]:
        """Create schema appropriate for each pass type"""
        if pass_type == "algorithm_refinement":
            return {
                "type": "object", 
                "properties": {
                    "additional_algorithms": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "description": {"type": "string"},
                                "formula_or_steps": {"type": "string"}
                            },
                            "required": ["name", "type", "description"]
                        }
                    },
                    "algorithm_completeness_score": {"type": "number", "minimum": 1, "maximum": 10},
                    "refinement_notes": {"type": "string"}
                },
                "required": ["additional_algorithms", "algorithm_completeness_score"],
                "additionalProperties": False
            }
        elif pass_type == "quality_validation":
            return {
                "type": "object",
                "properties": {
                    "quality_score": {"type": "number", "minimum": 1, "maximum": 10},
                    "missing_elements": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "accuracy_issues": {
                        "type": "array", 
                        "items": {"type": "string"}
                    },
                    "completeness_percentage": {"type": "number", "minimum": 0, "maximum": 100},
                    "improvement_suggestions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "validation_notes": {"type": "string"}
                },
                "required": ["quality_score", "completeness_percentage"],
                "additionalProperties": False
            }
        else:  # broad_extraction
            return {
                "type": "object",
                "properties": {
                    "theory_name": {"type": "string"},
                    "theory_type_classification": {"type": "string"},
                    "key_entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "entity_type": {"type": "string"}
                            },
                            "required": ["name", "description"]
                        }
                    },
                    "key_relations": {
                        "type": "array", 
                        "items": {
                            "type": "object",
                            "properties": {
                                "from_concept": {"type": "string"},
                                "to_concept": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "description": {"type": "string"}
                            },
                            "required": ["from_concept", "to_concept", "relationship_type"]
                        }
                    },
                    "algorithms": {
                        "type": "array",
                        "items": {
                            "type": "object", 
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "description": {"type": "string"},
                                "formula_or_steps": {"type": "string"}
                            },
                            "required": ["name", "type", "description"]
                        }
                    },
                    "theory_purpose": {"type": "string"},
                    "extraction_quality": {"type": "number", "minimum": 1, "maximum": 10},
                    "extraction_notes": {"type": "string"}
                },
                "required": ["theory_name", "key_entities", "theory_purpose", "extraction_quality"],
                "additionalProperties": False
            }
    
    async def execute_pass(self, 
                          pass_number: int, 
                          pass_type: str, 
                          prompt: str, 
                          paper_text: str,
                          previous_data: Optional[Dict[str, Any]] = None) -> PassResult:
        """Execute a single extraction pass"""
        print(f"\n🔄 Pass {pass_number}: {pass_type}")
        print("-" * 50)
        
        schema = self.create_schema(pass_type)
        
        # For refinement passes, include previous extraction context
        if previous_data and pass_type != "broad_extraction":
            context = f"\n\nPREVIOUS EXTRACTION CONTEXT:\n{json.dumps(previous_data, indent=2)}\n\n"
            full_prompt = prompt + context + "ACADEMIC PAPER:\n\n" + paper_text
        else:
            full_prompt = prompt + "\n\nACADEMIC PAPER:\n\n" + paper_text
        
        messages = [{"role": "user", "content": full_prompt}]
        
        try:
            start_time = time.time()
            
            result = self.client.complete(
                messages=messages,
                model="gemini_2_5_flash",
                schema=schema,
                fallback_models=["o4_mini"],
                timeout=60
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            extraction = json.loads(result["response"].choices[0].message.content)
            
            # Extract metrics based on pass type
            if pass_type == "broad_extraction":
                entity_count = len(extraction.get('key_entities', []))
                relation_count = len(extraction.get('key_relations', []))
                algorithm_count = len(extraction.get('algorithms', []))
                quality_score = extraction.get('extraction_quality', 0.0)
                improvements = ["initial_extraction"]
            elif pass_type == "algorithm_refinement":
                entity_count = 0
                relation_count = 0
                algorithm_count = len(extraction.get('additional_algorithms', []))
                quality_score = extraction.get('algorithm_completeness_score', 0.0)
                improvements = [f"found_{algorithm_count}_additional_algorithms"]
            else:  # quality_validation
                entity_count = 0
                relation_count = 0
                algorithm_count = 0
                quality_score = extraction.get('quality_score', 0.0)
                improvements = extraction.get('improvement_suggestions', [])
            
            print(f"✅ Pass {pass_number} SUCCESS ({duration:.1f}s)")
            print(f"   Quality: {quality_score}/10")
            if algorithm_count > 0:
                print(f"   New Algorithms: {algorithm_count}")
            
            return PassResult(
                pass_number=pass_number,
                pass_type=pass_type,
                success=True,
                duration=duration,
                entity_count=entity_count,
                relation_count=relation_count,
                algorithm_count=algorithm_count,
                quality_score=quality_score,
                extraction_data=extraction,
                improvements=improvements
            )
            
        except Exception as e:
            print(f"❌ Pass {pass_number} FAILED: {str(e)[:100]}...")
            return PassResult(
                pass_number=pass_number,
                pass_type=pass_type,
                success=False,
                duration=0.0,
                entity_count=0,
                relation_count=0,
                algorithm_count=0,
                quality_score=0.0,
                extraction_data={},
                improvements=[],
                error=str(e)
            )
    
    def merge_extractions(self, pass1_data: Dict[str, Any], pass2_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge Pass 1 and Pass 2 extractions"""
        merged = pass1_data.copy()
        
        # Add additional algorithms from Pass 2
        if 'additional_algorithms' in pass2_data and pass2_data['additional_algorithms']:
            existing_algorithms = merged.get('algorithms', [])
            new_algorithms = pass2_data['additional_algorithms']
            merged['algorithms'] = existing_algorithms + new_algorithms
        
        return merged
    
    async def multi_pass_extraction(self, theory: TheoryTestCase) -> MultiPassResult:
        """Execute complete multi-pass extraction for one theory"""
        print(f"\n🎯 MULTI-PASS EXTRACTION: {theory.name}")
        print("=" * 60)
        
        paper_text = self.load_paper(theory.paper_path)
        if not paper_text:
            return MultiPassResult(
                theory_name=theory.name,
                total_passes=0,
                total_duration=0.0,
                final_quality=0.0,
                quality_improvement=0.0,
                algorithm_improvement=0,
                passes=[],
                success=False
            )
        
        passes = []
        start_time = time.time()
        
        # Pass 1: Broad extraction
        pass1_prompt = self.get_pass1_prompt()
        pass1_result = await self.execute_pass(1, "broad_extraction", pass1_prompt, paper_text)
        passes.append(pass1_result)
        
        if not pass1_result.success:
            return MultiPassResult(
                theory_name=theory.name,
                total_passes=1,
                total_duration=pass1_result.duration,
                final_quality=0.0,
                quality_improvement=0.0,
                algorithm_improvement=0,
                passes=passes,
                success=False
            )
        
        initial_quality = pass1_result.quality_score
        initial_algorithms = pass1_result.algorithm_count
        
        # Pass 2: Algorithm refinement
        pass2_prompt = self.get_pass2_prompt(pass1_result.extraction_data)
        pass2_result = await self.execute_pass(2, "algorithm_refinement", pass2_prompt, paper_text, pass1_result.extraction_data)
        passes.append(pass2_result)
        
        # Merge Pass 1 and Pass 2 data
        if pass2_result.success:
            merged_data = self.merge_extractions(pass1_result.extraction_data, pass2_result.extraction_data)
            final_algorithm_count = len(merged_data.get('algorithms', []))
        else:
            merged_data = pass1_result.extraction_data
            final_algorithm_count = initial_algorithms
        
        # Pass 3: Quality validation
        pass3_prompt = self.get_pass3_prompt(merged_data)
        pass3_result = await self.execute_pass(3, "quality_validation", pass3_prompt, paper_text, merged_data)
        passes.append(pass3_result)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate final metrics
        if pass3_result.success:
            final_quality = pass3_result.quality_score
        else:
            final_quality = initial_quality
        
        quality_improvement = final_quality - initial_quality
        algorithm_improvement = final_algorithm_count - initial_algorithms
        
        print(f"\n📊 MULTI-PASS SUMMARY")
        print("-" * 30)
        print(f"Initial Quality: {initial_quality}/10")
        print(f"Final Quality: {final_quality}/10")
        print(f"Quality Improvement: {quality_improvement:+.1f}")
        print(f"Algorithm Improvement: {algorithm_improvement:+d}")
        print(f"Total Duration: {total_duration:.1f}s")
        
        return MultiPassResult(
            theory_name=theory.name,
            total_passes=len(passes),
            total_duration=total_duration,
            final_quality=final_quality,
            quality_improvement=quality_improvement,
            algorithm_improvement=algorithm_improvement,
            passes=passes,
            success=all(p.success for p in passes)
        )
    
    def get_test_theories(self) -> List[TheoryTestCase]:
        """Get theories for multi-pass testing"""
        return [
            TheoryTestCase(
                name="Conversion Theory (Motifs)",
                paper_path="lit_review/literature/conversion_theory/Conversion Motifs.txt",
                theory_type="taxonomic",
                description="Religious conversion - test case for procedure detection improvement"
            ),
            TheoryTestCase(
                name="Prospect Theory",
                paper_path="PROSPECT_THEORY_CORE_CONCEPTS.md",
                theory_type="mathematical",
                description="Mathematical decision theory - control case with known algorithms"
            )
        ]
    
    async def run_multi_pass_tests(self) -> Dict[str, Any]:
        """Run multi-pass extraction tests"""
        theories = self.get_test_theories()
        results = []
        
        print("🎯 MULTI-PASS EXTRACTION TESTING")
        print("=" * 60)
        print(f"Testing {len(theories)} theories with 3-pass refinement approach")
        
        for theory in theories:
            result = await self.multi_pass_extraction(theory)
            results.append(result)
            
            # Brief pause between theories
            await asyncio.sleep(2)
        
        # Calculate summary statistics
        successful_tests = [r for r in results if r.success]
        if successful_tests:
            avg_quality_improvement = sum(r.quality_improvement for r in successful_tests) / len(successful_tests)
            avg_algorithm_improvement = sum(r.algorithm_improvement for r in successful_tests) / len(successful_tests)
            avg_final_quality = sum(r.final_quality for r in successful_tests) / len(successful_tests)
        else:
            avg_quality_improvement = 0.0
            avg_algorithm_improvement = 0.0
            avg_final_quality = 0.0
        
        return {
            'summary': {
                'total_theories': len(theories),
                'successful_extractions': len(successful_tests),
                'avg_quality_improvement': avg_quality_improvement,
                'avg_algorithm_improvement': avg_algorithm_improvement,
                'avg_final_quality': avg_final_quality
            },
            'detailed_results': [asdict(r) for r in results]
        }
    
    def save_results(self, analysis: Dict[str, Any]) -> str:
        """Save multi-pass test results"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"multi_pass_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return results_file

async def main():
    """Run multi-pass extraction testing"""
    extractor = MultiPassExtractor()
    
    print("Starting multi-pass extraction testing...")
    print("This will test iterative refinement for quality improvement.\n")
    
    analysis = await extractor.run_multi_pass_tests()
    results_file = extractor.save_results(analysis)
    
    print(f"\n📊 MULTI-PASS TEST ANALYSIS")
    print("=" * 50)
    
    summary = analysis['summary']
    print(f"Successful tests: {summary['successful_extractions']}/{summary['total_theories']}")
    print(f"Avg quality improvement: {summary['avg_quality_improvement']:+.1f}")
    print(f"Avg algorithm improvement: {summary['avg_algorithm_improvement']:+.1f}")
    print(f"Avg final quality: {summary['avg_final_quality']:.1f}/10")
    
    print(f"\n💾 Full results saved: {results_file}")
    return analysis

if __name__ == "__main__":
    asyncio.run(main())