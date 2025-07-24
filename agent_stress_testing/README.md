# KGAS Agent Stress Testing Framework

## Purpose

Test and validate the dual-agent research architecture for KGAS, stress-testing different coordination patterns, memory integration strategies, and workflow execution approaches.

## Directory Structure

```
agent_stress_testing/
├── README.md                          # This file
├── dual_agent_tests/                  # Basic dual-agent coordination tests
│   ├── basic_coordination_test.py     # Simple research-execution coordination
│   ├── context_switching_test.py      # Test different prompting strategies
│   └── parallel_execution_test.py     # Test subagent coordination
├── memory_integration_tests/          # Memory MCP integration tests
│   ├── knowledge_graph_test.py        # Test server-memory integration
│   ├── preference_learning_test.py    # Test mem0-mcp integration
│   ├── zettelkasten_test.py          # Test research note connections
│   └── cross_session_context_test.py  # Test memory persistence
├── workflow_execution_tests/          # Workflow stress tests
│   ├── complex_workflow_test.py       # Multi-step analysis workflows
│   ├── error_recovery_test.py         # Test error handling and recovery
│   ├── tool_coordination_test.py      # Test cross-modal tool coordination
│   └── performance_benchmark_test.py  # Measure execution efficiency
├── claude_code_integration/           # Claude Code SDK integration tests
│   ├── sdk_coordination_test.py       # Test SDK-based agent coordination
│   ├── hooks_integration_test.py      # Test hook-based context switching
│   ├── worktree_strategy_test.py      # Test git worktree agent separation
│   └── headless_orchestration_test.py # Test headless mode coordination
├── research_scenario_tests/           # End-to-end research scenario tests
│   ├── literature_review_test.py      # Test literature analysis workflow
│   ├── discourse_analysis_test.py     # Test social science analysis
│   ├── cross_modal_analysis_test.py   # Test graph/table/vector integration
│   └── collaborative_research_test.py # Test multi-user scenarios
├── stress_test_configs/               # Configuration files for stress tests
│   ├── agent_prompts.yaml            # Different agent prompting strategies
│   ├── memory_configs.yaml           # Memory MCP server configurations
│   ├── workflow_specs.yaml           # Test workflow specifications
│   └── performance_baselines.yaml    # Performance benchmarks and SLAs
├── test_data/                         # Sample data for stress tests
│   ├── sample_documents/             # Test documents for analysis
│   ├── research_scenarios/           # Predefined research scenarios
│   └── expected_outputs/             # Expected test results
└── results/                          # Stress test results and analysis
    ├── performance_metrics/          # Performance measurement results
    ├── error_analysis/              # Error pattern analysis
    └── recommendations/             # Improvement recommendations
```

## Test Categories

### 1. Dual-Agent Coordination Tests
- **Basic Coordination**: Test simple research question → workflow execution → interpretation
- **Context Switching**: Validate different prompting strategies work as intended
- **Parallel Execution**: Test multiple subagents working simultaneously
- **Agent Communication**: Test workflow specification handoff between agents

### 2. Memory Integration Tests  
- **Knowledge Graph**: Test persistent research context storage and retrieval
- **Preference Learning**: Test user pattern recognition and adaptation
- **Research Notes**: Test Zettelkasten-style connected knowledge building
- **Cross-Session Context**: Test memory persistence across research sessions

### 3. Workflow Execution Tests
- **Complex Workflows**: Test multi-step, cross-modal analysis workflows
- **Error Recovery**: Test graceful error handling and recovery strategies
- **Tool Coordination**: Test coordination between 121+ KGAS tools
- **Performance Benchmarks**: Measure execution efficiency and resource usage

### 4. Claude Code Integration Tests
- **SDK Coordination**: Test programmatic agent coordination using Claude Code SDK
- **Hooks Integration**: Test hook-based context switching and validation
- **Worktree Strategy**: Test git worktree-based agent separation
- **Headless Orchestration**: Test automated workflow orchestration

### 5. Research Scenario Tests
- **Literature Review**: End-to-end literature analysis and synthesis
- **Discourse Analysis**: Social science text analysis workflows
- **Cross-Modal Analysis**: Graph/table/vector analysis integration
- **Collaborative Research**: Multi-user research coordination

## Success Metrics

### Performance Metrics
- **Agent Efficiency**: Execution agent 40% faster than conversational agent
- **Memory Utilization**: Cross-session context reduces repeated explanations by 60%
- **Workflow Success Rate**: 95%+ completion rate for complex multi-step analyses
- **Error Recovery**: 90%+ successful recovery from tool execution errors

### Quality Metrics
- **Research Quality**: Methodology appropriateness and result interpretation accuracy
- **User Experience**: Conversational agent provides helpful, educational responses
- **Context Consistency**: Agents maintain consistent research context across interactions
- **Memory Accuracy**: Stored research patterns accurately reflect user preferences

### Scalability Metrics
- **Concurrent Users**: Support multiple researchers simultaneously
- **Session Persistence**: Memory systems scale across extended research projects
- **Tool Coordination**: Efficient orchestration of 121+ analysis tools
- **Resource Usage**: Optimal memory and compute resource utilization

## Running Tests

```bash
# Run all dual-agent coordination tests
python -m pytest dual_agent_tests/ -v

# Run memory integration tests  
python -m pytest memory_integration_tests/ -v

# Run specific stress test category
python -m pytest workflow_execution_tests/ -v --timeout=300

# Run end-to-end research scenario tests
python -m pytest research_scenario_tests/ -v --slow

# Generate performance report
python generate_stress_test_report.py
```

## Development Phases

### Phase 1: Basic Framework (Current)
- Set up testing directory structure
- Implement basic dual-agent coordination tests
- Test simple memory integration patterns

### Phase 2: Memory Integration
- Implement memory MCP server integration tests
- Test cross-session context persistence
- Validate memory-enhanced agent interactions

### Phase 3: Advanced Coordination
- Test complex workflow execution patterns
- Implement error recovery and resilience testing
- Test Claude Code SDK integration strategies

### Phase 4: Research Scenarios
- Implement end-to-end research workflow tests
- Test real-world research scenarios
- Validate research quality and user experience metrics

### Phase 5: Production Readiness
- Performance optimization based on stress test results
- Error handling improvements
- Documentation and deployment guidance

## Key Research Questions

1. **Optimal Agent Separation**: What's the best balance between conversational and execution contexts?
2. **Memory Architecture**: Which memory MCP combinations provide the best research context enhancement?
3. **Workflow Coordination**: How to efficiently coordinate complex, multi-step research workflows?
4. **Error Recovery**: What are the most effective strategies for handling tool execution failures?
5. **User Experience**: How to provide educational, patient interaction while maintaining execution efficiency?

## Contributing

When adding new stress tests:
1. Follow the directory structure and naming conventions
2. Include clear test documentation and expected outcomes
3. Add configuration files for reproducible test scenarios
4. Update performance baselines and success metrics
5. Document any new patterns or insights discovered

This framework will help validate and optimize the dual-agent research architecture before full implementation.