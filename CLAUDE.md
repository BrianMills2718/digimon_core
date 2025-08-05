# KGAS Development Instructions - Contract-First Tool Migration

## ⚠️ **CRITICAL: CONTRACT-FIRST MIGRATION IN PROGRESS** ⚠️

**NO BACKWARDS COMPATIBILITY NEEDED** - Single developer environment, no production data.

This system is undergoing a complete tool interface migration from multiple competing interfaces to a single contract-first design as specified in ADR-001 and ADR-028.

## Current Migration Status (2025-08-05)

### 🎯 **Migration Goal**
Unify all ~80 tools to use the contract-first KGASTool interface defined in `/src/core/tool_contract.py`, eliminating the current split between Tool protocol and BaseTool implementations.

### 📊 **Current State**
- **Orchestrator**: Uses Tool protocol from `/src/core/tool_protocol.py`
- **Tools**: Mix of BaseTool and various interfaces
- **Services**: API mismatches requiring adaptation

### ✅ **Analysis Complete**
The following analysis documents provide full context:
- `Contract_First_Uncertainty_Analysis.md` - Root cause analysis
- `Interface_Mapping_Documentation.md` - Tool interface inventory
- `Service_API_Documentation.md` - Service API gaps
- `Contract_First_Revised_Plan.md` - 4-week migration plan

## Task 1: Fix Validation Attribute Mismatch

**Goal**: Make ToolValidationResult compatible with orchestrator expectations

### Investigation Required
1. Open `/src/core/tool_contract.py`
2. Find the `ToolValidationResult` class (around line 63)
3. Verify it has `errors` attribute but not `validation_errors`

### Implementation Steps

1. **Add compatibility property to ToolValidationResult**:
   ```python
   # In /src/core/tool_contract.py, add to ToolValidationResult class:
   
   @property
   def validation_errors(self) -> List[str]:
       """Compatibility property for orchestrator expectations.
       
       The orchestrator expects 'validation_errors' but we use 'errors'.
       This property provides compatibility during migration.
       """
       return self.errors
   ```

2. **Test the fix**:
   Create `test_validation_compatibility.py`:
   ```python
   from src.core.tool_contract import ToolValidationResult
   
   # Test that both attributes work
   result = ToolValidationResult(is_valid=False, errors=["Test error"])
   assert result.errors == ["Test error"]
   assert result.validation_errors == ["Test error"]  # Via property
   print("✅ Validation compatibility confirmed")
   ```

3. **Run test**:
   ```bash
   python test_validation_compatibility.py
   ```

### Evidence Required
Create `Evidence_Validation_Fix.md` showing:
1. The property addition in tool_contract.py
2. Test script output
3. Confirmation both attributes accessible

## Task 2: Update Orchestrator to Use ToolRequest/ToolResult

**Goal**: Modify orchestrator to use contract-first interfaces directly

### Investigation Required
1. Open `/src/core/orchestration/workflow_engines/sequential_engine.py`
2. Find `execute_pipeline` method (around line 30)
3. Note it expects `input_data: Dict[str, Any]`
4. Note it calls `tool.execute(current_data)` passing dict

### Implementation Steps

1. **Update imports in sequential_engine.py**:
   ```python
   # Add to imports
   from ...tool_contract import ToolRequest, ToolResult, KGASTool
   ```

2. **Change execute_pipeline signature**:
   ```python
   def execute_pipeline(self, tools: List[KGASTool], initial_request: ToolRequest,
                       monitors: List[Any] = None) -> Dict[str, Any]:
       """Execute pipeline tools sequentially using contract-first interface.
       
       Args:
           tools: List of KGASTool implementations
           initial_request: Initial ToolRequest for first tool
           monitors: Optional execution monitors
       """
   ```

3. **Update execution logic**:
   ```python
   # Replace current_data dict approach with ToolRequest/ToolResult
   current_request = initial_request
   
   for i, tool in enumerate(tools):
       # Validate using KGASTool interface
       validation_result = tool.validate_input(current_request.input_data)
       if not validation_result.is_valid:
           raise ValueError(f"Validation failed: {validation_result.errors}")
       
       # Execute with ToolRequest
       result = tool.execute(current_request)
       
       # Check result status
       if result.status == "error":
           raise RuntimeError(f"Tool failed: {result.error_details}")
       
       # Create next request from result
       if i < len(tools) - 1:
           current_request = ToolRequest(
               input_data=result.data,
               workflow_id=initial_request.workflow_id
           )
   ```

4. **Remove field adapter usage**:
   - Delete all references to `self.field_adapter`
   - Remove field adapter imports
   - Delete field adaptation logic

5. **Test with simple tool**:
   Create `test_orchestrator_update.py`:
   ```python
   from src.core.orchestration.workflow_engines.sequential_engine import SequentialEngine
   from src.core.tool_contract import ToolRequest, KGASTool
   from src.core.config_manager import ConfigManager
   
   # Create minimal test tool
   class TestTool(KGASTool):
       # Implement required methods
       pass
   
   # Test orchestrator
   config = ConfigManager()
   engine = SequentialEngine(config)
   request = ToolRequest(input_data={"test": "data"})
   
   # Should work with new interface
   result = engine.execute_pipeline([TestTool()], request)
   print("✅ Orchestrator updated successfully")
   ```

### Evidence Required
Create `Evidence_Orchestrator_Update.md` showing:
1. Diff of sequential_engine.py changes
2. Test execution output
3. Confirmation ToolRequest/ToolResult flow works

## Task 3: Update Service APIs

**Goal**: Fix service method mismatches without adapters

### Investigation Required
1. Check `Service_API_Documentation.md` for gaps:
   - ProvenanceService missing `create_tool_execution_record`
   - IdentityService missing `resolve_entity`
2. Identify which tools use these missing methods

### Implementation Steps

#### 3.1 Update Tools Using ProvenanceService

**Find affected tools**:
```bash
grep -r "create_tool_execution_record" src/tools/
```

**For each tool found**, replace:
```python
# OLD: Single method call
record = provenance.create_tool_execution_record(
    tool_id=self.tool_id,
    workflow_id=workflow_id,
    input_summary=summary,
    success=True
)

# NEW: Two-step process
operation_id = provenance.start_operation(
    tool_id=self.tool_id,
    operation_type="tool_execution",
    inputs=[input_summary],
    parameters={"workflow_id": workflow_id}
)
provenance.complete_operation(
    operation_id=operation_id,
    success=True
)
```

#### 3.2 Update Tools Using IdentityService

**Find affected tools**:
```bash
grep -r "resolve_entity" src/tools/
```

**For each tool found**, replace:
```python
# OLD: resolve_entity call
entity_id = identity.resolve_entity(
    surface_form=text,
    entity_type=etype,
    source_ref=source
)

# NEW: Use actual methods
similar = identity.find_similar_entities(
    surface_form=text,
    entity_type=etype,
    threshold=0.8
)

if similar:
    entity_id = similar[0]['entity_id']
    mention_id = identity.create_mention(
        surface_form=text,
        start_pos=0,
        end_pos=len(text),
        source_ref=source,
        entity_id=entity_id
    )
else:
    # Create new entity via mention
    mention_id = identity.create_mention(
        surface_form=text,
        start_pos=0,
        end_pos=len(text),
        source_ref=source,
        entity_type=etype
    )
    entity_data = identity.get_entity_by_mention(mention_id)
    entity_id = entity_data['entity_id'] if entity_data else None
```

### Evidence Required
Create `Evidence_Service_Updates.md` showing:
1. List of tools updated
2. Before/after code snippets
3. Test confirmation that tools work with real service methods

## Task 4: Migrate First Tool (T03TextLoader)

**Goal**: Complete migration of simplest tool as template for others

### Implementation Steps

1. **Create new implementation** at `/src/tools/phase1/t03_text_loader_kgas.py`:
   ```python
   """T03 Text Loader - Contract-First Implementation"""
   
   from pathlib import Path
   from typing import List, Dict, Any
   import logging
   
   from src.core.tool_contract import (
       KGASTool, ToolRequest, ToolResult, 
       ToolValidationResult, ConfidenceScore
   )
   from src.core.service_manager import ServiceManager
   
   logger = logging.getLogger(__name__)
   
   
   class T03TextLoaderKGAS(KGASTool):
       """Text file loader implementing contract-first interface."""
       
       def __init__(self, service_manager: ServiceManager):
           super().__init__(tool_id="T03", tool_name="Text File Loader")
           self.service_manager = service_manager
           self.description = "Loads text files with encoding detection"
           
       def execute(self, request: ToolRequest) -> ToolResult:
           """Execute text loading with contract interface."""
           try:
               # Extract file path from request
               file_path = request.input_data.get("file_path")
               if not file_path:
                   return self.create_error_result(
                       request, "Missing required field: file_path"
                   )
               
               # Load file
               path = Path(file_path)
               content = path.read_text(encoding='utf-8')
               
               # Track with provenance (using real methods)
               op_id = self.service_manager.provenance_service.start_operation(
                   tool_id=self.tool_id,
                   operation_type="file_load",
                   inputs=[str(file_path)],
                   parameters={"encoding": "utf-8"}
               )
               
               # Create result
               result_data = {
                   "content": content,
                   "file_path": str(file_path),
                   "size_bytes": len(content),
                   "encoding": "utf-8"
               }
               
               # Complete provenance
               self.service_manager.provenance_service.complete_operation(
                   operation_id=op_id,
                   outputs=[f"Loaded {len(content)} bytes"],
                   success=True
               )
               
               # Return success result
               return ToolResult(
                   status="success",
                   data=result_data,
                   confidence=ConfidenceScore.create_high_confidence(1.0, 10),
                   metadata={"tool_version": "1.0.0"},
                   provenance=op_id,
                   request_id=request.request_id
               )
               
           except Exception as e:
               return self.create_error_result(request, str(e))
       
       def validate_input(self, input_data: Any) -> ToolValidationResult:
           """Validate input has required file_path."""
           result = ToolValidationResult(is_valid=True)
           
           if not isinstance(input_data, dict):
               result.add_error("Input must be a dictionary")
               return result
               
           if "file_path" not in input_data:
               result.add_error("Missing required field: file_path")
               
           file_path = input_data.get("file_path")
           if file_path and not Path(file_path).exists():
               result.add_error(f"File not found: {file_path}")
               
           return result
       
       def get_input_schema(self) -> Dict[str, Any]:
           """Define input schema."""
           return {
               "type": "object",
               "properties": {
                   "file_path": {"type": "string", "description": "Path to text file"}
               },
               "required": ["file_path"]
           }
       
       def get_output_schema(self) -> Dict[str, Any]:
           """Define output schema."""
           return {
               "type": "object",
               "properties": {
                   "content": {"type": "string"},
                   "file_path": {"type": "string"},
                   "size_bytes": {"type": "integer"},
                   "encoding": {"type": "string"}
               },
               "required": ["content", "file_path"]
           }
       
       def get_theory_compatibility(self) -> List[str]:
           """No theory compatibility for basic loader."""
           return []
   ```

2. **Test the migrated tool**:
   Create `test_t03_migration.py`:
   ```python
   from src.core.service_manager import ServiceManager
   from src.core.tool_contract import ToolRequest
   from src.tools.phase1.t03_text_loader_kgas import T03TextLoaderKGAS
   
   # Create test file
   with open("test.txt", "w") as f:
       f.write("Test content")
   
   # Test tool
   service_manager = ServiceManager()
   tool = T03TextLoaderKGAS(service_manager)
   
   request = ToolRequest(input_data={"file_path": "test.txt"})
   result = tool.execute(request)
   
   assert result.status == "success"
   assert result.data["content"] == "Test content"
   print("✅ T03 successfully migrated to KGASTool")
   ```

3. **Update tool registry** to use new implementation

4. **Delete old implementation** once confirmed working

### Evidence Required
Create `Evidence_T03_Migration.md` showing:
1. Full new implementation
2. Test output
3. Comparison with old implementation
4. Confirmation it works in pipeline

## Success Criteria

Each task is complete when:

1. **Task 1**: Both `errors` and `validation_errors` work on ToolValidationResult
2. **Task 2**: Orchestrator uses ToolRequest/ToolResult throughout
3. **Task 3**: No tools call non-existent service methods  
4. **Task 4**: T03 fully migrated and old version deleted

## Development Workflow

For each task:

1. **Read existing code** to understand current state
2. **Make minimal changes** to achieve goal
3. **Test immediately** with focused test script
4. **Document evidence** in markdown file
5. **Commit with descriptive message**

## No Backwards Compatibility Rules

- **Delete old code** as soon as new code works
- **No adapter methods** - fix the real issue
- **No bridge patterns** - direct implementation only
- **No feature flags** - cut over directly

## Next Phase After These Tasks

Once these 4 tasks complete, proceed to:
- Mass migration of T01-T14 (simple loaders)
- Then T15A, T15B (processors)
- Then T31, T34, T49, T68 (Neo4j tools)
- Finally remaining analysis tools

The goal is a single, clean contract-first interface across all tools within 4 weeks.