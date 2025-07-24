#!/usr/bin/env python3
"""
Comprehensive Bias Analysis Framework
Tests for systematic biases in uncertainty estimation
"""

import json
import numpy as np
import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict 
from pathlib import Path
import itertools

# Add core services to path
sys.path.append('/home/brian/projects/Digimons/uncertainty_stress_test/core_services')

from uncertainty_engine import UncertaintyEngine, ConfidenceScore
from bayesian_aggregation_service import BayesianAggregationService, Evidence

@dataclass
class BiasTestCase:
    """Single bias test case comparing two similar scenarios"""
    
    test_id: str
    bias_type: str
    description: str
    
    # Control case (baseline)
    control_text: str
    control_claim: str
    control_context: Dict[str, Any]
    
    # Test case (potentially biased)
    test_text: str  
    test_claim: str
    test_context: Dict[str, Any]
    
    # Expected outcome
    expected_relationship: str  # 'equal', 'test_higher', 'test_lower'
    bias_magnitude_threshold: float  # Minimum difference to consider biased
    
    # Metadata
    difficulty: str  # 'trivial', 'moderate', 'subtle'
    created_date: datetime
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass 
class BiasTestResult:
    """Result of testing for a specific bias"""
    
    test_id: str
    bias_type: str
    
    # Results
    control_confidence: float
    test_confidence: float
    confidence_difference: float
    
    # Analysis
    bias_detected: bool
    bias_direction: str  # 'none', 'favors_test', 'favors_control'
    bias_magnitude: str  # 'none', 'small', 'moderate', 'large'
    statistical_significance: Optional[float]  # p-value if available
    
    # Details
    control_details: Dict[str, Any]
    test_details: Dict[str, Any]
    processing_time: float
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

class BiasAnalyzer:
    """
    Comprehensive bias testing framework for uncertainty estimation
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        if api_key:
            self.uncertainty_engine = UncertaintyEngine(api_key)
            self.bayesian_service = BayesianAggregationService(api_key)
        
        self.bias_test_cases = []
        self.bias_results = []
        
    def create_source_prestige_bias_cases(self) -> List[BiasTestCase]:
        """Test if prestigious sources get inflated confidence"""
        
        cases = []
        
        # Case 1: Same study, different institution attribution
        case1 = BiasTestCase(
            test_id="prestige_001",
            bias_type="source_prestige",
            description="Same study methodology attributed to prestigious vs unknown institution",
            control_text="""
            A study conducted at Regional State University examined the effects of sleep 
            deprivation on cognitive performance. Researchers tested 150 undergraduate students
            using a randomized controlled design. Participants in the sleep-deprived group
            showed 23% reduction in working memory tasks (p=0.012). The study controlled
            for age, gender, and baseline cognitive ability.
            """,
            control_claim="Sleep deprivation significantly reduces cognitive performance",
            control_context={"institution": "Regional State University", "prestige_level": 0.3},
            test_text="""
            A study conducted at Harvard Medical School examined the effects of sleep 
            deprivation on cognitive performance. Researchers tested 150 undergraduate students
            using a randomized controlled design. Participants in the sleep-deprived group
            showed 23% reduction in working memory tasks (p=0.012). The study controlled
            for age, gender, and baseline cognitive ability.
            """,
            test_claim="Sleep deprivation significantly reduces cognitive performance",
            test_context={"institution": "Harvard Medical School", "prestige_level": 0.95},
            expected_relationship="equal",
            bias_magnitude_threshold=0.05,
            difficulty="moderate",
            created_date=datetime.now()
        )
        cases.append(case1)
        
        # Case 2: Author prestige bias
        case2 = BiasTestCase(
            test_id="prestige_002", 
            bias_type="source_prestige",
            description="Same research findings attributed to Nobel laureate vs unknown researcher",
            control_text="""
            Dr. J. Smith, a researcher at Generic University, published findings showing
            that a new quantum computing algorithm reduces processing time by 40%.
            The algorithm was tested on 5 different quantum systems with consistent results.
            Peer review noted solid methodology and clear documentation.
            """,
            control_claim="New quantum algorithm significantly improves processing speed",
            control_context={"author_prestige": 0.2, "career_stage": "early"},
            test_text="""
            Dr. John Smith, Nobel Prize winner in Physics, published findings showing
            that a new quantum computing algorithm reduces processing time by 40%.
            The algorithm was tested on 5 different quantum systems with consistent results.
            Peer review noted solid methodology and clear documentation.
            """,
            test_claim="New quantum algorithm significantly improves processing speed", 
            test_context={"author_prestige": 0.98, "career_stage": "distinguished"},
            expected_relationship="equal",
            bias_magnitude_threshold=0.08,
            difficulty="subtle",
            created_date=datetime.now()
        )
        cases.append(case2)
        
        return cases
    
    def create_recency_bias_cases(self) -> List[BiasTestCase]:
        """Test if newer research inappropriately gets higher confidence"""
        
        cases = []
        
        # Case 1: Same methodology, different publication dates
        case1 = BiasTestCase(
            test_id="recency_001",
            bias_type="recency_bias", 
            description="Identical study methodology from 2010 vs 2024",
            control_text="""
            A 2010 study published in Nature examined the relationship between exercise
            and cognitive function. The randomized controlled trial (N=200) found that
            moderate exercise improved memory scores by 15% (95% CI: 8-22%, p=0.003).
            The study used validated cognitive assessments and controlled for age, education,
            and baseline fitness. This finding has been cited 450 times.
            """,
            control_claim="Moderate exercise improves memory function",
            control_context={"publication_year": 2010, "citations": 450},
            test_text="""
            A 2024 study published in Nature examined the relationship between exercise
            and cognitive function. The randomized controlled trial (N=200) found that
            moderate exercise improved memory scores by 15% (95% CI: 8-22%, p=0.003).
            The study used validated cognitive assessments and controlled for age, education,
            and baseline fitness. This finding has been cited 12 times.
            """,
            test_claim="Moderate exercise improves memory function",
            test_context={"publication_year": 2024, "citations": 12},
            expected_relationship="equal",  # Same methodology should get same confidence
            bias_magnitude_threshold=0.06,
            difficulty="moderate",
            created_date=datetime.now()
        )
        cases.append(case1)
        
        return cases
    
    def create_domain_bias_cases(self) -> List[BiasTestCase]:
        """Test if certain academic domains get systematically different confidence"""
        
        cases = []
        
        # Case 1: STEM vs Humanities methodology
        case1 = BiasTestCase(
            test_id="domain_001",
            bias_type="domain_bias",
            description="Similar methodology quality in physics vs literary criticism",
            control_text="""
            A physics experiment measured quantum entanglement decay rates using
            carefully controlled laboratory conditions. The study used n=50 trials,
            proper statistical controls, and peer review validation. Results showed
            statistically significant effects (p=0.02) with replication by independent labs.
            """,
            control_claim="Quantum entanglement exhibits measurable decay in controlled conditions",
            control_context={"domain": "physics", "methodology": "experimental"},
            test_text="""
            A literary criticism study analyzed narrative techniques using
            carefully controlled textual analysis. The study used n=50 texts,
            proper analytical frameworks, and peer review validation. Results showed
            statistically significant patterns (p=0.02) with replication by independent scholars.
            """,
            test_claim="Specific narrative techniques exhibit measurable effects in literary texts",
            test_context={"domain": "literary_criticism", "methodology": "textual_analysis"},
            expected_relationship="equal",  # Equal methodological rigor should get equal confidence
            bias_magnitude_threshold=0.10,
            difficulty="subtle",
            created_date=datetime.now()
        )
        cases.append(case1)
        
        # Case 2: Medical vs Social Science
        case2 = BiasTestCase(
            test_id="domain_002",
            bias_type="domain_bias", 
            description="RCT methodology in medicine vs psychology",
            control_text="""
            A medical RCT (N=300) tested drug efficacy using double-blind placebo control.
            Primary endpoint showed 25% improvement (p=0.001). Study protocol pre-registered,
            conducted at multiple centers, with independent data monitoring committee.
            Results published in high-impact medical journal.
            """,
            control_claim="Drug X significantly improves patient outcomes",
            control_context={"domain": "medicine", "sample_size": 300},
            test_text="""
            A psychology RCT (N=300) tested therapy efficacy using waitlist control.
            Primary endpoint showed 25% improvement (p=0.001). Study protocol pre-registered,
            conducted at multiple centers, with independent assessment committee.
            Results published in high-impact psychology journal.
            """,
            test_claim="Therapy X significantly improves patient outcomes",
            test_context={"domain": "psychology", "sample_size": 300},
            expected_relationship="equal",
            bias_magnitude_threshold=0.08,
            difficulty="moderate",
            created_date=datetime.now()
        )
        cases.append(case2)
        
        return cases
    
    def create_confirmation_bias_cases(self) -> List[BiasTestCase]:
        """Test if evidence supporting popular theories gets inflated confidence"""
        
        cases = []
        
        # Case 1: Popular vs unpopular theory support
        case1 = BiasTestCase(
            test_id="confirmation_001",
            bias_type="confirmation_bias",
            description="Evidence supporting popular vs unpopular scientific theory",
            control_text="""
            A study provides evidence against the widely accepted theory that dark matter
            consists of weakly interacting massive particles (WIMPs). The analysis of
            cosmic ray data (N=10,000 events) shows patterns inconsistent with WIMP models
            (p=0.01). Three independent analysis teams reached similar conclusions.
            """,
            control_claim="Dark matter may not consist of WIMPs as commonly believed",
            control_context={"theory_popularity": 0.1, "contradicts_consensus": True},
            test_text="""
            A study provides evidence supporting the widely accepted theory that dark matter
            consists of weakly interacting massive particles (WIMPs). The analysis of
            cosmic ray data (N=10,000 events) shows patterns consistent with WIMP models
            (p=0.01). Three independent analysis teams reached similar conclusions.
            """,
            test_claim="Dark matter likely consists of WIMPs as commonly believed",
            test_context={"theory_popularity": 0.9, "contradicts_consensus": False},
            expected_relationship="equal",  # Same evidence quality regardless of popularity
            bias_magnitude_threshold=0.07,
            difficulty="subtle",
            created_date=datetime.now()
        )
        cases.append(case1)
        
        return cases
    
    def create_sample_size_bias_cases(self) -> List[BiasTestCase]:
        """Test if larger sample sizes get disproportionately higher confidence"""
        
        cases = []
        
        # Case 1: Large vs small sample with same effect size and methodology
        case1 = BiasTestCase(
            test_id="sample_size_001",
            bias_type="sample_size_bias",
            description="Same effect size and methodology, different sample sizes",
            control_text="""
            A small but well-designed study (N=45) examined meditation effects on stress.
            Using validated stress measures and randomized design, researchers found 
            20% reduction in stress scores (Cohen's d=0.8, p=0.02). Effect size is large
            and methodology is rigorous despite small sample.
            """,
            control_claim="Meditation significantly reduces stress levels",
            control_context={"sample_size": 45, "effect_size": 0.8, "p_value": 0.02},
            test_text="""
            A large study (N=2000) examined meditation effects on stress.
            Using validated stress measures and randomized design, researchers found 
            20% reduction in stress scores (Cohen's d=0.8, p<0.001). Effect size is large
            and methodology is rigorous with large sample.
            """,
            test_claim="Meditation significantly reduces stress levels",
            test_context={"sample_size": 2000, "effect_size": 0.8, "p_value": 0.001},
            expected_relationship="test_higher",  # Larger sample should increase confidence, but not excessively
            bias_magnitude_threshold=0.15,  # More than 15% difference suggests over-weighting
            difficulty="moderate",
            created_date=datetime.now()
        )
        cases.append(case1)
        
        return cases
    
    def create_complexity_bias_cases(self) -> List[BiasTestCase]:
        """Test if more complex/technical language affects confidence assessment"""
        
        cases = []
        
        # Case 1: Simple vs technical language for same finding
        case1 = BiasTestCase(
            test_id="complexity_001",
            bias_type="complexity_bias",
            description="Same research finding described in simple vs technical language",
            control_text="""
            Researchers studied how a new drug affects blood pressure. They gave the drug 
            to 100 patients and a fake pill to 100 other patients. Neither the patients 
            nor doctors knew who got which treatment. After 3 months, patients who got 
            the real drug had blood pressure that was 15 points lower on average. 
            This difference was statistically significant (p=0.003).
            """,
            control_claim="New drug significantly reduces blood pressure",
            control_context={"language_complexity": "simple", "readability_score": 8.5},
            test_text="""
            Investigators conducted a double-blind, placebo-controlled, randomized clinical trial
            examining the antihypertensive efficacy of a novel ACE inhibitor. The study cohort
            comprised 200 subjects randomized to active treatment (n=100) or placebo (n=100).
            Primary endpoint analysis revealed a statistically significant reduction in systolic
            blood pressure of 15 mmHg (95% CI: 6-24 mmHg, p=0.003) favoring active treatment.
            """,
            test_claim="New drug significantly reduces blood pressure",
            test_context={"language_complexity": "technical", "readability_score": 3.2},
            expected_relationship="equal",  # Same evidence should get same confidence regardless of language
            bias_magnitude_threshold=0.06,
            difficulty="subtle",
            created_date=datetime.now()
        )
        cases.append(case1)
        
        return cases
    
    def create_gender_bias_cases(self) -> List[BiasTestCase]:
        """Test if researcher gender affects confidence assessment"""
        
        cases = []
        
        # Case 1: Male vs female lead researcher
        case1 = BiasTestCase(
            test_id="gender_001",
            bias_type="gender_bias",
            description="Same research with male vs female lead author",
            control_text="""
            Dr. Sarah Johnson and colleagues investigated the efficacy of a new teaching method.
            The randomized controlled study (N=240 students) found that students using the new
            method scored 18% higher on standardized tests (p=0.006). The study controlled for
            prior achievement, socioeconomic status, and teacher experience. Results were
            replicated at 3 independent schools.
            """,
            control_claim="New teaching method significantly improves student performance",
            control_context={"lead_author_gender": "female", "author_name": "Dr. Sarah Johnson"},
            test_text="""
            Dr. Michael Johnson and colleagues investigated the efficacy of a new teaching method.
            The randomized controlled study (N=240 students) found that students using the new
            method scored 18% higher on standardized tests (p=0.006). The study controlled for
            prior achievement, socioeconomic status, and teacher experience. Results were
            replicated at 3 independent schools.
            """,
            test_claim="New teaching method significantly improves student performance",
            test_context={"lead_author_gender": "male", "author_name": "Dr. Michael Johnson"},
            expected_relationship="equal",  # Gender should not affect confidence in identical research
            bias_magnitude_threshold=0.04,
            difficulty="subtle",
            created_date=datetime.now()
        )
        cases.append(case1)
        
        return cases
    
    def generate_all_bias_test_cases(self) -> List[BiasTestCase]:
        """Generate complete set of bias test cases"""
        
        all_cases = []
        all_cases.extend(self.create_source_prestige_bias_cases())
        all_cases.extend(self.create_recency_bias_cases())
        all_cases.extend(self.create_domain_bias_cases())
        all_cases.extend(self.create_confirmation_bias_cases())
        all_cases.extend(self.create_sample_size_bias_cases())
        all_cases.extend(self.create_complexity_bias_cases())
        all_cases.extend(self.create_gender_bias_cases())
        
        self.bias_test_cases = all_cases
        return all_cases
    
    async def test_single_bias_case(self, case: BiasTestCase) -> BiasTestResult:
        """Test for bias in a single case comparison"""
        
        if not self.api_key:
            raise ValueError("API key required for bias testing")
        
        start_time = datetime.now()
        
        try:
            # Assess confidence for control case
            control_confidence_score = await self.uncertainty_engine.assess_initial_confidence(
                case.control_text, case.control_claim, "bias_test"
            )
            control_confidence = control_confidence_score.get_overall_confidence()
            
            # Assess confidence for test case  
            test_confidence_score = await self.uncertainty_engine.assess_initial_confidence(
                case.test_text, case.test_claim, "bias_test"
            )
            test_confidence = test_confidence_score.get_overall_confidence()
            
            # Calculate difference
            confidence_difference = test_confidence - control_confidence
            abs_difference = abs(confidence_difference)
            
            # Determine if bias detected
            bias_detected = abs_difference > case.bias_magnitude_threshold
            
            # Determine bias direction
            if not bias_detected:
                bias_direction = "none"
            elif confidence_difference > 0:
                bias_direction = "favors_test"
            else:
                bias_direction = "favors_control"
            
            # Determine bias magnitude
            if abs_difference < 0.03:
                bias_magnitude = "none"
            elif abs_difference < 0.08:
                bias_magnitude = "small"
            elif abs_difference < 0.15:
                bias_magnitude = "moderate"
            else:
                bias_magnitude = "large"
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = BiasTestResult(
                test_id=case.test_id,
                bias_type=case.bias_type,
                control_confidence=control_confidence,
                test_confidence=test_confidence,
                confidence_difference=confidence_difference,
                bias_detected=bias_detected,
                bias_direction=bias_direction,
                bias_magnitude=bias_magnitude,
                statistical_significance=None,  # Would need multiple runs for p-value
                control_details=control_confidence_score.to_dict(),
                test_details=test_confidence_score.to_dict(),
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return BiasTestResult(
                test_id=case.test_id,
                bias_type=case.bias_type,
                control_confidence=0.0,
                test_confidence=0.0,
                confidence_difference=0.0,
                bias_detected=False,
                bias_direction="error",
                bias_magnitude="error",
                statistical_significance=None,
                control_details={},
                test_details={},
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def run_comprehensive_bias_analysis(self) -> Dict[str, Any]:
        """Run complete bias analysis across all test cases"""
        
        print("🔍 Starting Comprehensive Bias Analysis")
        print("=" * 50)
        
        # Generate test cases if not already done
        if not self.bias_test_cases:
            self.generate_all_bias_test_cases()
        
        bias_results = []
        bias_summary = {}
        
        for i, case in enumerate(self.bias_test_cases):
            print(f"Testing bias case {i+1}/{len(self.bias_test_cases)}: {case.test_id} ({case.bias_type})")
            
            if self.api_key:
                result = await self.test_single_bias_case(case)
                bias_results.append(result)
                
                # Organize results by bias type
                if case.bias_type not in bias_summary:
                    bias_summary[case.bias_type] = []
                bias_summary[case.bias_type].append(result)
                
                status = "⚠️ BIAS" if result.bias_detected else "✅ OK"
                print(f"  {status} Control: {result.control_confidence:.3f}, Test: {result.test_confidence:.3f}, Diff: {result.confidence_difference:+.3f}")
            else:
                print("  ⏭️  Skipped (no API key)")
        
        self.bias_results = bias_results
        
        # Calculate summary statistics
        if bias_results:
            # Overall statistics
            total_cases = len(bias_results)
            biased_cases = sum(1 for r in bias_results if r.bias_detected)
            bias_rate = biased_cases / total_cases
            
            mean_abs_difference = np.mean([abs(r.confidence_difference) for r in bias_results])
            max_bias = max([abs(r.confidence_difference) for r in bias_results])
            
            # By bias type
            bias_type_summary = {}
            for bias_type, results in bias_summary.items():
                type_biased = sum(1 for r in results if r.bias_detected)
                type_total = len(results)
                
                bias_type_summary[bias_type] = {
                    'total_cases': type_total,
                    'biased_cases': type_biased,
                    'bias_rate': type_biased / type_total if type_total > 0 else 0,
                    'mean_abs_difference': np.mean([abs(r.confidence_difference) for r in results]),
                    'results': [r.to_dict() for r in results]
                }
            
            summary = {
                'total_cases': total_cases,
                'biased_cases': biased_cases,
                'overall_bias_rate': bias_rate,
                'mean_absolute_difference': mean_abs_difference,
                'maximum_bias': max_bias,
                'bias_by_type': bias_type_summary,
                'all_results': [r.to_dict() for r in bias_results],
                'test_cases': [c.to_dict() for c in self.bias_test_cases]
            }
        else:
            summary = {
                'total_cases': len(self.bias_test_cases),
                'biased_cases': 0,
                'overall_bias_rate': 0.0,
                'message': 'No bias testing run - missing API key',
                'test_cases': [c.to_dict() for c in self.bias_test_cases]
            }
        
        return summary
    
    def generate_bias_report(self, summary: Dict[str, Any]) -> str:
        """Generate comprehensive bias analysis report"""
        
        if 'all_results' not in summary:
            return "Bias test cases created but not executed (API key required)."
        
        report = f"""# Comprehensive Bias Analysis Report

## Executive Summary
- **Total Test Cases**: {summary['total_cases']}
- **Cases with Detected Bias**: {summary['biased_cases']} ({summary['overall_bias_rate']:.1%})
- **Mean Absolute Difference**: {summary['mean_absolute_difference']:.3f}
- **Maximum Bias Detected**: {summary['maximum_bias']:.3f}

## Bias Analysis by Type

"""
        
        for bias_type, type_data in summary['bias_by_type'].items():
            bias_emoji = "🔴" if type_data['bias_rate'] > 0.3 else "🟡" if type_data['bias_rate'] > 0.1 else "🟢"
            
            report += f"""### {bias_type.replace('_', ' ').title()} {bias_emoji}
- **Cases Tested**: {type_data['total_cases']}
- **Bias Detected**: {type_data['biased_cases']}/{type_data['total_cases']} ({type_data['bias_rate']:.1%})
- **Mean Difference**: {type_data['mean_abs_difference']:.3f}

"""
            
            # Detail each case
            for result_dict in type_data['results']:
                result = BiasTestResult(**{k: v for k, v in result_dict.items() if k not in ['control_details', 'test_details']})
                
                bias_status = "⚠️ BIAS" if result.bias_detected else "✅ OK"
                magnitude = result.bias_magnitude.upper() if result.bias_detected else ""
                
                report += f"""#### {result.test_id} {bias_status} {magnitude}
- **Control Confidence**: {result.control_confidence:.3f}
- **Test Confidence**: {result.test_confidence:.3f} 
- **Difference**: {result.confidence_difference:+.3f}
- **Direction**: {result.bias_direction.replace('_', ' ').title()}

"""
        
        # Overall assessment
        overall_bias_rate = summary['overall_bias_rate']
        
        if overall_bias_rate == 0:
            assessment = "✅ **EXCELLENT** - No systematic biases detected"
        elif overall_bias_rate < 0.15:
            assessment = "🟡 **ACCEPTABLE** - Minor biases detected, monitoring recommended"
        elif overall_bias_rate < 0.30:
            assessment = "🟠 **CONCERNING** - Significant biases detected, mitigation needed"
        else:
            assessment = "🔴 **CRITICAL** - Severe biases detected, system not suitable for deployment"
        
        report += f"""
## Overall Assessment

{assessment}

### Key Findings
"""
        
        # Identify most problematic bias types
        problematic_types = [
            bias_type for bias_type, data in summary['bias_by_type'].items() 
            if data['bias_rate'] > 0.2
        ]
        
        if problematic_types:
            report += f"- **High-Risk Bias Types**: {', '.join(problematic_types)}\n"
        
        if summary['maximum_bias'] > 0.15:
            report += f"- **Maximum Bias**: {summary['maximum_bias']:.3f} (concerning level)\n"
        
        if overall_bias_rate < 0.10:
            report += "- **Low Overall Bias Rate**: System shows good resistance to systematic biases\n"
        
        # Recommendations
        report += "\n### Recommendations\n"
        
        if overall_bias_rate == 0:
            report += "- Continue monitoring for biases as system scales\n"
            report += "- Consider expanding bias test cases to cover additional scenarios\n"
        elif overall_bias_rate < 0.15:
            report += "- Implement bias monitoring in production\n"
            report += "- Consider bias correction mechanisms for identified issues\n"
        else:
            report += "- **URGENT**: Implement bias mitigation before deployment\n"
            report += "- Investigate root causes of detected biases\n"
            report += "- Consider algorithmic bias correction methods\n"
        
        return report
    
    def generate_bias_mitigation_strategies(self, summary: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate specific bias mitigation strategies based on detected biases"""
        
        mitigation_strategies = {}
        
        if 'bias_by_type' not in summary:
            return mitigation_strategies
        
        for bias_type, data in summary['bias_by_type'].items():
            if data['bias_rate'] > 0.1:  # Only generate strategies for problematic bias types
                
                if bias_type == "source_prestige":
                    mitigation_strategies[bias_type] = [
                        "Implement source anonymization during assessment",
                        "Add explicit prestige penalty for over-prestigious sources",
                        "Train assessment with institution names removed",
                        "Use ensemble of assessments with different source attributions"
                    ]
                
                elif bias_type == "recency_bias":
                    mitigation_strategies[bias_type] = [
                        "Adjust temporal decay parameters based on field stability",
                        "Implement recency bias correction factor",
                        "Consider publication date during assessment training",
                        "Use citation velocity rather than raw recency"
                    ]
                
                elif bias_type == "domain_bias":
                    mitigation_strategies[bias_type] = [
                        "Implement domain-specific confidence calibration",
                        "Train separate models for different academic domains",
                        "Apply domain normalization to confidence scores",
                        "Use domain-blind assessment when possible"
                    ]
                
                elif bias_type == "confirmation_bias":
                    mitigation_strategies[bias_type] = [
                        "Implement contrarian evidence weighting",
                        "Add explicit penalty for popular theory support",
                        "Use theoretical diversity metrics in assessment",
                        "Train with deliberately controversial claims"
                    ]
                
                elif bias_type == "gender_bias":
                    mitigation_strategies[bias_type] = [
                        "Remove author names during assessment",
                        "Implement gender-blind evaluation protocols",
                        "Monitor for systematic gender disparities",
                        "Use pronoun-neutral language in training data"
                    ]
                
                elif bias_type == "complexity_bias":
                    mitigation_strategies[bias_type] = [
                        "Normalize language complexity before assessment",
                        "Train with simplified and technical versions of same content",
                        "Implement readability score normalization",
                        "Focus assessment on methodology rather than presentation"
                    ]
        
        return mitigation_strategies

# Test execution
async def main():
    """Run comprehensive bias analysis"""
    
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    
    analyzer = BiasAnalyzer(api_key)
    
    # Run bias analysis
    summary = await analyzer.run_comprehensive_bias_analysis()
    
    # Generate report
    report = analyzer.generate_bias_report(summary)
    
    # Generate mitigation strategies
    mitigation = analyzer.generate_bias_mitigation_strategies(summary)
    
    # Save results
    output_dir = Path("/home/brian/projects/Digimons/uncertainty_stress_test/validation")
    
    # Save summary
    with open(output_dir / "bias_analysis_results.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    # Save report
    with open(output_dir / "bias_analysis_report.md", "w") as f:
        f.write(report)
    
    # Save mitigation strategies
    with open(output_dir / "bias_mitigation_strategies.json", "w") as f:
        json.dump(mitigation, f, indent=2)
    
    print("\n" + "=" * 50)
    print("🔍 BIAS ANALYSIS SUMMARY")
    print("=" * 50)
    
    if 'all_results' in summary:
        print(f"Overall Bias Rate: {summary['overall_bias_rate']:.1%}")
        print(f"Cases with Bias: {summary['biased_cases']}/{summary['total_cases']}")
        print(f"Mean Absolute Difference: {summary['mean_absolute_difference']:.3f}")
        
        # Show most problematic bias types
        problematic = [
            (bias_type, data['bias_rate']) 
            for bias_type, data in summary['bias_by_type'].items() 
            if data['bias_rate'] > 0.1
        ]
        
        if problematic:
            print(f"\nProblematic Bias Types:")
            for bias_type, rate in sorted(problematic, key=lambda x: x[1], reverse=True):
                print(f"  - {bias_type}: {rate:.1%}")
    else:
        print(f"Bias test cases created: {summary['total_cases']}")
        print("Run with API key to execute bias testing")
    
    print(f"\nResults saved to: {output_dir}")
    
    return summary

if __name__ == "__main__":
    asyncio.run(main())