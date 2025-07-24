#!/usr/bin/env python3
"""
Ground Truth Validation Framework
Creates test cases where we can mathematically determine correct confidence levels
"""

import json
import numpy as np
import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Add core services to path
sys.path.append('/home/brian/projects/Digimons/uncertainty_stress_test/core_services')

from uncertainty_engine import UncertaintyEngine, ConfidenceScore
from bayesian_aggregation_service import BayesianAggregationService, Evidence
from cerqual_assessor import CERQualAssessor, CERQualEvidence, StudyMetadata

@dataclass
class GroundTruthCase:
    """Test case with known correct confidence level"""
    
    case_id: str
    case_type: str  # 'perfect_strong', 'perfect_weak', 'contradictory', etc.
    description: str
    
    # Input materials
    text_content: str
    claim: str
    evidence_pieces: List[Evidence]
    domain: str
    
    # Expected outcomes (ground truth)
    expected_confidence_min: float
    expected_confidence_max: float
    expected_confidence_target: float
    confidence_reasoning: str
    
    # Test metadata  
    certainty_level: str  # 'mathematical', 'expert_consensus', 'literature_based'
    difficulty: str  # 'trivial', 'moderate', 'complex'
    created_date: datetime
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class ValidationResult:
    """Result of testing our system against ground truth"""
    
    case_id: str
    ground_truth_target: float
    system_estimate: float
    absolute_error: float
    relative_error: float
    within_expected_range: bool
    
    # Detailed breakdown
    confidence_score_details: Dict
    processing_time: float
    
    # Qualitative assessment
    error_severity: str  # 'acceptable', 'concerning', 'critical'
    error_analysis: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

class GroundTruthValidator:
    """
    Creates and validates against ground truth confidence cases
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        if api_key:
            self.uncertainty_engine = UncertaintyEngine(api_key)
            self.bayesian_service = BayesianAggregationService(api_key)
            self.cerqual_assessor = CERQualAssessor(api_key)
        
        self.ground_truth_cases = []
        self.validation_results = []
        
    def create_perfect_strong_cases(self) -> List[GroundTruthCase]:
        """Create cases where confidence should be very high (0.85-0.95)"""
        
        cases = []
        
        # Case 1: Multiple high-quality consistent sources
        case1 = GroundTruthCase(
            case_id="strong_001",
            case_type="perfect_strong",
            description="Five peer-reviewed studies, large samples, consistent findings, recent publication",
            text_content="""
            Five independent peer-reviewed studies published in Nature, Science, and Cell between 2022-2024 
            demonstrate that Treatment X increases recovery rates by 85-90% (N=2,450, 1,890, 3,200, 2,100, 1,750).
            All studies used randomized controlled trial design with double-blinding. 
            Meta-analysis (p<0.001, I²=5%) confirms consistent effect across populations.
            No significant adverse effects reported. Studies funded by independent government agencies.
            """,
            claim="Treatment X significantly improves recovery rates compared to standard care",
            evidence_pieces=[
                Evidence(
                    content="RCT study 1: Treatment X vs placebo, N=2450, recovery rate 89% vs 45%, p<0.001",
                    source="Nature Medicine 2024",
                    timestamp=datetime(2024, 3, 15),
                    reliability=0.95,
                    evidence_type="peer_reviewed",
                    domain="medical_research"
                ),
                Evidence(
                    content="RCT study 2: Treatment X efficacy, N=1890, recovery rate 87% vs 42%, p<0.001",
                    source="Science Translational Medicine 2023",
                    timestamp=datetime(2023, 11, 20),
                    reliability=0.95,
                    evidence_type="peer_reviewed", 
                    domain="medical_research"
                ),
                Evidence(
                    content="Meta-analysis of Treatment X: Combined N=11,390, effect size 2.1 (95% CI: 1.9-2.3)",
                    source="Cochrane Review 2024",
                    timestamp=datetime(2024, 1, 10),
                    reliability=0.98,
                    evidence_type="systematic_review",
                    domain="medical_research"
                )
            ],
            domain="medical_research",
            expected_confidence_min=0.85,
            expected_confidence_max=0.95,
            expected_confidence_target=0.90,
            confidence_reasoning="Multiple high-quality RCTs with large samples, consistent results, meta-analysis confirmation, recent data",
            certainty_level="mathematical",
            difficulty="trivial",
            created_date=datetime.now()
        )
        cases.append(case1)
        
        # Case 2: Established scientific fact
        case2 = GroundTruthCase(
            case_id="strong_002",
            case_type="perfect_strong",
            description="Well-established scientific principle with overwhelming evidence",
            text_content="""
            The relationship between smoking and lung cancer has been established through over 200 
            epidemiological studies spanning 70 years. Relative risk ranges from 15-30x for heavy smokers.
            Dose-response relationship clearly established. Biological mechanisms well understood.
            Supported by animal studies, cell culture studies, and population-level data.
            No credible contradictory evidence exists in peer-reviewed literature.
            """,
            claim="Cigarette smoking significantly increases lung cancer risk",
            evidence_pieces=[
                Evidence(
                    content="Meta-analysis: 200+ studies, RR=20.0 (95% CI: 18.5-21.5) for lung cancer in smokers",
                    source="Cancer Epidemiology Reviews 2020",
                    timestamp=datetime(2020, 6, 1),
                    reliability=0.98,
                    evidence_type="systematic_review",
                    domain="epidemiology"
                )
            ],
            domain="epidemiology",
            expected_confidence_min=0.95,
            expected_confidence_max=0.99,
            expected_confidence_target=0.97,
            confidence_reasoning="Overwhelming evidence over decades, clear dose-response, established mechanisms",
            certainty_level="mathematical",
            difficulty="trivial",
            created_date=datetime.now()
        )
        cases.append(case2)
        
        return cases
    
    def create_perfect_weak_cases(self) -> List[GroundTruthCase]:
        """Create cases where confidence should be very low (0.10-0.30)"""
        
        cases = []
        
        # Case 1: Single poor-quality study
        case1 = GroundTruthCase(
            case_id="weak_001",
            case_type="perfect_weak",
            description="Single small study, methodological flaws, contradicts established knowledge",
            text_content="""
            A single study (N=15) published in a predatory journal claims that drinking coffee
            reduces IQ by 50 points. The study used convenience sampling from a single coffee shop,
            no control group, no blinding, and IQ was measured with an online quiz.
            Authors have no relevant expertise. Study contradicts 100+ previous studies showing
            either neutral or positive cognitive effects of moderate coffee consumption.
            """,
            claim="Coffee consumption significantly reduces cognitive performance",
            evidence_pieces=[
                Evidence(
                    content="Coffee study: N=15, convenience sample, online IQ test, claims 50-point reduction",
                    source="Journal of Alternative Facts 2024",
                    timestamp=datetime(2024, 1, 1),
                    reliability=0.15,
                    evidence_type="low_quality_study",
                    domain="nutrition_research"
                )
            ],
            domain="nutrition_research",
            expected_confidence_min=0.05,
            expected_confidence_max=0.20,
            expected_confidence_target=0.12,
            confidence_reasoning="Single poor-quality study, small sample, major methodological flaws, contradicts established evidence",
            certainty_level="mathematical",
            difficulty="trivial",
            created_date=datetime.now()
        )
        cases.append(case1)
        
        # Case 2: Contradictory evidence
        case2 = GroundTruthCase(
            case_id="weak_002",
            case_type="perfect_weak",
            description="Equal amounts of contradictory evidence from similar quality sources",
            text_content="""
            Three studies claim Treatment Y is effective (effect sizes: 0.3, 0.4, 0.2).
            Three other studies claim Treatment Y is ineffective (effect sizes: -0.1, 0.0, -0.2).
            All studies have similar methodology (RCTs, N=200-400 each) and quality ratings.
            No clear reason for the contradictory findings. Recent systematic review concludes
            "evidence is insufficient to determine efficacy."
            """,
            claim="Treatment Y is effective for improving outcomes",
            evidence_pieces=[
                Evidence(
                    content="RCT 1: Treatment Y effective, N=300, effect size 0.3, p=0.02",
                    source="Medical Journal A 2023",
                    timestamp=datetime(2023, 6, 1),
                    reliability=0.80,
                    evidence_type="peer_reviewed",
                    domain="medical_research"
                ),
                Evidence(
                    content="RCT 2: Treatment Y ineffective, N=280, effect size -0.1, p=0.45",
                    source="Medical Journal B 2023",
                    timestamp=datetime(2023, 7, 1),
                    reliability=0.80,
                    evidence_type="peer_reviewed",
                    domain="medical_research"
                ),
                Evidence(
                    content="Systematic review: Evidence insufficient, heterogeneity high (I²=85%)",
                    source="Cochrane Review 2024",
                    timestamp=datetime(2024, 2, 1),
                    reliability=0.95,
                    evidence_type="systematic_review",
                    domain="medical_research"
                )
            ],
            domain="medical_research",
            expected_confidence_min=0.15,
            expected_confidence_max=0.35,
            expected_confidence_target=0.25,
            confidence_reasoning="Contradictory evidence of similar quality, high heterogeneity, systematic review inconclusive",
            certainty_level="mathematical",
            difficulty="moderate",
            created_date=datetime.now()
        )
        cases.append(case2)
        
        return cases
    
    def create_moderate_confidence_cases(self) -> List[GroundTruthCase]:
        """Create cases where confidence should be moderate (0.50-0.70)"""
        
        cases = []
        
        # Case 1: Limited but consistent evidence
        case1 = GroundTruthCase(
            case_id="moderate_001",
            case_type="moderate_confidence",
            description="Two good quality studies with consistent findings, but limited scope",
            text_content="""
            Two well-designed studies investigate whether mindfulness meditation improves academic performance.
            Study 1 (N=120): 8-week mindfulness program increased GPA by 0.3 points (p=0.01).
            Study 2 (N=95): 6-week program increased test scores by 12% (p=0.03).
            Both used randomized controlled designs with appropriate controls.
            However, both studies limited to undergraduate psychology students at similar universities.
            Generalizability unclear. Mechanism not well understood.
            """,
            claim="Mindfulness meditation improves academic performance",
            evidence_pieces=[
                Evidence(
                    content="RCT 1: Mindfulness program, N=120, GPA increase 0.3 points, p=0.01",
                    source="Educational Psychology Journal 2023",
                    timestamp=datetime(2023, 9, 1),
                    reliability=0.85,
                    evidence_type="peer_reviewed",
                    domain="educational_research"
                ),
                Evidence(
                    content="RCT 2: Mindfulness intervention, N=95, test score increase 12%, p=0.03",
                    source="Mindfulness Research Journal 2023",
                    timestamp=datetime(2023, 11, 1),
                    reliability=0.80,
                    evidence_type="peer_reviewed",
                    domain="educational_research"
                )
            ],
            domain="educational_research",
            expected_confidence_min=0.55,
            expected_confidence_max=0.70,
            expected_confidence_target=0.62,
            confidence_reasoning="Two good quality consistent studies, but limited scope and generalizability concerns",
            certainty_level="expert_consensus",
            difficulty="moderate",
            created_date=datetime.now()
        )
        cases.append(case1)
        
        return cases
    
    def create_edge_cases(self) -> List[GroundTruthCase]:
        """Create challenging edge cases to test system robustness"""
        
        cases = []
        
        # Case 1: High quality methodology, surprising result
        case1 = GroundTruthCase(
            case_id="edge_001",
            case_type="edge_case",
            description="Excellent methodology but result contradicts established theory",
            text_content="""
            A large-scale RCT (N=5,000) published in Nature finds that a new physics theory
            predicts experimental results with 99.9% accuracy, contradicting Einstein's relativity
            in specific conditions. Study uses gold-standard methodology, multiple independent
            replications, international collaboration. However, the finding contradicts 100+ years
            of established physics and would require rewriting textbooks.
            """,
            claim="New physics theory X is more accurate than Einstein's relativity in domain Y",
            evidence_pieces=[
                Evidence(
                    content="Large RCT: N=5000, new theory 99.9% accurate vs relativity 78% accurate, p<0.001",
                    source="Nature Physics 2024",
                    timestamp=datetime(2024, 4, 1),
                    reliability=0.98,
                    evidence_type="peer_reviewed",
                    domain="physics"
                )
            ],
            domain="physics",
            expected_confidence_min=0.40,
            expected_confidence_max=0.65,
            expected_confidence_target=0.52,
            confidence_reasoning="Excellent methodology but extraordinary claim requires extraordinary evidence. Single study insufficient to overturn established theory.",
            certainty_level="expert_consensus",
            difficulty="complex",
            created_date=datetime.now()
        )
        cases.append(case1)
        
        return cases
    
    def generate_all_ground_truth_cases(self) -> List[GroundTruthCase]:
        """Generate complete set of ground truth validation cases"""
        
        all_cases = []
        all_cases.extend(self.create_perfect_strong_cases())
        all_cases.extend(self.create_perfect_weak_cases())
        all_cases.extend(self.create_moderate_confidence_cases())
        all_cases.extend(self.create_edge_cases())
        
        self.ground_truth_cases = all_cases
        return all_cases
    
    async def validate_single_case(self, case: GroundTruthCase) -> ValidationResult:
        """Test our uncertainty system against a single ground truth case"""
        
        if not self.api_key:
            raise ValueError("API key required for validation")
        
        start_time = datetime.now()
        
        try:
            # Run our uncertainty assessment
            confidence_score = await self.uncertainty_engine.assess_initial_confidence(
                case.text_content, case.claim, case.domain
            )
            
            system_estimate = confidence_score.get_overall_confidence()
            
            # Calculate errors
            absolute_error = abs(system_estimate - case.expected_confidence_target)
            relative_error = absolute_error / case.expected_confidence_target
            within_range = (case.expected_confidence_min <= system_estimate <= case.expected_confidence_max)
            
            # Determine error severity
            if absolute_error < 0.10:
                error_severity = "acceptable"
            elif absolute_error < 0.25:
                error_severity = "concerning"
            else:
                error_severity = "critical"
            
            # Generate error analysis
            if system_estimate > case.expected_confidence_max:
                error_analysis = f"System overconfident by {absolute_error:.3f}. May not properly weigh limitations."
            elif system_estimate < case.expected_confidence_min:
                error_analysis = f"System underconfident by {absolute_error:.3f}. May be overly conservative."
            else:
                error_analysis = f"System estimate within expected range. Error magnitude: {absolute_error:.3f}"
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = ValidationResult(
                case_id=case.case_id,
                ground_truth_target=case.expected_confidence_target,
                system_estimate=system_estimate,
                absolute_error=absolute_error,
                relative_error=relative_error,
                within_expected_range=within_range,
                confidence_score_details=confidence_score.to_dict(),
                processing_time=processing_time,
                error_severity=error_severity,
                error_analysis=error_analysis
            )
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ValidationResult(
                case_id=case.case_id,
                ground_truth_target=case.expected_confidence_target,
                system_estimate=0.0,
                absolute_error=case.expected_confidence_target,
                relative_error=1.0,
                within_expected_range=False,
                confidence_score_details={},
                processing_time=processing_time,
                error_severity="critical",
                error_analysis=f"System error: {str(e)}"
            )
    
    async def run_full_validation(self) -> Dict[str, Any]:
        """Run validation against all ground truth cases"""
        
        print("🧪 Starting Ground Truth Validation")
        print("=" * 50)
        
        # Generate all test cases
        if not self.ground_truth_cases:
            self.generate_all_ground_truth_cases()
        
        validation_results = []
        
        for i, case in enumerate(self.ground_truth_cases):
            print(f"Testing case {i+1}/{len(self.ground_truth_cases)}: {case.case_id}")
            
            if self.api_key:  # Only run with real API
                result = await self.validate_single_case(case)
                validation_results.append(result)
                
                status = "✅" if result.within_expected_range else "❌"
                print(f"  {status} Expected: {case.expected_confidence_target:.3f}, Got: {result.system_estimate:.3f}, Error: {result.absolute_error:.3f}")
            else:
                print("  ⏭️  Skipped (no API key)")
        
        self.validation_results = validation_results
        
        # Calculate summary statistics
        if validation_results:
            within_range_count = sum(1 for r in validation_results if r.within_expected_range)
            mean_absolute_error = np.mean([r.absolute_error for r in validation_results])
            mean_relative_error = np.mean([r.relative_error for r in validation_results])
            
            acceptable_errors = sum(1 for r in validation_results if r.error_severity == "acceptable")
            concerning_errors = sum(1 for r in validation_results if r.error_severity == "concerning")
            critical_errors = sum(1 for r in validation_results if r.error_severity == "critical")
            
            summary = {
                'total_cases': len(validation_results),
                'within_expected_range': within_range_count,
                'accuracy_rate': within_range_count / len(validation_results),
                'mean_absolute_error': mean_absolute_error,
                'mean_relative_error': mean_relative_error,
                'error_distribution': {
                    'acceptable': acceptable_errors,
                    'concerning': concerning_errors,
                    'critical': critical_errors
                },
                'validation_results': [r.to_dict() for r in validation_results],
                'ground_truth_cases': [c.to_dict() for c in self.ground_truth_cases]
            }
        else:
            summary = {
                'total_cases': len(self.ground_truth_cases),
                'within_expected_range': 0,
                'accuracy_rate': 0.0,
                'message': 'No validation run - missing API key',
                'ground_truth_cases': [c.to_dict() for c in self.ground_truth_cases]
            }
        
        return summary
    
    def generate_validation_report(self, summary: Dict[str, Any]) -> str:
        """Generate human-readable validation report"""
        
        if 'validation_results' not in summary:
            return "Ground truth validation cases created but not tested (API key required)."
        
        report = f"""# Ground Truth Validation Report

## Summary Statistics
- **Total Test Cases**: {summary['total_cases']}
- **Within Expected Range**: {summary['within_expected_range']}/{summary['total_cases']} ({summary['accuracy_rate']:.1%})
- **Mean Absolute Error**: {summary['mean_absolute_error']:.3f}
- **Mean Relative Error**: {summary['mean_relative_error']:.1%}

## Error Distribution
- **Acceptable** (≤0.10 error): {summary['error_distribution']['acceptable']} cases
- **Concerning** (0.10-0.25 error): {summary['error_distribution']['concerning']} cases  
- **Critical** (>0.25 error): {summary['error_distribution']['critical']} cases

## Detailed Results

"""
        
        for result_dict in summary['validation_results']:
            result = ValidationResult(**{k: v for k, v in result_dict.items() if k != 'confidence_score_details'})
            
            status_emoji = "✅" if result.within_expected_range else "❌"
            severity_emoji = {"acceptable": "🟢", "concerning": "🟡", "critical": "🔴"}.get(result.error_severity, "⚪")
            
            report += f"""### {result.case_id} {status_emoji} {severity_emoji}
- **Expected**: {result.ground_truth_target:.3f}
- **System Estimate**: {result.system_estimate:.3f}
- **Absolute Error**: {result.absolute_error:.3f}
- **Analysis**: {result.error_analysis}

"""
        
        # Assessment and recommendations
        accuracy = summary['accuracy_rate']
        mae = summary['mean_absolute_error']
        
        if accuracy >= 0.8 and mae <= 0.15:
            assessment = "✅ **EXCELLENT** - System performs well on ground truth cases"
        elif accuracy >= 0.6 and mae <= 0.25:
            assessment = "🟡 **ACCEPTABLE** - System performance adequate but needs improvement"
        else:
            assessment = "🔴 **POOR** - System performance unacceptable, major issues identified"
        
        report += f"""
## Overall Assessment

{assessment}

### Recommendations
"""
        
        if summary['error_distribution']['critical'] > 0:
            report += f"- **Critical**: {summary['error_distribution']['critical']} cases with major errors need investigation\n"
        
        if mae > 0.20:
            report += "- **Calibration**: Mean absolute error too high, system needs recalibration\n"
        
        if accuracy < 0.7:
            report += "- **Accuracy**: Too many estimates outside expected ranges\n"
        
        if summary['error_distribution']['acceptable'] == len(summary['validation_results']):
            report += "- **Status**: System ready for deployment\n"
        
        return report

# Test execution
async def main():
    """Run ground truth validation"""
    
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    
    validator = GroundTruthValidator(api_key)
    
    # Run validation
    summary = await validator.run_full_validation()
    
    # Generate report
    report = validator.generate_validation_report(summary)
    
    # Save results
    output_dir = Path("/home/brian/projects/Digimons/uncertainty_stress_test/validation")
    
    # Save summary
    with open(output_dir / "ground_truth_validation_results.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    # Save report
    with open(output_dir / "ground_truth_validation_report.md", "w") as f:
        f.write(report)
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    if 'validation_results' in summary:
        print(f"Accuracy Rate: {summary['accuracy_rate']:.1%}")
        print(f"Mean Absolute Error: {summary['mean_absolute_error']:.3f}")
        print(f"Critical Errors: {summary['error_distribution']['critical']}")
    else:
        print(f"Ground truth cases created: {summary['total_cases']}")
        print("Run with API key to test system performance")
    
    print(f"\nResults saved to: {output_dir}")
    
    return summary

if __name__ == "__main__":
    asyncio.run(main())