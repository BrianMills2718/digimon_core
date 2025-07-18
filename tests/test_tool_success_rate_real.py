import pytest
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.tool_factory import ToolFactory
from core.evidence_logger import EvidenceLogger

class TestToolSuccessRateReal:
    """REAL tool testing with NO MOCKS - Zero Tolerance for Deceptive Practices"""
    
    def test_tool_discovery_real(self):
        """Test that tools can be ACTUALLY discovered and instantiated"""
        tool_factory = ToolFactory()
        discovered_tools = tool_factory.discover_all_tools()
        
        assert len(discovered_tools) > 0, "No tools discovered"
        
        # Verify ACTUAL tool discovery, not just file existence
        working_tools = 0
        for tool_name, tool_info in discovered_tools.items():
            if tool_info.get("status") == "discovered" and "classes" in tool_info:
                working_tools += 1
                
        assert working_tools >= 1, f"Expected at least 1 working tool, found {working_tools}"
        
    def test_tool_functionality_real(self):
        """Test ACTUAL tool functionality audit with real instantiation"""
        tool_factory = ToolFactory()
        audit_results = tool_factory.audit_all_tools()
        
        assert audit_results["total_tools"] > 0, "No tools found for audit"
        
        # Verify ACTUAL functionality, not mocked results
        real_working_tools = 0
        for tool_name, result in audit_results["tool_results"].items():
            if result.get("status") == "working":
                real_working_tools += 1
                
        assert real_working_tools >= 1, f"Expected at least 1 actually working tool, found {real_working_tools}"
        
    def test_success_rate_calculation_real(self):
        """Test that success rate reflects ACTUAL functionality"""
        tool_factory = ToolFactory()
        success_rate = tool_factory.get_success_rate()
        
        # Get detailed audit for verification
        audit = tool_factory.audit_all_tools()
        calculated_rate = (audit["working_tools"] / audit["total_tools"]) * 100 if audit["total_tools"] > 0 else 0
        
        assert abs(success_rate - calculated_rate) < 0.1, f"Success rate calculation error: {success_rate} vs {calculated_rate}"
        assert success_rate >= 5.0, f"Success rate {success_rate:.1f}% indicates total system failure"
        
    def test_evidence_logging_real(self):
        """Test that tool audit results are ACTUALLY logged to evidence"""
        evidence_logger = EvidenceLogger()
        tool_factory = ToolFactory()
        
        audit_results = tool_factory.audit_all_tools()
        success_rate = tool_factory.get_success_rate()
        
        # Log the ACTUAL results
        evidence_data = {
            "audit_results": audit_results,
            "success_rate": success_rate,
            "timestamp": datetime.now().isoformat(),
            "test_type": "real_functionality_test"
        }
        
        verification_hash = evidence_logger.log_with_verification("REAL_TOOL_SUCCESS_RATE_TEST", evidence_data)
        
        assert verification_hash is not None, "Evidence logging failed"
        assert len(verification_hash) == 64, "Invalid verification hash length"
        
        # Verify the evidence was actually written
        assert os.path.exists(evidence_logger.evidence_file), "Evidence file not created"
        
    def test_tool_instantiation_real(self):
        """Test ACTUAL tool instantiation without any mocking"""
        tool_factory = ToolFactory()
        tool_factory.discover_all_tools()
        
        instantiated_tools = []
        failed_instantiations = []
        
        for tool_name, tool_info in tool_factory.discovered_tools.items():
            if "classes" in tool_info:
                for tool_class in tool_info["classes"]:
                    try:
                        # ACTUALLY instantiate the tool
                        instance = tool_class()
                        
                        # Verify it has the required execute method
                        assert hasattr(instance, 'execute'), f"Tool {tool_name} missing execute method"
                        assert callable(instance.execute), f"Tool {tool_name} execute method not callable"
                        
                        instantiated_tools.append(f"{tool_name}.{tool_class.__name__}")
                        
                    except Exception as e:
                        failed_instantiations.append(f"{tool_name}.{tool_class.__name__}: {str(e)}")
        
        # Log ACTUAL instantiation results
        evidence_logger = EvidenceLogger()
        evidence_logger.log_with_verification("REAL_TOOL_INSTANTIATION_TEST", {
            "successful_instantiations": instantiated_tools,
            "failed_instantiations": failed_instantiations,
            "success_count": len(instantiated_tools),
            "failure_count": len(failed_instantiations)
        })
        
        assert len(instantiated_tools) >= 1, f"No tools actually instantiated: {len(instantiated_tools)}"