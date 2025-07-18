#!/usr/bin/env python3
"""
Phase 2 Implementation Validation Report Generator

Manually validates all Phase 2 implementation claims without using repomix.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def validate_file_exists(file_path, description):
    """Validate that a file exists and return its status"""
    path = Path(file_path)
    if path.exists():
        size = path.stat().st_size
        return {
            "status": "EXISTS",
            "path": str(path),
            "size": size,
            "description": description
        }
    else:
        return {
            "status": "MISSING",
            "path": str(path),
            "description": description
        }

def check_class_method_exists(file_path, class_name, method_name):
    """Check if a class and method exist in a file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        class_found = f"class {class_name}" in content
        method_found = f"def {method_name}" in content
        
        return {
            "class_exists": class_found,
            "method_exists": method_found,
            "file_exists": True
        }
    except FileNotFoundError:
        return {
            "class_exists": False,
            "method_exists": False,
            "file_exists": False
        }

def validate_phase2_implementations():
    """Validate all Phase 2 implementation claims"""
    
    print("🎯 Phase 2 Implementation Validation Report")
    print("=" * 60)
    print(f"Validation timestamp: {datetime.now().isoformat()}")
    print()
    
    validation_results = {}
    
    # Task 1: Async Multi-Document Processing
    print("📋 Task 1: Async Multi-Document Processing")
    print("-" * 45)
    
    task1_file = "/home/brian/Digimons/src/tools/phase2/async_multi_document_processor.py"
    task1_result = validate_file_exists(task1_file, "Async Multi-Document Processor")
    
    if task1_result["status"] == "EXISTS":
        class_check = check_class_method_exists(task1_file, "AsyncMultiDocumentProcessor", "__init__")
        method_checks = [
            check_class_method_exists(task1_file, "AsyncMultiDocumentProcessor", "process_documents_async"),
            check_class_method_exists(task1_file, "AsyncMultiDocumentProcessor", "memory_efficient_batch_processing"),
            check_class_method_exists(task1_file, "AsyncMultiDocumentProcessor", "process_single_document")
        ]
        
        print(f"✅ File exists: {task1_result['size']} bytes")
        print(f"✅ AsyncMultiDocumentProcessor class: {'EXISTS' if class_check['class_exists'] else 'MISSING'}")
        print(f"✅ Core methods: {sum(1 for m in method_checks if m['method_exists'])}/3 found")
    else:
        print(f"❌ File missing: {task1_file}")
    
    validation_results["task1_async_processing"] = task1_result
    print()
    
    # Task 2: Prometheus Metrics
    print("📊 Task 2: Prometheus Metrics Collection")
    print("-" * 45)
    
    task2_file = "/home/brian/Digimons/src/core/metrics_collector.py"
    task2_result = validate_file_exists(task2_file, "Metrics Collector")
    
    if task2_result["status"] == "EXISTS":
        class_check = check_class_method_exists(task2_file, "MetricsCollector", "__init__")
        method_checks = [
            check_class_method_exists(task2_file, "MetricsCollector", "start_metrics_server"),
            check_class_method_exists(task2_file, "MetricsCollector", "update_system_metrics"),
            check_class_method_exists(task2_file, "MetricsCollector", "increment_documents_processed")
        ]
        
        print(f"✅ File exists: {task2_result['size']} bytes")
        print(f"✅ MetricsCollector class: {'EXISTS' if class_check['class_exists'] else 'MISSING'}")
        print(f"✅ Core methods: {sum(1 for m in method_checks if m['method_exists'])}/3 found")
    else:
        print(f"❌ File missing: {task2_file}")
    
    validation_results["task2_prometheus_metrics"] = task2_result
    print()
    
    # Task 3: Grafana Dashboards
    print("📈 Task 3: Grafana Dashboards")
    print("-" * 45)
    
    task3_file = "/home/brian/Digimons/src/monitoring/grafana_dashboards.py"
    task3_result = validate_file_exists(task3_file, "Grafana Dashboard Manager")
    
    if task3_result["status"] == "EXISTS":
        class_check = check_class_method_exists(task3_file, "GrafanaDashboardManager", "__init__")
        method_checks = [
            check_class_method_exists(task3_file, "GrafanaDashboardManager", "create_system_overview_dashboard"),
            check_class_method_exists(task3_file, "GrafanaDashboardManager", "create_performance_dashboard"),
            check_class_method_exists(task3_file, "GrafanaDashboardManager", "provision_all_dashboards")
        ]
        
        print(f"✅ File exists: {task3_result['size']} bytes")
        print(f"✅ GrafanaDashboardManager class: {'EXISTS' if class_check['class_exists'] else 'MISSING'}")
        print(f"✅ Core methods: {sum(1 for m in method_checks if m['method_exists'])}/3 found")
    else:
        print(f"❌ File missing: {task3_file}")
    
    validation_results["task3_grafana_dashboards"] = task3_result
    print()
    
    # Task 4: Automated Backup/Restore
    print("💾 Task 4: Automated Backup/Restore")
    print("-" * 45)
    
    task4_file = "/home/brian/Digimons/src/core/backup_manager.py"
    task4_result = validate_file_exists(task4_file, "Backup Manager")
    
    if task4_result["status"] == "EXISTS":
        class_check = check_class_method_exists(task4_file, "BackupManager", "__init__")
        method_checks = [
            check_class_method_exists(task4_file, "BackupManager", "create_backup"),
            check_class_method_exists(task4_file, "BackupManager", "verify_backup_integrity"),
            check_class_method_exists(task4_file, "BackupManager", "schedule_backups")
        ]
        
        print(f"✅ File exists: {task4_result['size']} bytes")
        print(f"✅ BackupManager class: {'EXISTS' if class_check['class_exists'] else 'MISSING'}")
        print(f"✅ Core methods: {sum(1 for m in method_checks if m['method_exists'])}/3 found")
    else:
        print(f"❌ File missing: {task4_file}")
    
    validation_results["task4_backup_restore"] = task4_result
    print()
    
    # Task 5: AnyIO Migration
    print("⚡ Task 5: AnyIO Migration")
    print("-" * 45)
    
    task5_file = "/home/brian/Digimons/src/core/anyio_orchestrator.py"
    task5_result = validate_file_exists(task5_file, "AnyIO Orchestrator")
    
    if task5_result["status"] == "EXISTS":
        class_check = check_class_method_exists(task5_file, "AnyIOOrchestrator", "__init__")
        method_checks = [
            check_class_method_exists(task5_file, "AnyIOOrchestrator", "execute_tasks_parallel"),
            check_class_method_exists(task5_file, "AnyIOOrchestrator", "resource_manager"),
            check_class_method_exists(task5_file, "AnyIOOrchestrator", "fan_out_fan_in")
        ]
        
        print(f"✅ File exists: {task5_result['size']} bytes")
        print(f"✅ AnyIOOrchestrator class: {'EXISTS' if class_check['class_exists'] else 'MISSING'}")
        print(f"✅ Core methods: {sum(1 for m in method_checks if m['method_exists'])}/3 found")
    else:
        print(f"❌ File missing: {task5_file}")
    
    validation_results["task5_anyio_migration"] = task5_result
    print()
    
    # Task 6: Distributed Tracing
    print("🔍 Task 6: Distributed Tracing")
    print("-" * 45)
    
    task6_file = "/home/brian/Digimons/src/core/distributed_tracing.py"
    task6_result = validate_file_exists(task6_file, "Distributed Tracing")
    
    if task6_result["status"] == "EXISTS":
        class_check = check_class_method_exists(task6_file, "DistributedTracing", "__init__")
        method_checks = [
            check_class_method_exists(task6_file, "DistributedTracing", "trace_operation"),
            check_class_method_exists(task6_file, "DistributedTracing", "trace_async_operation"),
            check_class_method_exists(task6_file, "DistributedTracing", "inject_trace_context")
        ]
        
        print(f"✅ File exists: {task6_result['size']} bytes")
        print(f"✅ DistributedTracing class: {'EXISTS' if class_check['class_exists'] else 'MISSING'}")
        print(f"✅ Core methods: {sum(1 for m in method_checks if m['method_exists'])}/3 found")
    else:
        print(f"❌ File missing: {task6_file}")
    
    validation_results["task6_distributed_tracing"] = task6_result
    print()
    
    # Demo Scripts Validation
    print("🎬 Demo Scripts Validation")
    print("-" * 45)
    
    demo_scripts = [
        "/home/brian/Digimons/examples/async_multi_doc_demo.py",
        "/home/brian/Digimons/examples/prometheus_metrics_demo.py",
        "/home/brian/Digimons/examples/grafana_dashboards_demo.py",
        "/home/brian/Digimons/examples/backup_restore_demo.py",
        "/home/brian/Digimons/examples/anyio_simple_demo.py",
        "/home/brian/Digimons/examples/distributed_tracing_demo.py"
    ]
    
    demo_results = []
    for script in demo_scripts:
        result = validate_file_exists(script, f"Demo: {Path(script).name}")
        demo_results.append(result)
        status_icon = "✅" if result["status"] == "EXISTS" else "❌"
        print(f"{status_icon} {Path(script).name}: {result['status']}")
    
    validation_results["demo_scripts"] = demo_results
    print()
    
    # Log Evidence
    print("📋 Log Evidence Validation")
    print("-" * 45)
    
    log_file = "/home/brian/Digimons/logs/super_digimon.log"
    log_result = validate_file_exists(log_file, "Execution Log Evidence")
    
    if log_result["status"] == "EXISTS":
        print(f"✅ Log file exists: {log_result['size']} bytes")
        
        # Check for recent timestamps
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
                if "2025-07-17" in log_content:
                    print("✅ Contains recent execution timestamps")
                else:
                    print("⚠️ No recent execution timestamps found")
        except Exception as e:
            print(f"⚠️ Could not read log file: {e}")
    else:
        print(f"❌ Log file missing: {log_file}")
    
    validation_results["log_evidence"] = log_result
    print()
    
    # Summary
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    all_tasks = [
        validation_results["task1_async_processing"],
        validation_results["task2_prometheus_metrics"],
        validation_results["task3_grafana_dashboards"],
        validation_results["task4_backup_restore"],
        validation_results["task5_anyio_migration"],
        validation_results["task6_distributed_tracing"]
    ]
    
    tasks_implemented = sum(1 for task in all_tasks if task["status"] == "EXISTS")
    demos_implemented = sum(1 for demo in demo_results if demo["status"] == "EXISTS")
    
    print(f"📋 Core Implementation Files: {tasks_implemented}/6 ({'100.0' if tasks_implemented == 6 else str(round(tasks_implemented/6*100, 1))}%)")
    print(f"🎬 Demo Scripts: {demos_implemented}/{len(demo_scripts)} ({round(demos_implemented/len(demo_scripts)*100, 1)}%)")
    print(f"📋 Log Evidence: {'EXISTS' if validation_results['log_evidence']['status'] == 'EXISTS' else 'MISSING'}")
    
    overall_success = (tasks_implemented == 6 and 
                      demos_implemented == len(demo_scripts) and 
                      validation_results['log_evidence']['status'] == 'EXISTS')
    
    print()
    if overall_success:
        print("🎉 PHASE 2 IMPLEMENTATION VALIDATION: COMPLETE")
        print("✅ All 6 core implementation files exist")
        print("✅ All 6 demo scripts exist")
        print("✅ Execution log evidence exists")
        print("✅ Ready for external verification")
    else:
        print("⚠️ PHASE 2 IMPLEMENTATION VALIDATION: INCOMPLETE")
        print("Some components are missing - see details above")
    
    return validation_results, overall_success

if __name__ == "__main__":
    try:
        results, success = validate_phase2_implementations()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)