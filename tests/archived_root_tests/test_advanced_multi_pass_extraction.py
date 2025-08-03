#!/usr/bin/env python3
"""
Advanced Multi-Pass V12 Schema Testing
Tests sophisticated extraction approaches with context-aware passes, concept mixing, and patching

Advanced Approaches to Test:
1. 6-Category Component-Specific Prompt (full implementation)
2. Context-Aware Multi-Pass (feeding previous stage results)
3. Concept Mixing Reviews (cross-pollination between extractions)
4. Patching vs Rewriting (incremental vs full replacement)
5. Termination Conditions (COMPLETE trigger system)
"""

import os
import json
import time
import asyncio
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple
import copy

# Add universal model tester to path
sys.path.append(str(Path(__file__).parent / "universal_model_tester"))
from universal_model_client import UniversalModelClient

@dataclass
class AdvancedPassResult:
    pass_number: int
    pass_type: str
    approach: str  # "rewrite", "patch", "concept_mix"
    success: bool
    duration: float
    quality_score: float
    completeness_assessment: str  # "INCOMPLETE", "NEEDS_REVIEW", "COMPLETE"
    improvements_made: List[str]
    extraction_data: Dict[str, Any]
    context_used: bool
    termination_triggered: bool
    error: Optional[str] = None

@dataclass
class AdvancedExtractionResult:
    theory_name: str
    approach_name: str
    total_passes: int
    total_duration: float
    final_quality: float
    final_completeness: str
    algorithm_count_progression: List[int]
    quality_progression: List[float]
    passes: List[AdvancedPassResult]
    success: bool
    early_termination: bool

class AdvancedMultiPassTester:
    def __init__(self):
        self.client = UniversalModelClient()
    
    def get_6_category_prompt(self) -> str:
        """
        Full 6-category component-specific prompt (enhanced version)
        """
        return """
You are a theory extraction specialist. Analyze this academic paper and extract theoretical components with maximum precision:

1. THEORY NAME: Exact name from the paper
2. KEY ENTITIES: Main concepts/variables (preserve exact terminology)
3. KEY RELATIONS: How concepts connect (include direction and nature)
4. OPERATIONAL COMPONENTS - Extract ALL that apply across these 6 categories:
   a) FORMULAS: Mathematical equations, calculations, or quantitative expressions
   b) PROCEDURES: Step-by-step processes, workflows, or systematic methods
   c) RULES: Decision criteria, classification logic, or conditional statements
   d) SEQUENCES: Ordered steps, phases, or temporal progressions
   e) FRAMEWORKS: Structured approaches, conceptual models, or organizing principles
   f) ALGORITHMS: Computational procedures, logical operations, or systematic calculations
5. THEORY PURPOSE: What questions this theory answers
6. THEORY TYPE: Classification (causal, taxonomic, procedural, mathematical, etc.)

Focus on precision and use the author's exact terminology throughout.
For each operational component, specify which category it belongs to (a-f).
Rate your extraction quality from 1-10 and assess completeness: INCOMPLETE, NEEDS_REVIEW, or COMPLETE.
"""
    
    def get_context_aware_refinement_prompt(self, previous_extraction: Dict[str, Any]) -> str:
        """
        Context-aware refinement prompt that builds on previous extraction
        """
        current_algorithms = len(previous_extraction.get('algorithms', []))
        current_quality = previous_extraction.get('extraction_quality', 0)
        
        return f"""
CONTEXT-AWARE REFINEMENT PASS

Previous extraction achieved {current_quality}/10 quality with {current_algorithms} operational components.

PREVIOUS EXTRACTION CONTEXT:
{json.dumps(previous_extraction, indent=2)}

Now re-examine the academic paper with this context in mind. Look for:

1. MISSED COMPONENTS: Any operational elements not captured in previous extraction
2. CATEGORY REFINEMENT: Better categorization of existing components across:
   - FORMULAS (mathematical expressions)
   - PROCEDURES (step-by-step processes) 
   - RULES (decision criteria)
   - SEQUENCES (ordered phases)
   - FRAMEWORKS (structured approaches)
   - ALGORITHMS (computational methods)
3. RELATIONSHIP ENHANCEMENT: Additional connections between concepts
4. PRECISION IMPROVEMENT: More accurate descriptions using author's terminology

Output ONLY the improvements/additions you find. Use PATCH format:
- ADD: New components to add
- MODIFY: Existing components to refine
- ENHANCE: Relationships to improve

Assess completeness: INCOMPLETE, NEEDS_REVIEW, or COMPLETE
If COMPLETE, this terminates the refinement cycle.
"""
    
    def get_concept_mixing_prompt(self, extractions: List[Dict[str, Any]]) -> str:
        """
        Concept mixing prompt that cross-pollinates between multiple extractions
        """
        return f"""
CONCEPT MIXING REVIEW PASS

You have {len(extractions)} different extractions of the same theory. Cross-pollinate insights:

EXTRACTION VARIATIONS:
{json.dumps(extractions, indent=2)}

Identify:
1. CONCEPT VARIATIONS: Different ways the same concept is described
2. COMPLEMENTARY ELEMENTS: Components found in one extraction but not others
3. SYNTHESIS OPPORTUNITIES: How to combine the best aspects of each extraction
4. CONSISTENCY PATTERNS: Which elements appear across multiple extractions (high confidence)
5. UNIQUE INSIGHTS: Novel components found in only one extraction (need validation)

Create a MIXED extraction that:
- Combines the strongest elements from each variation
- Resolves terminology inconsistencies using author's exact terms
- Synthesizes complementary operational components
- Maintains theoretical coherence

Rate synthesis quality 1-10 and completeness: INCOMPLETE, NEEDS_REVIEW, or COMPLETE
"""
    
    def get_patching_prompt(self, base_extraction: Dict[str, Any], patch_suggestions: Dict[str, Any]) -> str:
        """
        Patching prompt for incremental improvements
        """
        return f"""
INCREMENTAL PATCHING PASS

Base extraction:
{json.dumps(base_extraction, indent=2)}

Suggested patches:
{json.dumps(patch_suggestions, indent=2)}

Apply patches incrementally to improve the base extraction:

1. VALIDATE PATCHES: Check if suggested improvements are accurate to the paper
2. APPLY CAREFULLY: Make minimal, precise changes that enhance quality
3. PRESERVE STRUCTURE: Maintain existing good elements while improving gaps
4. MAINTAIN CONSISTENCY: Ensure patches align with existing terminology and structure

Output the PATCHED extraction with:
- All validated improvements applied
- Original structure preserved where good
- Enhanced components where patches add value
- Rejected patches noted with reasons

Rate patched extraction quality 1-10 and assess: INCOMPLETE, NEEDS_REVIEW, or COMPLETE
"""
    
    def create_schema_for_pass_type(self, pass_type: str) -> Dict[str, Any]:
        """
        Create appropriate schema for different pass types
        """
        if pass_type == "initial_6_category":
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
                    "operational_components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "category": {"type": "string", "enum": ["FORMULAS", "PROCEDURES", "RULES", "SEQUENCES", "FRAMEWORKS", "ALGORITHMS"]},
                                "description": {"type": "string"},
                                "implementation": {"type": "string"}
                            },
                            "required": ["name", "category", "description"]
                        }
                    },
                    "theory_purpose": {"type": "string"},
                    "extraction_quality": {"type": "number", "minimum": 1, "maximum": 10},
                    "completeness_assessment": {"type": "string", "enum": ["INCOMPLETE", "NEEDS_REVIEW", "COMPLETE"]},
                    "extraction_notes": {"type": "string"}
                },
                "required": ["theory_name", "key_entities", "theory_purpose", "extraction_quality", "completeness_assessment"],
                "additionalProperties": False
            }
        
        elif pass_type == "context_refinement":
            return {
                "type": "object",
                "properties": {
                    "refinements": {
                        "type": "object",
                        "properties": {
                            "add_components": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "category": {"type": "string"},
                                        "description": {"type": "string"},
                                        "implementation": {"type": "string"}
                                    },
                                    "required": ["name", "category", "description"]
                                }
                            },
                            "modify_components": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "original_name": {"type": "string"},
                                        "new_name": {"type": "string"},
                                        "new_description": {"type": "string"},
                                        "reason": {"type": "string"}
                                    },
                                    "required": ["original_name", "reason"]
                                }
                            },
                            "enhance_relations": {
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
                            }
                        }
                    },
                    "quality_improvement": {"type": "number", "minimum": 1, "maximum": 10},
                    "completeness_assessment": {"type": "string", "enum": ["INCOMPLETE", "NEEDS_REVIEW", "COMPLETE"]},
                    "improvement_notes": {"type": "string"}
                },
                "required": ["refinements", "quality_improvement", "completeness_assessment"],
                "additionalProperties": False
            }
        
        else:  # concept_mixing, patching
            return {
                "type": "object",
                "properties": {
                    "synthesized_extraction": {
                        "type": "object",
                        "properties": {
                            "theory_name": {"type": "string"},
                            "key_entities": {"type": "array", "items": {"type": "object"}},
                            "key_relations": {"type": "array", "items": {"type": "object"}},
                            "operational_components": {"type": "array", "items": {"type": "object"}},
                            "theory_purpose": {"type": "string"}
                        }
                    },
                    "synthesis_quality": {"type": "number", "minimum": 1, "maximum": 10},
                    "completeness_assessment": {"type": "string", "enum": ["INCOMPLETE", "NEEDS_REVIEW", "COMPLETE"]},
                    "synthesis_improvements": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "synthesis_notes": {"type": "string"}
                },
                "required": ["synthesized_extraction", "synthesis_quality", "completeness_assessment"],
                "additionalProperties": False
            }
    
    async def execute_advanced_pass(self, 
                                  pass_number: int,
                                  pass_type: str,
                                  approach: str,
                                  prompt: str,
                                  paper_text: str,
                                  context_data: Optional[Dict[str, Any]] = None) -> AdvancedPassResult:
        """
        Execute an advanced extraction pass with context and termination logic
        """
        print(f"\n🔄 Pass {pass_number}: {pass_type} ({approach})")
        print("-" * 60)
        
        schema = self.create_schema_for_pass_type(pass_type)
        
        # Build prompt with context if provided
        if context_data:
            full_prompt = prompt + "\n\nACADEMIC PAPER:\n\n" + paper_text
            context_used = True
        else:
            full_prompt = prompt + "\n\nACADEMIC PAPER:\n\n" + paper_text
            context_used = False
        
        messages = [{"role": "user", "content": full_prompt}]
        
        try:
            start_time = time.time()
            
            result = self.client.complete(
                messages=messages,
                model="gemini_2_5_flash",
                schema=schema,
                fallback_models=["o4_mini"],
                timeout=90  # Longer timeout for complex passes
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            extraction = json.loads(result["response"].choices[0].message.content)
            
            # Extract pass-specific metrics
            if pass_type == "initial_6_category":
                quality_score = extraction.get('extraction_quality', 0.0)
                completeness = extraction.get('completeness_assessment', 'INCOMPLETE')
                improvements = [f"6_category_extraction"]
                component_count = len(extraction.get('operational_components', []))
            elif pass_type == "context_refinement":
                quality_score = extraction.get('quality_improvement', 0.0)
                completeness = extraction.get('completeness_assessment', 'INCOMPLETE')
                refinements = extraction.get('refinements', {})
                add_count = len(refinements.get('add_components', []))
                modify_count = len(refinements.get('modify_components', []))
                improvements = [f"added_{add_count}_components", f"modified_{modify_count}_components"]
            else:  # concept_mixing, patching
                quality_score = extraction.get('synthesis_quality', 0.0)
                completeness = extraction.get('completeness_assessment', 'INCOMPLETE')
                improvements = extraction.get('synthesis_improvements', [])
            
            termination_triggered = (completeness == 'COMPLETE')
            
            print(f"✅ Pass {pass_number} SUCCESS ({duration:.1f}s)")
            print(f"   Quality: {quality_score}/10")
            print(f"   Completeness: {completeness}")
            print(f"   Termination: {'YES' if termination_triggered else 'NO'}")
            if pass_type == "initial_6_category":
                print(f"   Components: {component_count}")
            
            return AdvancedPassResult(
                pass_number=pass_number,
                pass_type=pass_type,
                approach=approach,
                success=True,
                duration=duration,
                quality_score=quality_score,
                completeness_assessment=completeness,
                improvements_made=improvements,
                extraction_data=extraction,
                context_used=context_used,
                termination_triggered=termination_triggered
            )
            
        except Exception as e:
            print(f"❌ Pass {pass_number} FAILED: {str(e)[:100]}...")
            return AdvancedPassResult(
                pass_number=pass_number,
                pass_type=pass_type,
                approach=approach,
                success=False,
                duration=0.0,
                quality_score=0.0,
                completeness_assessment='INCOMPLETE',
                improvements_made=[],
                extraction_data={},
                context_used=False,
                termination_triggered=False,
                error=str(e)
            )
    
    def apply_patches(self, base_extraction: Dict[str, Any], patches: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply patches to base extraction
        """
        patched = copy.deepcopy(base_extraction)
        
        refinements = patches.get('refinements', {})
        
        # Add new components
        if 'add_components' in refinements:
            existing_components = patched.get('operational_components', [])
            new_components = refinements['add_components']
            patched['operational_components'] = existing_components + new_components
        
        # Modify existing components
        if 'modify_components' in refinements:
            components = patched.get('operational_components', [])
            for mod in refinements['modify_components']:
                for comp in components:
                    if comp.get('name') == mod.get('original_name'):
                        if 'new_name' in mod:
                            comp['name'] = mod['new_name']
                        if 'new_description' in mod:
                            comp['description'] = mod['new_description']
        
        # Add enhanced relations
        if 'enhance_relations' in refinements:
            existing_relations = patched.get('key_relations', [])
            new_relations = refinements['enhance_relations']
            patched['key_relations'] = existing_relations + new_relations
        
        return patched
    
    async def run_advanced_extraction(self, theory_name: str, paper_text: str, approach_name: str) -> AdvancedExtractionResult:
        """
        Run advanced multi-pass extraction with specified approach
        """
        print(f"\n🎯 ADVANCED EXTRACTION: {theory_name}")
        print(f"📋 Approach: {approach_name}")
        print("=" * 70)
        
        passes = []
        start_time = time.time()
        max_passes = 5
        early_termination = False
        
        algorithm_progression = []
        quality_progression = []
        
        # Pass 1: Initial 6-category extraction
        initial_prompt = self.get_6_category_prompt()
        pass1 = await self.execute_advanced_pass(1, "initial_6_category", approach_name, initial_prompt, paper_text)
        passes.append(pass1)
        
        if not pass1.success:
            return self._create_failed_result(theory_name, approach_name, passes, 0.0)
        
        current_extraction = pass1.extraction_data
        algorithm_progression.append(len(current_extraction.get('operational_components', [])))
        quality_progression.append(pass1.quality_score)
        
        if pass1.termination_triggered:
            early_termination = True
            print("🏁 Early termination triggered by COMPLETE assessment")
        
        # Continue with approach-specific passes if not terminated
        pass_number = 2
        while pass_number <= max_passes and not early_termination:
            
            if approach_name == "context_aware_refinement":
                # Context-aware refinement approach
                refinement_prompt = self.get_context_aware_refinement_prompt(current_extraction)
                pass_result = await self.execute_advanced_pass(
                    pass_number, "context_refinement", approach_name, 
                    refinement_prompt, paper_text, current_extraction
                )
                passes.append(pass_result)
                
                if pass_result.success:
                    # Apply patches to current extraction
                    current_extraction = self.apply_patches(current_extraction, pass_result.extraction_data)
                    algorithm_progression.append(len(current_extraction.get('operational_components', [])))
                    quality_progression.append(pass_result.quality_score)
                    
                    if pass_result.termination_triggered:
                        early_termination = True
                        print("🏁 Context refinement triggered termination")
                        break
            
            elif approach_name == "concept_mixing":
                # Create variations for concept mixing
                if pass_number == 2:
                    # Generate multiple extractions for mixing
                    variations = []
                    for i in range(2):  # Create 2 variations
                        var_prompt = self.get_6_category_prompt() + f"\n\nVariation {i+1}: Focus on different aspects and terminology."
                        var_result = await self.execute_advanced_pass(
                            f"{pass_number}.{i+1}", "initial_6_category", f"{approach_name}_variation", 
                            var_prompt, paper_text
                        )
                        if var_result.success:
                            variations.append(var_result.extraction_data)
                    
                    # Mix concepts
                    if variations:
                        mixing_prompt = self.get_concept_mixing_prompt([current_extraction] + variations)
                        mix_result = await self.execute_advanced_pass(
                            pass_number, "concept_mixing", approach_name,
                            mixing_prompt, paper_text, {"variations": [current_extraction] + variations}
                        )
                        passes.append(mix_result)
                        
                        if mix_result.success:
                            current_extraction = mix_result.extraction_data.get('synthesized_extraction', current_extraction)
                            algorithm_progression.append(len(current_extraction.get('operational_components', [])))
                            quality_progression.append(mix_result.quality_score)
                            
                            if mix_result.termination_triggered:
                                early_termination = True
                                print("🏁 Concept mixing triggered termination")
                                break
            
            elif approach_name == "incremental_patching":
                # Incremental patching approach
                refinement_prompt = self.get_context_aware_refinement_prompt(current_extraction)
                patch_suggestions = await self.execute_advanced_pass(
                    f"{pass_number}a", "context_refinement", f"{approach_name}_suggestion",
                    refinement_prompt, paper_text, current_extraction
                )
                
                if patch_suggestions.success:
                    # Apply patches incrementally
                    patching_prompt = self.get_patching_prompt(current_extraction, patch_suggestions.extraction_data)
                    patch_result = await self.execute_advanced_pass(
                        f"{pass_number}b", "patching", approach_name,
                        patching_prompt, paper_text, 
                        {"base": current_extraction, "patches": patch_suggestions.extraction_data}
                    )
                    passes.extend([patch_suggestions, patch_result])
                    
                    if patch_result.success:
                        current_extraction = patch_result.extraction_data.get('synthesized_extraction', current_extraction)
                        algorithm_progression.append(len(current_extraction.get('operational_components', [])))
                        quality_progression.append(patch_result.quality_score)
                        
                        if patch_result.termination_triggered:
                            early_termination = True
                            print("🏁 Incremental patching triggered termination")
                            break
            
            pass_number += 1
            
            # Brief pause between passes
            await asyncio.sleep(2)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate final metrics
        final_quality = quality_progression[-1] if quality_progression else 0.0
        final_algorithm_count = algorithm_progression[-1] if algorithm_progression else 0
        final_completeness = passes[-1].completeness_assessment if passes else 'INCOMPLETE'
        
        print(f"\n📊 ADVANCED EXTRACTION SUMMARY")
        print("-" * 40)
        print(f"Approach: {approach_name}")
        print(f"Total Passes: {len(passes)}")
        print(f"Final Quality: {final_quality}/10")
        print(f"Algorithm Progression: {algorithm_progression}")
        print(f"Quality Progression: {quality_progression}")
        print(f"Early Termination: {'YES' if early_termination else 'NO'}")
        print(f"Total Duration: {total_duration:.1f}s")
        
        return AdvancedExtractionResult(
            theory_name=theory_name,
            approach_name=approach_name,
            total_passes=len(passes),
            total_duration=total_duration,
            final_quality=final_quality,
            final_completeness=final_completeness,
            algorithm_count_progression=algorithm_progression,
            quality_progression=quality_progression,
            passes=passes,
            success=all(p.success for p in passes),
            early_termination=early_termination
        )
    
    def _create_failed_result(self, theory_name: str, approach_name: str, passes: List, duration: float) -> AdvancedExtractionResult:
        """Create failed result"""
        return AdvancedExtractionResult(
            theory_name=theory_name,
            approach_name=approach_name,
            total_passes=len(passes),
            total_duration=duration,
            final_quality=0.0,
            final_completeness='INCOMPLETE',
            algorithm_count_progression=[],
            quality_progression=[],
            passes=passes,
            success=False,
            early_termination=False
        )
    
    def load_paper(self, paper_path: str) -> str:
        """Load paper text"""
        full_path = Path(__file__).parent / paper_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error loading {paper_path}: {e}")
            return ""
        
        # Truncate for consistent testing
        if len(text) > 12000:
            text = text[:12000] + "\n\n[TRUNCATED FOR ADVANCED TESTING]"
        return text
    
    async def run_parallel_advanced_tests(self) -> Dict[str, Any]:
        """
        Run all advanced approaches in parallel across multiple extractions
        """
        print("🚀 ADVANCED MULTI-PASS TESTING FRAMEWORK")
        print("=" * 70)
        print("Testing advanced approaches:")
        print("1. 6-Category Component-Specific")
        print("2. Context-Aware Refinement") 
        print("3. Concept Mixing Reviews")
        print("4. Incremental Patching")
        print("5. Termination Conditions (COMPLETE)")
        
        # Test theories
        test_theories = [
            ("Conversion Theory", "lit_review/literature/conversion_theory/Conversion Motifs.txt"),
            ("Prospect Theory", "PROSPECT_THEORY_CORE_CONCEPTS.md")
        ]
        
        # Test approaches
        approaches = [
            "context_aware_refinement",
            "concept_mixing", 
            "incremental_patching"
        ]
        
        all_results = []
        
        # Run tests in parallel for each theory-approach combination
        for theory_name, paper_path in test_theories:
            paper_text = self.load_paper(paper_path)
            if not paper_text:
                continue
                
            print(f"\n🎯 Testing theory: {theory_name}")
            print("-" * 50)
            
            for approach in approaches:
                try:
                    result = await self.run_advanced_extraction(theory_name, paper_text, approach)
                    all_results.append(result)
                except Exception as e:
                    print(f"❌ Failed {approach} for {theory_name}: {e}")
                
                # Brief pause between approaches
                await asyncio.sleep(3)
        
        return self.analyze_advanced_results(all_results)
    
    def analyze_advanced_results(self, results: List[AdvancedExtractionResult]) -> Dict[str, Any]:
        """
        Analyze results from all advanced approaches
        """
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return {"error": "No successful advanced extractions"}
        
        # Group by approach
        by_approach = {}
        for result in successful_results:
            approach = result.approach_name
            if approach not in by_approach:
                by_approach[approach] = []
            by_approach[approach].append(result)
        
        # Analyze each approach
        approach_analysis = {}
        for approach, approach_results in by_approach.items():
            avg_quality = sum(r.final_quality for r in approach_results) / len(approach_results)
            avg_duration = sum(r.total_duration for r in approach_results) / len(approach_results)
            avg_passes = sum(r.total_passes for r in approach_results) / len(approach_results)
            early_termination_rate = sum(1 for r in approach_results if r.early_termination) / len(approach_results)
            
            # Algorithm progression analysis
            all_progressions = [r.algorithm_count_progression for r in approach_results]
            avg_final_algorithms = sum(prog[-1] for prog in all_progressions if prog) / len(all_progressions)
            
            approach_analysis[approach] = {
                "test_count": len(approach_results),
                "avg_final_quality": avg_quality,
                "avg_duration": avg_duration,
                "avg_passes": avg_passes,
                "avg_final_algorithms": avg_final_algorithms,
                "early_termination_rate": early_termination_rate,
                "quality_range": [min(r.final_quality for r in approach_results), 
                                max(r.final_quality for r in approach_results)]
            }
        
        # Find best approach
        best_approach = max(approach_analysis.keys(), 
                          key=lambda k: approach_analysis[k]['avg_final_quality'])
        
        return {
            "summary": {
                "total_tests": len(results),
                "successful_tests": len(successful_results),
                "approaches_tested": list(by_approach.keys()),
                "best_approach": best_approach
            },
            "approach_analysis": approach_analysis,
            "detailed_results": [asdict(r) for r in successful_results]
        }
    
    def save_results(self, analysis: Dict[str, Any]) -> str:
        """Save advanced test results"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"advanced_multi_pass_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return results_file

async def main():
    """Run advanced multi-pass testing framework"""
    tester = AdvancedMultiPassTester()
    
    print("Starting advanced multi-pass extraction testing...")
    print("This tests sophisticated approaches with context, mixing, and patching.\n")
    
    analysis = await tester.run_parallel_advanced_tests()
    results_file = tester.save_results(analysis)
    
    print(f"\n📊 ADVANCED TESTING ANALYSIS")
    print("=" * 60)
    
    if 'approach_analysis' in analysis:
        print(f"Best Approach: {analysis['summary']['best_approach']}")
        print(f"Total Tests: {analysis['summary']['total_tests']}")
        print(f"Successful Tests: {analysis['summary']['successful_tests']}")
        
        print(f"\nApproach Performance:")
        for approach, metrics in analysis['approach_analysis'].items():
            print(f"\n{approach}:")
            print(f"  Avg Quality: {metrics['avg_final_quality']:.1f}/10")
            print(f"  Avg Duration: {metrics['avg_duration']:.1f}s")
            print(f"  Avg Passes: {metrics['avg_passes']:.1f}")
            print(f"  Early Termination: {metrics['early_termination_rate']:.1%}")
            print(f"  Avg Algorithms: {metrics['avg_final_algorithms']:.1f}")
    
    print(f"\n💾 Full results saved: {results_file}")
    return analysis

if __name__ == "__main__":
    asyncio.run(main())