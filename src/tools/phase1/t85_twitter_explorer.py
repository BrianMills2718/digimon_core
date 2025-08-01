"""
T85: Twitter API Explorer Tool

A comprehensive Twitter data exploration tool that integrates TwitterExplorer
functionality into the KGAS architecture using contract-first design.
"""

import time
import json
import yaml
import psutil
import logging
import os
import re
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import Google Gemini
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus, ToolErrorCode
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)

# API Configuration
RAPIDAPI_TWITTER_HOST = "twitter-api45.p.rapidapi.com"
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_TWITTER_HOST}"
GEMINI_MODEL_NAME = "gemini-1.5-pro"
API_TIMEOUT_SECONDS = 30


class TwitterExplorerTool(BaseTool):
    """T85: Twitter API Explorer with Graph Building Capabilities"""
    
    def __init__(self, services: ServiceManager):
        super().__init__(services)
        self.tool_id = "T85_TWITTER_EXPLORER"
        
        # Load API keys from environment
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.rapidapi_key = os.getenv("TWITTER_API45_API_KEY") or os.getenv("RAPIDAPI_KEY")
        
        # Initialize Gemini client
        self._gemini_model = None
        self._initialize_gemini()
        
        logger.info(f"Initialized {self.tool_id}")
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        # Load contract from YAML file
        contract_path = Path(__file__).parent.parent.parent.parent / "contracts" / "tools" / "T85_TWITTER_EXPLORER.yaml"
        
        try:
            with open(contract_path, 'r') as f:
                contract_data = yaml.safe_load(f)
            
            return ToolContract(
                tool_id=contract_data["tool_id"],
                name=contract_data["name"],
                description=contract_data["description"],
                category=contract_data["category"],
                input_schema=contract_data["input_schema"],
                output_schema=contract_data["output_schema"],
                dependencies=contract_data["dependencies"],
                performance_requirements=contract_data["performance_requirements"],
                error_conditions=contract_data["error_conditions"]
            )
        except Exception as e:
            logger.error(f"Failed to load contract: {e}")
            # Return minimal contract as fallback
            return ToolContract(
                tool_id=self.tool_id,
                name="Twitter API Explorer",
                description="Explore Twitter data via natural language queries",
                category="social_media_analysis",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "api_keys": {
                            "type": "object",
                            "properties": {
                                "gemini_key": {"type": "string"},
                                "rapidapi_key": {"type": "string"}
                            },
                            "required": ["gemini_key", "rapidapi_key"]
                        }
                    },
                    "required": ["query", "api_keys"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "entities": {"type": "array"},
                        "relationships": {"type": "array"},
                        "graph_data": {"type": "object"},
                        "processing_stats": {"type": "object"}
                    },
                    "required": ["summary", "entities", "relationships", "processing_stats"]
                },
                dependencies=["google-generativeai", "requests", "networkx"],
                performance_requirements={
                    "max_execution_time": 120.0,
                    "max_memory_mb": 500,
                    "min_accuracy": 0.85
                },
                error_conditions=[
                    "INVALID_QUERY", "MISSING_API_KEYS", "INVALID_API_CREDENTIALS",
                    "RATE_LIMIT_EXCEEDED", "API_TIMEOUT"
                ]
            )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        if not input_data or not isinstance(input_data, dict):
            return False
        
        # Check required fields
        if "query" not in input_data:
            return False
        
        if not input_data["query"] or not isinstance(input_data["query"], str):
            return False
        
        if len(input_data["query"].strip()) == 0:
            return False
        
        # Check API keys
        if "api_keys" not in input_data:
            return False
        
        api_keys = input_data["api_keys"]
        if not isinstance(api_keys, dict):
            return False
        
        if "gemini_key" not in api_keys or "rapidapi_key" not in api_keys:
            return False
        
        if not api_keys["gemini_key"] or not api_keys["rapidapi_key"]:
            return False
        
        return True
    
    def _initialize_gemini(self):
        """Initialize Gemini model for query planning"""
        if not genai:
            logger.warning("google-generativeai not installed. LLM query planning will not work.")
            return
        
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            return
        
        try:
            genai.configure(api_key=self.gemini_api_key)
            self._gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            logger.info("Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self._gemini_model = None
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute Twitter query with comprehensive error handling"""
        self._start_execution()
        
        try:
            # Handle None request
            if request is None:
                return self._create_error_result(
                    None,
                    "INVALID_INPUT",
                    "Request cannot be None"
                )
            
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result(
                    request,
                    "INVALID_INPUT",
                    "Input validation failed against tool contract"
                )
            
            # Extract parameters
            query = request.input_data["query"]
            api_keys = request.input_data["api_keys"]
            max_results = request.input_data.get("max_results", 100)
            include_graph = request.input_data.get("include_graph", True)
            timeout_seconds = request.input_data.get("timeout_seconds", 60)
            
            # Log execution start
            operation_id = None
            if self.services and hasattr(self.services, 'provenance_service'):
                operation_id = self.services.provenance_service.start_operation(
                    operation_type="twitter_query_execution",
                    used={"query": query},  # Used resources
                    agent_details={"tool_id": self.tool_id},
                    parameters={
                        "query": query,
                        "max_results": max_results,
                        "include_graph": include_graph,
                        "timeout_seconds": timeout_seconds
                    }
                )
            
            # Execute Twitter query with actual implementation
            result_data = self._execute_twitter_query(
                query, api_keys, max_results, include_graph, timeout_seconds
            )
            
            # Calculate execution metrics
            execution_time, memory_used = self._end_execution()
            self.status = ToolStatus.READY
            
            # Complete operation with results
            if operation_id and self.services and hasattr(self.services, 'provenance_service'):
                self.services.provenance_service.complete_operation(
                    operation_id=operation_id,
                    outputs=[f"twitter_results_{operation_id}"],  # Output references
                    success=True,
                    metadata={
                        "entities_extracted": len(result_data.get("entities", [])),
                        "relationships_extracted": len(result_data.get("relationships", [])),
                        "api_calls_made": result_data.get("processing_stats", {}).get("total_api_calls", 0),
                        "execution_time": execution_time
                    }
                )
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data=result_data,
                metadata={
                    "tool_version": "1.0.0",
                    "query": query,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            self.status = ToolStatus.ERROR
            execution_time, memory_used = self._end_execution()
            
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return self._create_error_result(
                request,
                "UNEXPECTED_ERROR",
                f"Unexpected error during Twitter query execution: {str(e)}",
                execution_time,
                memory_used
            )
    
    def _execute_twitter_query(self, query: str, api_keys: Dict[str, str], 
                              max_results: int, include_graph: bool, 
                              timeout_seconds: int) -> Dict[str, Any]:
        """Execute Twitter query with real API integration"""
        
        try:
            # Step 1: Plan the query execution using LLM
            query_plan = self._plan_query_execution(query, api_keys["gemini_key"])
            
            if query_plan.get("response_type") != "PLAN":
                # Return clarification or error
                return {
                    "summary": query_plan.get("message_to_user", "Unable to process query"),
                    "entities": [],
                    "relationships": [],
                    "graph_data": {"nodes": [], "edges": [], "metadata": {"node_count": 0, "edge_count": 0, "connected_components": 0}},
                    "api_execution_log": [],
                    "processing_stats": {
                        "total_api_calls": 0,
                        "total_execution_time": 0.0,
                        "entities_extracted": 0,
                        "relationships_extracted": 0,
                        "query_complexity_score": self._calculate_query_complexity(query)
                    }
                }
            
            # Step 2: Execute the API plan
            api_results = self._execute_api_plan(
                query_plan["api_plan"], 
                api_keys["rapidapi_key"], 
                timeout_seconds
            )
            
            # Step 3: Extract entities from results
            entities = self._extract_entities_from_results(api_results)
            
            # Step 4: Extract relationships from results
            relationships = self._extract_relationships_from_results(api_results, entities)
            
            # Step 5: Build graph data if requested
            graph_data = self._build_graph_data(entities, relationships) if include_graph else {
                "nodes": [], "edges": [], "metadata": {"node_count": 0, "edge_count": 0, "connected_components": 0}
            }
            
            # Step 6: Generate summary
            summary = self._generate_summary(query, entities, relationships)
            
            # Step 7: Calculate processing stats
            processing_stats = {
                "total_api_calls": len(api_results),
                "total_execution_time": sum(result.get("response_time", 0) for result in api_results),
                "entities_extracted": len(entities),
                "relationships_extracted": len(relationships),
                "query_complexity_score": self._calculate_query_complexity(query)
            }
            
            return {
                "summary": summary,
                "entities": entities,
                "relationships": relationships,
                "graph_data": graph_data,
                "api_execution_log": api_results,
                "processing_stats": processing_stats
            }
            
        except Exception as e:
            logger.error(f"Error executing Twitter query: {e}", exc_info=True)
            return {
                "summary": f"Error executing query: {str(e)}",
                "entities": [],
                "relationships": [],
                "graph_data": {"nodes": [], "edges": [], "metadata": {"node_count": 0, "edge_count": 0, "connected_components": 0}},
                "api_execution_log": [],
                "processing_stats": {
                    "total_api_calls": 0,
                    "total_execution_time": 0.0,
                    "entities_extracted": 0,
                    "relationships_extracted": 0,
                    "query_complexity_score": self._calculate_query_complexity(query)
                }
            }
    
    def _extract_username_from_query(self, query: str) -> Optional[str]:
        """Extract username from query"""
        import re
        match = re.search(r'@(\w+)', query)
        return match.group(1) if match else None
    
    def _generate_summary(self, query: str, entities: List[Dict], relationships: List[Dict]) -> str:
        """Generate summary of findings"""
        if not entities and not relationships:
            return f"No Twitter data found for query: '{query}'"
        
        entity_count = len(entities)
        relationship_count = len(relationships)
        
        summary_parts = []
        if entity_count > 0:
            entity_types = list(set(e["entity_type"] for e in entities))
            summary_parts.append(f"Found {entity_count} entities ({', '.join(entity_types)})")
        
        if relationship_count > 0:
            rel_types = list(set(r["relationship_type"] for r in relationships))
            summary_parts.append(f"Found {relationship_count} relationships ({', '.join(rel_types)})")
        
        return ". ".join(summary_parts) if summary_parts else f"Processed query: '{query}'"
    
    def _calculate_query_complexity(self, query: str) -> float:
        """Calculate query complexity score (0.0 to 1.0)"""
        complexity_indicators = [
            ("followers", 0.3),
            ("following", 0.3),
            ("timeline", 0.2),
            ("replies", 0.4),
            ("retweets", 0.3),
            ("conversation", 0.5),
            ("thread", 0.4),
            ("analyze", 0.6),
            ("compare", 0.7),
            ("all", 0.5),
            ("recent", 0.2)
        ]
        
        base_complexity = 0.1  # Base complexity for any query
        for indicator, weight in complexity_indicators:
            if indicator in query.lower():
                base_complexity += weight
        
        # Normalize to 0.0-1.0 range
        return min(base_complexity, 1.0)
    
    def _plan_query_execution(self, query: str, gemini_key: str) -> Dict[str, Any]:
        """Plan query execution using Gemini LLM"""
        if not self._gemini_model:
            logger.error("Gemini model not initialized")
            return {
                "response_type": "ERROR",
                "message_to_user": "Query planning service unavailable"
            }
        
        # Create planning prompt
        planning_prompt = f"""
You are an expert AI assistant tasked with exploring Twitter data using specific API tools.
Your goal is to understand the user's request and create a step-by-step execution plan.

Available Twitter API Endpoints:
1. screenname.php - Get user profile by username (params: screenname)
2. timeline.php - Get user's tweets/timeline (params: screenname, optional: cursor)
3. followers.php - Get user's followers (params: screenname, optional: cursor) 
4. following.php - Get users being followed (params: screenname, optional: cursor)
5. search.php - Search tweets and users (params: query, optional: cursor)

Instructions:
1. Analyze the user's request for clarity and feasibility
2. If unclear or unfeasible, respond with response_type: "CLARIFICATION"
3. If clear and feasible, respond with response_type: "PLAN" and create api_plan array
4. Each plan step should have: step (number), endpoint (filename), params (dict), reason (string)

User Query: "{query}"

Respond with JSON only:
"""
        
        try:
            response = self._gemini_model.generate_content(planning_prompt)
            plan_text = response.text.strip()
            
            # Try to extract JSON from response
            if plan_text.startswith("```json"):
                plan_text = plan_text[7:]
            if plan_text.endswith("```"):
                plan_text = plan_text[:-3]
            
            plan = json.loads(plan_text)
            logger.info(f"Generated query plan: {plan}")
            return plan
            
        except Exception as e:
            logger.error(f"Error generating query plan: {e}")
            return {
                "response_type": "ERROR", 
                "message_to_user": f"Query planning failed: {str(e)}"
            }
    
    def _execute_api_plan(self, api_plan: List[Dict], rapidapi_key: str, timeout_seconds: int) -> List[Dict]:
        """Execute the API plan steps"""
        results = []
        
        for step in api_plan:
            try:
                step_num = step.get("step", len(results) + 1)
                endpoint = step.get("endpoint")
                params = step.get("params", {})
                reason = step.get("reason", "")
                
                logger.info(f"Executing step {step_num}: {endpoint} - {reason}")
                
                # Make API call
                start_time = time.time()
                response_data = self._make_twitter_api_call(endpoint, params, rapidapi_key, timeout_seconds)
                response_time = time.time() - start_time
                
                step_result = {
                    "step": step_num,
                    "endpoint": endpoint,
                    "parameters": params,
                    "reason": reason,
                    "response_time": response_time,
                    "status": "success" if "error" not in response_data else "error",
                    "data": response_data
                }
                
                results.append(step_result)
                
                # Small delay between API calls
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error executing step {step.get('step', '?')}: {e}")
                step_result = {
                    "step": step.get("step", len(results) + 1),
                    "endpoint": step.get("endpoint", "unknown"),
                    "parameters": step.get("params", {}),
                    "reason": step.get("reason", ""),
                    "response_time": 0.0,
                    "status": "error",
                    "data": {"error": str(e)}
                }
                results.append(step_result)
        
        return results
    
    def _make_twitter_api_call(self, endpoint: str, params: Dict, rapidapi_key: str, timeout_seconds: int) -> Dict:
        """Make a single Twitter API call via RapidAPI"""
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": RAPIDAPI_TWITTER_HOST
        }
        
        url = f"{RAPIDAPI_BASE_URL}/{endpoint}"
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout_seconds)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                return {"error": "Rate limit exceeded", "status_code": 429}
            else:
                return {"error": f"HTTP {e.response.status_code}: {e.response.text}", "status_code": e.response.status_code}
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {str(e)}"}
    
    def _extract_entities_from_results(self, api_results: List[Dict]) -> List[Dict]:
        """Extract entities from API results"""
        entities = []
        entity_id_counter = 1
        
        for result in api_results:
            if result.get("status") != "success":
                continue
                
            data = result.get("data", {})
            endpoint = result.get("endpoint", "")
            
            # Extract entities based on endpoint type
            if endpoint == "screenname.php":
                # User profile data
                if "profile" in data:
                    entity = {
                        "entity_id": f"user_{entity_id_counter}",
                        "entity_type": "TwitterUser",
                        "surface_form": f"@{data.get('profile', 'unknown')}",
                        "canonical_name": data.get("profile", "unknown"),
                        "confidence": 0.95,
                        "metadata": {
                            "name": data.get("name", ""),
                            "followers_count": data.get("followers", 0),
                            "following_count": data.get("friends", 0),
                            "verified": data.get("blue_verified", False),
                            "description": data.get("desc", ""),
                            "rest_id": data.get("rest_id", "")
                        }
                    }
                    entities.append(entity)
                    entity_id_counter += 1
                    
            elif endpoint == "timeline.php" and "timeline" in data:
                # Tweet data
                for tweet in data["timeline"]:
                    if isinstance(tweet, dict):
                        entity = {
                            "entity_id": f"tweet_{entity_id_counter}",
                            "entity_type": "Tweet",
                            "surface_form": tweet.get("text", "")[:50] + "...",
                            "canonical_name": tweet.get("tweet_id", f"tweet_{entity_id_counter}"),
                            "confidence": 0.90,
                            "metadata": {
                                "tweet_id": tweet.get("tweet_id", ""),
                                "text": tweet.get("text", ""),
                                "created_at": tweet.get("created_at", ""),
                                "retweet_count": tweet.get("retweet_count", 0),
                                "like_count": tweet.get("like_count", 0),
                                "author": tweet.get("author", {})
                            }
                        }
                        entities.append(entity)
                        entity_id_counter += 1
                        
            elif endpoint == "search.php" and "timeline" in data:
                # Search results - same structure as timeline
                for tweet in data["timeline"]:
                    if isinstance(tweet, dict):
                        entity = {
                            "entity_id": f"tweet_{entity_id_counter}",
                            "entity_type": "Tweet",
                            "surface_form": tweet.get("text", "")[:50] + "...",
                            "canonical_name": tweet.get("tweet_id", f"tweet_{entity_id_counter}"),
                            "confidence": 0.90,
                            "metadata": {
                                "tweet_id": tweet.get("tweet_id", ""),
                                "text": tweet.get("text", ""),
                                "created_at": tweet.get("created_at", ""),
                                "retweet_count": tweet.get("retweets", 0),
                                "like_count": tweet.get("favorites", 0),
                                "author": tweet.get("user_info", {}),
                                "search_query": result.get("parameters", {}).get("query", "")
                            }
                        }
                        entities.append(entity)
                        entity_id_counter += 1
                        
                        # Also extract users from search results
                        user_info = tweet.get("user_info", {})
                        if user_info and user_info.get("screen_name"):
                            user_entity = {
                                "entity_id": f"user_{entity_id_counter}",
                                "entity_type": "TwitterUser",
                                "surface_form": f"@{user_info.get('screen_name', 'unknown')}",
                                "canonical_name": user_info.get("screen_name", "unknown"),
                                "confidence": 0.90,
                                "metadata": {
                                    "name": user_info.get("name", ""),
                                    "description": user_info.get("description", ""),
                                    "followers_count": user_info.get("followers_count", 0),
                                    "verified": user_info.get("verified", False),
                                    "rest_id": user_info.get("rest_id", "")
                                }
                            }
                            entities.append(user_entity)
                            entity_id_counter += 1
                        
            elif endpoint in ["followers.php", "following.php"]:
                # Follower/following data
                data_key = "followers" if endpoint == "followers.php" else "following"
                if data_key in data:
                    for user in data[data_key]:
                        if isinstance(user, dict):
                            entity = {
                                "entity_id": f"user_{entity_id_counter}",
                                "entity_type": "TwitterUser", 
                                "surface_form": f"@{user.get('screen_name', 'unknown')}",
                                "canonical_name": user.get("screen_name", "unknown"),
                                "confidence": 0.90,
                                "metadata": {
                                    "name": user.get("name", ""),
                                    "description": user.get("description", ""),
                                    "rest_id": user.get("rest_id", "")
                                }
                            }
                            entities.append(entity)
                            entity_id_counter += 1
        
        return entities
    
    def _extract_relationships_from_results(self, api_results: List[Dict], entities: List[Dict]) -> List[Dict]:
        """Extract relationships from API results"""
        relationships = []
        relationship_id_counter = 1
        
        # Create entity lookup by canonical name
        entity_lookup = {entity["canonical_name"]: entity["entity_id"] for entity in entities}
        
        for result in api_results:
            if result.get("status") != "success":
                continue
                
            data = result.get("data", {})
            endpoint = result.get("endpoint", "")
            
            # Extract relationships based on endpoint
            if endpoint == "followers.php":
                # Follow relationships
                main_user = result.get("parameters", {}).get("screenname", "")
                if main_user in entity_lookup and "followers" in data:
                    main_user_id = entity_lookup[main_user]
                    for follower in data["followers"]:
                        if isinstance(follower, dict):
                            follower_name = follower.get("screen_name", "")
                            if follower_name in entity_lookup:
                                relationship = {
                                    "relationship_id": f"rel_{relationship_id_counter}",
                                    "source_entity_id": entity_lookup[follower_name],
                                    "target_entity_id": main_user_id,
                                    "relationship_type": "FOLLOWS",
                                    "confidence": 0.95,
                                    "metadata": {}
                                }
                                relationships.append(relationship)
                                relationship_id_counter += 1
                                
            elif endpoint == "following.php":
                # Following relationships
                main_user = result.get("parameters", {}).get("screenname", "")
                if main_user in entity_lookup and "following" in data:
                    main_user_id = entity_lookup[main_user]
                    for following in data["following"]:
                        if isinstance(following, dict):
                            following_name = following.get("screen_name", "")
                            if following_name in entity_lookup:
                                relationship = {
                                    "relationship_id": f"rel_{relationship_id_counter}",
                                    "source_entity_id": main_user_id,
                                    "target_entity_id": entity_lookup[following_name],
                                    "relationship_type": "FOLLOWS",
                                    "confidence": 0.95,
                                    "metadata": {}
                                }
                                relationships.append(relationship)
                                relationship_id_counter += 1
        
        return relationships
    
    def _build_graph_data(self, entities: List[Dict], relationships: List[Dict]) -> Dict[str, Any]:
        """Build graph data for Neo4j storage"""
        nodes = []
        edges = []
        
        # Build nodes
        for entity in entities:
            node = {
                "id": entity["entity_id"],
                "type": entity["entity_type"],
                "properties": {
                    "canonical_name": entity["canonical_name"],
                    "surface_form": entity["surface_form"],
                    "confidence": entity["confidence"],
                    **entity.get("metadata", {})
                }
            }
            nodes.append(node)
        
        # Build edges
        for relationship in relationships:
            edge = {
                "source": relationship["source_entity_id"],
                "target": relationship["target_entity_id"],
                "type": relationship["relationship_type"],
                "properties": {
                    "confidence": relationship["confidence"],
                    **relationship.get("metadata", {})
                }
            }
            edges.append(edge)
        
        # Calculate metadata
        node_count = len(nodes)
        edge_count = len(edges)
        
        # Simple connected components calculation (all nodes with edges are in one component)
        connected_nodes = set()
        for edge in edges:
            connected_nodes.add(edge["source"])
            connected_nodes.add(edge["target"])
        
        connected_components = 1 if connected_nodes else 0
        if node_count > len(connected_nodes):
            connected_components += (node_count - len(connected_nodes))  # Isolated nodes
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "node_count": node_count,
                "edge_count": edge_count,
                "connected_components": connected_components
            }
        }
    
    def _create_error_result(self, request: ToolRequest, error_code: str, 
                           error_message: str, execution_time: float = 0.0, 
                           memory_used: int = 0) -> ToolResult:
        """Create standardized error result"""
        # Handle None request gracefully
        query = "unknown"
        operation = "unknown"
        
        if request is not None:
            if hasattr(request, 'input_data') and request.input_data:
                query = request.input_data.get("query", "unknown")
            if hasattr(request, 'operation'):
                operation = request.operation
        
        return ToolResult(
            tool_id=self.tool_id,
            status="error",
            data={
                "error": True,
                "query": query,
                "timestamp": datetime.now().isoformat()
            },
            metadata={
                "error_context": "twitter_query_execution",
                "request_operation": operation
            },
            execution_time=execution_time,
            memory_used=memory_used,
            error_code=error_code,
            error_message=error_message
        )
    
    def health_check(self) -> ToolResult:
        """Check tool health and readiness"""
        try:
            # Check dependencies and service availability
            dependencies_healthy = True
            dependency_status = {}
            
            # Check service manager
            if self.services:
                service_health = self.services.health_check() if hasattr(self.services, 'health_check') else {}
                dependencies_healthy = all(service_health.values()) if service_health else True
                dependency_status = service_health
            
            # Check if we can load contract
            contract_loaded = True
            try:
                contract = self.get_contract()
                contract_loaded = contract.tool_id == self.tool_id
            except Exception:
                contract_loaded = False
                dependencies_healthy = False
            
            # Overall health status
            healthy = dependencies_healthy and contract_loaded and self.status != ToolStatus.ERROR
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "error",
                data={
                    "healthy": healthy,
                    "contract_loaded": contract_loaded,
                    "dependencies_healthy": dependencies_healthy,
                    "dependency_status": dependency_status,
                    "tool_status": self.status.value,
                    "supported_operations": ["query"]
                },
                metadata={
                    "health_check_timestamp": datetime.now().isoformat(),
                    "tool_version": "1.0.0"
                },
                execution_time=0.0,
                memory_used=0
            )
            
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"healthy": False, "error": str(e)},
                metadata={"health_check_timestamp": datetime.now().isoformat()},
                execution_time=0.0,
                memory_used=0,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
    
    def cleanup(self) -> bool:
        """Clean up tool resources"""
        try:
            # Reset status
            self.status = ToolStatus.READY
            
            # Clean up any TwitterExplorer components
            if self._llm_handler:
                self._llm_handler = None
            if self._api_client:
                self._api_client = None
            if self._graph_manager:
                self._graph_manager = None
            
            logger.info(f"Cleaned up {self.tool_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False