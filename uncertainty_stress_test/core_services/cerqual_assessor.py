#!/usr/bin/env python3
"""
CERQual Assessor - Formal implementation of CERQual framework
Uses real LLM analysis to assess Confidence in Evidence from Reviews
"""

import json
import numpy as np
import asyncio
import aiohttp
import os
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StudyMetadata:
    """Metadata for individual studies in CERQual assessment"""
    
    study_id: str
    title: str
    authors: List[str]
    publication_year: int
    study_design: str  # 'qualitative', 'mixed_methods', 'systematic_review', etc.
    sample_size: Optional[int] = None
    population: str = "not_specified"
    setting: str = "not_specified"
    data_collection_method: str = "not_specified"
    analysis_method: str = "not_specified"
    bias_risk: str = "moderate"  # 'low', 'moderate', 'high'
    funding_source: str = "not_specified"
    conflicts_of_interest: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class CERQualEvidence:
    """Evidence structure for CERQual assessment"""
    
    finding: str  # The qualitative finding or theme
    supporting_studies: List[StudyMetadata]
    context: str  # Context in which the finding applies
    explanation: str  # Detailed explanation of the finding
    
    # Assessment context
    research_question: str
    review_scope: str
    assessment_date: datetime
    
    def to_dict(self) -> Dict:
        result = {
            "finding": self.finding,
            "supporting_studies": [study.to_dict() for study in self.supporting_studies],
            "context": self.context,
            "explanation": self.explanation,
            "research_question": self.research_question,
            "review_scope": self.review_scope,
            "assessment_date": self.assessment_date.isoformat()
        }
        return result

@dataclass
class CERQualAssessment:
    """Complete CERQual assessment result"""
    
    # Dimension scores (0-1)
    methodological_limitations: float
    relevance: float
    coherence: float
    adequacy: float
    
    # Overall confidence
    overall_confidence: str  # 'high', 'moderate', 'low', 'very_low'
    numeric_confidence: float  # 0-1
    
    # Detailed assessments
    dimension_details: Dict[str, Any]
    assessment_reasoning: str
    key_concerns: List[str]
    confidence_factors: List[str]
    
    # Metadata
    assessment_date: datetime
    assessor_info: str
    evidence_summary: str
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['assessment_date'] = self.assessment_date.isoformat()
        return result

class CERQualAssessor:
    """
    Formal CERQual (Confidence in Evidence from Reviews of Qualitative research) implementation
    Uses real LLM analysis to perform systematic quality assessment
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        self.assessment_history = []
        self.api_base = "https://api.openai.com/v1"
        self.api_calls_made = 0
        
        # CERQual dimension weights (can be adjusted based on review context)
        self.dimension_weights = {
            'methodological_limitations': 0.3,
            'relevance': 0.25,
            'coherence': 0.25,
            'adequacy': 0.2
        }
    
    async def _make_llm_call(self, prompt: str, max_tokens: int = 1000) -> str:
        """Make LLM API call"""
        self.api_calls_made += 1
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base}/chat/completions", 
                                      headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"API call failed: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"LLM API call error: {e}")
            return ""
    
    async def assess_methodological_limitations(self, evidence: CERQualEvidence) -> Dict[str, Any]:
        """Assess methodological limitations dimension"""
        
        studies_summary = self._create_studies_summary(evidence.supporting_studies)
        
        prompt = f"""
        Assess the METHODOLOGICAL LIMITATIONS for this qualitative evidence synthesis.
        
        EVIDENCE FINDING:
        {evidence.finding}
        
        RESEARCH QUESTION:
        {evidence.research_question}
        
        SUPPORTING STUDIES SUMMARY:
        {studies_summary}
        
        Assess methodological limitations using CERQual criteria. Provide JSON response:
        {{
            "overall_score": 0.0-1.0,
            "study_design_quality": 0.0-1.0,
            "data_collection_rigor": 0.0-1.0,
            "analysis_appropriateness": 0.0-1.0,
            "researcher_reflexivity": 0.0-1.0,
            "bias_risk_assessment": 0.0-1.0,
            "reporting_quality": 0.0-1.0,
            "ethical_considerations": 0.0-1.0,
            "major_limitations": [
                {{
                    "limitation": "specific limitation",
                    "severity": "minor|moderate|serious",
                    "affected_studies": ["study1", "study2"],
                    "impact_on_confidence": "description"
                }}
            ],
            "strengths": ["strength1", "strength2"],
            "assessment_reasoning": "detailed explanation",
            "confidence_in_assessment": 0.0-1.0
        }}
        
        Consider CERQual guidance:
        - Are study designs appropriate for the research question?
        - Are data collection methods clearly described and appropriate?
        - Are analysis methods systematic and rigorous?  
        - Is there evidence of researcher reflexivity?
        - Are potential biases acknowledged and addressed?
        - Is reporting transparent and complete?
        - Are ethical issues appropriately handled?
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=1200)
            return self._parse_json_response(response, "methodological_limitations")
        except Exception as e:
            logger.error(f"Error in methodological assessment: {e}")
            return self._default_methodological_assessment()
    
    async def assess_relevance(self, evidence: CERQualEvidence) -> Dict[str, Any]:
        """Assess relevance dimension"""
        
        prompt = f"""
        Assess the RELEVANCE of the evidence to the research question using CERQual criteria.
        
        RESEARCH QUESTION:
        {evidence.research_question}
        
        EVIDENCE FINDING:
        {evidence.finding}
        
        CONTEXT:
        {evidence.context}
        
        REVIEW SCOPE:
        {evidence.review_scope}
        
        SUPPORTING STUDIES:
        {len(evidence.supporting_studies)} studies from {self._get_study_years_range(evidence.supporting_studies)}
        
        Provide JSON assessment:
        {{
            "overall_score": 0.0-1.0,
            "population_relevance": 0.0-1.0,
            "setting_relevance": 0.0-1.0,
            "phenomenon_relevance": 0.0-1.0,
            "contextual_relevance": 0.0-1.0,
            "temporal_relevance": 0.0-1.0,
            "cultural_relevance": 0.0-1.0,
            "relevance_concerns": [
                {{
                    "concern": "specific relevance issue",
                    "severity": "minor|moderate|serious",
                    "explanation": "why this affects relevance"
                }}
            ],
            "relevance_strengths": ["strength1", "strength2"],
            "applicability_context": "where findings are most applicable",
            "transferability_assessment": "assessment of transferability",
            "assessment_reasoning": "detailed explanation",
            "confidence_in_assessment": 0.0-1.0
        }}
        
        Consider:
        - How closely do study populations match the review question?
        - Are settings and contexts appropriate?
        - Is the phenomenon of interest clearly addressed?
        - Are there important contextual factors that limit applicability?
        - How current and relevant are the studies temporally?
        - Are there cultural or geographic relevance issues?
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=1200)
            return self._parse_json_response(response, "relevance")
        except Exception as e:
            logger.error(f"Error in relevance assessment: {e}")
            return self._default_relevance_assessment()
    
    async def assess_coherence(self, evidence: CERQualEvidence) -> Dict[str, Any]:
        """Assess coherence dimension"""
        
        prompt = f"""
        Assess the COHERENCE of findings across studies using CERQual criteria.
        
        EVIDENCE FINDING:
        {evidence.finding}
        
        EXPLANATION:
        {evidence.explanation}
        
        NUMBER OF SUPPORTING STUDIES: {len(evidence.supporting_studies)}
        
        STUDY DESIGNS: {self._get_study_designs(evidence.supporting_studies)}
        
        Assess coherence and provide JSON:
        {{
            "overall_score": 0.0-1.0,
            "finding_consistency": 0.0-1.0,
            "variation_explanation": 0.0-1.0,
            "pattern_clarity": 0.0-1.0,
            "contradictory_evidence": 0.0-1.0,
            "context_sensitivity": 0.0-1.0,
            "conceptual_coherence": 0.0-1.0,
            "coherence_issues": [
                {{
                    "issue": "specific coherence problem",
                    "affected_studies": ["study1", "study2"],
                    "explanation": "why this affects coherence",
                    "potential_resolution": "possible explanation"
                }}
            ],
            "coherence_strengths": [
                {{
                    "strength": "coherence strength",
                    "evidence": "supporting evidence"
                }}
            ],
            "variation_patterns": [
                {{
                    "variation": "type of variation observed",
                    "explanation": "explanation for variation",
                    "impact": "impact on overall finding"
                }}
            ],
            "assessment_reasoning": "detailed explanation",
            "confidence_in_assessment": 0.0-1.0
        }}
        
        Consider:
        - Are findings consistent across studies?
        - Can variations be explained by context or methodology?
        - Are patterns clear and well-articulated?
        - How do contradictory findings affect coherence?
        - Is there conceptual coherence in the overall finding?
        - Are contextual factors appropriately considered?
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=1200)
            return self._parse_json_response(response, "coherence")
        except Exception as e:
            logger.error(f"Error in coherence assessment: {e}")
            return self._default_coherence_assessment()
    
    async def assess_adequacy(self, evidence: CERQualEvidence) -> Dict[str, Any]:
        """Assess adequacy dimension"""
        
        total_participants = sum(study.sample_size for study in evidence.supporting_studies 
                               if study.sample_size is not None)
        
        prompt = f"""
        Assess the ADEQUACY of data for supporting the evidence finding using CERQual criteria.
        
        EVIDENCE FINDING:
        {evidence.finding}
        
        DATA ADEQUACY INFORMATION:
        - Number of studies: {len(evidence.supporting_studies)}
        - Total participants: {total_participants if total_participants > 0 else "Not specified"}
        - Study designs: {self._get_study_designs(evidence.supporting_studies)}
        - Data collection methods: {self._get_data_collection_methods(evidence.supporting_studies)}
        
        RESEARCH QUESTION SCOPE:
        {evidence.research_question}
        
        Provide JSON assessment:
        {{
            "overall_score": 0.0-1.0,
            "quantity_adequacy": 0.0-1.0,
            "depth_adequacy": 0.0-1.0,
            "breadth_adequacy": 0.0-1.0,
            "saturation_assessment": 0.0-1.0,
            "diversity_adequacy": 0.0-1.0,
            "richness_adequacy": 0.0-1.0,
            "adequacy_concerns": [
                {{
                    "concern": "specific adequacy issue",
                    "type": "quantity|depth|breadth|diversity|richness",
                    "severity": "minor|moderate|serious",
                    "explanation": "why this is a concern",
                    "impact": "impact on confidence"
                }}
            ],
            "adequacy_strengths": [
                {{
                    "strength": "adequacy strength",
                    "evidence": "supporting evidence"
                }}
            ],
            "saturation_evidence": [
                {{
                    "indicator": "saturation indicator",
                    "strength": "weak|moderate|strong"
                }}
            ],
            "missing_perspectives": ["perspective1", "perspective2"],
            "data_richness_indicators": ["indicator1", "indicator2"],
            "assessment_reasoning": "detailed explanation",
            "confidence_in_assessment": 0.0-1.0
        }}
        
        Consider CERQual adequacy criteria:
        - Is there sufficient quantity of data?
        - Is the data rich and thick enough?
        - Is there adequate breadth across relevant contexts?
        - Is there evidence of theoretical or data saturation?
        - Are diverse perspectives adequately represented?
        - Are there important gaps or missing perspectives?
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=1200)
            return self._parse_json_response(response, "adequacy")
        except Exception as e:
            logger.error(f"Error in adequacy assessment: {e}")
            return self._default_adequacy_assessment()
    
    async def perform_complete_cerqual_assessment(self, evidence: CERQualEvidence) -> CERQualAssessment:
        """Perform complete CERQual assessment across all dimensions"""
        
        logger.info(f"Starting complete CERQual assessment for: {evidence.finding[:100]}...")
        
        # Assess all dimensions in parallel for efficiency
        dimension_tasks = [
            self.assess_methodological_limitations(evidence),
            self.assess_relevance(evidence),
            self.assess_coherence(evidence),
            self.assess_adequacy(evidence)
        ]
        
        dimension_results = await asyncio.gather(*dimension_tasks)
        
        methodological_assessment = dimension_results[0]
        relevance_assessment = dimension_results[1]
        coherence_assessment = dimension_results[2]
        adequacy_assessment = dimension_results[3]
        
        # Calculate overall confidence
        overall_score = (
            self.dimension_weights['methodological_limitations'] * methodological_assessment['overall_score'] +
            self.dimension_weights['relevance'] * relevance_assessment['overall_score'] +
            self.dimension_weights['coherence'] * coherence_assessment['overall_score'] +
            self.dimension_weights['adequacy'] * adequacy_assessment['overall_score']
        )
        
        # Convert to CERQual confidence levels
        if overall_score >= 0.8:
            confidence_level = 'high'
            numeric_confidence = 0.9
        elif overall_score >= 0.65:
            confidence_level = 'moderate'
            numeric_confidence = 0.75
        elif overall_score >= 0.45:
            confidence_level = 'low'
            numeric_confidence = 0.55
        else:
            confidence_level = 'very_low'
            numeric_confidence = 0.3
        
        # Compile key concerns and confidence factors
        key_concerns = []
        confidence_factors = []
        
        for dimension_name, assessment in [
            ('methodological_limitations', methodological_assessment),
            ('relevance', relevance_assessment),
            ('coherence', coherence_assessment),
            ('adequacy', adequacy_assessment)
        ]:
            # Extract concerns
            if f'{dimension_name.split("_")[0]}_concerns' in assessment:
                concerns = assessment[f'{dimension_name.split("_")[0]}_concerns']
                for concern in concerns:
                    if concern.get('severity') in ['moderate', 'serious']:
                        key_concerns.append(f"{dimension_name}: {concern.get('concern', 'Unknown concern')}")
            
            # Extract strengths
            strength_key = f'{dimension_name.split("_")[0]}_strengths'
            if strength_key in assessment:
                for strength in assessment[strength_key]:
                    if isinstance(strength, dict):
                        confidence_factors.append(f"{dimension_name}: {strength.get('strength', strength)}")
                    else:
                        confidence_factors.append(f"{dimension_name}: {strength}")
        
        # Generate assessment reasoning
        reasoning = await self._generate_overall_reasoning(
            evidence, overall_score, confidence_level,
            methodological_assessment, relevance_assessment, 
            coherence_assessment, adequacy_assessment
        )
        
        # Create final assessment
        assessment = CERQualAssessment(
            methodological_limitations=methodological_assessment['overall_score'],
            relevance=relevance_assessment['overall_score'],
            coherence=coherence_assessment['overall_score'],
            adequacy=adequacy_assessment['overall_score'],
            overall_confidence=confidence_level,
            numeric_confidence=numeric_confidence,
            dimension_details={
                'methodological_limitations': methodological_assessment,
                'relevance': relevance_assessment,
                'coherence': coherence_assessment,
                'adequacy': adequacy_assessment
            },
            assessment_reasoning=reasoning,
            key_concerns=key_concerns,
            confidence_factors=confidence_factors,
            assessment_date=datetime.now(),
            assessor_info="KGAS CERQual Assessor v1.0",
            evidence_summary=f"Finding: {evidence.finding[:200]}... ({len(evidence.supporting_studies)} studies)"
        )
        
        # Store assessment
        self.assessment_history.append(assessment)
        
        logger.info(f"CERQual assessment completed: {confidence_level} confidence ({numeric_confidence:.3f})")
        
        return assessment
    
    async def _generate_overall_reasoning(self, evidence: CERQualEvidence, overall_score: float,
                                        confidence_level: str, *dimension_assessments) -> str:
        """Generate overall assessment reasoning"""
        
        prompt = f"""
        Generate a comprehensive reasoning statement for this CERQual assessment.
        
        EVIDENCE FINDING:
        {evidence.finding}
        
        OVERALL SCORE: {overall_score:.3f}
        CONFIDENCE LEVEL: {confidence_level}
        
        DIMENSION SCORES:
        - Methodological Limitations: {dimension_assessments[0]['overall_score']:.3f}
        - Relevance: {dimension_assessments[1]['overall_score']:.3f}
        - Coherence: {dimension_assessments[2]['overall_score']:.3f}
        - Adequacy: {dimension_assessments[3]['overall_score']:.3f}
        
        NUMBER OF STUDIES: {len(evidence.supporting_studies)}
        
        Generate a structured reasoning statement that:
        1. Explains the overall confidence level
        2. Highlights the strongest and weakest dimensions
        3. Discusses key factors influencing confidence
        4. Provides guidance on evidence use and limitations
        5. Suggests areas for future research if confidence is lower
        
        Keep it professional and concise (200-300 words).
        """
        
        try:
            reasoning = await self._make_llm_call(prompt, max_tokens=400)
            return reasoning.strip()
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return f"CERQual assessment completed with {confidence_level} confidence based on {len(evidence.supporting_studies)} studies. Overall score: {overall_score:.3f}."
    
    def _create_studies_summary(self, studies: List[StudyMetadata]) -> str:
        """Create a summary of studies for LLM processing"""
        
        summary_lines = []
        for i, study in enumerate(studies[:10]):  # Limit to first 10 studies
            summary_lines.append(
                f"{i+1}. {study.title[:80]}... ({study.publication_year}) - "
                f"{study.study_design}, n={study.sample_size or 'Not specified'}, "
                f"Bias risk: {study.bias_risk}"
            )
        
        if len(studies) > 10:
            summary_lines.append(f"... and {len(studies) - 10} more studies")
        
        return "\n".join(summary_lines)
    
    def _get_study_years_range(self, studies: List[StudyMetadata]) -> str:
        """Get range of study publication years"""
        years = [study.publication_year for study in studies]
        return f"{min(years)}-{max(years)}" if years else "Unknown"
    
    def _get_study_designs(self, studies: List[StudyMetadata]) -> str:
        """Get summary of study designs"""
        designs = [study.study_design for study in studies]
        design_counts = defaultdict(int)
        for design in designs:
            design_counts[design] += 1
        
        return ", ".join([f"{design}({count})" for design, count in design_counts.items()])
    
    def _get_data_collection_methods(self, studies: List[StudyMetadata]) -> str:
        """Get summary of data collection methods"""
        methods = [study.data_collection_method for study in studies]
        method_counts = defaultdict(int)
        for method in methods:
            method_counts[method] += 1
        
        return ", ".join([f"{method}({count})" for method, count in method_counts.items()])
    
    def _parse_json_response(self, response: str, dimension: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing {dimension} JSON response: {e}")
        
        return self._default_dimension_assessment(dimension)
    
    def _default_dimension_assessment(self, dimension: str) -> Dict[str, Any]:
        """Default assessment when LLM parsing fails"""
        return {
            'overall_score': 0.5,
            'assessment_reasoning': f"Default {dimension} assessment due to parsing error",
            'confidence_in_assessment': 0.3
        }
    
    def _default_methodological_assessment(self) -> Dict[str, Any]:
        return {
            'overall_score': 0.5,
            'study_design_quality': 0.5,
            'data_collection_rigor': 0.5,
            'analysis_appropriateness': 0.5,
            'major_limitations': [],
            'strengths': [],
            'assessment_reasoning': 'Default assessment',
            'confidence_in_assessment': 0.3
        }
    
    def _default_relevance_assessment(self) -> Dict[str, Any]:
        return {
            'overall_score': 0.6,
            'population_relevance': 0.6,
            'setting_relevance': 0.6,
            'relevance_concerns': [],
            'relevance_strengths': [],
            'assessment_reasoning': 'Default assessment',
            'confidence_in_assessment': 0.3
        }
    
    def _default_coherence_assessment(self) -> Dict[str, Any]:
        return {
            'overall_score': 0.5,
            'finding_consistency': 0.5,
            'coherence_issues': [],
            'coherence_strengths': [],
            'assessment_reasoning': 'Default assessment',
            'confidence_in_assessment': 0.3
        }
    
    def _default_adequacy_assessment(self) -> Dict[str, Any]:
        return {
            'overall_score': 0.4,
            'quantity_adequacy': 0.4,
            'depth_adequacy': 0.4,
            'adequacy_concerns': [],
            'adequacy_strengths': [],
            'assessment_reasoning': 'Default assessment',
            'confidence_in_assessment': 0.3
        }
    
    def generate_cerqual_report(self, assessment: CERQualAssessment, evidence: CERQualEvidence) -> str:
        """Generate comprehensive CERQual assessment report"""
        
        report = f"""
# CERQual Assessment Report

## Evidence Finding
**Finding**: {evidence.finding}

**Research Question**: {evidence.research_question}

**Context**: {evidence.context}

**Number of Supporting Studies**: {len(evidence.supporting_studies)}

## Overall CERQual Assessment
**Confidence Level**: {assessment.overall_confidence.upper()}
**Numeric Confidence**: {assessment.numeric_confidence:.3f}

## Dimension Scores

### 1. Methodological Limitations: {assessment.methodological_limitations:.3f}
{self._format_dimension_details(assessment.dimension_details['methodological_limitations'])}

### 2. Relevance: {assessment.relevance:.3f}
{self._format_dimension_details(assessment.dimension_details['relevance'])}

### 3. Coherence: {assessment.coherence:.3f}
{self._format_dimension_details(assessment.dimension_details['coherence'])}

### 4. Adequacy: {assessment.adequacy:.3f}
{self._format_dimension_details(assessment.dimension_details['adequacy'])}

## Assessment Reasoning
{assessment.assessment_reasoning}

## Key Concerns
{self._format_list(assessment.key_concerns)}

## Confidence Factors
{self._format_list(assessment.confidence_factors)}

## Study Summary
{self._format_study_summary(evidence.supporting_studies)}

## Assessment Metadata
- **Assessment Date**: {assessment.assessment_date.strftime('%Y-%m-%d %H:%M:%S')}
- **Assessor**: {assessment.assessor_info}
- **API Calls Made**: {self.api_calls_made}

---
*This assessment follows CERQual (Confidence in Evidence from Reviews of Qualitative research) methodology for systematic evaluation of qualitative evidence.*
"""
        
        return report
    
    def _format_dimension_details(self, details: Dict[str, Any]) -> str:
        """Format dimension details for report"""
        reasoning = details.get('assessment_reasoning', 'No detailed reasoning available')
        return f"- **Assessment**: {reasoning[:200]}..."
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items for report"""
        if not items:
            return "- None identified"
        return "\n".join([f"- {item}" for item in items])
    
    def _format_study_summary(self, studies: List[StudyMetadata]) -> str:
        """Format study summary for report"""
        if not studies:
            return "No studies provided"
        
        summary = f"**Total Studies**: {len(studies)}\n"
        summary += f"**Publication Years**: {self._get_study_years_range(studies)}\n"
        summary += f"**Study Designs**: {self._get_study_designs(studies)}\n"
        
        # Sample of studies
        summary += "\n**Sample Studies**:\n"
        for i, study in enumerate(studies[:5]):
            summary += f"{i+1}. {study.title[:60]}... ({study.publication_year})\n"
        
        if len(studies) > 5:
            summary += f"... and {len(studies) - 5} more studies\n"
        
        return summary

# Example usage and testing
async def test_cerqual_assessor():
    """Test CERQual assessor with synthetic qualitative research data"""
    
    assessor = CERQualAssessor()
    
    # Create sample studies
    sample_studies = [
        StudyMetadata(
            study_id="study_001",
            title="Experiences of government transparency in democratic contexts",
            authors=["Smith, J.", "Brown, A."],
            publication_year=2020,
            study_design="qualitative",
            sample_size=25,
            population="citizens",
            setting="urban_democratic",
            data_collection_method="semi_structured_interviews",
            analysis_method="thematic_analysis",
            bias_risk="low"
        ),
        StudyMetadata(
            study_id="study_002", 
            title="Public perceptions of institutional accountability",
            authors=["Johnson, M."],
            publication_year=2019,
            study_design="mixed_methods",
            sample_size=40,
            population="stakeholders",
            setting="government_agencies",
            data_collection_method="interviews_and_surveys",
            analysis_method="framework_analysis",
            bias_risk="moderate"
        )
    ]
    
    # Create evidence structure
    evidence = CERQualEvidence(
        finding="Citizens report increased trust in government when transparency measures are implemented, particularly when information is accessible and accountability mechanisms are visible.",
        supporting_studies=sample_studies,
        context="Democratic governance contexts with established transparency policies",
        explanation="Multiple studies consistently show that transparency initiatives lead to improved citizen trust, especially when combined with accountability mechanisms.",
        research_question="How do transparency measures affect citizen trust in government institutions?",
        review_scope="Qualitative studies of citizen experiences with government transparency",
        assessment_date=datetime.now()
    )
    
    # Perform CERQual assessment
    assessment = await assessor.perform_complete_cerqual_assessment(evidence)
    
    # Generate report
    report = assessor.generate_cerqual_report(assessment, evidence)
    
    return {
        "assessment": assessment.to_dict(),
        "report": report,
        "api_calls_made": assessor.api_calls_made
    }

if __name__ == "__main__":
    # Run test
    result = asyncio.run(test_cerqual_assessor())
    
    # Save results
    with open("/home/brian/projects/Digimons/uncertainty_stress_test/validation/cerqual_test_results.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print("CERQual Assessment Test Results:")
    print(f"Overall confidence: {result['assessment']['overall_confidence']}")
    print(f"Numeric confidence: {result['assessment']['numeric_confidence']:.3f}")
    print(f"API calls made: {result['api_calls_made']}")
    
    # Save report
    with open("/home/brian/projects/Digimons/uncertainty_stress_test/validation/cerqual_assessment_report.md", "w") as f:
        f.write(result['report'])