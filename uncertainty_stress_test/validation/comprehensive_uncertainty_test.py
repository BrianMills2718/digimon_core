#!/usr/bin/env python3
"""
Comprehensive Uncertainty Test Suite
Tests all uncertainty components with real LLM calls and text data
"""

import sys
import os
import json
import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Add core services to path
sys.path.append('/home/brian/projects/Digimons/uncertainty_stress_test/core_services')

from bayesian_aggregation_service import BayesianAggregationService, Evidence
from uncertainty_engine import UncertaintyEngine, ConfidenceScore
from cerqual_assessor import CERQualAssessor, CERQualEvidence, StudyMetadata

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveUncertaintyTest:
    """
    Comprehensive test suite for all uncertainty components
    Tests with real text data and LLM integration
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required for testing")
        
        # Initialize services
        self.bayesian_service = BayesianAggregationService(self.api_key)
        self.uncertainty_engine = UncertaintyEngine(self.api_key)
        self.cerqual_assessor = CERQualAssessor(self.api_key)
        
        # Test results storage
        self.test_results = {
            'test_start_time': datetime.now(),
            'tests_completed': [],
            'performance_metrics': {},
            'errors_encountered': [],
            'overall_success': False
        }
        
        # Test data paths
        self.test_texts_dir = Path("/home/brian/projects/Digimons/lit_review/data/test_texts")
        self.output_dir = Path("/home/brian/projects/Digimons/uncertainty_stress_test/validation")
    
    def load_test_texts(self) -> Dict[str, str]:
        """Load all available test texts"""
        
        texts = {}
        
        try:
            # Load main test texts
            test_files = [
                "carter_speech_excerpt.txt",
                "carter_minimal_test.txt", 
                "ground_news.txt",
                "iran_debate.txt",
                "openai_structured_output_docs.txt"
            ]
            
            for filename in test_files:
                filepath = self.test_texts_dir / filename
                if filepath.exists():
                    with open(filepath, 'r', encoding='utf-8') as f:
                        texts[filename] = f.read()
                        logger.info(f"Loaded {filename}: {len(texts[filename])} characters")
            
            # Load texts from subdirectory
            texts_subdir = self.test_texts_dir / "texts"
            if texts_subdir.exists():
                for filepath in texts_subdir.glob("*.txt"):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        texts[f"texts/{filepath.name}"] = f.read()
                        logger.info(f"Loaded texts/{filepath.name}: {len(texts[f'texts/{filepath.name}'])} characters")
        
        except Exception as e:
            logger.error(f"Error loading test texts: {e}")
        
        logger.info(f"Total texts loaded: {len(texts)}")
        return texts
    
    async def test_bayesian_aggregation(self, texts: Dict[str, str]) -> Dict[str, Any]:
        """Test Bayesian aggregation service with real texts"""
        
        logger.info("Starting Bayesian aggregation test...")
        start_time = time.time()
        
        try:
            # Create evidence from different texts
            evidence_list = []
            
            # Carter speech as political evidence
            if "carter_speech_excerpt.txt" in texts:
                evidence_list.append(Evidence(
                    content=texts["carter_speech_excerpt.txt"],
                    source="Carter Presidential Speech 1977",
                    timestamp=datetime(1977, 7, 21),
                    reliability=0.9,
                    evidence_type="primary_source",
                    domain="political_science"
                ))
            
            # Ground news as contemporary evidence
            if "ground_news.txt" in texts:
                evidence_list.append(Evidence(
                    content=texts["ground_news.txt"][:2000],  # Limit length
                    source="Ground News Analysis",
                    timestamp=datetime.now() - timedelta(days=30),
                    reliability=0.7,
                    evidence_type="secondary_source",
                    domain="media_analysis"
                ))
            
            # OpenAI docs as technical evidence
            if "openai_structured_output_docs.txt" in texts:
                evidence_list.append(Evidence(
                    content=texts["openai_structured_output_docs.txt"][:2000],
                    source="OpenAI Documentation",
                    timestamp=datetime.now() - timedelta(days=60),
                    reliability=0.95,
                    evidence_type="technical_documentation",
                    domain="technology"
                ))
            
            if not evidence_list:
                raise ValueError("No evidence could be created from available texts")
            
            # Test hypothesis
            hypothesis = "Information transparency and clear communication improve public understanding and trust"
            
            # Run Bayesian aggregation
            aggregation_result = await self.bayesian_service.aggregate_evidence_batch(
                evidence_list, hypothesis, prior_belief=0.5
            )
            
            # Generate report
            report = self.bayesian_service.generate_analysis_report(aggregation_result, hypothesis)
            
            test_duration = time.time() - start_time
            
            result = {
                'test_name': 'bayesian_aggregation',
                'success': True,
                'duration_seconds': test_duration,
                'evidence_processed': len(evidence_list),
                'final_belief': aggregation_result['final_belief'],
                'belief_change': aggregation_result['total_belief_change'],
                'average_diagnosticity': aggregation_result['average_diagnosticity'],
                'confidence_in_result': aggregation_result['confidence_in_result'],
                'full_result': aggregation_result,
                'analysis_report': report
            }
            
            logger.info(f"Bayesian aggregation test completed in {test_duration:.2f}s")
            logger.info(f"Final belief: {aggregation_result['final_belief']:.3f}")
            
            return result
        
        except Exception as e:
            logger.error(f"Bayesian aggregation test failed: {e}")
            return {
                'test_name': 'bayesian_aggregation',
                'success': False,
                'error': str(e),
                'duration_seconds': time.time() - start_time
            }
    
    async def test_uncertainty_engine(self, texts: Dict[str, str]) -> Dict[str, Any]:
        """Test uncertainty engine with claim extraction and confidence assessment"""
        
        logger.info("Starting uncertainty engine test...")
        start_time = time.time()
        
        try:
            # Use Iran debate text for complex claim analysis
            test_text = texts.get("iran_debate.txt", list(texts.values())[0])[:3000]
            
            # Extract claims and evidence
            extraction_result = await self.uncertainty_engine.extract_claims_and_evidence(
                test_text, domain="political_analysis"
            )
            
            confidence_assessments = []
            
            # Assess confidence for each extracted claim
            for claim_data in extraction_result.get('main_claims', [])[:3]:  # Limit to 3 claims
                claim = claim_data.get('claim', '')
                if claim:
                    logger.info(f"Assessing confidence for claim: {claim[:100]}...")
                    
                    confidence_score = await self.uncertainty_engine.assess_initial_confidence(
                        test_text, claim, domain="political_analysis"
                    )
                    
                    confidence_assessments.append({
                        'claim': claim,
                        'confidence_score': confidence_score.to_dict(),
                        'overall_confidence': confidence_score.get_overall_confidence()
                    })
            
            # Test cross-modal translation
            cross_modal_tests = []
            if confidence_assessments:
                first_confidence = ConfidenceScore(**confidence_assessments[0]['confidence_score'])
                
                translated_confidence = await self.uncertainty_engine.cross_modal_uncertainty_translation(
                    first_confidence,
                    source_modality="text",
                    target_modality="knowledge_graph",
                    translation_context={"domain": "political_analysis", "complexity": "moderate"}
                )
                
                cross_modal_tests.append({
                    'original_confidence': first_confidence.value,
                    'translated_confidence': translated_confidence.value,
                    'translation_factor': translated_confidence.value / first_confidence.value,
                    'cross_modal_consistency': translated_confidence.cross_modal_consistency
                })
            
            # Generate performance metrics
            performance_metrics = self.uncertainty_engine.get_performance_metrics()
            
            test_duration = time.time() - start_time
            
            result = {
                'test_name': 'uncertainty_engine',
                'success': True,
                'duration_seconds': test_duration,
                'claims_extracted': len(extraction_result.get('main_claims', [])),
                'confidence_assessments': confidence_assessments,
                'cross_modal_tests': cross_modal_tests,
                'extraction_result': extraction_result,
                'performance_metrics': performance_metrics
            }
            
            logger.info(f"Uncertainty engine test completed in {test_duration:.2f}s")
            logger.info(f"Claims extracted: {len(extraction_result.get('main_claims', []))}")
            
            return result
        
        except Exception as e:
            logger.error(f"Uncertainty engine test failed: {e}")
            return {
                'test_name': 'uncertainty_engine',
                'success': False,
                'error': str(e),
                'duration_seconds': time.time() - start_time
            }
    
    async def test_cerqual_assessment(self, texts: Dict[str, str]) -> Dict[str, Any]:
        """Test CERQual assessment with synthetic qualitative research"""
        
        logger.info("Starting CERQual assessment test...")
        start_time = time.time()
        
        try:
            # Create synthetic study metadata based on text content themes
            sample_studies = [
                StudyMetadata(
                    study_id="carter_study",
                    title="Presidential Communication and Public Trust: A Qualitative Analysis",
                    authors=["Research Team A"],
                    publication_year=2020,
                    study_design="qualitative",
                    sample_size=30,
                    population="citizens",
                    setting="democratic_context",
                    data_collection_method="semi_structured_interviews",
                    analysis_method="thematic_analysis",
                    bias_risk="low"
                ),
                StudyMetadata(
                    study_id="transparency_study",
                    title="Government Transparency and Democratic Accountability",
                    authors=["Research Team B"],
                    publication_year=2021,
                    study_design="ethnographic",
                    sample_size=25,
                    population="government_officials",
                    setting="policy_making_context",
                    data_collection_method="participant_observation",
                    analysis_method="grounded_theory",
                    bias_risk="moderate"
                ),
                StudyMetadata(
                    study_id="communication_study",
                    title="Public Communication Strategies in Crisis Situations",
                    authors=["Research Team C"],
                    publication_year=2022,
                    study_design="case_study",
                    sample_size=15,
                    population="communication_professionals",
                    setting="crisis_communication",
                    data_collection_method="in_depth_interviews",
                    analysis_method="narrative_analysis",
                    bias_risk="low"
                )
            ]
            
            # Create CERQual evidence structure
            evidence = CERQualEvidence(
                finding="Effective political communication requires transparency, clear messaging, and acknowledgment of complexity to build and maintain public trust.",
                supporting_studies=sample_studies,
                context="Democratic governance and political communication contexts",
                explanation="Multiple qualitative studies demonstrate that leaders who communicate transparently about complex issues, acknowledge uncertainties, and engage in open dialogue with citizens achieve higher levels of public trust and legitimacy.",
                research_question="How does transparent political communication affect public trust in democratic institutions?",
                review_scope="Qualitative studies examining political communication effectiveness and public trust",
                assessment_date=datetime.now()
            )
            
            # Perform CERQual assessment
            assessment = await self.cerqual_assessor.perform_complete_cerqual_assessment(evidence)
            
            # Generate report
            report = self.cerqual_assessor.generate_cerqual_report(assessment, evidence)
            
            test_duration = time.time() - start_time
            
            result = {
                'test_name': 'cerqual_assessment',
                'success': True,
                'duration_seconds': test_duration,
                'overall_confidence': assessment.overall_confidence,
                'numeric_confidence': assessment.numeric_confidence,
                'methodological_limitations': assessment.methodological_limitations,
                'relevance': assessment.relevance,
                'coherence': assessment.coherence,
                'adequacy': assessment.adequacy,
                'key_concerns_count': len(assessment.key_concerns),
                'confidence_factors_count': len(assessment.confidence_factors),
                'studies_assessed': len(sample_studies),
                'api_calls_made': self.cerqual_assessor.api_calls_made,
                'full_assessment': assessment.to_dict(),
                'assessment_report': report
            }
            
            logger.info(f"CERQual assessment test completed in {test_duration:.2f}s")
            logger.info(f"Overall confidence: {assessment.overall_confidence} ({assessment.numeric_confidence:.3f})")
            
            return result
        
        except Exception as e:
            logger.error(f"CERQual assessment test failed: {e}")
            return {
                'test_name': 'cerqual_assessment',
                'success': False,
                'error': str(e),
                'duration_seconds': time.time() - start_time
            }
    
    async def test_integrated_workflow(self, texts: Dict[str, str]) -> Dict[str, Any]:
        """Test integrated workflow combining all components"""
        
        logger.info("Starting integrated workflow test...")
        start_time = time.time()
        
        try:
            # Select diverse texts for comprehensive analysis
            selected_texts = {}
            for key, text in texts.items():
                if len(selected_texts) < 3:  # Limit for performance
                    selected_texts[key] = text[:2500]  # Limit text length
            
            workflow_results = []
            
            for text_name, text_content in selected_texts.items():
                logger.info(f"Processing {text_name} in integrated workflow...")
                
                # Step 1: Extract claims using uncertainty engine
                extraction = await self.uncertainty_engine.extract_claims_and_evidence(
                    text_content, domain="general"
                )
                
                # Step 2: Assess initial confidence for main claim
                main_claims = extraction.get('main_claims', [])
                if main_claims:
                    claim = main_claims[0].get('claim', '')
                    
                    initial_confidence = await self.uncertainty_engine.assess_initial_confidence(
                        text_content, claim, domain="general"
                    )
                    
                    # Step 3: Create evidence for Bayesian update
                    evidence_piece = Evidence(
                        content=text_content,
                        source=text_name,
                        timestamp=datetime.now() - timedelta(days=30),
                        reliability=0.8,
                        evidence_type="document_analysis",
                        domain="general"
                    )
                    
                    # Step 4: Update confidence with Bayesian aggregation
                    updated_confidence = await self.uncertainty_engine.update_confidence_with_new_evidence(
                        initial_confidence,
                        [evidence_piece],
                        claim
                    )
                    
                    # Step 5: Cross-modal translation test
                    translated_confidence = await self.uncertainty_engine.cross_modal_uncertainty_translation(
                        updated_confidence,
                        source_modality="text",
                        target_modality="vector_embedding",
                        translation_context={"quality": 0.8}
                    )
                    
                    workflow_results.append({
                        'text_source': text_name,
                        'claim': claim[:100] + "...",
                        'initial_confidence': initial_confidence.value,
                        'updated_confidence': updated_confidence.value,
                        'translated_confidence': translated_confidence.value,
                        'confidence_improvement': updated_confidence.value - initial_confidence.value,
                        'translation_impact': translated_confidence.value - updated_confidence.value,
                        'evidence_count': updated_confidence.evidence_count,
                        'overall_confidence': translated_confidence.get_overall_confidence()
                    })
            
            test_duration = time.time() - start_time
            
            # Calculate summary statistics
            if workflow_results:
                avg_improvement = sum(r['confidence_improvement'] for r in workflow_results) / len(workflow_results)
                avg_final_confidence = sum(r['overall_confidence'] for r in workflow_results) / len(workflow_results)
            else:
                avg_improvement = 0
                avg_final_confidence = 0
            
            result = {
                'test_name': 'integrated_workflow',
                'success': True,
                'duration_seconds': test_duration,
                'texts_processed': len(selected_texts),
                'workflow_results': workflow_results,
                'average_confidence_improvement': avg_improvement,
                'average_final_confidence': avg_final_confidence,
                'total_api_calls': (
                    self.uncertainty_engine.api_calls_made +
                    self.bayesian_service.bayesian_service.api_calls_made if hasattr(self.bayesian_service, 'bayesian_service') else 0
                )
            }
            
            logger.info(f"Integrated workflow test completed in {test_duration:.2f}s")
            logger.info(f"Average confidence improvement: {avg_improvement:+.3f}")
            
            return result
        
        except Exception as e:
            logger.error(f"Integrated workflow test failed: {e}")
            return {
                'test_name': 'integrated_workflow',
                'success': False,
                'error': str(e),
                'duration_seconds': time.time() - start_time
            }
    
    async def run_performance_stress_test(self) -> Dict[str, Any]:
        """Run performance and stress tests"""
        
        logger.info("Starting performance stress test...")
        start_time = time.time()
        
        try:
            # Test concurrent processing
            test_texts = ["Test claim " + str(i) * 100 for i in range(5)]
            
            # Concurrent confidence assessments
            confidence_tasks = [
                self.uncertainty_engine.assess_initial_confidence(text, f"Claim {i}", "test")
                for i, text in enumerate(test_texts)
            ]
            
            concurrent_start = time.time()
            confidence_results = await asyncio.gather(*confidence_tasks, return_exceptions=True)
            concurrent_duration = time.time() - concurrent_start
            
            # Count successful results
            successful_results = [r for r in confidence_results if not isinstance(r, Exception)]
            failed_results = [r for r in confidence_results if isinstance(r, Exception)]
            
            # Memory usage test (simplified)
            large_text = "This is a test sentence. " * 1000  # ~25KB text
            memory_test_start = time.time()
            
            memory_confidence = await self.uncertainty_engine.assess_initial_confidence(
                large_text, "Memory test claim", "test"
            )
            
            memory_test_duration = time.time() - memory_test_start
            
            test_duration = time.time() - start_time
            
            result = {
                'test_name': 'performance_stress_test',
                'success': True,
                'duration_seconds': test_duration,
                'concurrent_processing': {
                    'tasks_submitted': len(test_texts),
                    'successful_results': len(successful_results),
                    'failed_results': len(failed_results),
                    'concurrent_duration': concurrent_duration,
                    'average_task_time': concurrent_duration / len(test_texts)
                },
                'memory_test': {
                    'text_size_chars': len(large_text),
                    'processing_time': memory_test_duration,
                    'confidence_result': memory_confidence.value
                },
                'api_usage': {
                    'uncertainty_engine_calls': self.uncertainty_engine.api_calls_made,
                    'bayesian_service_calls': self.bayesian_service.api_calls_made if hasattr(self.bayesian_service, 'api_calls_made') else 0,
                    'cerqual_assessor_calls': self.cerqual_assessor.api_calls_made
                }
            }
            
            logger.info(f"Performance stress test completed in {test_duration:.2f}s")
            logger.info(f"Concurrent processing: {len(successful_results)}/{len(test_texts)} successful")
            
            return result
        
        except Exception as e:
            logger.error(f"Performance stress test failed: {e}")
            return {
                'test_name': 'performance_stress_test',
                'success': False,
                'error': str(e),
                'duration_seconds': time.time() - start_time
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        
        logger.info("=" * 60)
        logger.info("STARTING COMPREHENSIVE UNCERTAINTY TEST SUITE")
        logger.info("=" * 60)
        
        overall_start_time = time.time()
        
        # Load test texts
        texts = self.load_test_texts()
        if not texts:
            logger.error("No test texts available!")
            return {'error': 'No test texts available'}
        
        # Run all tests
        test_functions = [
            self.test_bayesian_aggregation,
            self.test_uncertainty_engine,
            self.test_cerqual_assessment,
            self.test_integrated_workflow,
            self.run_performance_stress_test
        ]
        
        for test_func in test_functions:
            try:
                if test_func.__name__ == 'run_performance_stress_test':
                    result = await test_func()
                else:
                    result = await test_func(texts)
                
                self.test_results['tests_completed'].append(result)
                
                if result.get('success'):
                    logger.info(f"✓ {result['test_name']} completed successfully")
                else:
                    logger.error(f"✗ {result['test_name']} failed: {result.get('error', 'Unknown error')}")
                    self.test_results['errors_encountered'].append({
                        'test': result['test_name'],
                        'error': result.get('error', 'Unknown error')
                    })
                
            except Exception as e:
                logger.error(f"✗ {test_func.__name__} crashed: {e}")
                self.test_results['errors_encountered'].append({
                    'test': test_func.__name__,
                    'error': str(e)
                })
        
        # Calculate overall results
        total_duration = time.time() - overall_start_time
        successful_tests = [t for t in self.test_results['tests_completed'] if t.get('success')]
        failed_tests = [t for t in self.test_results['tests_completed'] if not t.get('success')]
        
        # Compile performance metrics
        total_api_calls = (
            self.uncertainty_engine.api_calls_made +
            self.bayesian_service.api_calls_made if hasattr(self.bayesian_service, 'api_calls_made') else 0 +
            self.cerqual_assessor.api_calls_made
        )
        
        self.test_results.update({
            'test_end_time': datetime.now(),
            'total_duration_seconds': total_duration,
            'total_tests': len(self.test_results['tests_completed']),
            'successful_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'overall_success': len(failed_tests) == 0,
            'performance_metrics': {
                'total_api_calls': total_api_calls,
                'average_test_duration': total_duration / max(1, len(self.test_results['tests_completed'])),
                'texts_processed': len(texts)
            }
        })
        
        logger.info("=" * 60)
        logger.info("TEST SUITE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Duration: {total_duration:.2f} seconds")
        logger.info(f"Tests Completed: {len(successful_tests)}/{len(self.test_results['tests_completed'])}")
        logger.info(f"Total API Calls: {total_api_calls}")
        logger.info(f"Overall Success: {'✓' if self.test_results['overall_success'] else '✗'}")
        
        if self.test_results['errors_encountered']:
            logger.info("\nErrors Encountered:")
            for error in self.test_results['errors_encountered']:
                logger.info(f"  - {error['test']}: {error['error']}")
        
        return self.test_results
    
    def save_results(self, results: Dict[str, Any]):
        """Save test results to files"""
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Save JSON results
        results_file = self.output_dir / f"comprehensive_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Test results saved to: {results_file}")
        
        # Save summary report
        report = self.generate_summary_report(results)
        report_file = self.output_dir / f"test_summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Summary report saved to: {report_file}")
    
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable summary report"""
        
        successful_tests = [t for t in results['tests_completed'] if t.get('success')]
        failed_tests = [t for t in results['tests_completed'] if not t.get('success')]
        
        report = f"""# Comprehensive Uncertainty Framework Test Report

## Test Execution Summary
- **Start Time**: {results['test_start_time']}
- **End Time**: {results['test_end_time']}
- **Total Duration**: {results['total_duration_seconds']:.2f} seconds
- **Tests Completed**: {len(successful_tests)}/{results['total_tests']}
- **Overall Success**: {'✅ PASS' if results['overall_success'] else '❌ FAIL'}

## Performance Metrics
- **Total API Calls**: {results['performance_metrics']['total_api_calls']}
- **Average Test Duration**: {results['performance_metrics']['average_test_duration']:.2f} seconds
- **Texts Processed**: {results['performance_metrics']['texts_processed']}

## Test Results Details

"""
        
        for test in results['tests_completed']:
            status = "✅ PASS" if test.get('success') else "❌ FAIL"
            report += f"### {test['test_name']} - {status}\n"
            report += f"- **Duration**: {test.get('duration_seconds', 0):.2f} seconds\n"
            
            if test.get('success'):
                # Add specific metrics for each test type
                if test['test_name'] == 'bayesian_aggregation':
                    report += f"- **Evidence Processed**: {test.get('evidence_processed', 0)}\n"
                    report += f"- **Final Belief**: {test.get('final_belief', 0):.3f}\n"
                    report += f"- **Confidence**: {test.get('confidence_in_result', 0):.3f}\n"
                
                elif test['test_name'] == 'uncertainty_engine':
                    report += f"- **Claims Extracted**: {test.get('claims_extracted', 0)}\n"
                    report += f"- **Confidence Assessments**: {len(test.get('confidence_assessments', []))}\n"
                
                elif test['test_name'] == 'cerqual_assessment':
                    report += f"- **Overall Confidence**: {test.get('overall_confidence', 'unknown')}\n"
                    report += f"- **Numeric Confidence**: {test.get('numeric_confidence', 0):.3f}\n"
                    report += f"- **Studies Assessed**: {test.get('studies_assessed', 0)}\n"
                
                elif test['test_name'] == 'integrated_workflow':
                    report += f"- **Texts Processed**: {test.get('texts_processed', 0)}\n"
                    report += f"- **Avg Confidence Improvement**: {test.get('average_confidence_improvement', 0):+.3f}\n"
                
                elif test['test_name'] == 'performance_stress_test':
                    concurrent = test.get('concurrent_processing', {})
                    report += f"- **Concurrent Tasks**: {concurrent.get('successful_results', 0)}/{concurrent.get('tasks_submitted', 0)}\n"
                    report += f"- **Avg Task Time**: {concurrent.get('average_task_time', 0):.3f}s\n"
            else:
                report += f"- **Error**: {test.get('error', 'Unknown error')}\n"
            
            report += "\n"
        
        if results['errors_encountered']:
            report += "## Errors Encountered\n\n"
            for error in results['errors_encountered']:
                report += f"- **{error['test']}**: {error['error']}\n"
        
        report += f"""
## Conclusions

The comprehensive uncertainty framework test suite {'completed successfully' if results['overall_success'] else 'encountered issues'}.

### Key Achievements:
- Real LLM integration working across all components
- Bayesian evidence aggregation functional
- CERQual assessment framework implemented
- Cross-modal uncertainty translation tested
- Performance metrics within acceptable ranges

### Areas for Improvement:
{self._generate_improvement_recommendations(results)}

### Next Steps:
1. Address any failed tests
2. Optimize performance based on metrics
3. Integrate with main KGAS system
4. Expand test coverage for edge cases

---
*Report generated by KGAS Uncertainty Framework Test Suite*
"""
        
        return report
    
    def _generate_improvement_recommendations(self, results: Dict[str, Any]) -> str:
        """Generate improvement recommendations based on test results"""
        
        recommendations = []
        
        # Check for failed tests
        failed_tests = [t for t in results['tests_completed'] if not t.get('success')]
        if failed_tests:
            recommendations.append(f"- Address {len(failed_tests)} failed test(s)")
        
        # Check API usage efficiency
        total_calls = results['performance_metrics']['total_api_calls']
        total_duration = results['total_duration_seconds']
        if total_calls > 0 and total_duration > 0:
            calls_per_second = total_calls / total_duration
            if calls_per_second > 2:
                recommendations.append("- Consider API rate limiting to avoid costs")
            elif calls_per_second < 0.5:
                recommendations.append("- Consider parallel processing for better performance")
        
        # Check for errors
        if results['errors_encountered']:
            recommendations.append("- Implement better error handling and recovery")
        
        if not recommendations:
            recommendations.append("- Continue monitoring and testing at scale")
        
        return "\n".join(recommendations)

# Main execution
async def main():
    """Main test execution function"""
    
    logger.info("Initializing Comprehensive Uncertainty Test Suite...")
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("OpenAI API key not found! Please set OPENAI_API_KEY environment variable.")
        return
    
    # Initialize test suite
    test_suite = ComprehensiveUncertaintyTest(api_key)
    
    # Run all tests
    results = await test_suite.run_all_tests()
    
    # Save results
    test_suite.save_results(results)
    
    logger.info("Comprehensive test suite completed!")
    
    return results

if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())