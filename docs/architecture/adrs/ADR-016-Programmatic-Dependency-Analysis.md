# ADR-016: Programmatic Dependency Analysis for Dynamic Parallel Execution

**Date**: 2025-08-01  
**Status**: Accepted  
**Deciders**: Development Team  

## Context

The current parallel execution system relies on hardcoded tool-specific rules to determine which tools can run in parallel. This approach:

- Requires manual configuration for each new tool combination
- Cannot automatically discover new parallel opportunities
- Does not scale as the system grows
- Violates the principle of dynamic tool orchestration

### Current Problems
```python
# Current approach: Hardcoded rules
safe_pairs = {
    ("T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"),  # Manual entry required
    ("T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"),  # For each pair
}
```

When adding new tools, developers must:
1. Manually analyze dependencies
2. Test parallel combinations
3. Add hardcoded safety rules
4. Update multiple configuration files

## Decision

We will implement a **Programmatic Dependency Analysis Framework** that automatically:

1. **Calculates dependency levels** from tool contracts
2. **Detects resource conflicts** through systematic analysis
3. **Finds parallel opportunities** using algorithmic approaches
4. **Validates execution safety** without hardcoded rules

### Core Principles

1. **Zero Manual Configuration**: New tools automatically integrated
2. **Contract-Based Analysis**: Use tool contracts to determine dependencies and resources
3. **Resource Conflict Detection**: Systematic analysis of database, file, and state access patterns
4. **Algorithmic Optimization**: Find optimal parallel execution plans programmatically
5. **Validation Through Simulation**: Prove correctness before execution

## Architecture

### 1. Contract-Based Dependency Discovery
```python
class ToolContractAnalyzer:
    def extract_dependencies(self, tool_contract):
        """Extract all dependencies from tool contract YAML"""
        
    def extract_resources(self, tool_contract):
        """Extract database, file, and state resources accessed"""
        
    def calculate_dependency_level(self, tool_id, all_contracts):
        """Calculate topological level from dependency graph"""
```

### 2. Resource Conflict Analysis
```python
class ResourceConflictAnalyzer:
    def analyze_database_conflicts(self, tool1, tool2):
        """Check if tools conflict on database read/write operations"""
        
    def analyze_file_conflicts(self, tool1, tool2):
        """Check if tools access same files concurrently"""
        
    def analyze_state_conflicts(self, tool1, tool2):
        """Check if tools modify shared application state"""
```

### 3. Parallel Opportunity Discovery
```python
class ParallelOpportunityFinder:
    def find_all_parallel_groups(self, tools_at_level):
        """Find maximal sets of tools that can run in parallel"""
        
    def optimize_execution_plan(self, dependency_graph):
        """Generate optimal parallel execution plan"""
        
    def estimate_performance_gain(self, parallel_plan):
        """Predict speedup from parallel execution"""
```

### 4. Execution Plan Validation
```python
class ExecutionPlanValidator:
    def simulate_execution(self, plan):
        """Simulate parallel execution to detect race conditions"""
        
    def validate_data_flow(self, plan):
        """Ensure data dependencies are preserved"""
        
    def measure_actual_performance(self, plan):
        """Execute and measure real performance gains"""
```

## Implementation Plan

### Phase 1: Contract Analysis Framework
- Parse tool contract YAML files
- Extract dependencies, inputs, outputs, resources
- Build complete dependency graph
- Calculate accurate dependency levels

### Phase 2: Resource Conflict Detection
- Analyze database access patterns (read/write/create)
- Detect file system conflicts
- Identify shared state modifications
- Create resource conflict matrix

### Phase 3: Algorithmic Parallel Discovery
- Implement maximal clique finding for parallel groups
- Generate optimal execution DAGs
- Handle complex multi-way parallelization
- Optimize for resource utilization

### Phase 4: Validation and Performance
- Execution simulation framework
- Race condition detection
- Performance measurement and comparison
- Automated regression testing

## Benefits

### For New Tool Integration
```python
# Adding T99_SENTIMENT_ANALYZER
# OLD: Manual configuration required
safe_pairs.add(("T99_SENTIMENT_ANALYZER", "T31_ENTITY_BUILDER"))  # Manual

# NEW: Automatic discovery
# System reads T99 contract, discovers it:
# - Depends on T23A_SPACY_NER (Level 3)  
# - Only reads entity data (no conflicts)
# - Can parallelize with T27, T31 automatically
```

### For System Scalability
- **O(n²) → O(n log n)**: Better algorithmic complexity
- **Zero Configuration**: No manual rules needed
- **Automatic Optimization**: Finds optimal execution plans
- **Validated Safety**: Prevents race conditions programmatically

### For Development Velocity
- **Self-Documenting**: Tool contracts define behavior
- **Testable**: Simulation validates correctness
- **Maintainable**: No hardcoded tool-specific logic
- **Extensible**: Works for any future tools

## Risks and Mitigations

### Risk: Over-Conservative Analysis
**Mitigation**: Implement confidence levels and optional manual overrides

### Risk: Performance Overhead
**Mitigation**: Cache analysis results, optimize for common cases

### Risk: Complex Debugging
**Mitigation**: Comprehensive logging and visualization tools

## Success Criteria

1. **New tools automatically integrated** without manual parallel configuration
2. **Performance improvements** of >50% for parallelizable workloads  
3. **Zero race conditions** in production parallel execution
4. **Maintainable codebase** with no tool-specific hardcoded rules
5. **Comprehensive test suite** validating all parallel combinations

## References

- Tool Contract Schema: `config/schemas/tool_contract_schema.yaml`
- Current Parallel Execution: `src/execution/dynamic_executor.py`
- Dependency Analysis: `src/execution/dependency_analyzer.py`

## Notes

This ADR replaces the current hardcoded approach with a systematic, algorithmic solution that scales with system growth and maintains safety through programmatic validation.