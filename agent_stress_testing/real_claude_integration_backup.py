#!/usr/bin/env python3
"""
Real Claude Code Integration for Agent Stress Testing

Replaces all mocks with real Claude Code API integration for authentic testing.
"""

import asyncio
import json
import time
import subprocess
import tempfile
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from pathlib import Path


@dataclass
class ClaudeResponse:
    """Response from Claude Code API"""
    content: str
    usage: Dict[str, int]
    model: str
    response_time: float
    tool_calls: List[Dict[str, Any]]
    error: Optional[str] = None


class RealClaudeCodeClient:
    """Real Claude Code client for agent stress testing"""
    
    def __init__(self, 
                 system_prompt: str,
                 model: str = "claude-3-5-sonnet-20241022",
                 max_tokens: int = 4000,
                 temperature: float = 0.7,
                 tools: List[str] = None):
        self.system_prompt = system_prompt
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.tools = tools or []
        
        # Performance tracking
        self.call_history = []
        self.total_tokens_used = 0
        self.total_calls = 0
        self.total_response_time = 0.0
        
        # Validate Claude Code CLI availability
        self._validate_claude_cli()
    
    def _validate_claude_cli(self):
        """Validate that Claude Code CLI is available and configured"""
        try:
            result = subprocess.run(['claude', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise RuntimeError("Claude CLI not available or not configured")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise RuntimeError(f"Claude CLI validation failed: {e}")
    
    def _parse_tool_calls(self, response_content: str) -> List[Dict[str, Any]]:
        """Parse tool calls from Claude Code response"""
        import re
        tool_calls = []
        
        # Look for function call blocks in the response
        function_call_pattern = r'<function_calls>(.*?)</function_calls>'
        function_blocks = re.findall(function_call_pattern, response_content, re.DOTALL)
        
        for block in function_blocks:
            # Extract individual function invocations
            invoke_pattern = r'<invoke name="([^"]+)">(.*?)</invoke>'
            invocations = re.findall(invoke_pattern, block, re.DOTALL)
            
            for function_name, params_block in invocations:
                # Extract parameters
                param_pattern = r'<parameter name="([^"]+)">([^<]*)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                full_prompt = f"""System: {self.system_prompt}

User: {prompt}"""
                f.write(full_prompt)
                temp_file = f.name
            
            # Build Claude CLI command
            cmd = [
                'claude',
                '--model', self.model,
                '--max-tokens', str(self.max_tokens),
                '--temperature', str(self.temperature),
                temp_file
            ]
            
            # Execute Claude CLI
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            response_time = time.time() - start_time
            
            # Clean up temp file
            os.unlink(temp_file)
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                return ClaudeResponse(
                    content="",
                    usage={"input_tokens": 0, "output_tokens": 0},
                    model=self.model,
                    response_time=response_time,
                    tool_calls=[],
                    error=error_msg
                )
            
            response_content = stdout.decode('utf-8')
            
            # Parse tool calls from Claude Code response
            tool_calls = self._parse_tool_calls(response_content)
            
            # Estimate token usage (rough approximation)
            input_tokens = len(full_prompt.split())
            output_tokens = len(response_content.split())
            
            # Update tracking
            self.total_calls += 1
            self.total_tokens_used += input_tokens + output_tokens
            self.total_response_time += response_time
            
            call_record = {
                "timestamp": start_time,
                "prompt_length": len(prompt),
                "response_length": len(response_content),
                "response_time": response_time,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "tool_calls_count": len(tool_calls)
            }
            self.call_history.append(call_record)
            
            return ClaudeResponse(
                content=response_content,
                usage={"input_tokens": input_tokens, "output_tokens": output_tokens},
                model=self.model,
                response_time=response_time,
                tool_calls=tool_calls,
                error=None
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ClaudeResponse(
                content="",
                usage={"input_tokens": 0, "output_tokens": 0},
                model=self.model,
                response_time=response_time,
                tool_calls=[],
                error=str(e)
            )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this client"""
        if self.total_calls == 0:
            return {
                "total_calls": 0,
                "avg_response_time": 0.0,
                "total_tokens": 0,
                "avg_tokens_per_call": 0.0
            }
        
        return {
            "total_calls": self.total_calls,
            "avg_response_time": self.total_response_time / self.total_calls,
            "total_tokens": self.total_tokens_used,
            "avg_tokens_per_call": self.total_tokens_used / self.total_calls,
            "call_history": self.call_history[-10:]  # Last 10 calls
        }


class DualAgentCoordinator:
    """Real dual-agent coordinator using actual Claude Code API"""
    
    def __init__(self, research_config: Dict[str, Any], execution_config: Dict[str, Any]):
        self.research_agent = RealClaudeCodeClient(
            system_prompt=research_config["system_prompt"],
            model=research_config.get("model", "claude-3-5-sonnet-20241022"),
            max_tokens=research_config.get("max_tokens", 4000),
            temperature=research_config.get("temperature", 0.7),
            tools=research_config.get("tools", [])
        )
        
        self.execution_agent = RealClaudeCodeClient(
            system_prompt=execution_config["system_prompt"],
            model=execution_config.get("model", "claude-3-5-sonnet-20241022"),
            max_tokens=execution_config.get("max_tokens", 4000),
            temperature=execution_config.get("temperature", 0.3),
            tools=execution_config.get("tools", [])
        )
        
        self.coordination_log = []
    
    async def execute_research_workflow(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute real research workflow with dual-agent coordination"""
        start_time = time.time()
        
        try:
            # Step 1: Research agent designs workflow
            workflow_prompt = f"""
Research Query: {query}
Context: {json.dumps(context or {}, indent=2)}

Design a comprehensive research workflow that includes:
1. Specific analysis steps
2. Tool requirements  
3. Expected outputs
4. Quality validation methods

Provide a structured workflow specification that can be executed systematically.
"""
            
            workflow_response = await self.research_agent.query(workflow_prompt)
            if workflow_response.error:
                raise RuntimeError(f"Research agent error: {workflow_response.error}")
            
            # Step 2: Extract workflow specification
            workflow_spec = self._extract_workflow_from_response(workflow_response.content)
            
            # Step 3: Execution agent validates and executes
            execution_prompt = f"""
Execute this research workflow specification:

{workflow_spec}

Provide detailed execution results including:
1. Step-by-step progress
2. Outputs generated
3. Quality metrics
4. Performance statistics
5. Any errors or issues encountered
"""
            
            execution_response = await self.execution_agent.query(execution_prompt)
            if execution_response.error:
                raise RuntimeError(f"Execution agent error: {execution_response.error}")
            
            # Step 4: Research agent interprets results
            interpretation_prompt = f"""
Interpret these research execution results:

Original Query: {query}
Execution Results: {execution_response.content}

Provide:
1. Key findings and insights
2. Research implications
3. Methodology assessment
4. Recommendations for further research
"""
            
            interpretation_response = await self.research_agent.query(interpretation_prompt)
            if interpretation_response.error:
                raise RuntimeError(f"Interpretation error: {interpretation_response.error}")
            
            total_time = time.time() - start_time
            
            return {
                "status": "success",
                "query": query,
                "workflow_design": workflow_response.content,
                "workflow_specification": workflow_spec,
                "execution_results": execution_response.content,
                "research_interpretation": interpretation_response.content,
                "performance_metrics": {
                    "total_time": total_time,
                    "research_agent_stats": self.research_agent.get_performance_stats(),
                    "execution_agent_stats": self.execution_agent.get_performance_stats()
                },
                "token_usage": {
                    "workflow_design": workflow_response.usage,
                    "execution": execution_response.usage,
                    "interpretation": interpretation_response.usage
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "query": query,
                "partial_results": {
                    "research_agent_stats": self.research_agent.get_performance_stats(),
                    "execution_agent_stats": self.execution_agent.get_performance_stats()
                }
            }
    
    def _extract_workflow_from_response(self, response: str) -> str:
        """Extract workflow specification from response"""
        # Simple extraction - in real implementation, would parse structured formats
        lines = response.split('\n')
        workflow_lines = []
        in_workflow = False
        
        for line in lines:
            if 'workflow' in line.lower() or 'steps' in line.lower():
                in_workflow = True
            if in_workflow:
                workflow_lines.append(line)
        
        return '\n'.join(workflow_lines) if workflow_lines else response