# Simplified Tool Registry Architecture

**Version**: 1.0  
**Status**: Target Architecture  
**Last Updated**: 2025-07-23  

## Overview

KGAS implements a **simplified, direct tool registry pattern** that eliminates the over-abstraction of the previous 4-layer factory approach. This design provides tool management with minimal complexity while maintaining flexibility and testability.

## Architecture Comparison

### Previous Over-Abstracted Approach ❌
```
ToolFactory → Adapter → Tool → Protocol Implementation
     ↓           ↓        ↓              ↓
  Creates    Wraps    Implements    Defines Interface
  Complex    Simple    Business     Abstract Contract
  Factory    Tool      Logic        Protocol
```

**Problems**:
- 4 layers of abstraction for simple tool execution
- Complex factory patterns with little benefit
- Adapter layers that add no value
- Difficult to understand and maintain

### New Simplified Approach ✅
```
ToolRegistry → BaseTool Implementation
     ↓               ↓
  Direct         Implements
  Registration   Business Logic
  Simple         With Services
  Lookup
```

**Benefits**:
- Direct tool registration and instantiation
- Minimal abstraction overhead
- Easy to understand and test
- Maintains flexibility through dependency injection

## Core Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Application Layer                               │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                 MCP Server                                      │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐│ │
│  │  │   Tool API   │ │  Discovery   │ │      Health Checks       ││ │
│  │  └──────────────┘ └──────────────┘ └──────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Tool Registry                                    │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │             Tool Management                                     │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐│ │
│  │  │ Registration   │  │  Instantiation │  │    Lifecycle       ││ │
│  │  │   Manager      │  │    Manager     │  │    Manager         ││ │
│  │  └────────────────┘  └────────────────┘  └────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Tool Layer                                     │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    BaseTool                                     │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐│ │
│  │  │   Interface    │  │   Execution    │  │   Service Access   ││ │
│  │  │  Definition    │  │    Logic       │  │   Via Container    ││ │
│  │  └────────────────┘  └────────────────┘  └────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                Concrete Tool Implementations                    │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐│ │
│  │  │ T01PdfLoader   │  │ T02WordLoader  │  │ T50Community       ││ │
│  │  │      Tool      │  │      Tool      │  │   Detection        ││ │
│  │  └────────────────┘  └────────────────┘  └────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Service Container                                │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────┐ │
│  │IdentityService   │ │ QualityService   │ │ ProvenanceService    │ │
│  └──────────────────┘ └──────────────────┘ └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Tool Registry Implementation

### Core ToolRegistry Class

```python
from typing import Type, Dict, Any, List, Optional
from threading import RLock
import logging

class ToolRegistry:
    """Simplified tool registry with direct registration and instantiation"""
    
    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self._tools: Dict[str, Type[BaseTool]] = {}
        self._instances: Dict[str, BaseTool] = {}
        self._lock = RLock()
        self.logger = logging.getLogger(__name__)
    
    def register(self, tool_class: Type[BaseTool]) -> None:
        """Register a tool class for instantiation"""
        with self._lock:
            tool_id = tool_class.get_tool_id()
            
            if tool_id in self._tools:
                self.logger.warning(f"Tool {tool_id} already registered, overwriting")
            
            # Validate tool class
            self._validate_tool_class(tool_class)
            
            # Register tool
            self._tools[tool_id] = tool_class
            self.logger.info(f"Registered tool: {tool_id} ({tool_class.__name__})")
    
    def get_tool(self, tool_id: str) -> BaseTool:
        """Get tool instance, creating if necessary"""
        with self._lock:
            # Return cached instance if available
            if tool_id in self._instances:
                return self._instances[tool_id]
            
            # Create new instance
            tool_instance = self._create_tool(tool_id)
            
            # Cache instance for reuse (optional - can be disabled for stateless tools)
            if tool_instance.is_stateful():
                self._instances[tool_id] = tool_instance
            
            return tool_instance
    
    def create_fresh_tool(self, tool_id: str) -> BaseTool:
        """Create a fresh tool instance (bypasses cache)"""
        with self._lock:
            return self._create_tool(tool_id)
    
    def _create_tool(self, tool_id: str) -> BaseTool:
        """Create tool instance with dependency injection"""
        if tool_id not in self._tools:
            raise ToolNotFoundError(f"Tool '{tool_id}' not registered")
        
        tool_class = self._tools[tool_id]
        
        try:
            # Create tool with service container injection
            tool_instance = tool_class(self.service_container)
            
            # Validate tool was created correctly
            self._validate_tool_instance(tool_instance)
            
            self.logger.debug(f"Created tool instance: {tool_id}")
            return tool_instance
            
        except Exception as e:
            self.logger.error(f"Failed to create tool {tool_id}: {e}")
            raise ToolCreationError(f"Failed to create tool '{tool_id}': {e}") from e
    
    def list_tools(self) -> List[str]:
        """Get list of registered tool IDs"""
        with self._lock:
            return list(self._tools.keys())
    
    def get_tool_info(self, tool_id: str) -> Dict[str, Any]:
        """Get information about a registered tool"""
        with self._lock:
            if tool_id not in self._tools:
                raise ToolNotFoundError(f"Tool '{tool_id}' not registered")
            
            tool_class = self._tools[tool_id]
            return {
                "tool_id": tool_id,
                "class_name": tool_class.__name__,
                "module": tool_class.__module__,
                "description": getattr(tool_class, "__doc__", "No description"),
                "capabilities": getattr(tool_class, "CAPABILITIES", []),
                "version": getattr(tool_class, "VERSION", "1.0.0")
            }
    
    def get_all_tool_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered tools"""
        return {tool_id: self.get_tool_info(tool_id) for tool_id in self.list_tools()}
    
    def unregister(self, tool_id: str) -> bool:
        """Unregister a tool (useful for testing)"""
        with self._lock:
            if tool_id in self._tools:
                del self._tools[tool_id]
                if tool_id in self._instances:
                    # Clean up instance
                    instance = self._instances[tool_id]
                    if hasattr(instance, 'cleanup'):
                        instance.cleanup()
                    del self._instances[tool_id]
                
                self.logger.info(f"Unregistered tool: {tool_id}")
                return True
            return False
    
    def clear_cache(self) -> None:
        """Clear all cached tool instances"""
        with self._lock:
            for instance in self._instances.values():
                if hasattr(instance, 'cleanup'):
                    instance.cleanup()
            self._instances.clear()
            self.logger.info("Cleared tool instance cache")
    
    def _validate_tool_class(self, tool_class: Type[BaseTool]) -> None:
        """Validate tool class meets requirements"""
        # Check inheritance
        if not issubclass(tool_class, BaseTool):
            raise InvalidToolError(f"Tool class {tool_class.__name__} must inherit from BaseTool")
        
        # Check required methods
        required_methods = ['get_tool_id', 'execute']
        for method in required_methods:
            if not hasattr(tool_class, method):
                raise InvalidToolError(f"Tool class {tool_class.__name__} missing required method: {method}")
        
        # Check tool_id is not empty
        try:
            tool_id = tool_class.get_tool_id()
            if not tool_id or not isinstance(tool_id, str):
                raise InvalidToolError(f"Tool class {tool_class.__name__} must return valid string tool_id")
        except Exception as e:
            raise InvalidToolError(f"Tool class {tool_class.__name__} get_tool_id() failed: {e}")
    
    def _validate_tool_instance(self, tool_instance: BaseTool) -> None:
        """Validate created tool instance"""
        if not isinstance(tool_instance, BaseTool):
            raise InvalidToolError("Created tool instance is not a BaseTool")
        
        # Verify tool can provide its ID
        tool_id = tool_instance.get_tool_id()
        if not tool_id:
            raise InvalidToolError("Tool instance returned empty tool_id")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of registry and tools"""
        with self._lock:
            status = {
                "registry_healthy": True,
                "total_tools_registered": len(self._tools),
                "total_instances_cached": len(self._instances),
                "tools": {}
            }
            
            # Check each tool's health
            for tool_id, tool_class in self._tools.items():
                try:
                    if tool_id in self._instances:
                        instance = self._instances[tool_id]
                        if hasattr(instance, 'get_health'):
                            tool_health = instance.get_health()
                        else:
                            tool_health = {"status": "unknown", "message": "No health check implemented"}
                    else:
                        tool_health = {"status": "not_instantiated"}
                    
                    status["tools"][tool_id] = {
                        "class": tool_class.__name__,
                        "health": tool_health,
                        "cached": tool_id in self._instances
                    }
                except Exception as e:
                    status["tools"][tool_id] = {
                        "class": tool_class.__name__,
                        "health": {"status": "error", "error": str(e)},
                        "cached": tool_id in self._instances
                    }
            
            return status


class ToolNotFoundError(Exception):
    """Raised when requesting unregistered tool"""
    pass

class ToolCreationError(Exception):
    """Raised when tool creation fails"""
    pass

class InvalidToolError(Exception):
    """Raised when tool doesn't meet requirements"""
    pass
```

## BaseTool Simplified Interface

### Streamlined BaseTool Class

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import time
from datetime import datetime

class BaseTool(ABC):
    """Simplified base class for all KGAS tools"""
    
    # Class-level metadata (optional)
    VERSION = "1.0.0"
    CAPABILITIES = []
    
    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.tool_id = self.get_tool_id()
        
        # Validate dependencies are available
        self._validate_dependencies()
    
    # Core Interface Methods (Required)
    
    @abstractmethod
    def get_tool_id(self) -> str:
        """Return unique tool identifier (e.g., 'T01', 'T50')"""
        pass
    
    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute tool operation with input validation and error handling"""
        pass
    
    # Service Access (Provided by Base Class)
    
    @property
    def identity_service(self) -> IIdentityService:
        """Access to identity service"""
        return self.service_container.get(IIdentityService)
    
    @property
    def quality_service(self) -> IQualityService:
        """Access to quality service"""
        return self.service_container.get(IQualityService)
    
    @property
    def provenance_service(self) -> IProvenanceService:
        """Access to provenance service"""
        return self.service_container.get(IProvenanceService)
    
    @property
    def schema_manager(self) -> ISchemaManager:
        """Access to schema manager"""
        return self.service_container.get(ISchemaManager)
    
    # Optional Extension Points
    
    def is_stateful(self) -> bool:
        """Whether tool maintains state (affects caching behavior)"""
        return False
    
    def get_health(self) -> Dict[str, Any]:
        """Return tool health status"""
        return {
            "status": "healthy",
            "tool_id": self.tool_id,
            "last_check": datetime.utcnow().isoformat()
        }
    
    def cleanup(self) -> None:
        """Clean up resources when tool is removed"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return list of tool capabilities"""
        return self.CAPABILITIES
    
    def get_version(self) -> str:
        """Return tool version"""
        return self.VERSION
    
    # Helper Methods (Provided by Base Class)
    
    def _validate_dependencies(self) -> None:
        """Validate required services are available"""
        required_services = [
            IIdentityService,
            IQualityService,
            IProvenanceService,
            ISchemaManager
        ]
        
        for service_type in required_services:
            if not self.service_container.is_registered(service_type):
                raise ToolDependencyError(
                    f"Tool {self.tool_id} requires {service_type.__name__} but it's not registered"
                )
    
    def _record_execution(self, request: ToolRequest, result: ToolResult) -> None:
        """Record tool execution for provenance"""
        try:
            operation = Operation(
                type="tool_execution",
                tool_id=self.tool_id,
                inputs=request.input_data,
                outputs=result.data,
                status=result.status,
                execution_time=result.execution_time,
                created_at=datetime.utcnow()
            )
            self.provenance_service.record_operation(operation)
        except Exception as e:
            # Don't fail tool execution if provenance recording fails
            logging.warning(f"Failed to record provenance for {self.tool_id}: {e}")

class ToolDependencyError(Exception):
    """Raised when tool dependencies are not available"""
    pass
```

## Tool Implementation Example

### Concrete Tool Implementation

```python
class T01PdfLoaderTool(BaseTool):
    """PDF document loader tool - simplified implementation"""
    
    VERSION = "2.0.0"
    CAPABILITIES = ["pdf_processing", "text_extraction", "metadata_extraction"]
    
    def get_tool_id(self) -> str:
        return "T01"
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Load PDF document and extract entities"""
        start_time = time.time()
        
        try:
            # Validate input
            self._validate_pdf_input(request.input_data)
            
            # Load PDF content
            pdf_content = self._load_pdf_content(request.input_data["file_path"])
            
            # Extract entities
            entities = self._extract_entities(pdf_content)
            
            # Enhance with quality assessment
            quality_entities = self._assess_entity_quality(entities)
            
            # Convert to database format
            db_entities = self._convert_to_database_format(quality_entities)
            
            # Create result
            result = ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "entities": db_entities,
                    "document_id": request.input_data["file_path"],
                    "entity_count": len(db_entities),
                    "content_length": len(pdf_content)
                },
                execution_time=time.time() - start_time
            )
            
            # Record for provenance
            self._record_execution(request, result)
            
            return result
            
        except Exception as e:
            error_result = ToolResult(
                tool_id=self.tool_id,
                status="error",
                error=str(e),
                execution_time=time.time() - start_time
            )
            
            # Record error for provenance
            self._record_execution(request, error_result)
            
            return error_result
    
    def _validate_pdf_input(self, input_data: Dict[str, Any]) -> None:
        """Validate PDF input parameters"""
        if "file_path" not in input_data:
            raise ValueError("Missing required parameter: file_path")
        
        file_path = input_data["file_path"]
        if not isinstance(file_path, str) or not file_path.endswith('.pdf'):
            raise ValueError("file_path must be a PDF file")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    def _load_pdf_content(self, file_path: str) -> str:
        """Load and extract text from PDF"""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text()
        return text_content
    
    def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities from text content"""
        # Use identity service for entity extraction
        extraction_result = self.identity_service.extract_entities(content)
        return extraction_result.entities
    
    def _assess_entity_quality(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assess quality of extracted entities"""
        quality_entities = []
        for entity in entities:
            quality = self.quality_service.assess_quality(entity)
            enhanced_entity = {
                **entity,
                "quality_tier": quality.tier,
                "confidence": quality.confidence
            }
            quality_entities.append(enhanced_entity)
        return quality_entities
    
    def _convert_to_database_format(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert entities to database storage format"""
        db_entities = []
        for entity_data in entities:
            # Create Pydantic model
            entity = Entity(**entity_data)
            # Convert to database format
            db_format = self.schema_manager.to_database(entity)
            db_entities.append(db_format)
        return db_entities
    
    def get_health(self) -> Dict[str, Any]:
        """Check tool health"""
        try:
            # Test PDF processing capability
            test_result = self._test_pdf_processing()
            
            return {
                "status": "healthy" if test_result else "degraded",
                "tool_id": self.tool_id,
                "version": self.VERSION,
                "last_check": datetime.utcnow().isoformat(),
                "capabilities_tested": ["pdf_processing", "entity_extraction"]
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "tool_id": self.tool_id,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _test_pdf_processing(self) -> bool:
        """Test PDF processing capability"""
        # Simple capability test
        try:
            import PyPDF2
            return True
        except ImportError:
            return False
```

## Registry Bootstrap and Configuration

### Application Bootstrap

```python
class ToolRegistryBootstrapper:
    """Bootstrap tool registry with all KGAS tools"""
    
    @staticmethod
    def create_registry(service_container: ServiceContainer) -> ToolRegistry:
        """Create and populate tool registry"""
        registry = ToolRegistry(service_container)
        
        # Register Phase 1 tools
        ToolRegistryBootstrapper._register_phase1_tools(registry)
        
        # Register Phase 2 tools
        ToolRegistryBootstrapper._register_phase2_tools(registry)
        
        # Validate registry
        ToolRegistryBootstrapper._validate_registry(registry)
        
        return registry
    
    @staticmethod
    def _register_phase1_tools(registry: ToolRegistry) -> None:
        """Register all Phase 1 document processing tools"""
        phase1_tools = [
            T01PdfLoaderTool,
            T02WordLoaderTool,
            T03TextLoaderTool,
            T04MarkdownLoaderTool,
            T05CsvLoaderTool,
            T06JsonLoaderTool,
            T07HtmlLoaderTool,
            T08XmlLoaderTool,
            T09YamlLoaderTool,
            T10ExcelLoaderTool,
            T11PowerPointLoaderTool,
            T12ZipLoaderTool,
            T13WebScraperTool,
            T14EmailParserTool,
            T15ATextChunkerTool,
            T23ASpacyNerTool,
            T27RelationshipExtractorTool,
            T31EntityBuilderTool,
            T34EdgeBuilderTool,
            T49MultihopQueryTool,
            T68PageRankCalculatorTool
        ]
        
        for tool_class in phase1_tools:
            registry.register(tool_class)
    
    @staticmethod
    def _register_phase2_tools(registry: ToolRegistry) -> None:
        """Register all Phase 2 graph analytics tools"""
        phase2_tools = [
            T50CommunityDetectionTool,
            T51CentralityAnalysisTool,
            T52GraphClusteringTool,
            T53NetworkMotifsTool,
            T54GraphVisualizationTool,
            T55TemporalAnalysisTool,
            T56GraphMetricsTool,
            T57PathAnalysisTool,
            T58GraphComparisonTool,
            # T59, T60 pending implementation
        ]
        
        for tool_class in phase2_tools:
            registry.register(tool_class)
    
    @staticmethod
    def _validate_registry(registry: ToolRegistry) -> None:
        """Validate registry is properly configured"""
        tool_count = len(registry.list_tools())
        
        if tool_count == 0:
            raise RegistryValidationError("No tools registered")
        
        # Test creation of a few key tools
        key_tools = ["T01", "T50"]
        for tool_id in key_tools:
            try:
                tool = registry.get_tool(tool_id)
                if not tool:
                    raise RegistryValidationError(f"Failed to create key tool: {tool_id}")
            except Exception as e:
                raise RegistryValidationError(f"Key tool {tool_id} creation failed: {e}")
        
        logging.info(f"Tool registry validated: {tool_count} tools registered")

class RegistryValidationError(Exception):
    """Raised when registry validation fails"""
    pass
```

### Application Integration

```python
class KGASApplication:
    """Main KGAS application with simplified tool management"""
    
    def __init__(self):
        self.service_container = None
        self.tool_registry = None
        self.mcp_server = None
    
    def initialize(self) -> None:
        """Initialize KGAS application"""
        # 1. Create service container
        self.service_container = ServiceBootstrapper.configure_container()
        
        # 2. Create tool registry
        self.tool_registry = ToolRegistryBootstrapper.create_registry(self.service_container)
        
        # 3. Create MCP server
        self.mcp_server = MCPServer(self.tool_registry)
        
        logging.info("KGAS application initialized successfully")
    
    def start(self) -> None:
        """Start KGAS application"""
        if not self.tool_registry:
            raise RuntimeError("Application not initialized")
        
        self.mcp_server.start()
        logging.info("KGAS application started")
    
    def stop(self) -> None:
        """Stop KGAS application"""
        if self.mcp_server:
            self.mcp_server.stop()
        
        if self.tool_registry:
            self.tool_registry.clear_cache()
        
        if self.service_container:
            # Cleanup services
            for service_type in [INeo4jManager, ISQLiteManager]:
                try:
                    service = self.service_container.get(service_type)
                    if hasattr(service, 'close'):
                        service.close()
                except:
                    pass
        
        logging.info("KGAS application stopped")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall application health"""
        return {
            "application": "KGAS",
            "status": "healthy" if self.tool_registry else "unhealthy",
            "services": self.service_container.get_health_status() if self.service_container else {},
            "tools": self.tool_registry.get_health_status() if self.tool_registry else {},
            "timestamp": datetime.utcnow().isoformat()
        }
```

## Testing Strategy

### Registry Testing

```python
class TestToolRegistry:
    """Test tool registry functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.service_container = ServiceContainer()
        # Register mock services for testing
        self.service_container.register_instance(IIdentityService, MockIdentityService())
        self.service_container.register_instance(IQualityService, MockQualityService())
        
        self.registry = ToolRegistry(self.service_container)
    
    def test_tool_registration(self):
        """Test tool registration and retrieval"""
        # Register test tool
        self.registry.register(TestTool)
        
        # Verify registration
        assert "TEST" in self.registry.list_tools()
        
        # Create tool instance
        tool = self.registry.get_tool("TEST")
        assert isinstance(tool, TestTool)
        assert tool.get_tool_id() == "TEST"
    
    def test_tool_dependency_injection(self):
        """Test service dependency injection"""
        self.registry.register(TestTool)
        tool = self.registry.get_tool("TEST")
        
        # Verify services are injected
        assert tool.identity_service is not None
        assert tool.quality_service is not None
    
    def test_error_handling(self):
        """Test error handling"""
        # Test unregistered tool
        with pytest.raises(ToolNotFoundError):
            self.registry.get_tool("NONEXISTENT")
        
        # Test invalid tool class
        with pytest.raises(InvalidToolError):
            self.registry.register(InvalidTool)  # Tool that doesn't inherit BaseTool

class TestTool(BaseTool):
    """Test tool for registry testing"""
    
    def get_tool_id(self) -> str:
        return "TEST"
    
    def execute(self, request: ToolRequest) -> ToolResult:
        return ToolResult(
            tool_id="TEST",
            status="success",
            data={"message": "test executed"}
        )
```

## Benefits of Simplified Architecture

### 1. **Reduced Complexity**
- Eliminated 3 unnecessary abstraction layers
- Direct tool registration and instantiation
- Easy to understand and maintain

### 2. **Better Performance**
- No adapter overhead
- Direct method calls
- Efficient tool lookup

### 3. **Easier Testing**
- Simple dependency injection
- Direct tool instantiation for tests
- Clear error conditions

### 4. **Maintained Flexibility**
- Service locator pattern preserves loose coupling
- Easy to add new tools
- Configurable service implementations

### 5. **Clear Responsibilities**
```python
# Clear separation of concerns
ToolRegistry        → Tool lifecycle management
BaseTool           → Common tool functionality  
ConcreteTools      → Business logic implementation
ServiceContainer   → Dependency management
```

The simplified tool registry architecture eliminates unnecessary complexity while maintaining all the benefits of dependency injection and service-oriented design. This approach is easier to understand, test, and maintain while providing the flexibility needed for KGAS's diverse tool ecosystem.