#!/usr/bin/env python3
"""
A/B Testing Framework for V12 Schema Prompt Optimization
Tests different prompt variants to improve algorithm extraction quality

TDD Approach:
1. Test baseline performance with current prompt
2. Test improved prompt variants
3. Compare results with statistical significance
4. Provide evidence-based recommendations
"""

import os
import json
import time
import asyncio
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
import statistics

# Add universal model tester to path
sys.path.append(str(Path(__file__).parent / "universal_model_tester"))
from universal_model_client import UniversalModelClient

@dataclass
class PromptVariant:
    name: str
    description: str
    prompt_text: str
    expected_improvement: str

@dataclass
class ExtractionResult:
    theory_name: str
    prompt_variant: str
    success: bool
    model_used: str
    duration: float
    entity_count: int
    relation_count: int
    algorithm_count: int
    quality_score: float
    extraction_data: Dict[str, Any]
    error: Optional[str] = None

@dataclass
class TheoryTestCase:
    name: str
    paper_path: str
    theory_type: str
    expected_algorithms: int  # Expected number of algorithms/procedures
    description: str

class PromptABTester:
    def __init__(self):
        self.client = UniversalModelClient()
        self.results: List[ExtractionResult] = []
    
    def get_prompt_variants(self) -> List[PromptVariant]:
        """Define prompt variants for A/B testing"""
        return [
            PromptVariant(
                name="baseline",
                description="Current V12 prompt (baseline)",
                prompt_text="""
You are a theory extraction specialist. Analyze this academic paper and extract:

1. THEORY NAME: Exact name from the paper
2. KEY ENTITIES: Main concepts/variables (preserve exact terminology)
3. KEY RELATIONS: How concepts connect (include direction and nature)
4. ALGORITHMS: Any formulas, procedures, or logical processes
5. THEORY PURPOSE: What questions this theory answers
6. THEORY TYPE: Classification (causal, taxonomic, procedural, mathematical, etc.)

Focus on precision and use the author's exact terminology throughout.
Rate your extraction quality from 1-10 based on completeness and fidelity.
""",
                expected_improvement="baseline measurement"
            ),
            
            PromptVariant(
                name="explicit_process_focus",
                description="Explicit focus on procedures and processes",
                prompt_text="""
You are a theory extraction specialist. Analyze this academic paper and extract:

1. THEORY NAME: Exact name from the paper
2. KEY ENTITIES: Main concepts/variables (preserve exact terminology)
3. KEY RELATIONS: How concepts connect (include direction and nature)
4. PROCEDURES & PROCESSES: Extract ALL of the following that appear in the theory:
   - Mathematical formulas or equations
   - Step-by-step procedures or workflows  
   - Decision-making processes or frameworks
   - Classification rules or criteria
   - Logical sequences or protocols
   - Computational methods or algorithms
5. THEORY PURPOSE: What questions this theory answers
6. THEORY TYPE: Classification (causal, taxonomic, procedural, mathematical, etc.)

Focus on precision and use the author's exact terminology throughout.
Pay special attention to any HOW-TO elements - what does this theory tell us how to do?
Rate your extraction quality from 1-10 based on completeness and fidelity.
""",
                expected_improvement="better algorithm/procedure detection"
            ),
            
            PromptVariant(
                name="question_driven",
                description="Question-driven algorithm extraction",
                prompt_text="""
You are a theory extraction specialist. Analyze this academic paper and extract:

1. THEORY NAME: Exact name from the paper
2. KEY ENTITIES: Main concepts/variables (preserve exact terminology)
3. KEY RELATIONS: How concepts connect (include direction and nature)
4. HOW-TO ELEMENTS: What does this theory tell us HOW to do?
   - How to calculate or compute something?
   - How to make decisions or choices?
   - How to classify or categorize?
   - How to follow a process or sequence?
   - How to apply rules or criteria?
   - What formulas or equations are provided?
5. THEORY PURPOSE: What questions this theory answers
6. THEORY TYPE: Classification (causal, taxonomic, procedural, mathematical, etc.)

Focus on precision and use the author's exact terminology throughout.
Look specifically for actionable elements - steps, procedures, formulas, rules.
Rate your extraction quality from 1-10 based on completeness and fidelity.
""",
                expected_improvement="more intuitive algorithm identification"
            ),
            
            PromptVariant(
                name="component_specific",
                description="Component-specific algorithm breakdown",
                prompt_text="""
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
""",
                expected_improvement="systematic component identification"
            )
        ]
    
    def get_test_theories(self) -> List[TheoryTestCase]:
        """Define theories for testing - focus on those with known algorithm deficits"""
        return [
            TheoryTestCase(
                name="Conversion Theory (Motifs)",
                paper_path="lit_review/literature/conversion_theory/Conversion Motifs.txt",
                theory_type="taxonomic",
                expected_algorithms=2,  # Should have motif identification process + classification steps
                description="Religious conversion process - previously extracted 0 algorithms, should have procedures"
            ),
            TheoryTestCase(
                name="Risk Seeking Preferences", 
                paper_path="lit_review/literature/risk_seeking_preferences/Risk Seeking Preferences: An Investigation of Framing Effects across Decisional Domains.txt",
                theory_type="causal",
                expected_algorithms=1,  # Should have decision-making framework
                description="Decision-making under risk - previously extracted 0 algorithms, should have process"
            ),
            TheoryTestCase(
                name="Social Marketing Theory",
                paper_path="lit_review/literature/social_marketing/Social Marketing Theory.txt", 
                theory_type="procedural",
                expected_algorithms=3,  # Should have multiple procedures
                description="Marketing procedures - previously extracted 3 algorithms, good test case"
            ),
            TheoryTestCase(
                name="Prospect Theory",
                paper_path="PROSPECT_THEORY_CORE_CONCEPTS.md",
                theory_type="mathematical", 
                expected_algorithms=4,  # Known to have formulas
                description="Mathematical decision theory - baseline control with known algorithms"
            )
        ]
    
    def load_paper(self, paper_path: str) -> str:
        """Load paper text, truncate if needed"""
        full_path = Path(__file__).parent / paper_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error loading {paper_path}: {e}")
            return ""
        
        # Truncate to manageable size for consistent testing
        if len(text) > 12000:
            text = text[:12000] + "\n\n[TRUNCATED FOR TESTING CONSISTENCY]"
        return text
    
    def create_test_schema(self) -> Dict[str, Any]:
        """Create consistent schema for all prompt variants"""
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
    
    async def test_single_extraction(self, theory: TheoryTestCase, prompt_variant: PromptVariant) -> ExtractionResult:
        """Test extraction for one theory with one prompt variant"""
        print(f"\n🧪 Testing: {theory.name} with {prompt_variant.name}")
        print("-" * 60)
        
        paper_text = self.load_paper(theory.paper_path)
        if not paper_text:
            return ExtractionResult(
                theory_name=theory.name,
                prompt_variant=prompt_variant.name,
                success=False,
                model_used="none",
                duration=0.0,
                entity_count=0,
                relation_count=0,
                algorithm_count=0,
                quality_score=0.0,
                extraction_data={},
                error=f"Could not load paper: {theory.paper_path}"
            )
        
        schema = self.create_test_schema()
        messages = [
            {
                "role": "user",
                "content": f"{prompt_variant.prompt_text}\n\nACADEMIC PAPER:\n\n{paper_text}"
            }
        ]
        
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
            
            extraction = json.loads(result["response"].choices[0].message.content)
            
            # Extract metrics
            entity_count = len(extraction.get('key_entities', []))
            relation_count = len(extraction.get('key_relations', []))
            algorithm_count = len(extraction.get('algorithms', []))
            quality_score = extraction.get('extraction_quality', 0.0)
            
            print(f"✅ SUCCESS - {result['model_used']} ({end_time - start_time:.1f}s)")
            print(f"   Entities: {entity_count}, Relations: {relation_count}")
            print(f"   Algorithms: {algorithm_count} (expected: {theory.expected_algorithms})")
            print(f"   Quality: {quality_score}/10")
            
            return ExtractionResult(
                theory_name=theory.name,
                prompt_variant=prompt_variant.name,
                success=True,
                model_used=result["model_used"],
                duration=end_time - start_time,
                entity_count=entity_count,
                relation_count=relation_count,
                algorithm_count=algorithm_count,
                quality_score=quality_score,
                extraction_data=extraction
            )
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)[:100]}...")
            return ExtractionResult(
                theory_name=theory.name,
                prompt_variant=prompt_variant.name,
                success=False,
                model_used="error",
                duration=0.0,
                entity_count=0,
                relation_count=0,
                algorithm_count=0,
                quality_score=0.0,
                extraction_data={},
                error=str(e)
            )
    
    async def run_ab_tests(self) -> Dict[str, Any]:
        """Run comprehensive A/B tests across all prompt variants and theories"""
        prompt_variants = self.get_prompt_variants()
        test_theories = self.get_test_theories()
        
        print("🎯 V12 SCHEMA PROMPT A/B TESTING")
        print("=" * 60)
        print(f"Testing {len(prompt_variants)} prompt variants on {len(test_theories)} theories")
        print(f"Total tests: {len(prompt_variants) * len(test_theories)}")
        
        results = []
        
        # Test each theory with each prompt variant
        for theory in test_theories:
            for prompt_variant in prompt_variants:
                result = await self.test_single_extraction(theory, prompt_variant)
                results.append(result)
                self.results.append(result)
                
                # Brief pause between tests to avoid rate limiting
                await asyncio.sleep(2)
        
        return self.analyze_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze A/B test results with statistical analysis"""
        if not self.results:
            return {"error": "No results to analyze"}
        
        # Group results by prompt variant
        by_prompt = {}
        for result in self.results:
            if result.success:
                variant = result.prompt_variant
                if variant not in by_prompt:
                    by_prompt[variant] = {
                        'results': [],
                        'algorithm_counts': [],
                        'quality_scores': [],
                        'durations': []
                    }
                
                by_prompt[variant]['results'].append(result)
                by_prompt[variant]['algorithm_counts'].append(result.algorithm_count)
                by_prompt[variant]['quality_scores'].append(result.quality_score)
                by_prompt[variant]['durations'].append(result.duration)
        
        # Calculate metrics for each prompt variant
        analysis = {}
        for variant, data in by_prompt.items():
            if data['algorithm_counts']:  # Only if we have data
                analysis[variant] = {
                    'test_count': len(data['results']),
                    'avg_algorithm_count': statistics.mean(data['algorithm_counts']),
                    'avg_quality_score': statistics.mean(data['quality_scores']),
                    'avg_duration': statistics.mean(data['durations']),
                    'algorithm_stdev': statistics.stdev(data['algorithm_counts']) if len(data['algorithm_counts']) > 1 else 0,
                    'quality_stdev': statistics.stdev(data['quality_scores']) if len(data['quality_scores']) > 1 else 0,
                    'success_rate': len([r for r in data['results'] if r.success]) / len(data['results'])
                }
        
        # Find best performing variant
        best_variant = None
        best_score = 0
        if analysis:
            for variant, metrics in analysis.items():
                # Composite score: algorithm detection + quality
                composite_score = metrics['avg_algorithm_count'] + metrics['avg_quality_score']
                if composite_score > best_score:
                    best_score = composite_score
                    best_variant = variant
        
        return {
            'analysis': analysis,
            'best_variant': best_variant,
            'total_tests': len(self.results),
            'successful_tests': len([r for r in self.results if r.success]),
            'detailed_results': [asdict(r) for r in self.results]
        }
    
    def save_results(self, analysis: Dict[str, Any]) -> str:
        """Save test results with timestamp"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"prompt_ab_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return results_file

async def main():
    """Run A/B testing framework"""
    tester = PromptABTester()
    
    print("Starting A/B testing for V12 schema prompt optimization...")
    print("This will test baseline vs improved prompts for algorithm extraction.\n")
    
    analysis = await tester.run_ab_tests()
    results_file = tester.save_results(analysis)
    
    print(f"\n📊 A/B TEST ANALYSIS")
    print("=" * 50)
    
    if 'analysis' in analysis and analysis['analysis']:
        print(f"Best performing variant: {analysis.get('best_variant', 'unknown')}")
        print(f"Total tests: {analysis['total_tests']}")
        print(f"Successful tests: {analysis['successful_tests']}")
        
        print(f"\nVariant Performance Summary:")
        for variant, metrics in analysis['analysis'].items():
            print(f"\n{variant}:")
            print(f"  Avg Algorithms: {metrics['avg_algorithm_count']:.1f}")
            print(f"  Avg Quality: {metrics['avg_quality_score']:.1f}/10")
            print(f"  Success Rate: {metrics['success_rate']:.1%}")
            print(f"  Avg Duration: {metrics['avg_duration']:.1f}s")
    
    print(f"\n💾 Full results saved: {results_file}")
    return analysis

if __name__ == "__main__":
    asyncio.run(main())