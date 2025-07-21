#!/usr/bin/env python3
"""
Health Check Demo

Demonstrates the enhanced health check system with Phase 1 improvements.
Shows system health, readiness, and liveness checks.
"""

import sys
import os
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.health_checker import HealthChecker
from src.core.config_manager import ConfigurationManager


def print_health_check_result(name: str, result: dict):
    """Print a formatted health check result"""
    print(f"\n🏥 {name}")
    print("=" * 50)
    
    if isinstance(result, dict):
        if "overall_status" in result:
            # System health check
            status = result["overall_status"]
            message = result["overall_message"]
            latency = result.get("total_latency_ms", 0)
            
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "unhealthy": "❌"
            }.get(status, "❓")
            
            print(f"{status_emoji} Status: {status}")
            print(f"💬 Message: {message}")
            print(f"⏱️ Latency: {latency:.2f}ms")
            
            if "summary" in result:
                summary = result["summary"]
                print(f"📊 Summary: {summary['healthy']} healthy, {summary['warning']} warnings, {summary['unhealthy']} unhealthy")
            
            if "checks" in result:
                print(f"\n📋 Individual Checks:")
                for check in result["checks"]:
                    check_emoji = {
                        "healthy": "✅",
                        "warning": "⚠️", 
                        "unhealthy": "❌"
                    }.get(check["status"], "❓")
                    print(f"  {check_emoji} {check['name']}: {check.get('message', check['status'])}")
                    
                    if check.get("latency_ms"):
                        print(f"      ⏱️ {check['latency_ms']}ms")
                    
                    if check.get("metadata"):
                        print(f"      📄 Metadata: {check['metadata']}")
        
        elif "ready" in result:
            # Readiness check
            ready = result["ready"]
            message = result["message"]
            
            ready_emoji = "✅" if ready else "❌"
            print(f"{ready_emoji} Ready: {ready}")
            print(f"💬 Message: {message}")
            
            if "critical_checks" in result:
                print(f"\n📋 Critical Checks:")
                for check in result["critical_checks"]:
                    check_emoji = {
                        "healthy": "✅",
                        "warning": "⚠️",
                        "unhealthy": "❌"
                    }.get(check["status"], "❓")
                    print(f"  {check_emoji} {check['name']}: {check.get('message', check['status'])}")
        
        elif "alive" in result:
            # Liveness check
            alive = result["alive"]
            message = result["message"]
            
            alive_emoji = "✅" if alive else "❌"
            print(f"{alive_emoji} Alive: {alive}")
            print(f"💬 Message: {message}")
            
            if "latency_ms" in result:
                print(f"⏱️ Latency: {result['latency_ms']}ms")
        
        else:
            # Generic result
            print(json.dumps(result, indent=2))
    else:
        print(str(result))


def main():
    """Main health check demo"""
    print("🎯 Phase 1 Health Check Demo")
    print("Enhanced health checks with Phase 1 improvements")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize health checker
        config = ConfigurationManager()
        health_checker = HealthChecker(config)
        
        print("\n🔧 Initializing health checker...")
        print("✅ Health checker initialized")
        
        # Run comprehensive system health check
        print("\n🔍 Running comprehensive system health check...")
        system_health = health_checker.check_system_health()
        print_health_check_result("System Health Check", system_health)
        
        # Run readiness check
        print("\n🔍 Running readiness check...")
        readiness = health_checker.get_readiness_status()
        print_health_check_result("Readiness Check", readiness)
        
        # Run liveness check
        print("\n🔍 Running liveness check...")
        liveness = health_checker.get_liveness_status()
        print_health_check_result("Liveness Check", liveness)
        
        # Run individual Phase 1 checks
        print("\n🔍 Running Phase 1 specific checks...")
        
        # API services check
        api_check = health_checker.check_api_services_health()
        print_health_check_result("API Services Check", api_check.to_dict())
        
        # Async clients check
        async_check = health_checker.check_async_clients_health()
        print_health_check_result("Async Clients Check", async_check.to_dict())
        
        # Phase 1 readiness check
        phase1_check = health_checker.check_phase1_readiness()
        print_health_check_result("Phase 1 Readiness Check", phase1_check.to_dict())
        
        # Overall assessment
        print("\n🎯 Overall Assessment")
        print("=" * 50)
        
        overall_status = system_health["overall_status"]
        ready = readiness["ready"]
        alive = liveness["alive"]
        
        if overall_status == "healthy" and ready and alive:
            print("✅ System is fully operational and ready for Phase 2")
            print("✅ All Phase 1 improvements are working correctly")
            return 0
        elif overall_status in ["healthy", "warning"] and ready and alive:
            print("⚠️ System is operational with some warnings")
            print("✅ Phase 1 improvements are mostly working")
            return 0
        else:
            print("❌ System has critical issues that need attention")
            print("❌ Phase 1 improvements may not be fully functional")
            return 1
            
    except Exception as e:
        print(f"\n❌ Health check demo failed: {e}")
        return 1


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n🛑 Health check demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)