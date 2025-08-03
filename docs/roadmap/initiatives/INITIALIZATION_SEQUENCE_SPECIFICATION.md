# Initialization Sequence Specification - KGAS System

## Current State Analysis

**Problem:** Undefined initialization order creates cascading failures  
**Impact:** Even when individual issues are fixed, system fails due to dependency conflicts  
**Solution:** Define canonical initialization sequence with validation and rollback  

## Current Problematic Sequence

```
1. ParallelOrchestrator.__init__()
   ├── super().__init__(config_path)           # SimpleSequentialOrchestrator
   │   ├── _load_config(config_path)           # ✅ FIXED: Logger order
   │   ├── self.mcp_adapter = MCPToolAdapter() # ❌ Import failures
   │   └── self.agents = {}
   ├── ExecutionMode configuration
   ├── ResourcePool creation
   └── self.logger setup                       # ✅ Working

2. orchestrator.initialize()
   ├── super().initialize()                   # SimpleSequentialOrchestrator.initialize()
   │   ├── mcp_adapter.initialize()           # ❌ Fails due to imports
   │   ├── Create agents                      # ❌ Agent type property issues
   │   │   ├── DocumentAgent(mcp_adapter)     # ❌ Property setter missing
   │   │   ├── AnalysisAgent(mcp_adapter)     # ❌ Same issue
   │   │   └── ...
   │   └── Communication setup                # ❌ Depends on failed agents
   └── Execution semaphore setup             # ✅ Works if we get here

FAILURE CASCADE: Each step depends on previous steps that are failing
```

## Required Dependency Graph

### Level 0: Foundation (No Dependencies)
```
- Logging configuration (module-level)
- Basic error handling setup  
- Path and environment detection
- Configuration schema validation
```

### Level 1: Core Services (Depends on Level 0)
```
- Configuration loading and validation
- Import resolution and fallback registration
- Basic service registry initialization
- Credential and security setup
```

### Level 2: Infrastructure (Depends on Level 1)
```
- Database connection setup (Neo4j, SQLite)
- Message bus initialization
- Performance monitoring setup
- Health check endpoints
```

### Level 3: Tool System (Depends on Level 2)
```
- MCP tool discovery and registration
- Tool adapter initialization
- Tool validation and testing
- Fallback tool registration
```

### Level 4: Agent System (Depends on Level 3)
```
- Agent class validation
- Agent instantiation with dependencies
- Agent capability registration
- Inter-agent communication setup
```

### Level 5: Orchestration (Depends on Level 4)
```
- Workflow engine initialization
- Resource pool setup
- Execution strategy configuration
- Monitoring and metrics activation
```

## Proposed Safe Initialization Sequence

### Phase 1: Foundation Setup
```python
async def initialize_foundation() -> FoundationContext:
    """Initialize foundational services with no dependencies."""
    
    context = FoundationContext()
    
    # 1.1 Logging (already working)
    context.logger = setup_logging()
    
    # 1.2 Environment detection
    context.execution_context = detect_execution_context()
    context.src_path = resolve_source_path()
    
    # 1.3 Configuration validation
    try:
        context.config = load_and_validate_config(config_path)
    except ConfigError as e:
        context.config = get_default_config()
        context.warnings.append(f"Using default config: {e}")
    
    # 1.4 Error handling setup
    context.error_handler = setup_error_handling(context.config)
    
    return context
```

### Phase 2: Service Infrastructure
```python
async def initialize_infrastructure(context: FoundationContext) -> InfrastructureContext:
    """Initialize core infrastructure services."""
    
    infra = InfrastructureContext(context)
    
    # 2.1 Import resolution
    infra.import_resolver = setup_import_resolution(context.src_path)
    
    # 2.2 Database connections (with fallbacks)
    try:
        infra.neo4j = await setup_neo4j_connection(context.config)
    except DatabaseError as e:
        infra.neo4j = None
        infra.warnings.append(f"Neo4j unavailable: {e}")
    
    # 2.3 Message bus
    infra.message_bus = MessageBus(context.config.get("communication", {}))
    await infra.message_bus.initialize()
    
    # 2.4 Health monitoring
    infra.health_monitor = HealthMonitor()
    infra.health_monitor.start()
    
    return infra
```

### Phase 3: Tool System
```python
async def initialize_tool_system(infra: InfrastructureContext) -> ToolContext:
    """Initialize MCP tools and adapters."""
    
    tools = ToolContext(infra)
    
    # 3.1 Import MCP components (with fallbacks)
    mcp_components = infra.import_resolver.resolve_mcp_imports()
    
    if mcp_components.available:
        # 3.2 Full MCP setup
        tools.mcp_adapter = MCPToolAdapter(mcp_components)
        await tools.mcp_adapter.initialize()
        tools.mode = "full"
    else:
        # 3.3 Limited mode setup
        tools.mcp_adapter = LimitedMCPAdapter()
        tools.mode = "limited"
        tools.warnings.append("Running in limited mode - MCP tools unavailable")
    
    # 3.4 Tool validation
    tools.available_tools = await tools.mcp_adapter.discover_tools()
    tools.validated_tools = await validate_tools(tools.available_tools)
    
    return tools
```

### Phase 4: Agent System
```python
async def initialize_agent_system(tools: ToolContext) -> AgentContext:
    """Initialize agents with validated dependencies."""
    
    agents = AgentContext(tools)
    
    # 4.1 Agent class validation
    await validate_agent_classes()  # Check agent_type property issues
    
    # 4.2 Agent creation with dependency injection
    for agent_config in tools.config.get("agents", []):
        try:
            agent = await create_agent_with_dependencies(
                agent_config, 
                tools.mcp_adapter,
                tools.message_bus
            )
            agents.register(agent)
        except AgentCreationError as e:
            agents.warnings.append(f"Agent {agent_config['type']} failed: {e}")
    
    # 4.3 Agent capability registration
    for agent in agents.all():
        capabilities = await agent.get_capabilities()
        agents.capability_registry.register(agent.agent_id, capabilities)
    
    # 4.4 Communication setup
    await setup_agent_communication(agents, tools.message_bus)
    
    return agents
```

### Phase 5: Orchestration Layer
```python
async def initialize_orchestration(agents: AgentContext) -> OrchestrationContext:
    """Initialize orchestration with validated components."""
    
    orchestration = OrchestrationContext(agents)
    
    # 5.1 Resource pool setup
    orchestration.resource_pool = ResourcePool(
        max_concurrent_agents=len(agents.all()),
        max_memory_mb=agents.config.get("max_memory_mb", 2048),
        max_reasoning_threads=agents.config.get("max_reasoning_threads", 3)
    )
    
    # 5.2 Execution strategy
    orchestration.execution_mode = ExecutionMode(
        agents.config.get("execution_mode", "parallel")
    )
    
    # 5.3 Workflow engine
    orchestration.workflow_engine = WorkflowEngine(
        agents.all(),
        orchestration.resource_pool
    )
    
    # 5.4 Performance monitoring
    orchestration.performance_monitor = PerformanceMonitor()
    orchestration.performance_monitor.start()
    
    return orchestration
```

## Validation and Rollback Strategy

### Validation at Each Phase
```python
class InitializationValidator:
    """Validates each initialization phase before proceeding."""
    
    async def validate_foundation(self, context: FoundationContext) -> bool:
        """Validate foundation phase completed successfully."""
        checks = [
            context.logger is not None,
            context.config is not None,
            context.error_handler is not None,
            len(context.errors) == 0  # No hard errors, warnings OK
        ]
        return all(checks)
    
    async def validate_infrastructure(self, infra: InfrastructureContext) -> bool:
        """Validate infrastructure phase."""
        checks = [
            infra.import_resolver is not None,
            infra.message_bus is not None,
            infra.health_monitor is not None,
            infra.message_bus.is_running()
        ]
        return all(checks)
    
    # ... validation for each phase
```

### Rollback Strategy
```python
class InitializationRollback:
    """Handles cleanup when initialization fails."""
    
    async def rollback_orchestration(self, orchestration: OrchestrationContext):
        """Clean up orchestration layer."""
        if orchestration.performance_monitor:
            orchestration.performance_monitor.stop()
        if orchestration.workflow_engine:
            await orchestration.workflow_engine.cleanup()
    
    async def rollback_agents(self, agents: AgentContext):
        """Clean up agent system."""
        for agent in agents.all():
            await agent.cleanup()
        agents.capability_registry.clear()
    
    # ... rollback for each phase
```

## Error Handling Strategy

### Error Classification
```python
class InitializationError(Exception):
    """Base class for initialization errors."""
    pass

class CriticalError(InitializationError):
    """Error that prevents system from functioning."""
    pass

class DegradedError(InitializationError):
    """Error that reduces functionality but allows operation."""
    pass

class WarningError(InitializationError):
    """Non-blocking issue that should be reported."""
    pass
```

### Error Recovery
```python
async def handle_initialization_error(error: InitializationError, phase: str):
    """Handle errors during initialization."""
    
    if isinstance(error, CriticalError):
        # Complete rollback and fail
        await full_rollback()
        raise SystemInitializationFailed(f"Critical error in {phase}: {error}")
    
    elif isinstance(error, DegradedError):
        # Continue with reduced functionality
        logger.warning(f"Degraded mode in {phase}: {error}")
        return DegradedMode(error)
    
    elif isinstance(error, WarningError):
        # Log warning and continue
        logger.warning(f"Warning in {phase}: {error}")
        return ContinueNormally()
```

## Implementation Plan

### Step 1: Refactor Current Initialization
```python
# Replace current orchestrator.__init__ and initialize() with:

async def initialize_system(config_path: str = None) -> SystemContext:
    """Initialize KGAS system with proper dependency ordering."""
    
    validator = InitializationValidator()
    rollback = InitializationRollback()
    
    try:
        # Phase 1: Foundation
        foundation = await initialize_foundation(config_path)
        if not await validator.validate_foundation(foundation):
            raise CriticalError("Foundation validation failed")
        
        # Phase 2: Infrastructure  
        infrastructure = await initialize_infrastructure(foundation)
        if not await validator.validate_infrastructure(infrastructure):
            await rollback.rollback_infrastructure(infrastructure)
            raise CriticalError("Infrastructure validation failed")
        
        # Phase 3: Tools
        tools = await initialize_tool_system(infrastructure)
        if not await validator.validate_tools(tools):
            await rollback.rollback_tools(tools)
            await rollback.rollback_infrastructure(infrastructure)
            raise CriticalError("Tool system validation failed")
        
        # Phase 4: Agents
        agents = await initialize_agent_system(tools)
        if not await validator.validate_agents(agents):
            # This might be degraded mode rather than failure
            if agents.has_any_working_agents():
                logger.warning("Some agents failed, continuing with reduced capability")
            else:
                await rollback.rollback_agents(agents)
                await rollback.rollback_tools(tools)
                await rollback.rollback_infrastructure(infrastructure)
                raise CriticalError("No working agents available")
        
        # Phase 5: Orchestration
        orchestration = await initialize_orchestration(agents)
        if not await validator.validate_orchestration(orchestration):
            await full_rollback()
            raise CriticalError("Orchestration validation failed")
        
        return SystemContext(foundation, infrastructure, tools, agents, orchestration)
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        await full_rollback()
        raise
```

### Step 2: Update Orchestrator Classes
```python
class ParallelOrchestrator:
    """Simplified orchestrator using validated system context."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.system_context = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self) -> bool:
        """Initialize using new dependency-ordered approach."""
        try:
            self.system_context = await initialize_system(self.config_path)
            return True
        except SystemInitializationFailed:
            return False
    
    async def process_request(self, request: str, context: Dict[str, Any] = None) -> Result:
        """Process request using validated system context."""
        if not self.system_context:
            return Result(
                success=False,
                error="System not initialized properly"
            )
        
        return await self.system_context.orchestration.process_request(request, context)
```

## Success Criteria

**Phase Validation:**
- [ ] Each phase can be validated independently
- [ ] Failed phases can be rolled back cleanly
- [ ] System can run in degraded mode when appropriate

**Error Handling:**
- [ ] Clear error messages for each failure type
- [ ] Graceful degradation for non-critical failures
- [ ] Complete rollback for critical failures

**System Reliability:**
- [ ] Consistent initialization across different contexts
- [ ] Predictable behavior in failure scenarios
- [ ] Easy debugging of initialization issues

## Monitoring and Diagnostics

### Initialization Metrics
```python
class InitializationMetrics:
    """Track initialization performance and issues."""
    
    def __init__(self):
        self.phase_timings = {}
        self.error_counts = {}
        self.warning_counts = {}
        self.degraded_modes = []
    
    def record_phase_timing(self, phase: str, duration: float):
        self.phase_timings[phase] = duration
    
    def record_error(self, phase: str, error_type: str):
        key = f"{phase}:{error_type}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    def get_health_report(self) -> Dict[str, Any]:
        return {
            "total_time": sum(self.phase_timings.values()),
            "phase_timings": self.phase_timings,
            "error_summary": self.error_counts,
            "degraded_modes": self.degraded_modes,
            "overall_health": "healthy" if not self.error_counts else "degraded"
        }
```

This specification provides a clear path from the current broken initialization to a robust, dependency-aware system that can handle failures gracefully and provide clear diagnostics for issues.