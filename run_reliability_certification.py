#!/usr/bin/env python3
"""
KGAS Reliability Certification Runner
Execute complete reliability certification to achieve 10/10 bulletproof certainty
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.reliability.master_reliability_certification import run_master_reliability_certification


def main():
    """Main entry point for reliability certification"""
    print("""
██╗  ██╗ ██████╗  █████╗ ███████╗
██║ ██╔╝██╔════╝ ██╔══██╗██╔════╝
█████╔╝ ██║  ███╗███████║███████╗
██╔═██╗ ██║   ██║██╔══██║╚════██║
██║  ██╗╚██████╔╝██║  ██║███████║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝

DISTRIBUTED TRANSACTION MANAGER
RELIABILITY CERTIFICATION SUITE
""")
    
    print("🎯 TARGET: 10/10 BULLETPROOF RELIABILITY CERTIFICATION")
    print("🔬 METHOD: COMPREHENSIVE TESTING WITH REAL DATABASES")
    print("⚡ NO MOCKING - REAL NEO4J + SQLITE INSTANCES ONLY")
    print()
    
    # Check for 24-hour test option
    include_24h = False
    if "--24h" in sys.argv or "--include-24h" in sys.argv:
        print("⚠️  24-HOUR CONTINUOUS TEST REQUESTED")
        print("   This will run the system continuously for 24 hours")
        print("   to detect any long-term stability issues.")
        print()
        response = input("   Continue with 24-hour test? (y/N): ")
        if response.lower() == 'y':
            include_24h = True
            print("   ✅ 24-hour test enabled")
    
    print("\n🚀 Starting Master Reliability Certification...")
    print("   This comprehensive test suite will:")
    print("   ├─ Test core ACID guarantees with real databases")
    print("   ├─ Validate failure recovery scenarios")
    print("   ├─ Stress test under production loads")
    if include_24h:
        print("   └─ Run 24-hour continuous stability test")
    else:
        print("   └─ Run 1-hour continuous stability test")
    
    print("\n⏱️  Estimated completion time:", end="")
    if include_24h:
        print(" 25-26 hours")
    else:
        print(" 2-3 hours")
    
    print("\n" + "="*60)
    
    try:
        # Run the certification
        certification = asyncio.run(run_master_reliability_certification(include_24h))
        
        # Print final summary
        verdict = certification['final_verdict']
        if certification['certification_results']['bulletproof_certified']:
            print("\n🎉 SUCCESS: BULLETPROOF 10/10 RELIABILITY ACHIEVED! 🎉")
            return 0
        elif certification['certification_results']['production_ready']:
            print("\n✅ SUCCESS: PRODUCTION READY 9/10 RELIABILITY ACHIEVED!")
            return 0
        else:
            print("\n❌ CERTIFICATION FAILED: System requires improvement")
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Certification interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n❌ CERTIFICATION FAILED: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("KGAS Reliability Certification")
        print()
        print("Usage:")
        print("  python run_reliability_certification.py          # Standard certification (1-3 hours)")
        print("  python run_reliability_certification.py --24h    # Include 24-hour test (~25 hours)")
        print("  python run_reliability_certification.py --help   # Show this help")
        print()
        print("This script runs comprehensive reliability testing including:")
        print("- Core ACID guarantee validation with real databases")
        print("- Comprehensive failure scenario testing")
        print("- Load testing under production conditions")
        print("- Continuous stability testing")
        print()
        print("Target: 10/10 bulletproof reliability certification")
        sys.exit(0)
    
    sys.exit(main())