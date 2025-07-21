# KGAS Tool Documentation Standards

**Purpose**: Establish consistent standards for tool documentation, counting, and status tracking  
**Last Updated**: 2025-07-21  
**Applies To**: All T-numbered tools in KGAS system

---

## Tool Count Standards

### Automated Tool Inventory
```bash
# Official tool count command
find src/tools -name "t[0-9]*_*.py" | wc -l

# Detailed tool listing
find src/tools -name "t[0-9]*_*.py" | sort
```

### Tool Count Requirements
1. **Automated Count**: Use standardized find command above
2. **Manual Verification**: Cross-check automated count against documentation claims
3. **Update Frequency**: Verify count monthly and after any tool additions/removals
4. **Documentation Updates**: Update ALL documentation when tool count changes

### Tool Inventory Tracking
Maintain accurate tool inventory in roadmap documentation:

```markdown
## Current Tool Count: [X] Tools

**Phase 1 Tools**: [count]
**Phase 2 Tools**: [count]  
**Phase 3 Tools**: [count]
**Cross-Modal Tools**: [count]
**Infrastructure Tools**: [count]

**Last Verified**: YYYY-MM-DD
**Verification Command**: `find src/tools -name "t[0-9]*_*.py" | wc -l`
```

---

## Tool Status Categories

### Status Definitions

#### **Implemented** ✅
- Tool code exists in proper location
- Basic functionality works (can execute without errors)
- Follows standard tool interface pattern
- Has basic input validation

#### **Tested** 🧪
- Tool has unit tests AND functional tests
- Tests demonstrate actual functionality with real data
- Integration tests show tool works with other components
- Performance tests validate acceptable execution times

#### **Integrated** 🔗
- Tool works in end-to-end workflows
- Properly integrated with service layer (Identity, Provenance, Quality)
- Works with pipeline orchestrator
- Handles failure cases gracefully

#### **Production-Ready** 🚀
- Meets all quality and performance standards
- Comprehensive error handling and logging
- Monitoring and health check integration
- Documentation complete and accurate

### Status Verification Commands

```bash
# Tool count verification
find src/tools -name "t[0-9]*_*.py" | wc -l

# Implementation status check for specific tool
python -c "
from src.tools.phase1.t23a_spacy_ner import SpacyNER
ner = SpacyNER()
result = ner.execute({'text': 'Test text with John Smith.'})
print(f'✅ T23A functional: {len(result.get(\"entities\", []))} entities extracted')
"

# Multi-layer agent implementation check
python -c "
from src.agents.workflow_agent import WorkflowAgent
print('✅ Multi-layer agent: IMPLEMENTED')
"
```

---

## Tool Documentation Requirements

### Tool Header Template
Every tool file must include this header:

```python
"""
Tool ID: T[XXX]
Name: [Tool Name]
Phase: [1|2|3]
Status: [Implemented|Tested|Integrated|Production-Ready]

Purpose: [Brief description of what this tool does]
Inputs: [Description of input data format]
Outputs: [Description of output data format]

Dependencies:
- [List of required services/components]

Integration:
- Identity Service: [Yes/No/Partial]
- Provenance Tracking: [Yes/No/Partial]  
- Quality Assessment: [Yes/No/Partial]

Last Updated: YYYY-MM-DD
"""
```

### Interface Documentation
All tools must document their execute method:

```python
def execute(self, input_data: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute [tool name] functionality.
    
    Args:
        input_data: Dictionary containing:
            - [key1]: [type] - [description]
            - [key2]: [type] - [description]
            
        context: Optional context dictionary containing:
            - validation_mode: bool - If True, use sample data
            - [other context keys]
    
    Returns:
        Dictionary containing:
            - status: str - "success" or "error"  
            - [result_key]: [type] - [description]
            - execution_time: float - Time taken in seconds
            - provenance_id: str - Unique operation identifier
    
    Raises:
        ValueError: [When this is raised]
        ConnectionError: [When this is raised]
    """
```

---

## Testing Standards for Tools

### Required Test Types

#### 1. **Unit Tests** (test_[tool]_unit.py)
```python
def test_tool_initialization():
    """Test tool can be created without errors."""
    
def test_tool_input_validation():
    """Test tool properly validates inputs."""
    
def test_tool_error_handling():
    """Test tool handles various error conditions."""
```

#### 2. **Functional Tests** (test_[tool]_functional.py)
```python
def test_tool_with_real_data():
    """Test tool with actual sample data."""
    
def test_tool_validation_mode():
    """Test tool works in validation mode with sample data."""
    
def test_tool_performance():
    """Test tool meets performance expectations."""
```

#### 3. **Integration Tests** (test_[tool]_integration.py)
```python
def test_tool_with_services():
    """Test tool integration with Identity/Provenance/Quality services."""
    
def test_tool_in_pipeline():
    """Test tool works in pipeline orchestrator."""
    
def test_tool_with_other_tools():
    """Test tool works with upstream/downstream tools."""
```

### Test Data Requirements
- Each tool must have sample test data in `test_data/` directory
- Test data should represent realistic use cases
- Include both positive and negative test cases
- Document test data sources and limitations

---

## Tool Interface Standards

### Standard Execute Method Pattern
```python
class ToolName:
    def __init__(self, service_manager: Optional[ServiceManager] = None):
        """Initialize with service manager for Identity/Provenance/Quality integration."""
        self.service_manager = service_manager or get_service_manager()
        self.identity_service = self.service_manager.identity_service
        self.provenance_service = self.service_manager.provenance_service
        self.quality_service = self.service_manager.quality_service
    
    def execute(self, input_data: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Standard execute method interface."""
        
        # 1. Input validation
        self._validate_inputs(input_data, context)
        
        # 2. Start provenance tracking
        operation_id = self.provenance_service.start_operation(
            operation=f"{self.__class__.__name__}.execute",
            inputs=input_data
        )
        
        try:
            # 3. Handle validation mode
            if context and context.get('validation_mode', False):
                return self._execute_validation_mode(input_data, context)
            
            # 4. Execute main functionality
            result = self._execute_main(input_data, context)
            
            # 5. Quality assessment
            quality_score = self.quality_service.assess_result(result)
            result['quality'] = quality_score
            
            # 6. Complete provenance tracking
            self.provenance_service.complete_operation(operation_id, result)
            result['provenance_id'] = operation_id
            
            return result
            
        except Exception as e:
            # 7. Error handling and logging
            self.provenance_service.log_error(operation_id, str(e))
            return {
                "status": "error",
                "error": str(e),
                "provenance_id": operation_id
            }
```

### Validation Mode Requirements
All tools must support validation mode for testing:
- Use sample data when `context.get('validation_mode') == True`
- Sample data should demonstrate tool functionality
- Validation mode should execute quickly (< 1 second preferred)
- Results should be realistic but can use mock data

---

## Quality Assurance Standards

### Code Quality Requirements
- All tools must pass linting (ruff, mypy)
- Type hints required for all public methods
- Docstrings required for all classes and public methods
- Error handling for all external dependencies

### Performance Standards
- Tool execution time must be reasonable for intended use
- Memory usage should be efficient for expected data sizes
- Tools should handle large inputs gracefully (with appropriate warnings)
- Timeout handling for long-running operations

### Documentation Accuracy
- Tool documentation must match actual implementation
- Parameter descriptions must be accurate and complete
- Example usage must be current and working
- Status headers must reflect actual implementation state

---

## Review and Maintenance

### Monthly Tool Review Process
1. **Count Verification**: Run automated tool count and verify against documentation
2. **Status Verification**: Check tool status claims against actual implementation
3. **Test Status**: Verify all tools have required test coverage
4. **Documentation Check**: Ensure documentation matches implementation
5. **Performance Review**: Check that tools still meet performance standards

### Tool Addition Process
1. **Create tool file** following naming convention (t[XXX]_[name].py)
2. **Implement standard interface** with proper service integration
3. **Add comprehensive tests** (unit, functional, integration)
4. **Update documentation** including tool count and capability registry
5. **Integration testing** to ensure tool works in full pipeline
6. **Update roadmap** to reflect new tool availability

### Tool Deprecation Process
1. **Mark tool as deprecated** in code and documentation
2. **Update tool count** in all relevant documentation
3. **Update capability registry** to reflect removed functionality
4. **Archive tool code** rather than deleting (for historical reference)
5. **Update integration tests** to exclude deprecated tool

---

These standards ensure consistent, accurate tool documentation and prevent discrepancies between claimed and actual tool capabilities. All team members must follow these standards when working with KGAS tools.