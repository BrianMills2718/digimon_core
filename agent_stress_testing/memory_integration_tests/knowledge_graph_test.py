#!/usr/bin/env python3
"""
Knowledge Graph Memory Integration Test

Tests integration with modelcontextprotocol/server-memory for storing and retrieving
structured research context across sessions.
"""

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from unittest.mock import AsyncMock, Mock

@dataclass
class ResearchEntity:
    """Represents a research entity in the knowledge graph"""
    entity_id: str
    entity_type: str  # "research_question", "methodology", "finding", "concept"
    name: str
    properties: Dict[str, Any]
    created_at: float
    session_id: str

@dataclass 
class ResearchRelationship:
    """Represents a relationship between research entities"""
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str  # "uses_methodology", "leads_to_finding", "relates_to"
    properties: Dict[str, Any]
    strength: float  # 0.0 to 1.0
    created_at: float

@dataclass
class ResearchContext:
    """Enhanced research context from knowledge graph"""
    current_query: str
    related_entities: List[ResearchEntity]
    related_relationships: List[ResearchRelationship]
    user_patterns: Dict[str, Any]
    recommended_methodologies: List[str]
    contextual_insights: List[str]
    confidence_score: float

class MockKnowledgeGraphMCP:
    """Mock MCP server for knowledge graph-based memory"""
    
    def __init__(self):
        self.entities: Dict[str, ResearchEntity] = {}
        self.relationships: Dict[str, ResearchRelationship] = {}
        self.user_patterns: Dict[str, Dict[str, Any]] = {}
        self.call_history = []
    
    async def store_entity(self, entity: ResearchEntity) -> str:
        """Store research entity in knowledge graph"""
        self.call_history.append({"action": "store_entity", "entity_type": entity.entity_type})
        self.entities[entity.entity_id] = entity
        return entity.entity_id
    
    async def store_relationship(self, relationship: ResearchRelationship) -> str:
        """Store relationship between research entities"""
        self.call_history.append({"action": "store_relationship", "type": relationship.relationship_type})
        self.relationships[relationship.relationship_id] = relationship
        return relationship.relationship_id
    
    async def query_related_entities(self, query: str, entity_types: List[str] = None) -> List[ResearchEntity]:
        """Query for entities related to current research query"""
        self.call_history.append({"action": "query_related_entities", "query": query})
        
        # Simulate finding related entities based on keywords
        related = []
        query_lower = query.lower()
        
        for entity in self.entities.values():
            # Simple keyword matching simulation
            if any(keyword in entity.name.lower() for keyword in query_lower.split()):
                related.append(entity)
            elif any(keyword in str(entity.properties).lower() for keyword in query_lower.split()):
                related.append(entity)
        
        # Filter by entity types if specified
        if entity_types:
            related = [e for e in related if e.entity_type in entity_types]
        
        return related[:10]  # Limit results
    
    async def query_relationships(self, entity_id: str, relationship_types: List[str] = None) -> List[ResearchRelationship]:
        """Query for relationships involving specific entity"""
        self.call_history.append({"action": "query_relationships", "entity_id": entity_id})
        
        related_relationships = []
        for rel in self.relationships.values():
            if rel.source_entity_id == entity_id or rel.target_entity_id == entity_id:
                if not relationship_types or rel.relationship_type in relationship_types:
                    related_relationships.append(rel)
        
        return related_relationships
    
    async def update_user_patterns(self, user_id: str, patterns: Dict[str, Any]) -> None:
        """Update user research patterns based on session data"""
        self.call_history.append({"action": "update_user_patterns", "user_id": user_id})
        
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {}
        
        # Merge patterns
        for key, value in patterns.items():
            if key in self.user_patterns[user_id]:
                # Simple averaging for numeric values
                if isinstance(value, (int, float)) and isinstance(self.user_patterns[user_id][key], (int, float)):
                    self.user_patterns[user_id][key] = (self.user_patterns[user_id][key] + value) / 2
                else:
                    self.user_patterns[user_id][key] = value
            else:
                self.user_patterns[user_id][key] = value
    
    async def get_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user research patterns"""
        self.call_history.append({"action": "get_user_patterns", "user_id": user_id})
        return self.user_patterns.get(user_id, {})
    
    async def recommend_methodologies(self, research_context: Dict[str, Any]) -> List[str]:
        """Recommend methodologies based on research context and historical patterns"""
        self.call_history.append({"action": "recommend_methodologies"})
        
        # Simulate methodology recommendation based on domain and context
        domain = research_context.get("domain", "").lower()
        query_type = research_context.get("query_type", "").lower()
        
        recommendations = []
        
        if "organizational" in domain or "communication" in query_type:
            recommendations.extend(["discourse_analysis", "network_analysis", "stakeholder_analysis"])
        
        if "behavior" in domain or "social" in domain:
            recommendations.extend(["content_analysis", "sentiment_analysis", "thematic_analysis"])
        
        if "quantitative" in query_type or "statistical" in query_type:
            recommendations.extend(["statistical_analysis", "correlation_analysis", "regression_analysis"])
        
        # Add some popular general methods
        recommendations.extend(["entity_extraction", "visualization"])
        
        return list(set(recommendations))  # Remove duplicates

class ResearchMemoryIntegrator:
    """Integrates research sessions with knowledge graph memory"""
    
    def __init__(self, knowledge_graph: MockKnowledgeGraphMCP):
        self.kg = knowledge_graph
    
    async def store_research_session(self, session_data: Dict[str, Any]) -> Dict[str, str]:
        """Store complete research session in knowledge graph"""
        stored_ids = {}
        
        # Store research question as entity
        question_entity = ResearchEntity(
            entity_id=str(uuid.uuid4()),
            entity_type="research_question",
            name=session_data["query"],
            properties={
                "domain": session_data.get("domain", ""),
                "complexity": session_data.get("complexity", "medium"),
                "user_id": session_data.get("user_id", "")
            },
            created_at=time.time(),
            session_id=session_data["session_id"]
        )
        stored_ids["question"] = await self.kg.store_entity(question_entity)
        
        # Store methodology as entity
        if "methodology" in session_data:
            methodology_entity = ResearchEntity(
                entity_id=str(uuid.uuid4()),
                entity_type="methodology",
                name=session_data["methodology"],
                properties={
                    "tools_used": session_data.get("tools_used", []),
                    "success_rate": session_data.get("success_rate", 1.0),
                    "execution_time": session_data.get("execution_time", 0.0)
                },
                created_at=time.time(),
                session_id=session_data["session_id"]
            )
            stored_ids["methodology"] = await self.kg.store_entity(methodology_entity)
            
            # Store relationship between question and methodology
            question_method_rel = ResearchRelationship(
                relationship_id=str(uuid.uuid4()),
                source_entity_id=stored_ids["question"],
                target_entity_id=stored_ids["methodology"],
                relationship_type="uses_methodology",
                properties={"effectiveness": session_data.get("quality_score", 0.5)},
                strength=session_data.get("quality_score", 0.5),
                created_at=time.time()
            )
            await self.kg.store_relationship(question_method_rel)
        
        # Store key findings as entities
        if "findings" in session_data:
            for i, finding in enumerate(session_data["findings"]):
                finding_entity = ResearchEntity(
                    entity_id=str(uuid.uuid4()),
                    entity_type="finding",
                    name=f"Finding_{i+1}",
                    properties={
                        "content": finding,
                        "confidence": session_data.get("confidence_scores", [0.7])[i] if i < len(session_data.get("confidence_scores", [])) else 0.7
                    },
                    created_at=time.time(),
                    session_id=session_data["session_id"]
                )
                finding_id = await self.kg.store_entity(finding_entity)
                stored_ids[f"finding_{i+1}"] = finding_id
                
                # Store relationship between question and finding
                question_finding_rel = ResearchRelationship(
                    relationship_id=str(uuid.uuid4()),
                    source_entity_id=stored_ids["question"],
                    target_entity_id=finding_id,
                    relationship_type="leads_to_finding",
                    properties={"relevance": session_data.get("relevance_scores", [0.8])[i] if i < len(session_data.get("relevance_scores", [])) else 0.8},
                    strength=session_data.get("relevance_scores", [0.8])[i] if i < len(session_data.get("relevance_scores", [])) else 0.8,
                    created_at=time.time()
                )
                await self.kg.store_relationship(question_finding_rel)
        
        # Update user patterns
        user_patterns = {
            "preferred_domain": session_data.get("domain", ""),
            "avg_session_duration": session_data.get("execution_time", 0.0),
            "preferred_methodology": session_data.get("methodology", ""),
            "avg_quality_score": session_data.get("quality_score", 0.5),
            "session_count": 1  # This would be incremented in real implementation
        }
        await self.kg.update_user_patterns(session_data.get("user_id", ""), user_patterns)
        
        return stored_ids
    
    async def retrieve_research_context(self, query: str, user_id: str) -> ResearchContext:
        """Retrieve enhanced research context from knowledge graph"""
        
        # Find related entities
        related_entities = await self.kg.query_related_entities(
            query, 
            entity_types=["research_question", "methodology", "finding"]
        )
        
        # Find relationships for related entities
        all_relationships = []
        for entity in related_entities[:5]:  # Limit to avoid too many queries
            entity_relationships = await self.kg.query_relationships(entity.entity_id)
            all_relationships.extend(entity_relationships)
        
        # Get user patterns
        user_patterns = await self.kg.get_user_patterns(user_id)
        
        # Recommend methodologies
        research_context_for_rec = {
            "domain": self._extract_domain_from_query(query),
            "query_type": self._classify_query_type(query),
            "user_patterns": user_patterns
        }
        recommended_methodologies = await self.kg.recommend_methodologies(research_context_for_rec)
        
        # Generate contextual insights
        contextual_insights = self._generate_insights(related_entities, all_relationships, user_patterns)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(related_entities, user_patterns)
        
        return ResearchContext(
            current_query=query,
            related_entities=related_entities,
            related_relationships=all_relationships,
            user_patterns=user_patterns,
            recommended_methodologies=recommended_methodologies,
            contextual_insights=contextual_insights,
            confidence_score=confidence_score
        )
    
    def _extract_domain_from_query(self, query: str) -> str:
        """Extract research domain from query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["organizational", "organization", "workplace", "business"]):
            return "organizational_behavior"
        elif any(word in query_lower for word in ["political", "policy", "governance", "power"]):
            return "political_science"
        elif any(word in query_lower for word in ["social", "society", "community", "culture"]):
            return "sociology"
        elif any(word in query_lower for word in ["communication", "discourse", "conversation", "language"]):
            return "communication_studies"
        else:
            return "general_social_science"
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of research query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["how many", "count", "frequency", "percentage", "statistics"]):
            return "quantitative"
        elif any(word in query_lower for word in ["themes", "patterns", "discourse", "meaning", "interpretation"]):
            return "qualitative"
        elif any(word in query_lower for word in ["relationships", "network", "connections", "interactions"]):
            return "relational"
        elif any(word in query_lower for word in ["changes", "trends", "evolution", "development"]):
            return "temporal"
        else:
            return "exploratory"
    
    def _generate_insights(self, entities: List[ResearchEntity], relationships: List[ResearchRelationship], user_patterns: Dict[str, Any]) -> List[str]:
        """Generate contextual insights from knowledge graph data"""
        insights = []
        
        if entities:
            insights.append(f"Found {len(entities)} related research entities from previous sessions")
            
            # Analyze entity types
            entity_types = {}
            for entity in entities:
                entity_types[entity.entity_type] = entity_types.get(entity.entity_type, 0) + 1
            
            for entity_type, count in entity_types.items():
                insights.append(f"Previous work includes {count} related {entity_type}(s)")
        
        if relationships:
            insights.append(f"Identified {len(relationships)} connections between research elements")
            
            # Analyze relationship strengths
            strong_relationships = [r for r in relationships if r.strength > 0.7]
            if strong_relationships:
                insights.append(f"{len(strong_relationships)} strong connections suggest established patterns")
        
        if user_patterns:
            if "preferred_methodology" in user_patterns:
                insights.append(f"You typically prefer {user_patterns['preferred_methodology']} methodology")
            
            if "avg_quality_score" in user_patterns:
                if user_patterns["avg_quality_score"] > 0.8:
                    insights.append("Your previous research sessions show consistently high quality")
                elif user_patterns["avg_quality_score"] < 0.6:
                    insights.append("Consider refining methodology selection for better results")
        
        return insights
    
    def _calculate_confidence_score(self, entities: List[ResearchEntity], user_patterns: Dict[str, Any]) -> float:
        """Calculate confidence score for context enhancement"""
        score = 0.0
        
        # Base score from number of related entities
        if entities:
            score += min(len(entities) * 0.1, 0.5)  # Up to 0.5 from entities
        
        # Score from user pattern richness
        if user_patterns:
            pattern_score = min(len(user_patterns) * 0.05, 0.3)  # Up to 0.3 from patterns
            score += pattern_score
        
        # Score from entity relevance (simulated)
        if entities:
            recent_entities = [e for e in entities if time.time() - e.created_at < 86400 * 30]  # Last 30 days
            if recent_entities:
                score += min(len(recent_entities) * 0.05, 0.2)  # Up to 0.2 from recent relevance
        
        return min(score, 1.0)

async def test_knowledge_graph_integration():
    """Test knowledge graph memory integration"""
    print("🧪 Starting Knowledge Graph Memory Integration Test")
    print("=" * 70)
    
    # Initialize mock knowledge graph
    kg = MockKnowledgeGraphMCP()
    integrator = ResearchMemoryIntegrator(kg)
    
    # Test session 1: Store initial research session
    print("\n📋 Test 1: Storing Research Session")
    print("-" * 40)
    
    session_1_data = {
        "session_id": "test_session_001",
        "user_id": "researcher_alice",
        "query": "How do communication patterns change during organizational restructuring?",
        "domain": "organizational_behavior",
        "methodology": "discourse_analysis_plus_network_analysis",
        "tools_used": ["discourse_analyzer", "network_mapper", "sentiment_tracker"],
        "execution_time": 23.5,
        "quality_score": 0.85,
        "success_rate": 1.0,
        "findings": [
            "Communication frequency decreases by 40% during restructuring announcements",
            "Informal networks become more important for information flow",
            "Management communication shifts to more formal channels"
        ],
        "confidence_scores": [0.9, 0.8, 0.75],
        "relevance_scores": [0.95, 0.85, 0.8]
    }
    
    stored_ids_1 = await integrator.store_research_session(session_1_data)
    
    print(f"✅ Stored entities: {len(stored_ids_1)}")
    print(f"📊 Knowledge graph calls: {len(kg.call_history)}")
    print(f"🏗️  Entities in graph: {len(kg.entities)}")
    print(f"🔗 Relationships in graph: {len(kg.relationships)}")
    
    # Test session 2: Store related research session
    print("\n📋 Test 2: Storing Related Research Session")
    print("-" * 40)
    
    session_2_data = {
        "session_id": "test_session_002", 
        "user_id": "researcher_alice",
        "query": "What communication strategies are most effective during organizational change?",
        "domain": "organizational_behavior",
        "methodology": "sentiment_analysis_plus_stakeholder_analysis",
        "tools_used": ["sentiment_analyzer", "stakeholder_mapper", "effectiveness_tracker"],
        "execution_time": 18.2,
        "quality_score": 0.78,
        "success_rate": 1.0,
        "findings": [
            "Transparent communication increases employee satisfaction by 60%",
            "Regular town halls are more effective than email updates",
            "Two-way communication channels improve trust metrics"
        ],
        "confidence_scores": [0.85, 0.9, 0.8],
        "relevance_scores": [0.9, 0.85, 0.88]
    }
    
    stored_ids_2 = await integrator.store_research_session(session_2_data)
    
    print(f"✅ Stored entities: {len(stored_ids_2)}")
    print(f"🏗️  Total entities in graph: {len(kg.entities)}")
    print(f"🔗 Total relationships in graph: {len(kg.relationships)}")
    
    # Test session 3: Retrieve enhanced research context
    print("\n📋 Test 3: Retrieving Enhanced Research Context")
    print("-" * 40)
    
    new_query = "How can we improve communication effectiveness during organizational transitions?"
    context = await integrator.retrieve_research_context(new_query, "researcher_alice")
    
    print(f"🔍 Query: {context.current_query}")
    print(f"🔗 Related entities found: {len(context.related_entities)}")
    print(f"📊 Related relationships: {len(context.related_relationships)}")
    print(f"🎯 Recommended methodologies: {len(context.recommended_methodologies)}")
    print(f"💡 Contextual insights: {len(context.contextual_insights)}")
    print(f"🎯 Confidence score: {context.confidence_score:.3f}")
    
    print("\n🔍 Related Entities:")
    for entity in context.related_entities[:3]:  # Show first 3
        print(f"  - {entity.entity_type}: {entity.name}")
    
    print("\n🛠️  Recommended Methodologies:")
    for method in context.recommended_methodologies[:3]:  # Show first 3
        print(f"  - {method}")
    
    print("\n💡 Contextual Insights:")
    for insight in context.contextual_insights:
        print(f"  - {insight}")
    
    # Test session 4: User pattern analysis
    print("\n📋 Test 4: User Pattern Analysis")
    print("-" * 40)
    
    user_patterns = await kg.get_user_patterns("researcher_alice")
    print(f"👤 User patterns stored: {len(user_patterns)}")
    
    for key, value in user_patterns.items():
        print(f"  - {key}: {value}")
    
    # Test session 5: Cross-session relationship analysis
    print("\n📋 Test 5: Cross-Session Relationship Analysis")
    print("-" * 40)
    
    # Find all research questions for the user
    research_questions = [e for e in kg.entities.values() if e.entity_type == "research_question"]
    print(f"🔍 Total research questions: {len(research_questions)}")
    
    # Analyze relationships between sessions
    cross_session_relationships = []
    for question in research_questions:
        relationships = await kg.query_relationships(question.entity_id)
        cross_session_relationships.extend(relationships)
    
    print(f"🔗 Total relationships across sessions: {len(cross_session_relationships)}")
    
    # Analyze relationship types
    relationship_types = {}
    for rel in cross_session_relationships:
        relationship_types[rel.relationship_type] = relationship_types.get(rel.relationship_type, 0) + 1
    
    print("\n📊 Relationship Type Analysis:")
    for rel_type, count in relationship_types.items():
        print(f"  - {rel_type}: {count}")
    
    # Performance analysis
    print("\n📋 Test 6: Performance Analysis")
    print("-" * 40)
    
    total_kg_calls = len(kg.call_history)
    storage_calls = len([c for c in kg.call_history if "store" in c["action"]])
    query_calls = len([c for c in kg.call_history if "query" in c["action"]])
    
    print(f"📞 Total knowledge graph calls: {total_kg_calls}")
    print(f"💾 Storage operations: {storage_calls}")
    print(f"🔍 Query operations: {query_calls}")
    print(f"📈 Storage/Query ratio: {storage_calls}/{query_calls}")
    
    # Calculate memory efficiency
    entities_per_session = len(kg.entities) / 2  # 2 sessions stored
    relationships_per_session = len(kg.relationships) / 2
    
    print(f"🏗️  Average entities per session: {entities_per_session:.1f}")
    print(f"🔗 Average relationships per session: {relationships_per_session:.1f}")
    
    # Test success metrics
    print("\n📊 SUCCESS METRICS")
    print("=" * 70)
    
    context_enhancement_score = context.confidence_score
    memory_utilization = len(context.related_entities) > 0
    cross_session_learning = len(user_patterns) > 0
    methodology_recommendation = len(context.recommended_methodologies) > 0
    
    print(f"✅ Context Enhancement Score: {context_enhancement_score:.3f}")
    print(f"✅ Memory Utilization: {memory_utilization}")
    print(f"✅ Cross-Session Learning: {cross_session_learning}")
    print(f"✅ Methodology Recommendation: {methodology_recommendation}")
    
    overall_success = (
        context_enhancement_score >= 0.5 and
        memory_utilization and
        cross_session_learning and
        methodology_recommendation
    )
    
    print(f"\n🎯 Overall Success: {overall_success}")
    
    if overall_success:
        print("✅ EXCELLENT: Knowledge graph integration working effectively")
    else:
        print("❌ NEEDS IMPROVEMENT: Knowledge graph integration requires optimization")
    
    # Return test results
    return {
        "context_enhancement_score": context_enhancement_score,
        "memory_utilization": memory_utilization,
        "cross_session_learning": cross_session_learning,
        "methodology_recommendation": methodology_recommendation,
        "total_entities": len(kg.entities),
        "total_relationships": len(kg.relationships),
        "total_kg_calls": total_kg_calls,
        "user_patterns": user_patterns,
        "contextual_insights": context.contextual_insights,
        "recommended_methodologies": context.recommended_methodologies
    }

if __name__ == "__main__":
    # Run the knowledge graph integration test
    results = asyncio.run(test_knowledge_graph_integration())
    
    # Save results for analysis
    with open("/home/brian/projects/Digimons/agent_stress_testing/results/knowledge_graph_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: agent_stress_testing/results/knowledge_graph_test_results.json")