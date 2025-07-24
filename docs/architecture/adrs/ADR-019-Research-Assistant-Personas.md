# ADR-019: Dual-Agent Research Architecture

**Status**: Accepted  
**Date**: 2025-07-23  
**Decision Makers**: KGAS Development Team  

## Context

Research workflows require two distinct types of AI interaction:

1. **Conversational Research Assistant**: Patient, explanatory, iterative dialogue for research exploration, question refinement, and results interpretation
2. **Workflow Execution Agent**: Efficient, focused task execution for running analysis workflows, tool coordination, and data processing

Current single-agent approaches force one agent to handle both conversational support and efficient execution, leading to suboptimal performance in both areas. Research users need patient explanation and iteration, while workflow execution needs speed and precision.

## Decision

We will implement a **Dual-Agent Research Architecture** that separates concerns between user interaction and workflow execution, leveraging Claude Code's existing subagent capabilities with specialized prompting and context strategies.

## Dual-Agent Architecture

### Research Interaction Agent (Primary)

**Purpose**: Handle user interaction, research guidance, and result interpretation  
**Context Strategy**: Full conversational memory, domain knowledge, research methodology  
**Prompting Strategy**: Patient, explanatory, educational  

```python
class ResearchInteractionAgent:
    """Patient research assistant for user interaction and guidance"""
    
    def __init__(self, claude_code_sdk: ClaudeCodeSDK):
        self.sdk = claude_code_sdk
        self.system_prompt = self._build_research_prompt()
        self.memory_context = ResearchMemoryContext()
    
    def _build_research_prompt(self) -> str:
        return """
You are an expert academic research assistant specializing in social science research.

Your role:
- Guide researchers through complex analysis workflows
- Explain methodologies and their appropriateness
- Help refine research questions and hypotheses
- Interpret analysis results in research context
- Provide educational context and domain background
- Ask clarifying questions to understand intent

Communication style:
- Be patient and explanatory
- Use academic language appropriately
- Provide reasoning for recommendations
- Offer multiple approaches when appropriate
- Build on the researcher's existing knowledge

Never execute analysis workflows directly - delegate to execution agent.
"""
    
    async def handle_research_query(self, query: str) -> ResearchResponse:
        """Handle conversational research interaction"""
        # Understand research intent
        intent = await self._analyze_research_intent(query)
        
        # Refine research question if needed
        refined_query = await self._refine_research_question(query, intent)
        
        # Generate workflow specification
        workflow_spec = await self._generate_workflow_spec(refined_query)
        
        # Delegate to execution agent
        execution_results = await self.delegate_to_execution(workflow_spec)
        
        # Interpret and explain results
        interpretation = await self._interpret_results(execution_results, intent)
        
        return ResearchResponse(
            refined_query=refined_query,
            methodology_explanation=workflow_spec.explanation,
            results=execution_results,
            interpretation=interpretation,
            follow_up_suggestions=self._suggest_follow_ups(interpretation)
        )
```

### Workflow Execution Agent (Subagent)

**Purpose**: Efficient execution of analysis workflows and tool coordination  
**Context Strategy**: Minimal - workflow specification and tool results only  
**Prompting Strategy**: Concise, task-focused, error-handling oriented  

```python
class WorkflowExecutionAgent:
    """Efficient task executor for analysis workflows"""
    
    def __init__(self, claude_code_sdk: ClaudeCodeSDK):
        self.sdk = claude_code_sdk
        self.system_prompt = self._build_execution_prompt()
        self.tool_registry = KGASToolRegistry()
    
    def _build_execution_prompt(self) -> str:
        return """
You are a precise workflow execution agent for KGAS research analysis.

Your role:
- Execute analysis workflows efficiently and accurately
- Coordinate cross-modal analysis tools (graph, table, vector)
- Handle errors gracefully with clear reporting
- Optimize tool usage for performance
- Maintain data provenance and quality metrics

Execution principles:
- Focus on task completion over explanation
- Provide concise status updates
- Report errors with actionable details
- Ensure data consistency across tool chains
- Minimize token usage while maintaining accuracy

Available tools: All 121 KGAS analysis tools plus cross-modal orchestration.
Context: You receive workflow specifications and execute them systematically.
"""
    
    async def execute_workflow(self, workflow_spec: WorkflowSpecification) -> ExecutionResults:
        """Execute research workflow with tool coordination"""
        execution_context = ExecutionContext(workflow_spec)
        
        try:
            # Validate workflow
            validation = await self._validate_workflow(workflow_spec)
            if not validation.is_valid:
                return ExecutionResults.error(validation.errors)
            
            # Execute phases sequentially
            results = {}
            for phase in workflow_spec.phases:
                phase_result = await self._execute_phase(phase, execution_context)
                results[phase.name] = phase_result
                execution_context.update_with_phase_result(phase.name, phase_result)
            
            # Generate cross-modal integration if specified
            if workflow_spec.requires_cross_modal:
                integration_result = await self._execute_cross_modal_integration(
                    results, workflow_spec.cross_modal_spec
                )
                results['cross_modal_integration'] = integration_result
            
            return ExecutionResults.success(
                results=results,
                provenance=execution_context.get_full_provenance(),
                performance_metrics=execution_context.get_performance_metrics()
            )
            
        except Exception as e:
            return ExecutionResults.error(
                error=str(e),
                partial_results=execution_context.get_partial_results(),
                recovery_suggestions=self._generate_recovery_suggestions(e, workflow_spec)
            )
```

## Memory Integration with MCP Servers

### Research Memory Architecture

**Persistent Knowledge Storage**: Integration with memory MCP servers for cross-session research context

```python
class ResearchMemoryIntegration:
    """Integrate with memory MCP servers for persistent research context"""
    
    def __init__(self):
        self.memory_servers = {
            # Knowledge graph-based memory for structured research context
            "knowledge_graph": "modelcontextprotocol/server-memory",
            
            # RAG-based memory for document and literature context  
            "document_memory": "mem0ai/mem0-mcp",
            
            # Zettelkasten for atomic research notes and connections
            "research_notes": "entanglr/zettelkasten-mcp",
            
            # Persistent summarization for large document analysis
            "summarization": "0xshellming/mcp-summarizer"
        }
    
    async def store_research_context(self, 
                                   session_id: str,
                                   research_context: ResearchContext) -> None:
        """Store research session context across memory systems"""
        
        # Store structured research relationships in knowledge graph
        await self.knowledge_graph.store_entities([
            Entity("research_question", research_context.question),
            Entity("methodology", research_context.methodology),
            Entity("domain", research_context.domain)
        ])
        
        # Store research patterns and preferences in mem0
        await self.document_memory.store_preference(
            f"User prefers {research_context.methodology} for {research_context.domain} research"
        )
        
        # Create atomic research notes in Zettelkasten
        await self.research_notes.create_note(
            title=f"Research Session {session_id}",
            content=research_context.summary,
            tags=[research_context.domain, research_context.methodology]
        )
    
    async def retrieve_research_context(self, 
                                      current_query: str,
                                      user_id: str) -> EnhancedContext:
        """Retrieve relevant research context from memory systems"""
        
        # Get related research from knowledge graph
        related_research = await self.knowledge_graph.query_related(current_query)
        
        # Get user research patterns from mem0
        user_patterns = await self.document_memory.get_user_patterns(user_id)
        
        # Find connected research notes from Zettelkasten
        connected_notes = await self.research_notes.find_connected(current_query)
        
        return EnhancedContext(
            related_research=related_research,
            user_patterns=user_patterns,
            connected_notes=connected_notes,
            recommended_approaches=self._synthesize_recommendations(
                related_research, user_patterns, connected_notes
            )
        )
```

## Implementation Strategies

### Claude Code SDK Integration

```python
class KGASDualAgentOrchestrator:
    """Orchestrate dual-agent research workflow using Claude Code SDK"""
    
    def __init__(self):
        # Research interaction agent with conversational prompting
        self.research_agent = ClaudeCodeSDK(
            system_prompt=self._research_assistant_prompt(),
            max_turns=15,  # Extended for conversation
            tools=["conceptual_analysis", "research_planning", "result_interpretation"],
            temperature=0.7  # More conversational
        )
        
        # Execution agent with task-focused prompting  
        self.execution_agent = ClaudeCodeSDK(
            system_prompt=self._execution_agent_prompt(),
            max_turns=5,   # Focused execution
            tools=["all_kgas_tools", "cross_modal_orchestration"],
            temperature=0.3  # More deterministic
        )
        
        # Memory integration
        self.memory = ResearchMemoryIntegration()
    
    async def handle_research_interaction(self, query: str, user_id: str) -> ResearchResponse:
        """Complete research interaction with dual-agent coordination"""
        
        # Enhance query with research memory
        enhanced_context = await self.memory.retrieve_research_context(query, user_id)
        enhanced_query = f"{query}\n\nRelevant context: {enhanced_context.summary}"
        
        # Research agent handles user interaction
        research_response = await self.research_agent.query(enhanced_query)
        
        # Extract workflow specification from research agent
        workflow_spec = self._extract_workflow_specification(research_response)
        
        if workflow_spec:
            # Execution agent runs the workflow
            execution_results = await self.execution_agent.execute_workflow(workflow_spec)
            
            # Research agent interprets results
            interpretation_query = f"""
            Research results: {execution_results}
            Original question: {query}
            Please interpret these results in research context and suggest next steps.
            """
            interpretation = await self.research_agent.query(interpretation_query)
            
            # Store research session in memory
            await self.memory.store_research_session(
                query, workflow_spec, execution_results, interpretation, user_id
            )
            
            return ResearchResponse(
                conversation=research_response,
                workflow_executed=workflow_spec,
                execution_results=execution_results,
                interpretation=interpretation
            )
        else:
            # Pure conversational response - no workflow needed
            return ResearchResponse(conversation=research_response)
```

### Git Worktree Strategy

```bash
# Set up specialized agent environments
git worktree add ../kgas-research research-interface
git worktree add ../kgas-execution workflow-execution

# Different CLAUDE.md files for different contexts
echo "# Research Assistant Mode
- Patient and explanatory interaction
- Focus on methodology and interpretation
- Educational approach to analysis" > ../kgas-research/CLAUDE.md

echo "# Execution Mode  
- Efficient workflow execution
- Minimal explanations unless errors
- Focus on tool coordination and results" > ../kgas-execution/CLAUDE.md
```

### Hook-Based Context Management

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "workflow_execution_.*",
      "hooks": [{
        "command": "python switch_to_execution_context.py"
      }]
    }],
    "PostToolUse": [{
      "matcher": "workflow_execution_.*",
      "hooks": [{
        "command": "python restore_research_context.py"  
      }]
    }]
  }
}
```

## Memory MCP Server Recommendations

### Priority 1: Essential Memory Infrastructure

**For KGAS implementation, prioritize these memory MCP servers:**

1. **modelcontextprotocol/server-memory** - Knowledge graph-based persistent memory
   - **Use**: Store research relationships, methodology patterns, cross-session context
   - **Integration**: Primary memory backend for both agents

2. **mem0ai/mem0-mcp** - Coding preferences and patterns memory  
   - **Use**: Remember user research preferences, methodology choices, successful patterns
   - **Integration**: Research agent personalization and workflow optimization

3. **entanglr/zettelkasten-mcp** - Atomic research notes and connections
   - **Use**: Build connected research knowledge base, link analysis sessions
   - **Integration**: Research note-taking and knowledge building across projects

### Priority 2: Enhanced Research Capabilities

4. **0xshellming/mcp-summarizer** - Multi-format content summarization
   - **Use**: Summarize large documents, research papers, analysis results
   - **Integration**: Both agents for content processing and result synthesis

5. **apecloud/ApeRAG** - Production RAG with Graph RAG and vector search
   - **Use**: Advanced literature search, document retrieval, context enhancement
   - **Integration**: Research agent for literature review and contextual enhancement

6. **upstash/context7** - Up-to-date code documentation
   - **Use**: Current methodology documentation, tool usage examples
   - **Integration**: Execution agent for tool coordination and methodology guidance

### Memory Architecture Integration

```python
class EnhancedKGASMemorySystem:
    """Comprehensive memory integration for dual-agent research system"""
    
    def __init__(self):
        self.memory_stack = {
            # Structured knowledge storage
            "knowledge_graph": MCPClient("modelcontextprotocol/server-memory"),
            
            # User preference learning  
            "preference_memory": MCPClient("mem0ai/mem0-mcp"),
            
            # Research note connections
            "research_notes": MCPClient("entanglr/zettelkasten-mcp"),
            
            # Content summarization
            "summarizer": MCPClient("0xshellming/mcp-summarizer"),
            
            # Advanced RAG capabilities
            "rag_system": MCPClient("apecloud/ApeRAG"),
            
            # Methodology documentation
            "methodology_docs": MCPClient("upstash/context7")
        }
    
    async def enhance_research_context(self, query: str, user_id: str) -> EnhancedContext:
        """Combine multiple memory systems for comprehensive context"""
        
        # Get related research patterns from knowledge graph
        related_patterns = await self.knowledge_graph.query_patterns(query)
        
        # Retrieve user research preferences
        user_prefs = await self.preference_memory.get_preferences(user_id, "research")
        
        # Find connected research notes  
        connected_notes = await self.research_notes.find_connections(query)
        
        # Get relevant methodology documentation
        methodology_docs = await self.methodology_docs.search_docs(query)
        
        # Perform RAG search for relevant literature
        literature_context = await self.rag_system.search_literature(query)
        
        return EnhancedContext(
            related_patterns=related_patterns,
            user_preferences=user_prefs,
            connected_notes=connected_notes,
            methodology_guidance=methodology_docs,
            literature_context=literature_context,
            synthesis=self._synthesize_context(
                related_patterns, user_prefs, connected_notes, 
                methodology_docs, literature_context
            )
        )
    
    async def store_research_session(self, session_data: ResearchSession) -> None:
        """Store research session across multiple memory systems"""
        
        # Store structured relationships in knowledge graph
        await self.knowledge_graph.store_session_relationships(session_data)
        
        # Learn user preferences from session
        await self.preference_memory.update_preferences(
            session_data.user_id, session_data.successful_patterns
        )
        
        # Create research notes with connections
        await self.research_notes.create_linked_note(
            session_data.summary, session_data.connections
        )
        
        # Summarize and store key insights
        summary = await self.summarizer.summarize_session(session_data)
        await self.knowledge_graph.store_insight(summary)
```

## Benefits

1. **Context Separation**: Optimized prompting for interaction vs execution
2. **Efficiency**: Focused execution without conversational overhead  
3. **User Experience**: Patient, explanatory interaction when needed
4. **Memory Persistence**: Cross-session research context and learning
5. **Scalability**: Parallel agent execution for complex research workflows

## Consequences

### Positive
- Better user experience with appropriate interaction style
- More efficient workflow execution
- Persistent research memory and learning
- Flexible coordination between different agent capabilities

### Negative  
- Increased complexity in agent coordination
- Need for robust workflow specification interface
- Memory system integration and maintenance overhead
- Potential context switching delays

## Implementation Priority

**Phase 2.2** - After Phase 2.1 analytics tools are complete

**Implementation Order**:
1. Basic dual-agent SDK integration
2. Memory MCP server integration (Priority 1 servers)
3. Advanced context enhancement (Priority 2 servers)
4. Hook-based optimization and git worktree strategies

## Success Metrics

1. **Agent Efficiency**: Execution agent completes workflows 40% faster than conversational agent
2. **User Satisfaction**: Research agent provides more helpful explanations and guidance
3. **Memory Utilization**: Cross-session context improves research quality and reduces repetitive explanation
4. **Workflow Success Rate**: Higher completion rates for complex multi-step analyses
5. **Research Quality**: Better methodology selection and result interpretation