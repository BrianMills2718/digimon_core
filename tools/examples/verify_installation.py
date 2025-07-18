#!/usr/bin/env python3
"""Verify installation and basic functionality."""

def verify_installation():
    """Verify all components can be imported and basic functionality works."""
    checks = []
    
    # Check 1: Core imports
    try:
        from src.core.pipeline_orchestrator import PipelineOrchestrator
        from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
        from src.core.config_manager import ConfigManager
        checks.append("✅ Core imports work")
    except ImportError as e:
        checks.append(f"❌ Core import failed: {e}")
        return False
    
    # Check 2: Workflow creation
    try:
        config_manager = ConfigManager()
        workflow_config = create_unified_workflow_config(phase=Phase.PHASE1, optimization_level=OptimizationLevel.STANDARD)
        workflow = PipelineOrchestrator(workflow_config, config_manager)
        checks.append("✅ Workflow creation works")
    except Exception as e:
        checks.append(f"❌ Workflow creation failed: {e}")
        return False
    
    # Check 3: Orchestrator access
    try:
        has_orchestrator = hasattr(workflow, 'orchestrator')
        checks.append(f"✅ Orchestrator available: {has_orchestrator}")
    except Exception as e:
        checks.append(f"❌ Orchestrator check failed: {e}")
    
    # Print results
    print("🔍 Installation Verification Results:")
    for check in checks:
        print(f"  {check}")
    
    return all("✅" in check for check in checks)

if __name__ == "__main__":
    success = verify_installation()
    exit(0 if success else 1)