#!/usr/bin/env python3
"""
MCP Server Tool Exposure Validation

Comprehensive validation system to ensure all KGAS tools are properly exposed
and functional through the MCP (Model Context Protocol) interface.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import sys
import inspect
from contextlib import asynccontextmanager

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import MCP components
from ..mcp_tools.server_manager import MCPServerManager, get_mcp_server_manager
from ..tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools, Phase1MCPToolsManager

# Import tool registry
from ..tools.tool_registry import ToolRegistry, ImplementationStatus

logger = logging.getLogger(__name__)


class ToolExposureStatus(Enum):
    """Tool exposure validation status"""
    EXPOSED = "exposed"
    NOT_EXPOSED = "not_exposed"
    EXPOSED_BUT_BROKEN = "exposed_but_broken"
    PARTIALLY_EXPOSED = "partially_exposed"
    UNKNOWN = "unknown"


class ValidationSeverity(Enum):
    """Validation issue severity"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ToolExposureResult:
    """Result of tool exposure validation"""
    tool_id: str
    tool_name: str
    exposure_status: ToolExposureStatus
    is_callable: bool = False
    mcp_functions_found: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationIssue:
    """Validation issue report"""
    severity: ValidationSeverity
    component: str
    issue_type: str
    description: str
    recommendation: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MCPToolValidationConfig:
    """Configuration for MCP tool validation"""
    test_timeout_seconds: float = 30.0
    enable_deep_testing: bool = True
    enable_performance_testing: bool = False
    test_with_sample_data: bool = True
    validate_tool_contracts: bool = True
    check_error_handling: bool = True
    validate_parameter_schemas: bool = True


class MCPToolExposureValidator:
    """Comprehensive MCP tool exposure validation system"""
    
    def __init__(self, config: Optional[MCPToolValidationConfig] = None):
        """Initialize MCP tool exposure validator"""
        self.config = config or MCPToolValidationConfig()
        self.tool_registry = ToolRegistry()
        
        # Validation state
        self.validation_results = {}
        self.validation_issues = []
        self.server_manager = None
        self.mcp_server = None
        
        # Expected tool mappings
        self.expected_phase1_tools = {
            "T01_PDF_LOADER": ["load_documents", "get_pdf_loader_info"],
            "T15A_TEXT_CHUNKER": ["chunk_text", "get_text_chunker_info"],
            "T23A_SPACY_NER": ["extract_entities", "get_supported_entity_types", "get_entity_extractor_info", "get_spacy_model_info"],
            "T27_RELATIONSHIP_EXTRACTOR": ["extract_relationships", "get_supported_relationship_types", "get_relationship_extractor_info"],
            "T31_ENTITY_BUILDER": ["build_entities", "get_entity_builder_info"],
            "T34_EDGE_BUILDER": ["build_edges", "get_edge_builder_info"],
            "T68_PAGERANK": ["calculate_pagerank", "get_top_entities", "get_pagerank_calculator_info"],
            "T49_MULTIHOP_QUERY": ["query_graph", "get_query_engine_info"]
        }
        
        self.expected_service_tools = {
            "IDENTITY_SERVICE": ["create_mention", "get_entity_by_mention", "link_mentions"],
            "PROVENANCE_SERVICE": ["start_operation", "complete_operation", "get_operation_lineage"],
            "QUALITY_SERVICE": ["assess_confidence", "propagate_confidence", "get_quality_report"],
            "WORKFLOW_SERVICE": ["create_checkpoint", "restore_checkpoint", "get_workflow_state"]
        }
        
        self.expected_server_tools = {
            "SERVER_MANAGEMENT": ["test_connection", "echo", "get_system_status"]
        }
        
        logger.info("MCP Tool Exposure Validator initialized")
    
    async def initialize_mcp_server(self) -> bool:
        """Initialize MCP server for validation"""
        try:
            logger.info("Initializing MCP server for validation...")
            
            # Get server manager
            self.server_manager = get_mcp_server_manager()
            
            # Register all tools
            self.server_manager.register_all_tools()
            
            # Get the FastMCP server instance
            self.mcp_server = self.server_manager.get_server()
            
            # Also register Phase 1 tools
            phase1_manager = Phase1MCPToolsManager()
            create_phase1_mcp_tools(self.mcp_server)
            
            logger.info("MCP server initialized successfully for validation")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {e}", exc_info=True)
            self._add_validation_issue(
                ValidationSeverity.CRITICAL,
                "MCP_SERVER",
                "INITIALIZATION_FAILED",
                f"MCP server initialization failed: {str(e)}",
                "Check MCP server configuration and dependencies"
            )
            return False
    
    async def validate_all_tool_exposure(self) -> Dict[str, Any]:
        """Validate exposure of all tools through MCP interface"""
        logger.info("Starting comprehensive MCP tool exposure validation...")
        
        start_time = time.time()
        
        # Initialize MCP server if not already done
        if not self.mcp_server:
            if not await self.initialize_mcp_server():
                return self._create_validation_summary(False, "MCP server initialization failed")
        
        # Validate different tool categories
        await self._validate_phase1_tool_exposure()
        await self._validate_service_tool_exposure()
        await self._validate_server_tool_exposure()
        await self._validate_tool_discoverability()
        
        if self.config.enable_deep_testing:
            await self._validate_tool_functionality()
        
        if self.config.validate_tool_contracts:
            await self._validate_tool_contracts()
        
        execution_time = time.time() - start_time
        
        # Generate validation summary
        return self._create_validation_summary(True, f"Validation completed in {execution_time:.2f}s")
    
    async def _validate_phase1_tool_exposure(self):
        """Validate Phase 1 tools are properly exposed"""
        logger.info("Validating Phase 1 tool exposure...")
        
        for tool_id, expected_functions in self.expected_phase1_tools.items():
            result = await self._validate_tool_exposure(
                tool_id, 
                expected_functions,
                category="phase1"
            )
            self.validation_results[tool_id] = result
    
    async def _validate_service_tool_exposure(self):
        """Validate core service tools are properly exposed"""
        logger.info("Validating service tool exposure...")
        
        for service_id, expected_functions in self.expected_service_tools.items():
            result = await self._validate_tool_exposure(
                service_id,
                expected_functions, 
                category="service"
            )
            self.validation_results[service_id] = result
    
    async def _validate_server_tool_exposure(self):
        """Validate server management tools are properly exposed"""
        logger.info("Validating server management tool exposure...")
        
        for tool_group, expected_functions in self.expected_server_tools.items():
            result = await self._validate_tool_exposure(
                tool_group,
                expected_functions,
                category="server"
            )
            self.validation_results[tool_group] = result
    
    async def _validate_tool_exposure(self, tool_id: str, expected_functions: List[str], category: str) -> ToolExposureResult:
        """Validate exposure of a specific tool"""
        logger.debug(f"Validating tool exposure: {tool_id}")
        
        result = ToolExposureResult(
            tool_id=tool_id,
            tool_name=tool_id.replace("_", " ").title(),
            exposure_status=ToolExposureStatus.UNKNOWN,
            metadata={"category": category}
        )
        
        try:
            # Get all available MCP tools
            available_tools = self._get_available_mcp_tools()
            
            # Check which expected functions are available
            found_functions = []
            missing_functions = []
            
            for func_name in expected_functions:
                if func_name in available_tools:
                    found_functions.append(func_name)
                else:
                    missing_functions.append(func_name)
            
            result.mcp_functions_found = found_functions
            
            # Determine exposure status
            if len(found_functions) == len(expected_functions):
                result.exposure_status = ToolExposureStatus.EXPOSED
            elif len(found_functions) > 0:
                result.exposure_status = ToolExposureStatus.PARTIALLY_EXPOSED
                result.validation_errors.append(f"Missing functions: {missing_functions}")
            else:
                result.exposure_status = ToolExposureStatus.NOT_EXPOSED
                result.validation_errors.append(f"No functions found for {tool_id}")
            
            # Test function callability if exposed
            if found_functions and self.config.enable_deep_testing:
                await self._test_tool_callability(result, found_functions)
            
        except Exception as e:
            logger.error(f"Error validating tool {tool_id}: {e}")
            result.exposure_status = ToolExposureStatus.UNKNOWN
            result.validation_errors.append(f"Validation error: {str(e)}")
        
        return result
    
    def _get_available_mcp_tools(self) -> Set[str]:
        """Get list of all available MCP tools"""
        if not self.mcp_server:
            return set()
        
        try:
            # Get tools from FastMCP server
            # This is implementation-specific to FastMCP
            tools = set()
            
            # Check if the server has a tools registry or similar
            if hasattr(self.mcp_server, '_tools'):
                tools.update(self.mcp_server._tools.keys())
            elif hasattr(self.mcp_server, 'tools'):
                tools.update(self.mcp_server.tools.keys())
            
            # Also check server manager tools
            if self.server_manager:
                server_info = self.server_manager.get_server_info()
                tool_collections = server_info.get('tool_collections', {})
                for collection_info in tool_collections.values():
                    if 'tools' in collection_info:
                        tools.update(collection_info['tools'])
            
            return tools
            
        except Exception as e:
            logger.error(f"Error getting available MCP tools: {e}")
            return set()
    
    async def _test_tool_callability(self, result: ToolExposureResult, function_names: List[str]):
        """Test if exposed tools are actually callable"""
        logger.debug(f"Testing callability for {result.tool_id}")
        
        for func_name in function_names:
            try:
                # Test with appropriate sample data
                test_result = await self._call_mcp_function_with_test_data(func_name)
                result.test_results[func_name] = test_result
                
                if test_result.get('success', False):
                    result.is_callable = True
                else:
                    result.validation_errors.append(f"Function {func_name} not callable: {test_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Error testing function {func_name}: {e}")
                result.test_results[func_name] = {
                    'success': False,
                    'error': str(e),
                    'error_type': 'test_exception'
                }
                result.validation_errors.append(f"Test error for {func_name}: {str(e)}")
        
        # Update exposure status based on callability
        if result.is_callable:
            if result.exposure_status == ToolExposureStatus.EXPOSED:
                pass  # Keep as EXPOSED
            elif result.exposure_status == ToolExposureStatus.PARTIALLY_EXPOSED:
                pass  # Keep as PARTIALLY_EXPOSED
        else:
            if result.exposure_status == ToolExposureStatus.EXPOSED:
                result.exposure_status = ToolExposureStatus.EXPOSED_BUT_BROKEN
            elif result.exposure_status == ToolExposureStatus.PARTIALLY_EXPOSED:
                result.exposure_status = ToolExposureStatus.EXPOSED_BUT_BROKEN
    
    async def _call_mcp_function_with_test_data(self, func_name: str) -> Dict[str, Any]:
        """Call MCP function with appropriate test data"""
        try:
            # Define test data for different function types
            test_data_map = {
                # Server management tools
                'test_connection': {},
                'echo': {'message': 'test'},
                'get_system_status': {},
                
                # Info/status functions (should work without parameters)
                'get_pdf_loader_info': {},
                'get_text_chunker_info': {},
                'get_entity_extractor_info': {},
                'get_spacy_model_info': {},
                'get_supported_entity_types': {},
                'get_supported_relationship_types': {},
                'get_relationship_extractor_info': {},
                'get_entity_builder_info': {},
                'get_edge_builder_info': {},
                'get_pagerank_calculator_info': {},
                'get_query_engine_info': {},
                'get_phase1_tool_registry': {},
                'validate_phase1_pipeline': {},
                'get_graph_statistics': {},
                
                # Functions that need minimal data
                'load_documents': {'document_paths': []},  # Empty list should not fail
                'chunk_text': {
                    'document_ref': 'test_doc',
                    'text': 'This is a test text for chunking.',
                    'document_confidence': 0.8
                },
                'extract_entities': {
                    'chunk_ref': 'test_chunk',
                    'text': 'John Smith works at OpenAI in San Francisco.',
                    'chunk_confidence': 0.8
                },
                'query_graph': {
                    'query_text': 'test query',
                    'max_hops': 1,
                    'result_limit': 5
                }
            }
            
            # Get test data for this function
            test_data = test_data_map.get(func_name, {})
            
            # Call the function via MCP server
            if hasattr(self.mcp_server, 'call_tool'):
                # If server has a call_tool method
                result = await self.mcp_server.call_tool(func_name, **test_data)
            elif hasattr(self.mcp_server, '_tools') and func_name in self.mcp_server._tools:
                # Direct function call
                func = self.mcp_server._tools[func_name]
                if asyncio.iscoroutinefunction(func):
                    result = await func(**test_data)
                else:
                    result = func(**test_data)
            else:
                return {
                    'success': False,
                    'error': f'Function {func_name} not found in MCP server',
                    'error_type': 'function_not_found'
                }
            
            return {
                'success': True,
                'result': result,
                'test_data': test_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'call_exception',
                'test_data': test_data_map.get(func_name, {})
            }
    
    async def _validate_tool_discoverability(self):
        """Validate that tools can be discovered through standard MCP mechanisms"""
        logger.info("Validating tool discoverability...")
        
        try:
            # Test server info endpoint
            if self.server_manager:
                server_info = self.server_manager.get_server_info()
                total_tools = server_info.get('total_tools', 0)
                
                if total_tools == 0:
                    self._add_validation_issue(
                        ValidationSeverity.ERROR,
                        "DISCOVERABILITY",
                        "NO_TOOLS_REPORTED",
                        "Server reports 0 total tools",
                        "Check tool registration process"
                    )
                else:
                    logger.info(f"Server reports {total_tools} total tools")
            
            # Test system status endpoint
            try:
                if hasattr(self.mcp_server, '_tools') and 'get_system_status' in self.mcp_server._tools:
                    status_func = self.mcp_server._tools['get_system_status']
                    status_result = status_func()
                    
                    if isinstance(status_result, dict) and 'total_tools' in status_result:
                        logger.info(f"System status reports {status_result['total_tools']} tools")
                    else:
                        self._add_validation_issue(
                            ValidationSeverity.WARNING,
                            "DISCOVERABILITY",
                            "INCOMPLETE_STATUS",
                            "System status does not report tool count",
                            "Enhance system status endpoint"
                        )
                        
            except Exception as e:
                self._add_validation_issue(
                    ValidationSeverity.WARNING,
                    "DISCOVERABILITY",
                    "STATUS_ERROR",
                    f"Error calling system status: {str(e)}",
                    "Check system status implementation"
                )
            
        except Exception as e:
            logger.error(f"Error validating discoverability: {e}")
            self._add_validation_issue(
                ValidationSeverity.ERROR,
                "DISCOVERABILITY",
                "VALIDATION_ERROR",
                f"Discoverability validation failed: {str(e)}",
                "Check MCP server implementation"
            )
    
    async def _validate_tool_functionality(self):
        """Deep validation of tool functionality"""
        logger.info("Validating tool functionality...")
        
        # Test critical path: info functions should always work
        critical_functions = [
            'test_connection',
            'get_system_status',
            'get_phase1_tool_registry',
            'validate_phase1_pipeline'
        ]
        
        for func_name in critical_functions:
            try:
                test_result = await self._call_mcp_function_with_test_data(func_name)
                if not test_result.get('success', False):
                    self._add_validation_issue(
                        ValidationSeverity.ERROR,
                        "FUNCTIONALITY",
                        "CRITICAL_FUNCTION_FAILED",
                        f"Critical function {func_name} failed: {test_result.get('error', 'Unknown')}",
                        f"Fix implementation of {func_name}"
                    )
                else:
                    logger.debug(f"Critical function {func_name} working correctly")
                    
            except Exception as e:
                self._add_validation_issue(
                    ValidationSeverity.ERROR,
                    "FUNCTIONALITY", 
                    "CRITICAL_FUNCTION_ERROR",
                    f"Error testing critical function {func_name}: {str(e)}",
                    f"Debug implementation of {func_name}"
                )
    
    async def _validate_tool_contracts(self):
        """Validate tool contracts and parameter schemas"""
        logger.info("Validating tool contracts...")
        
        # This would validate that tools implement expected interfaces
        # For now, we'll validate that info functions return expected data structures
        
        info_functions = [
            'get_pdf_loader_info',
            'get_entity_extractor_info',
            'get_pagerank_calculator_info'
        ]
        
        for func_name in info_functions:
            try:
                test_result = await self._call_mcp_function_with_test_data(func_name)
                if test_result.get('success', False):
                    result_data = test_result.get('result', {})
                    
                    # Validate expected fields in tool info
                    expected_fields = ['tool_id', 'status', 'description']
                    missing_fields = [field for field in expected_fields if field not in result_data]
                    
                    if missing_fields:
                        self._add_validation_issue(
                            ValidationSeverity.WARNING,
                            "CONTRACTS",
                            "MISSING_INFO_FIELDS",
                            f"Tool info for {func_name} missing fields: {missing_fields}",
                            "Standardize tool info response format"
                        )
                        
            except Exception as e:
                logger.error(f"Error validating contract for {func_name}: {e}")
    
    def _add_validation_issue(self, severity: ValidationSeverity, component: str, 
                            issue_type: str, description: str, recommendation: str, 
                            details: Dict[str, Any] = None):
        """Add a validation issue to the report"""
        issue = ValidationIssue(
            severity=severity,
            component=component,
            issue_type=issue_type,
            description=description,
            recommendation=recommendation,
            details=details or {}
        )
        self.validation_issues.append(issue)
        
        # Log based on severity
        if severity == ValidationSeverity.CRITICAL:
            logger.error(f"CRITICAL: {description}")
        elif severity == ValidationSeverity.ERROR:
            logger.error(f"ERROR: {description}")
        elif severity == ValidationSeverity.WARNING:
            logger.warning(f"WARNING: {description}")
        else:
            logger.info(f"INFO: {description}")
    
    def _create_validation_summary(self, success: bool, message: str) -> Dict[str, Any]:
        """Create comprehensive validation summary"""
        
        # Calculate statistics
        total_tools = len(self.validation_results)
        exposed_tools = sum(1 for r in self.validation_results.values() 
                          if r.exposure_status == ToolExposureStatus.EXPOSED)
        partially_exposed = sum(1 for r in self.validation_results.values()
                              if r.exposure_status == ToolExposureStatus.PARTIALLY_EXPOSED)
        not_exposed = sum(1 for r in self.validation_results.values()
                        if r.exposure_status == ToolExposureStatus.NOT_EXPOSED)
        broken_tools = sum(1 for r in self.validation_results.values()
                         if r.exposure_status == ToolExposureStatus.EXPOSED_BUT_BROKEN)
        
        # Calculate exposure rate
        exposure_rate = (exposed_tools / total_tools * 100) if total_tools > 0 else 0
        
        # Count issues by severity
        issue_counts = {}
        for severity in ValidationSeverity:
            issue_counts[severity.value] = sum(1 for issue in self.validation_issues 
                                             if issue.severity == severity)
        
        # Determine overall status
        if not success:
            overall_status = "FAILED"
        elif broken_tools > 0 or issue_counts.get('critical', 0) > 0:
            overall_status = "CRITICAL_ISSUES"
        elif issue_counts.get('error', 0) > 0:
            overall_status = "ERRORS_FOUND"
        elif issue_counts.get('warning', 0) > 0:
            overall_status = "WARNINGS_FOUND"
        else:
            overall_status = "HEALTHY"
        
        return {
            'validation_summary': {
                'overall_status': overall_status,
                'success': success,
                'message': message,
                'timestamp': datetime.now().isoformat()
            },
            'tool_exposure_statistics': {
                'total_tools_validated': total_tools,
                'fully_exposed': exposed_tools,
                'partially_exposed': partially_exposed,
                'not_exposed': not_exposed,
                'exposed_but_broken': broken_tools,
                'exposure_rate_percent': exposure_rate
            },
            'validation_issues': {
                'total_issues': len(self.validation_issues),
                'by_severity': issue_counts,
                'issues': [
                    {
                        'severity': issue.severity.value,
                        'component': issue.component,
                        'type': issue.issue_type,
                        'description': issue.description,
                        'recommendation': issue.recommendation,
                        'timestamp': issue.timestamp.isoformat()
                    }
                    for issue in self.validation_issues
                ]
            },
            'tool_results': {
                tool_id: {
                    'tool_name': result.tool_name,
                    'exposure_status': result.exposure_status.value,
                    'is_callable': result.is_callable,
                    'functions_found': result.mcp_functions_found,
                    'validation_errors': result.validation_errors,
                    'test_results': result.test_results,
                    'category': result.metadata.get('category', 'unknown')
                }
                for tool_id, result in self.validation_results.items()
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Check exposure rate
        total_tools = len(self.validation_results)
        exposed_tools = sum(1 for r in self.validation_results.values() 
                          if r.exposure_status == ToolExposureStatus.EXPOSED)
        exposure_rate = (exposed_tools / total_tools * 100) if total_tools > 0 else 0
        
        if exposure_rate < 50:
            recommendations.append("LOW PRIORITY: Less than 50% of tools are fully exposed via MCP - consider implementing missing tools")
        elif exposure_rate < 80:
            recommendations.append("MEDIUM PRIORITY: Tool exposure rate could be improved - implement remaining tools")
        else:
            recommendations.append("GOOD: High tool exposure rate achieved")
        
        # Check for broken tools
        broken_tools = sum(1 for r in self.validation_results.values()
                         if r.exposure_status == ToolExposureStatus.EXPOSED_BUT_BROKEN)
        if broken_tools > 0:
            recommendations.append(f"HIGH PRIORITY: {broken_tools} tools are exposed but not functional - fix implementation")
        
        # Check for critical issues
        critical_issues = sum(1 for issue in self.validation_issues 
                            if issue.severity == ValidationSeverity.CRITICAL)
        if critical_issues > 0:
            recommendations.append(f"URGENT: {critical_issues} critical issues found - address immediately")
        
        # Check for missing Phase 1 tools
        phase1_tools = {k: v for k, v in self.validation_results.items() if k.startswith('T')}
        missing_phase1 = sum(1 for r in phase1_tools.values()
                           if r.exposure_status == ToolExposureStatus.NOT_EXPOSED)
        if missing_phase1 > 0:
            recommendations.append(f"MEDIUM PRIORITY: {missing_phase1} Phase 1 tools not exposed - complete implementation")
        
        return recommendations
    
    async def export_validation_report(self, output_path: str) -> bool:
        """Export detailed validation report"""
        try:
            validation_summary = self._create_validation_summary(True, "Report exported")
            
            # Add additional details for report
            report = {
                **validation_summary,
                'export_metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'validator_config': {
                        'test_timeout_seconds': self.config.test_timeout_seconds,
                        'deep_testing_enabled': self.config.enable_deep_testing,
                        'contract_validation_enabled': self.config.validate_tool_contracts
                    }
                }
            }
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Validation report exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export validation report: {e}")
            return False


# Command line interface
async def main():
    """Main entry point for MCP tool validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="KGAS MCP Tool Exposure Validator")
    parser.add_argument("--output", type=str, help="Output path for validation report")
    parser.add_argument("--deep-testing", action="store_true", help="Enable deep functionality testing")
    parser.add_argument("--timeout", type=float, default=30.0, help="Test timeout in seconds")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create validator config
    config = MCPToolValidationConfig(
        test_timeout_seconds=args.timeout,
        enable_deep_testing=args.deep_testing
    )
    
    # Create and run validator
    validator = MCPToolExposureValidator(config)
    
    try:
        # Run validation
        logger.info("Starting MCP tool exposure validation...")
        results = await validator.validate_all_tool_exposure()
        
        # Print summary
        print(f"\nMCP Tool Exposure Validation Results")
        print("=" * 50)
        print(f"Overall Status: {results['validation_summary']['overall_status']}")
        print(f"Total Tools Validated: {results['tool_exposure_statistics']['total_tools_validated']}")
        print(f"Fully Exposed: {results['tool_exposure_statistics']['fully_exposed']}")
        print(f"Exposure Rate: {results['tool_exposure_statistics']['exposure_rate_percent']:.1f}%")
        print(f"Issues Found: {results['validation_issues']['total_issues']}")
        
        # Print recommendations
        if results['recommendations']:
            print(f"\nRecommendations:")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # Export report if requested
        if args.output:
            success = await validator.export_validation_report(args.output)
            if success:
                print(f"\nDetailed report exported to: {args.output}")
            else:
                print(f"\nFailed to export report to: {args.output}")
        
        return 0 if results['validation_summary']['success'] else 1
        
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))