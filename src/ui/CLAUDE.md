# UI Module - CLAUDE.md

## Overview
The `src/ui/` directory contains **user interface components** that provide a unified interface for interacting with the GraphRAG system across different phases and workflows. These components bridge the gap between the UI layer and the core GraphRAG functionality.

## UI Architecture

### UI Layer Pattern
The UI module follows a layered architecture pattern:
- **GraphRAGUI**: Main UI interface for system interaction
- **UIPhaseManager**: Phase management and execution for UI
- **UIProcessingResult**: UI-friendly result structures
- **Phase Adapters**: Interface between UI and GraphRAG phases

### Streamlit Integration Pattern
All UI components are designed for Streamlit integration:
- **File Upload**: Handle document uploads and processing
- **Progress Tracking**: Real-time progress updates
- **Error Handling**: User-friendly error messages
- **Visualization**: Graph and result visualization

## Individual Component Patterns

### GraphRAGUI (`graphrag_ui.py`)
**Purpose**: Main UI interface for GraphRAG system interaction

**Key Patterns**:
- **Unified Interface**: Single interface for all GraphRAG operations
- **Session Management**: Manage UI sessions and state
- **Workflow Creation**: Create workflows for different phases
- **Tool Execution**: Execute individual tools with parameters

**Usage**:
```python
from src.ui.graphrag_ui import GraphRAGUI

# Initialize UI
ui = GraphRAGUI()

# Create workflow for a phase
workflow = ui.create_workflow("phase1")

# Get available tools
tools = ui.get_available_tools("phase2")

# Execute a tool
result = ui.execute_tool("t01_pdf_loader", {"file_path": "document.pdf"})

# Process a document
result = ui.process_document("document.pdf", "phase1")

# Get system status
status = ui.get_system_status()
```

**Core Components**:

#### Workflow Management
```python
def create_workflow(self, phase: str) -> Dict[str, Any]:
    """Create workflow for specified phase"""
```

**Workflow Features**:
- **Phase Validation**: Validate phase names (phase1, phase2, phase3)
- **Tool Discovery**: Get available tools for the phase
- **Context Creation**: Create workflow context with configuration
- **Session Tracking**: Track session information and timestamps

#### Tool Execution
```python
def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a specific tool with given parameters"""
```

**Execution Features**:
- **Parameter Passing**: Pass parameters to tools
- **Orchestrator Integration**: Use PipelineOrchestrator for execution
- **Session Management**: Track execution in session context
- **Error Handling**: Handle tool execution errors gracefully

#### System Status
```python
def get_system_status(self) -> Dict[str, Any]:
    """Get current system status"""
```

**Status Features**:
- **Service Status**: Check service manager status
- **Database Connectivity**: Check Neo4j connection status
- **Configuration Status**: Get current configuration values
- **Session Information**: Track current session and phase

#### Document Processing
```python
def process_document(self, document_path: str, phase: str = "phase1") -> Dict[str, Any]:
    """Process a document through the specified phase"""
```

**Processing Features**:
- **Workflow Creation**: Create workflow for document processing
- **Phase Execution**: Execute document through specified phase
- **Progress Tracking**: Track processing progress
- **Result Formatting**: Format results for UI display

### UIPhaseManager (`ui_phase_adapter.py`)
**Purpose**: Phase management and execution for UI components

**Key Patterns**:
- **Phase Registry**: Manage available phases and capabilities
- **Input Validation**: Validate phase inputs before execution
- **Result Conversion**: Convert phase results to UI-friendly format
- **Error Handling**: Handle phase execution errors gracefully

**Usage**:
```python
from src.ui.ui_phase_adapter import UIPhaseManager, process_document_with_phase

# Get phase manager
manager = UIPhaseManager()

# Get available phases
phases = manager.get_available_phases()

# Get phase capabilities
capabilities = manager.get_phase_capabilities("phase1")

# Process document with phase
result = process_document_with_phase(
    phase_name="phase1",
    file_path="document.pdf",
    filename="document.pdf",
    queries=["What are the main entities?"]
)
```

**Core Components**:

#### Phase Initialization
```python
def _initialize(self):
    """Initialize the phase system"""
```

**Initialization Features**:
- **Adapter Initialization**: Initialize phase adapters
- **Phase Discovery**: Discover available phases
- **Capability Caching**: Cache phase capabilities
- **Error Handling**: Handle initialization errors

#### Input Validation
```python
def validate_phase_input(
    self, 
    phase_name: str, 
    documents: List[str], 
    queries: List[str],
    domain_description: Optional[str] = None
) -> List[str]:
    """Validate input for a specific phase"""
```

**Validation Features**:
- **Phase Availability**: Check if phase is available
- **Input Validation**: Validate documents and queries
- **Domain Validation**: Validate domain descriptions
- **Error Collection**: Collect all validation errors

#### Document Processing
```python
def process_document(
    self,
    phase_name: str,
    file_path: str,
    filename: str,
    queries: List[str],
    domain_description: Optional[str] = None,
    **kwargs
) -> UIProcessingResult:
    """Process a single document using the specified phase"""
```

**Processing Features**:
- **Request Creation**: Create ProcessingRequest objects
- **Phase Execution**: Execute phases through registry
- **Result Conversion**: Convert PhaseResult to UIProcessingResult
- **Error Handling**: Handle processing errors gracefully

#### Result Conversion
```python
def _convert_phase_result(self, phase_result: PhaseResult, filename: str) -> UIProcessingResult:
    """Convert PhaseResult to UIProcessingResult"""
```

**Conversion Features**:
- **Data Extraction**: Extract visualization data from results
- **Format Conversion**: Convert to UI-friendly format
- **Metric Calculation**: Calculate processing metrics
- **Error Handling**: Handle conversion errors

### UIProcessingResult
**Purpose**: UI-friendly result structure for phase processing

**Key Patterns**:
- **Structured Results**: Consistent result structure across phases
- **Error Information**: Comprehensive error information
- **Visualization Data**: Support for graph and query visualization
- **Phase-Specific Data**: Support for phase-specific information

**Data Structure**:
```python
@dataclass
class UIProcessingResult:
    # Basic info
    filename: str
    phase_name: str
    status: str  # "success", "error", "partial"
    processing_time: float
    
    # Core metrics
    entity_count: int
    relationship_count: int
    confidence_score: float
    
    # Error info
    error_message: Optional[str] = None
    
    # Detailed results (for visualization)
    graph_data: Optional[Dict[str, Any]] = None
    query_results: Optional[List[Dict[str, Any]]] = None
    visualizations: Optional[Dict[str, Any]] = None
    
    # Phase-specific data
    phase_specific_data: Optional[Dict[str, Any]] = None
```

**Result Features**:
- **Status Tracking**: Track processing status (success, error, partial)
- **Performance Metrics**: Track processing time and performance
- **Error Details**: Provide detailed error information
- **Visualization Support**: Support for graph and result visualization

## Common Commands & Workflows

### Development Commands
```bash
# Test UI initialization
python -c "from src.ui.graphrag_ui import GraphRAGUI; ui = GraphRAGUI(); print(ui.get_system_status())"

# Test phase manager
python -c "from src.ui.ui_phase_adapter import UIPhaseManager; manager = UIPhaseManager(); print(f'Available phases: {manager.get_available_phases()}')"

# Test workflow creation
python -c "from src.ui.graphrag_ui import GraphRAGUI; ui = GraphRAGUI(); print(ui.create_workflow('phase1'))"

# Test tool execution
python -c "from src.ui.graphrag_ui import GraphRAGUI; ui = GraphRAGUI(); print(ui.get_available_tools('phase1'))"
```

### Testing Commands
```bash
# Test phase validation
python -c "from src.ui.ui_phase_adapter import UIPhaseManager; manager = UIPhaseManager(); print(manager.validate_phase_input('phase1', ['test.pdf'], ['test query']))"

# Test document processing
python -c "from src.ui.ui_phase_adapter import process_document_with_phase; print(process_document_with_phase.__doc__)"

# Test phase capabilities
python -c "from src.ui.ui_phase_adapter import UIPhaseManager; manager = UIPhaseManager(); print(manager.get_phase_capabilities('phase1'))"

# Test UI phase requirements
python -c "from src.ui.ui_phase_adapter import UIPhaseManager; manager = UIPhaseManager(); print(manager.get_phase_requirements('phase1'))"
```

### Debugging Commands
```bash
# Check UI session
python -c "from src.ui.graphrag_ui import GraphRAGUI; ui = GraphRAGUI(); print(f'Session ID: {ui.session_id}')"

# Check phase initialization
python -c "from src.ui.ui_phase_adapter import UIPhaseManager; manager = UIPhaseManager(); print(f'Initialized: {manager.is_initialized()}')"

# Check available phases
python -c "from src.ui.ui_phase_adapter import get_available_ui_phases; print(get_available_ui_phases())"

# Test phase input validation
python -c "from src.ui.ui_phase_adapter import validate_ui_phase_input; print(validate_ui_phase_input('phase1', ['test.pdf'], ['test query']))"
```

## Code Style & Conventions

### UI Design Patterns
- **Unified Interface**: Single interface for all UI operations
- **Session Management**: Manage UI sessions and state
- **Error Handling**: User-friendly error messages and handling
- **Progress Tracking**: Real-time progress updates

### Naming Conventions
- **UI Classes**: Use `UI` suffix for UI-specific classes
- **Manager Classes**: Use `Manager` suffix for management classes
- **Result Classes**: Use `Result` suffix for result classes
- **Method Names**: Use descriptive names for UI operations

### Error Handling Patterns
- **User-Friendly Errors**: Provide clear, actionable error messages
- **Graceful Degradation**: Handle errors gracefully without crashing
- **Error Logging**: Log errors with context for debugging
- **Status Tracking**: Track error status in result objects

### Logging Patterns
- **UI Logging**: Log UI operations and user interactions
- **Session Logging**: Log session creation and management
- **Error Logging**: Log errors with user context
- **Performance Logging**: Log processing times and performance

## Integration Points

### Core Integration
- **Service Manager**: Integration with core service manager
- **Pipeline Orchestrator**: Integration with pipeline orchestrator
- **Configuration**: Integration with configuration system
- **Logging**: Integration with logging system

### Phase Integration
- **Phase Registry**: Integration with phase registry
- **Phase Adapters**: Integration with phase adapters
- **Processing Interface**: Integration with processing interface
- **Result Interface**: Integration with result interface

### Streamlit Integration
- **File Upload**: Integration with Streamlit file upload
- **Progress Bars**: Integration with Streamlit progress tracking
- **Error Display**: Integration with Streamlit error display
- **Visualization**: Integration with Streamlit visualization

### External Dependencies
- **Streamlit**: Web UI framework
- **Pathlib**: File path handling
- **Dataclasses**: Structured data models
- **Logging**: Standard Python logging

## Performance Considerations

### UI Responsiveness
- **Async Processing**: Use async processing for long operations
- **Progress Updates**: Provide real-time progress updates
- **Background Processing**: Process documents in background
- **Caching**: Cache frequently accessed data

### Memory Management
- **File Handling**: Handle large files efficiently
- **Result Caching**: Cache processing results
- **Session Cleanup**: Clean up session data
- **Resource Management**: Manage UI resources efficiently

### Speed Optimization
- **Lazy Loading**: Load UI components on demand
- **Parallel Processing**: Process multiple documents in parallel
- **Result Streaming**: Stream results as they become available
- **UI Optimization**: Optimize UI rendering and updates

## Testing Patterns

### Unit Testing
- **UI Testing**: Test UI components independently
- **Manager Testing**: Test phase manager functionality
- **Result Testing**: Test result conversion and formatting
- **Validation Testing**: Test input validation

### Integration Testing
- **Core Integration**: Test integration with core components
- **Phase Integration**: Test integration with phases
- **Streamlit Integration**: Test Streamlit integration
- **End-to-End**: Test complete UI workflow

### UI Testing
- **User Interaction**: Test user interactions and workflows
- **Error Scenarios**: Test error handling and display
- **Progress Tracking**: Test progress tracking and updates
- **Visualization**: Test result visualization

## Troubleshooting

### Common Issues
1. **Phase Initialization Issues**: Check phase adapter initialization
2. **File Upload Issues**: Check file handling and validation
3. **Processing Issues**: Check phase execution and error handling
4. **UI Responsiveness Issues**: Check async processing and progress updates

### Debug Commands
```bash
# Check UI initialization
python -c "from src.ui.graphrag_ui import GraphRAGUI; ui = GraphRAGUI(); print('UI initialized successfully')"

# Check phase manager
python -c "from src.ui.ui_phase_adapter import UIPhaseManager; manager = UIPhaseManager(); print(f'Phase manager initialized: {manager.is_initialized()}')"

# Check available phases
python -c "from src.ui.ui_phase_adapter import get_available_ui_phases; print(f'Available phases: {get_available_ui_phases()}')"

# Test phase validation
python -c "from src.ui.ui_phase_adapter import validate_ui_phase_input; errors = validate_ui_phase_input('phase1', [], []); print(f'Validation errors: {errors}')"
```

## Migration & Upgrades

### UI Migration
- **Interface Updates**: Update UI interfaces and APIs
- **Component Migration**: Migrate UI components
- **Result Migration**: Migrate result structures
- **Integration Migration**: Migrate integrations

### Phase Migration
- **Phase Updates**: Update phase interfaces and capabilities
- **Adapter Migration**: Migrate phase adapters
- **Registry Migration**: Migrate phase registry
- **Validation Migration**: Migrate validation rules

### Configuration Updates
- **UI Configuration**: Update UI configuration
- **Phase Configuration**: Update phase configuration
- **Integration Configuration**: Update integration settings
- **Performance Configuration**: Update performance settings 