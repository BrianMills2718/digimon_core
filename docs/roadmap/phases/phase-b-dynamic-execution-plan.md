# PHASE B: DYNAMIC EXECUTION & INTELLIGENT ORCHESTRATION (3-4 weeks)

**Prerequisites**: Phase A must be 100% complete and tested
**Objective**: Enable dynamic tool selection and adaptive execution based on question analysis and intermediate results

## PHASE B IMPLEMENTATION TASKS

### Task B.1: Advanced Question Analysis & Intent Classification (Week 1)

**Deliverable**: Sophisticated question analysis that determines optimal tool chains dynamically

**Files to Create**:
- `src/nlp/advanced_intent_classifier.py` - Multi-dimensional question classification
- `src/nlp/question_complexity_analyzer.py` - Analyze question complexity and requirements
- `src/nlp/context_extractor.py` - Extract contextual requirements from questions
- `tests/test_advanced_question_analysis.py` - Advanced question analysis testing

**Implementation Requirements**:
```python
# src/nlp/advanced_intent_classifier.py
class AdvancedIntentClassifier:
    """Multi-dimensional question classification for optimal tool selection"""
    
    def __init__(self):
        self.complexity_analyzer = QuestionComplexityAnalyzer()
        self.context_extractor = ContextExtractor()
        
    def classify_question(self, question: str) -> QuestionAnalysis:
        """Comprehensive question analysis for dynamic tool selection"""
        
        # Primary intent classification
        primary_intent = self._classify_primary_intent(question)
        
        # Secondary analysis dimensions
        complexity = self.complexity_analyzer.analyze_complexity(question)
        context_requirements = self.context_extractor.extract_context(question)
        
        # Determine optimal tool chain based on multi-dimensional analysis
        optimal_tools = self._determine_optimal_tools(
            primary_intent, complexity, context_requirements
        )
        
        return QuestionAnalysis(
            primary_intent=primary_intent,
            complexity_level=complexity.level,
            context_requirements=context_requirements,
            optimal_tool_chain=optimal_tools,
            execution_strategy=self._determine_execution_strategy(complexity, optimal_tools)
        )

# Question Complexity Levels:
COMPLEXITY_LEVELS = {
    "simple": {
        "description": "Single-step analysis, one tool sufficient",
        "examples": ["What entities are mentioned?", "How many pages?"],
        "max_tools": 3
    },
    "moderate": {
        "description": "Multi-step analysis, tool chaining required",
        "examples": ["What are the main themes and how do they connect?"],
        "max_tools": 6
    },
    "complex": {
        "description": "Deep analysis, multiple iterations, adaptive execution",
        "examples": ["Analyze the evolution of relationships throughout the document"],
        "max_tools": 8,
        "requires_adaptive_execution": True
    }
}
```

**Success Criteria**:
- Classify questions into 10+ distinct intent categories
- Determine optimal tool chains based on question complexity
- Handle multi-part questions requiring different analysis approaches
- Provide confidence scores for tool selection recommendations

### Task B.2: Dynamic DAG Builder & Execution Planner (Week 1)

**Deliverable**: Create dynamic execution graphs instead of fixed pipelines

**Files to Create**:
- `src/execution/dag_builder.py` - Build directed acyclic graphs for tool execution
- `src/execution/execution_planner.py` - Plan optimal execution strategies
- `src/execution/dependency_resolver.py` - Resolve tool dependencies dynamically
- `tests/test_dynamic_dag_building.py` - DAG building and execution testing

**Implementation Requirements**:
```python
# src/execution/dag_builder.py
class DynamicDAGBuilder:
    """Build execution DAGs based on question analysis and tool requirements"""
    
    def __init__(self):
        self.dependency_resolver = DependencyResolver()
        self.execution_planner = ExecutionPlanner()
        
    def build_execution_dag(self, question_analysis: QuestionAnalysis) -> ExecutionDAG:
        """Build optimal execution DAG for question requirements"""
        
        # Start with required tools from question analysis
        required_tools = question_analysis.optimal_tool_chain
        
        # Resolve dependencies between tools
        tool_dependencies = self.dependency_resolver.resolve_dependencies(required_tools)
        
        # Create execution graph
        dag = ExecutionDAG()
        
        # Add nodes for each tool
        for tool in required_tools:
            dag.add_tool_node(
                tool_id=tool,
                dependencies=tool_dependencies.get(tool, []),
                execution_config=self._get_tool_config(tool, question_analysis)
            )
        
        # Add conditional branches based on question complexity
        if question_analysis.complexity_level == "complex":
            dag = self._add_adaptive_branches(dag, question_analysis)
        
        return dag
    
    def _add_adaptive_branches(self, dag: ExecutionDAG, analysis: QuestionAnalysis) -> ExecutionDAG:
        """Add conditional execution branches for complex questions"""
        
        # Add decision points where execution can branch based on intermediate results
        decision_points = [
            {
                "after_tool": "T23A_SPACY_NER",
                "condition": "entity_count > 50",
                "true_branch": ["T31_ENTITY_BUILDER", "T68_PAGE_RANK"],
                "false_branch": ["T27_RELATIONSHIP_EXTRACTOR", "T34_EDGE_BUILDER"]
            },
            {
                "after_tool": "T27_RELATIONSHIP_EXTRACTOR", 
                "condition": "relationship_count == 0",
                "true_branch": ["enhanced_relationship_extraction"],
                "false_branch": ["continue_normal_flow"]
            }
        ]
        
        for decision in decision_points:
            dag.add_conditional_branch(**decision)
        
        return dag

# Execution DAG Structure:
class ExecutionDAG:
    def __init__(self):
        self.nodes = {}  # tool_id -> ToolNode
        self.edges = []  # (from_tool, to_tool, condition)
        self.decision_points = {}  # tool_id -> ConditionalBranch
        
    def add_tool_node(self, tool_id: str, dependencies: List[str], execution_config: dict):
        """Add tool execution node to DAG"""
        self.nodes[tool_id] = ToolNode(tool_id, dependencies, execution_config)
        
    def add_conditional_branch(self, after_tool: str, condition: str, 
                             true_branch: List[str], false_branch: List[str]):
        """Add conditional execution branch"""
        self.decision_points[after_tool] = ConditionalBranch(
            condition=condition,
            true_branch=true_branch,
            false_branch=false_branch
        )
```

**Success Criteria**:
- Generate optimal execution DAGs for different question types
- Handle tool dependencies automatically
- Support conditional execution branches
- Enable parallel execution where dependencies allow

### Task B.3: Adaptive Execution Engine (Week 2)

**Deliverable**: Execute DAGs with ability to modify execution based on intermediate results

**Files to Create**:
- `src/execution/adaptive_executor.py` - Execute DAGs with runtime adaptation
- `src/execution/result_analyzer.py` - Analyze intermediate results for decision making
- `src/execution/execution_controller.py` - Control and modify execution flow
- `tests/test_adaptive_execution.py` - Adaptive execution testing

**Implementation Requirements**:
```python
# src/execution/adaptive_executor.py
class AdaptiveExecutor:
    """Execute DAGs with runtime adaptation based on intermediate results"""
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.result_analyzer = ResultAnalyzer()
        self.execution_controller = ExecutionController()
        
    async def execute_adaptive_dag(self, dag: ExecutionDAG, 
                                 question: str) -> AdaptiveExecutionResult:
        """Execute DAG with runtime adaptation"""
        
        execution_state = ExecutionState(dag, question)
        
        while not execution_state.is_complete():
            # Get next tools to execute (based on dependencies and current state)
            ready_tools = execution_state.get_ready_tools()
            
            # Execute ready tools in parallel where possible
            tool_results = await self._execute_tools_parallel(ready_tools)
            
            # Update execution state with results
            execution_state.update_with_results(tool_results)
            
            # Check for decision points
            for tool_id, result in tool_results.items():
                if tool_id in dag.decision_points:
                    # Analyze result and make branching decision
                    decision = await self._make_branching_decision(
                        dag.decision_points[tool_id], 
                        result, 
                        execution_state
                    )
                    
                    # Modify execution plan based on decision
                    execution_state = self.execution_controller.apply_decision(
                        execution_state, decision
                    )
            
            # Check if we need to add new tools based on results
            additional_tools = await self._analyze_for_additional_tools(
                execution_state, question
            )
            
            if additional_tools:
                execution_state = self.execution_controller.add_tools(
                    execution_state, additional_tools
                )
        
        return AdaptiveExecutionResult(
            final_results=execution_state.get_all_results(),
            execution_path=execution_state.execution_history,
            adaptations_made=execution_state.adaptations
        )
    
    async def _make_branching_decision(self, branch: ConditionalBranch, 
                                     result: ToolResult, 
                                     state: ExecutionState) -> BranchingDecision:
        """Make intelligent branching decisions based on intermediate results"""
        
        # Evaluate condition against result
        condition_met = self.result_analyzer.evaluate_condition(
            branch.condition, result, state.get_context()
        )
        
        selected_branch = branch.true_branch if condition_met else branch.false_branch
        
        return BranchingDecision(
            condition=branch.condition,
            condition_met=condition_met,
            selected_tools=selected_branch,
            reasoning=f"Condition '{branch.condition}' evaluated to {condition_met}"
        )

# Adaptive Execution Examples:
ADAPTIVE_EXECUTION_SCENARIOS = {
    "low_entity_count": {
        "trigger": "T23A result has < 5 entities",
        "adaptation": "Lower confidence threshold and re-run T23A",
        "reasoning": "Low entity count may indicate overly strict thresholds"
    },
    "no_relationships_found": {
        "trigger": "T27 result has 0 relationships", 
        "adaptation": "Add enhanced relationship extraction with different patterns",
        "reasoning": "Standard patterns may not match document style"
    },
    "high_complexity_document": {
        "trigger": "Document > 100 pages or > 10K entities",
        "adaptation": "Enable chunked processing and incremental analysis",
        "reasoning": "Large documents require different processing strategies"
    }
}
```

**Success Criteria**:
- Execute DAGs with runtime decision making
- Modify execution plans based on intermediate results
- Handle execution failures with graceful fallbacks
- Provide detailed execution traces for debugging

### Task B.4: Enhanced Result Synthesis & Context Management (Week 2)

**Deliverable**: Intelligent synthesis of results from dynamic tool chains

**Files to Create**:
- `src/nlp/intelligent_synthesizer.py` - Advanced result synthesis
- `src/context/conversation_context.py` - Manage conversation context across questions
- `src/context/document_context.py` - Maintain document-level context and insights
- `tests/test_intelligent_synthesis.py` - Result synthesis testing

**Implementation Requirements**:
```python
# src/nlp/intelligent_synthesizer.py
class IntelligentSynthesizer:
    """Advanced synthesis of results from dynamic tool execution"""
    
    def __init__(self):
        self.context_manager = ConversationContext()
        self.document_context = DocumentContext()
        
    def synthesize_adaptive_results(self, question: str, 
                                  execution_result: AdaptiveExecutionResult,
                                  session_context: dict = None) -> SynthesizedAnswer:
        """Synthesize results from adaptive execution into coherent answer"""
        
        # Extract key insights from all tool results
        key_insights = self._extract_key_insights(execution_result.final_results)
        
        # Consider execution path for answer completeness
        execution_insights = self._analyze_execution_path(execution_result.execution_path)
        
        # Incorporate conversation context if available
        if session_context:
            context_insights = self.context_manager.get_relevant_context(
                question, session_context
            )
            key_insights.update(context_insights)
        
        # Build comprehensive answer
        answer = self._build_comprehensive_answer(
            question=question,
            insights=key_insights,
            execution_metadata=execution_insights,
            adaptations=execution_result.adaptations_made
        )
        
        return SynthesizedAnswer(
            primary_answer=answer.primary_response,
            supporting_evidence=answer.evidence,
            confidence_score=answer.confidence,
            execution_summary=answer.execution_summary,
            follow_up_suggestions=self._suggest_follow_ups(question, key_insights)
        )
    
    def _suggest_follow_ups(self, question: str, insights: dict) -> List[str]:
        """Suggest relevant follow-up questions based on analysis results"""
        
        suggestions = []
        
        # Based on entities found
        if insights.get('entities'):
            suggestions.append(f"How do these entities relate to each other?")
            suggestions.append(f"What roles do these entities play in the document?")
        
        # Based on relationships found
        if insights.get('relationships'):
            suggestions.append(f"Are there any other patterns in these relationships?")
            suggestions.append(f"Which relationships are most significant?")
        
        # Based on document structure
        if insights.get('document_structure'):
            suggestions.append(f"What are the main sections or themes?")
            suggestions.append(f"How does the document's structure support its arguments?")
        
        return suggestions[:3]  # Limit to top 3 suggestions

# Context Management:
class ConversationContext:
    """Manage context across multiple questions in a session"""
    
    def __init__(self):
        self.conversation_history = []
        self.accumulated_insights = {}
        self.user_interests = []
        
    def add_interaction(self, question: str, answer: SynthesizedAnswer):
        """Add Q&A interaction to context"""
        self.conversation_history.append({
            'question': question,
            'answer': answer,
            'timestamp': datetime.now(),
            'key_insights': answer.supporting_evidence
        })
        
        # Update accumulated insights
        self._update_accumulated_insights(answer.supporting_evidence)
        
        # Infer user interests from question patterns
        self._update_user_interests(question)
    
    def get_relevant_context(self, current_question: str, max_history: int = 3) -> dict:
        """Get relevant context for current question"""
        
        # Find related previous questions
        related_history = self._find_related_interactions(current_question, max_history)
        
        # Extract relevant accumulated insights
        relevant_insights = self._extract_relevant_insights(current_question)
        
        return {
            'related_history': related_history,
            'accumulated_insights': relevant_insights,
            'user_interests': self.user_interests
        }
```

**Success Criteria**:
- Synthesize results from variable tool chains into coherent answers
- Maintain conversation context across multiple questions
- Suggest relevant follow-up questions
- Provide confidence scores and supporting evidence

### Task B.5: Performance Optimization & Parallel Execution (Week 3)

**Deliverable**: Optimize execution performance through intelligent parallelization

**Files to Create**:
- `src/execution/parallel_executor.py` - Parallel tool execution management
- `src/execution/resource_manager.py` - Manage system resources during execution
- `src/execution/performance_optimizer.py` - Optimize execution strategies
- `tests/test_parallel_execution.py` - Parallel execution testing

**Implementation Requirements**:
```python
# src/execution/parallel_executor.py
class ParallelExecutor:
    """Execute independent tools in parallel for performance optimization"""
    
    def __init__(self, max_concurrent_tools: int = 4):
        self.max_concurrent_tools = max_concurrent_tools
        self.resource_manager = ResourceManager()
        self.semaphore = asyncio.Semaphore(max_concurrent_tools)
        
    async def execute_tools_parallel(self, tool_batch: List[ToolExecution]) -> Dict[str, ToolResult]:
        """Execute independent tools in parallel"""
        
        # Group tools by resource requirements
        tool_groups = self._group_by_resource_requirements(tool_batch)
        
        results = {}
        
        # Execute each group with appropriate resource allocation
        for group_name, tools in tool_groups.items():
            group_results = await self._execute_tool_group(tools, group_name)
            results.update(group_results)
        
        return results
    
    async def _execute_tool_group(self, tools: List[ToolExecution], 
                                group_name: str) -> Dict[str, ToolResult]:
        """Execute a group of tools with shared resource constraints"""
        
        # Allocate resources for this group
        resource_allocation = self.resource_manager.allocate_for_group(group_name, len(tools))
        
        # Create execution tasks
        tasks = []
        for tool in tools:
            task = self._execute_single_tool_with_resources(tool, resource_allocation)
            tasks.append(task)
        
        # Execute with semaphore to limit concurrency
        async with self.semaphore:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle any exceptions
        processed_results = {}
        for tool, result in zip(tools, results):
            if isinstance(result, Exception):
                processed_results[tool.tool_id] = ToolResult.error(str(result))
            else:
                processed_results[tool.tool_id] = result
        
        return processed_results
    
    def _group_by_resource_requirements(self, tools: List[ToolExecution]) -> Dict[str, List[ToolExecution]]:
        """Group tools by their resource requirements for optimal parallel execution"""
        
        groups = {
            'cpu_intensive': [],    # T23A, T27 (NLP processing)
            'io_intensive': [],     # T01 (file loading)  
            'memory_intensive': [], # T68 (PageRank calculations)
            'network_intensive': [] # External API calls
        }
        
        for tool in tools:
            resource_type = self._classify_tool_resources(tool.tool_id)
            groups[resource_type].append(tool)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}

# Resource Management:
class ResourceManager:
    """Manage system resources during tool execution"""
    
    def __init__(self):
        self.cpu_cores = os.cpu_count()
        self.available_memory = psutil.virtual_memory().available
        self.resource_allocations = {}
        
    def allocate_for_group(self, group_name: str, tool_count: int) -> ResourceAllocation:
        """Allocate appropriate resources for tool group"""
        
        allocation_strategies = {
            'cpu_intensive': ResourceAllocation(
                max_threads=min(tool_count, self.cpu_cores),
                memory_limit=self.available_memory // 4,
                priority='high'
            ),
            'io_intensive': ResourceAllocation(
                max_threads=tool_count * 2,  # IO can handle more concurrency
                memory_limit=self.available_memory // 8,
                priority='medium'
            ),
            'memory_intensive': ResourceAllocation(
                max_threads=1,  # Serialize memory-intensive operations
                memory_limit=self.available_memory // 2,
                priority='high'
            )
        }
        
        return allocation_strategies.get(group_name, ResourceAllocation.default())
```

**Success Criteria**:
- Execute independent tools in parallel with 2-4x performance improvement
- Manage system resources to prevent resource exhaustion
- Handle execution failures without affecting other parallel tools
- Optimize execution order based on tool dependencies and resource requirements

### Task B.6: Comprehensive Integration Testing & Validation (Week 4)

**Deliverable**: Complete testing of dynamic execution system

**Files to Create**:
- `tests/integration/test_dynamic_execution_e2e.py` - End-to-end dynamic execution testing
- `tests/integration/test_adaptive_scenarios.py` - Test various adaptive execution scenarios
- `scripts/validate_phase_b.py` - Phase B validation script
- `examples/phase_b_demo.py` - Advanced dynamic execution demonstration

**Test Scenarios**:
```python
# tests/integration/test_dynamic_execution_e2e.py
class TestDynamicExecution:
    """Test complete dynamic execution workflow"""
    
    async def test_simple_question_optimization(self):
        """Test: Simple question uses minimal optimal tool chain"""
        interface = NaturalLanguageInterface()
        
        question = "How many entities are mentioned?"
        response = await interface.ask_question(question)
        
        # Should use only T01 → T15A → T23A (minimal chain)
        execution_log = interface.get_last_execution_log()
        assert len(execution_log.tools_used) == 3
        assert execution_log.execution_time < 10  # Should be fast
    
    async def test_complex_question_adaptation(self):
        """Test: Complex question triggers adaptive execution"""
        interface = NaturalLanguageInterface()
        
        question = "Analyze the evolution of relationships throughout this document"
        response = await interface.ask_question(question)
        
        # Should use full tool chain + adaptive branching
        execution_log = interface.get_last_execution_log()
        assert len(execution_log.tools_used) >= 6
        assert len(execution_log.adaptations) > 0
        assert execution_log.branching_decisions_made > 0
    
    async def test_parallel_execution_performance(self):
        """Test: Independent tools execute in parallel"""
        interface = NaturalLanguageInterface()
        
        question = "What are the entities, relationships, and main themes?"
        start_time = time.time()
        response = await interface.ask_question(question)
        execution_time = time.time() - start_time
        
        # Should be faster than sequential execution
        execution_log = interface.get_last_execution_log()
        assert execution_log.parallel_execution_used
        assert execution_time < execution_log.estimated_sequential_time * 0.7
    
    async def test_context_awareness(self):
        """Test: Follow-up questions use conversation context"""
        interface = NaturalLanguageInterface()
        session_id = "test_session"
        
        # First question
        response1 = await interface.ask_question(
            "What entities are mentioned?", session_id
        )
        
        # Follow-up question should use context
        response2 = await interface.ask_question(
            "How do they relate?", session_id
        )
        
        # Should reference entities from first question
        assert any(entity in response2 for entity in extract_entities_from_response(response1))
```

**Success Criteria**:
- Dynamic tool selection based on question analysis working
- Adaptive execution modifies plans based on intermediate results
- Parallel execution provides performance improvements
- Context management enables intelligent follow-up question handling
- All Phase A functionality remains intact

## PHASE B COMPLETION CRITERIA

**Phase B is complete when**:
1. ✅ Questions dynamically mapped to optimal tool chains
2. ✅ DAG-based execution replaces fixed pipelines  
3. ✅ Adaptive execution modifies plans based on intermediate results
4. ✅ Parallel execution of independent tools working
5. ✅ Conversation context maintained across questions
6. ✅ Performance optimizations show measurable improvements
7. ✅ All Phase A functionality preserved and enhanced

**Validation Commands**:
```bash
python scripts/validate_phase_b.py  # Must show 100% success
python examples/phase_b_demo.py     # Must demonstrate dynamic execution
```

**After Phase B Completion**:
🔄 **Replace this Phase B section with Phase C tasks from `docs/roadmap/phases/phase-c-advanced-intelligence-plan.md`**

## Phase B Success Metrics

| **Capability** | **Current (Phase A)** | **Target (Phase B)** |
|----------------|----------------------|---------------------|
| Tool Selection | Fixed 8-tool chain | Dynamic based on question |
| Execution Strategy | Sequential only | Parallel + adaptive |
| Question Complexity | 5 basic types | 15+ types with sub-categories |
| Execution Time | 15-30 seconds | 5-15 seconds (parallel optimization) |
| Context Awareness | None | Multi-turn conversation context |
| Adaptation | None | Runtime plan modification |
