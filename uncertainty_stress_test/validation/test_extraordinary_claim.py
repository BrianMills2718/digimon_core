#!/usr/bin/env python3
"""
Test formal Bayesian engine with extraordinary claim
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add core services to path
sys.path.append('/home/brian/projects/Digimons/uncertainty_stress_test/core_services')

from formal_bayesian_llm_engine import FormalBayesianLLMEngine

async def test_extraordinary_claim():
    """Test with cold fusion - extraordinary claim requiring extraordinary evidence"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key available")
        return
    
    engine = FormalBayesianLLMEngine(api_key)
    
    # Extraordinary claim test case
    test_case = {
        "text": """
        A research team claims to have developed cold fusion technology that produces net energy gain. 
        Their experiments show consistent energy output exceeding input by 200%. The methodology appears 
        sound, equipment is properly calibrated, and results have been reproduced in their lab 5 times. 
        However, the claim contradicts established nuclear physics principles and previous cold fusion 
        attempts have failed. No independent replication has been attempted yet.
        """,
        "claim": "Cold fusion technology can produce net positive energy output",
        "domain": "nuclear_physics"
    }
    
    print("🚀 Testing Extraordinary Claim: Cold Fusion")
    print("=" * 50)
    
    # Perform assessment
    assessment = await engine.assess_claim_with_formal_bayesian(
        test_case["text"], test_case["claim"], test_case["domain"]
    )
    
    # Show key results
    print(f"\n📊 Results:")
    print(f"Posterior Belief: {assessment['posterior_belief']:.4f}")
    print(f"95% CI: [{assessment['confidence_bounds'][0]:.4f}, {assessment['confidence_bounds'][1]:.4f}]")
    print(f"Bayes Factor: {assessment['bayes_factor']:.4f}")
    print(f"Prior Belief: {assessment['parameters']['prior_belief']:.4f}")
    print(f"Likelihood P(E|H): {assessment['parameters']['likelihood_given_h']:.4f}")
    print(f"Likelihood P(E|¬H): {assessment['parameters']['likelihood_given_not_h']:.4f}")
    
    print(f"\n🧠 LLM Reasoning:")
    print(f"Prior: {assessment['parameters']['parameter_reasoning']['prior_belief']}")
    print(f"L(H): {assessment['parameters']['parameter_reasoning']['likelihood_given_h']}")
    print(f"L(¬H): {assessment['parameters']['parameter_reasoning']['likelihood_given_not_h']}")
    
    # Generate report
    report = engine.generate_formal_report(assessment)
    
    # Save results
    output_dir = Path("/home/brian/projects/Digimons/uncertainty_stress_test/validation")
    
    with open(output_dir / "extraordinary_claim_results.json", "w") as f:
        json.dump(assessment, f, indent=2, default=str)
    
    with open(output_dir / "extraordinary_claim_report.md", "w") as f:
        f.write(report)
    
    print(f"\n✅ Test complete. Expected range: 0.1-0.4")
    print(f"Actual: {assessment['posterior_belief']:.4f}")
    print(f"Within range: {'✅' if 0.1 <= assessment['posterior_belief'] <= 0.4 else '❌'}")
    
    return assessment

if __name__ == "__main__":
    assessment = asyncio.run(test_extraordinary_claim())