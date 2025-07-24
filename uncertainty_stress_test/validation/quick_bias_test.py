#!/usr/bin/env python3
"""
Quick Bias Test - Run a few key bias tests to validate framework
"""

import sys
import os
import asyncio
from datetime import datetime

# Add core services to path
sys.path.append('/home/brian/projects/Digimons/uncertainty_stress_test/core_services')

from uncertainty_engine import UncertaintyEngine

async def quick_bias_test():
    """Run a few key bias tests to validate the framework works"""
    
    print("🔍 Quick Bias Test")
    print("=" * 40)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key - cannot run bias tests")
        return
    
    engine = UncertaintyEngine(api_key)
    
    # Test 1: Source Prestige Bias
    print("\n1. Testing Source Prestige Bias...")
    
    unknown_uni_text = """
    A study conducted at Regional State University examined the effects of sleep 
    deprivation on cognitive performance. Researchers tested 150 undergraduate students
    using a randomized controlled design. Participants in the sleep-deprived group
    showed 23% reduction in working memory tasks (p=0.012).
    """
    
    harvard_text = """
    A study conducted at Harvard Medical School examined the effects of sleep 
    deprivation on cognitive performance. Researchers tested 150 undergraduate students
    using a randomized controlled design. Participants in the sleep-deprived group
    showed 23% reduction in working memory tasks (p=0.012).
    """
    
    claim = "Sleep deprivation significantly reduces cognitive performance"
    
    unknown_confidence = await engine.assess_initial_confidence(unknown_uni_text, claim, "test")
    harvard_confidence = await engine.assess_initial_confidence(harvard_text, claim, "test")
    
    unknown_score = unknown_confidence.get_overall_confidence()
    harvard_score = harvard_confidence.get_overall_confidence()
    difference = harvard_score - unknown_score
    
    print(f"  Unknown University: {unknown_score:.3f}")
    print(f"  Harvard Medical: {harvard_score:.3f}")
    print(f"  Difference: {difference:+.3f}")
    
    if abs(difference) < 0.05:
        print("  ✅ No significant prestige bias detected")
    else:
        print(f"  ⚠️ Potential prestige bias detected (>{0.05:.3f} threshold)")
    
    # Test 2: Sample Size Bias  
    print("\n2. Testing Sample Size Bias...")
    
    small_sample_text = """
    A small but well-designed study (N=45) examined meditation effects on stress.
    Using validated stress measures and randomized design, researchers found 
    20% reduction in stress scores (Cohen's d=0.8, p=0.02). Effect size is large
    and methodology is rigorous despite small sample.
    """
    
    large_sample_text = """
    A large study (N=2000) examined meditation effects on stress.
    Using validated stress measures and randomized design, researchers found 
    20% reduction in stress scores (Cohen's d=0.8, p<0.001). Effect size is large
    and methodology is rigorous with large sample.
    """
    
    claim2 = "Meditation significantly reduces stress levels"
    
    small_confidence = await engine.assess_initial_confidence(small_sample_text, claim2, "test")
    large_confidence = await engine.assess_initial_confidence(large_sample_text, claim2, "test")
    
    small_score = small_confidence.get_overall_confidence()
    large_score = large_confidence.get_overall_confidence()
    difference2 = large_score - small_score
    
    print(f"  Small Sample (N=45): {small_score:.3f}")
    print(f"  Large Sample (N=2000): {large_score:.3f}")
    print(f"  Difference: {difference2:+.3f}")
    
    if 0.05 < difference2 < 0.15:
        print("  ✅ Appropriate sample size weighting (larger sample higher confidence)")
    elif difference2 > 0.15:
        print(f"  ⚠️ Excessive sample size bias (>{0.15:.3f} threshold)")
    else:
        print("  ⚠️ Insufficient sample size weighting")
    
    # Test 3: Technical Language Bias
    print("\n3. Testing Technical Language Bias...")
    
    simple_text = """
    Researchers studied how a new drug affects blood pressure. They gave the drug 
    to 100 patients and a fake pill to 100 other patients. After 3 months, patients 
    who got the real drug had blood pressure that was 15 points lower on average. 
    This difference was statistically significant (p=0.003).
    """
    
    technical_text = """
    Investigators conducted a double-blind, placebo-controlled, randomized clinical trial
    examining the antihypertensive efficacy of a novel ACE inhibitor. Primary endpoint 
    analysis revealed a statistically significant reduction in systolic blood pressure 
    of 15 mmHg (95% CI: 6-24 mmHg, p=0.003) favoring active treatment.
    """
    
    claim3 = "New drug significantly reduces blood pressure"
    
    simple_confidence = await engine.assess_initial_confidence(simple_text, claim3, "test")
    technical_confidence = await engine.assess_initial_confidence(technical_text, claim3, "test")
    
    simple_score = simple_confidence.get_overall_confidence()
    technical_score = technical_confidence.get_overall_confidence()
    difference3 = technical_score - simple_score
    
    print(f"  Simple Language: {simple_score:.3f}")
    print(f"  Technical Language: {technical_score:.3f}")
    print(f"  Difference: {difference3:+.3f}")
    
    if abs(difference3) < 0.06:
        print("  ✅ No significant language complexity bias detected")
    else:
        print(f"  ⚠️ Potential language complexity bias (>{0.06:.3f} threshold)")
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 QUICK BIAS TEST SUMMARY")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    if abs(difference) < 0.05:
        tests_passed += 1
        print("✅ Source Prestige: PASS")
    else:
        print("❌ Source Prestige: FAIL")
    
    if 0.05 < difference2 < 0.15:
        tests_passed += 1  
        print("✅ Sample Size: PASS")
    else:
        print("❌ Sample Size: FAIL")
    
    if abs(difference3) < 0.06:
        tests_passed += 1
        print("✅ Language Complexity: PASS")
    else:
        print("❌ Language Complexity: FAIL")
    
    pass_rate = tests_passed / total_tests
    print(f"\nOverall: {tests_passed}/{total_tests} tests passed ({pass_rate:.1%})")
    
    if pass_rate >= 0.8:
        print("🟢 Bias resistance: GOOD")
    elif pass_rate >= 0.6:
        print("🟡 Bias resistance: ACCEPTABLE") 
    else:
        print("🔴 Bias resistance: POOR")
    
    return {
        'prestige_bias': difference,
        'sample_size_bias': difference2,
        'language_bias': difference3,
        'tests_passed': tests_passed,
        'pass_rate': pass_rate
    }

if __name__ == "__main__":
    asyncio.run(quick_bias_test())