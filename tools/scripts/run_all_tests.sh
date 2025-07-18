#!/bin/bash
# GraphRAG Comprehensive Test Runner
# Runs all test categories and reports results

echo "🧪 GraphRAG Comprehensive Test Suite"
echo "====================================="

# Track test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo ""
    echo "🔍 Running: $test_name"
    echo "Command: $test_command"
    echo "-------------------------------------"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        echo "✅ PASSED: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo "❌ FAILED: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Functional Integration Tests (Mandatory)
echo "🎯 FUNCTIONAL INTEGRATION TESTS"
run_test "Phase 1 Integration" "python tests/functional/test_functional_simple.py"
run_test "Cross-Component Integration" "python tests/functional/test_cross_component_integration.py"

# Performance Tests
echo ""
echo "⚡ PERFORMANCE TESTS"
run_test "Optimized Workflow Performance" "python tests/performance/test_optimized_workflow.py"
run_test "Performance Profiling" "python tests/performance/test_performance_profiling.py"

# Stress Tests
echo ""
echo "💪 STRESS & RELIABILITY TESTS"
run_test "Extreme Stress Conditions" "python tests/stress/test_extreme_stress_conditions.py"
run_test "Adversarial Testing" "python tests/stress/test_adversarial_comprehensive.py"

# Component Tests
echo ""
echo "🔧 COMPONENT TESTS"
run_test "Service Status Check" "python -c \"from src.core.service_manager import get_service_manager; sm = get_service_manager(); print('✅ Services initialized successfully')\""

# Generate Test Report
echo ""
echo "======================================"
echo "📊 TEST RESULTS SUMMARY"
echo "======================================"
echo "Total Tests:   $TOTAL_TESTS"
echo "Passed:        $PASSED_TESTS"
echo "Failed:        $FAILED_TESTS"
echo "Success Rate:  $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo "🎉 ALL TESTS PASSED - SYSTEM FULLY FUNCTIONAL"
    exit 0
else
    echo ""
    echo "⚠️  SOME TESTS FAILED - REVIEW ISSUES ABOVE"
    exit 1
fi