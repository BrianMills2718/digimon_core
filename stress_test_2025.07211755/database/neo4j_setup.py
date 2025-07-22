"""
Neo4j database setup and integration for stakeholder analysis
Handles graph storage, reified relationships, and cross-modal analysis
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# Add project paths
sys.path.append('/home/brian/projects/Digimons/src')
sys.path.append('/home/brian/projects/Digimons/stress_test_2025.07211755')

try:
    from neo4j import GraphDatabase
    from src.core.neo4j_manager import Neo4jManager
    from src.core.service_manager import get_service_manager
    from schemas.stakeholder_schemas import StakeholderEntity, StakeholderInfluence
    from schemas.base_schemas import StandardEntity, StandardRelationship
except ImportError as e:
    print(f"Warning: Import error: {e}")
    print("Running in mock mode...")

class StakeholderNeo4jManager:
    """
    Manages Neo4j operations for stakeholder analysis
    Implements reified n-ary relationships and cross-modal data preparation
    """
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        """Initialize Neo4j connection"""
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.connect()
    
    def connect(self):
        """Establish Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                print(f"✓ Neo4j connection successful: {self.uri}")
        except Exception as e:
            print(f"✗ Neo4j connection failed: {e}")
            self.driver = None
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
    
    def setup_schema(self):
        """
        Set up Neo4j schema for stakeholder analysis
        Creates indexes, constraints, and vector indexes
        """
        
        setup_queries = [
            # Constraints for unique IDs
            "CREATE CONSTRAINT stakeholder_id IF NOT EXISTS FOR (s:Stakeholder) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT organization_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE",
            "CREATE CONSTRAINT influence_id IF NOT EXISTS FOR (i:INFLUENCE_RELATION) REQUIRE i.id IS UNIQUE",
            
            # Indexes for performance
            "CREATE INDEX stakeholder_name IF NOT EXISTS FOR (s:Stakeholder) ON s.canonical_name",
            "CREATE INDEX stakeholder_type IF NOT EXISTS FOR (s:Stakeholder) ON s.stakeholder_type",
            "CREATE INDEX organization_name IF NOT EXISTS FOR (o:Organization) ON o.canonical_name",
            "CREATE INDEX salience_score IF NOT EXISTS FOR (s:Stakeholder) ON s.salience_score",
            
            # Vector index for embeddings (if available)
            """CREATE VECTOR INDEX stakeholder_embeddings IF NOT EXISTS 
               FOR (s:Stakeholder) ON s.embedding 
               OPTIONS {indexConfig: {
                 `vector.dimensions`: 384,
                 `vector.similarity_function`: 'cosine'
               }}""",
               
            # Text indexes for search
            "CREATE FULLTEXT INDEX stakeholder_fulltext IF NOT EXISTS FOR (s:Stakeholder) ON EACH [s.canonical_name, s.description]",
            "CREATE FULLTEXT INDEX organization_fulltext IF NOT EXISTS FOR (o:Organization) ON EACH [o.canonical_name, o.description]"
        ]
        
        if not self.driver:
            print("No Neo4j connection - skipping schema setup")
            return
        
        with self.driver.session() as session:
            for query in setup_queries:
                try:
                    session.run(query)
                    print(f"✓ Schema setup: {query.split()[1:4]}")
                except Exception as e:
                    if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                        print(f"• Schema already exists: {query.split()[1:4]}")
                    else:
                        print(f"✗ Schema setup failed: {e}")
    
    def clear_database(self):
        """Clear all data from database (for testing)"""
        if not self.driver:
            print("No Neo4j connection - skipping clear")
            return
            
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")
    
    def create_stakeholder(self, stakeholder: Dict[str, Any]) -> bool:
        """
        Create stakeholder node in Neo4j
        
        Args:
            stakeholder: Stakeholder data dictionary
            
        Returns:
            Success status
        """
        
        if not self.driver:
            print("No Neo4j connection - mock creation")
            return False
        
        query = """
        CREATE (s:Stakeholder {
            id: $id,
            canonical_name: $canonical_name,
            stakeholder_type: $stakeholder_type,
            entity_type: $entity_type,
            
            // Mitchell-Agle-Wood dimensions
            legitimacy: $legitimacy,
            legitimacy_confidence: $legitimacy_confidence,
            urgency: $urgency,
            urgency_confidence: $urgency_confidence,
            power: $power,
            power_confidence: $power_confidence,
            salience_score: $salience_score,
            mitchell_category: $mitchell_category,
            priority_tier: $priority_tier,
            
            // Metadata
            confidence: $confidence,
            quality_tier: $quality_tier,
            created_by: $created_by,
            created_at: $created_at,
            workflow_id: $workflow_id,
            
            // Additional properties
            description: $description,
            surface_forms: $surface_forms,
            mention_count: $mention_count
        })
        RETURN s.id as created_id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, stakeholder)
                created_id = result.single()["created_id"]
                print(f"✓ Created stakeholder: {created_id}")
                return True
        except Exception as e:
            print(f"✗ Failed to create stakeholder: {e}")
            return False
    
    def create_organization(self, organization: Dict[str, Any]) -> bool:
        """
        Create organization node in Neo4j
        
        Args:
            organization: Organization data dictionary
            
        Returns:
            Success status
        """
        
        if not self.driver:
            print("No Neo4j connection - mock creation")
            return False
        
        query = """
        CREATE (o:Organization {
            id: $id,
            canonical_name: $canonical_name,
            entity_type: $entity_type,
            organization_type: $organization_type,
            sector: $sector,
            size: $size,
            
            // Metadata
            confidence: $confidence,
            quality_tier: $quality_tier,
            created_by: $created_by,
            created_at: $created_at,
            workflow_id: $workflow_id,
            
            description: $description
        })
        RETURN o.id as created_id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, organization)
                created_id = result.single()["created_id"]
                print(f"✓ Created organization: {created_id}")
                return True
        except Exception as e:
            print(f"✗ Failed to create organization: {e}")
            return False
    
    def create_reified_influence_relationship(self, relationship: Dict[str, Any]) -> bool:
        """
        Create reified influence relationship using intermediate node
        Supports n-ary relationships with multiple participants
        
        Args:
            relationship: Relationship data dictionary
            
        Returns:
            Success status
        """
        
        if not self.driver:
            print("No Neo4j connection - mock creation")
            return False
        
        # First create the reified relationship node
        create_relation_query = """
        CREATE (r:INFLUENCE_RELATION {
            id: $id,
            relationship_type: $relationship_type,
            influence_strength: $influence_strength,
            influence_mechanism: $influence_mechanism,
            conditionality: $conditionality,
            temporal_scope: $temporal_scope,
            
            // Metadata
            confidence: $confidence,
            quality_tier: $quality_tier,
            created_by: $created_by,
            created_at: $created_at,
            workflow_id: $workflow_id,
            
            // Additional properties
            weight: $weight,
            direction: $direction
        })
        RETURN r.id as relation_id
        """
        
        # Then connect stakeholder and organization to the relationship
        connect_source_query = """
        MATCH (s:Stakeholder {id: $source_id})
        MATCH (r:INFLUENCE_RELATION {id: $relation_id})
        CREATE (s)-[:INFLUENCES_VIA {role: $source_role}]->(r)
        """
        
        connect_target_query = """
        MATCH (o:Organization {id: $target_id})
        MATCH (r:INFLUENCE_RELATION {id: $relation_id})
        CREATE (r)-[:TARGETS {role: $target_role}]->(o)
        """
        
        # Handle additional participants (for n-ary relations)
        connect_additional_query = """
        MATCH (e:Entity {id: $participant_id})
        MATCH (r:INFLUENCE_RELATION {id: $relation_id})
        CREATE (e)-[:PARTICIPATES_IN {role: $role}]->(r)
        """
        
        try:
            with self.driver.session() as session:
                # Create reified relationship node
                result = session.run(create_relation_query, relationship)
                relation_id = result.single()["relation_id"]
                
                # Connect source (stakeholder)
                session.run(connect_source_query, {
                    "source_id": relationship["source_id"],
                    "relation_id": relation_id,
                    "source_role": relationship.get("source_role_name", "influencer")
                })
                
                # Connect target (organization)
                session.run(connect_target_query, {
                    "target_id": relationship["target_id"],
                    "relation_id": relation_id,
                    "target_role": relationship.get("target_role_name", "influenced")
                })
                
                # Connect additional participants
                for participant_id, role in relationship.get("additional_participants", {}).items():
                    session.run(connect_additional_query, {
                        "participant_id": participant_id,
                        "relation_id": relation_id,
                        "role": role
                    })
                
                print(f"✓ Created reified influence relationship: {relation_id}")
                return True
                
        except Exception as e:
            print(f"✗ Failed to create reified relationship: {e}")
            return False
    
    def get_stakeholder_network(self) -> List[Dict[str, Any]]:
        """
        Retrieve complete stakeholder network for analysis
        
        Returns:
            List of network data for cross-modal analysis
        """
        
        if not self.driver:
            print("No Neo4j connection - returning mock data")
            return []
        
        query = """
        MATCH (s:Stakeholder)-[rv:INFLUENCES_VIA]->(r:INFLUENCE_RELATION)-[rt:TARGETS]->(o:Organization)
        OPTIONAL MATCH (p)-[rp:PARTICIPATES_IN]->(r)
        RETURN 
            s.id as stakeholder_id,
            s.canonical_name as stakeholder_name,
            s.salience_score as salience_score,
            s.stakeholder_type as stakeholder_type,
            s.legitimacy as legitimacy,
            s.urgency as urgency,
            s.power as power,
            s.mitchell_category as mitchell_category,
            
            r.id as relationship_id,
            r.influence_strength as influence_strength,
            r.influence_mechanism as influence_mechanism,
            r.conditionality as conditionality,
            r.temporal_scope as temporal_scope,
            
            o.id as organization_id,
            o.canonical_name as organization_name,
            o.organization_type as organization_type,
            
            collect(p.id) as additional_participants
        ORDER BY s.salience_score DESC
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                network_data = []
                
                for record in result:
                    network_data.append({
                        "stakeholder": {
                            "id": record["stakeholder_id"],
                            "name": record["stakeholder_name"],
                            "type": record["stakeholder_type"],
                            "salience_score": record["salience_score"],
                            "legitimacy": record["legitimacy"],
                            "urgency": record["urgency"],
                            "power": record["power"],
                            "mitchell_category": record["mitchell_category"]
                        },
                        "relationship": {
                            "id": record["relationship_id"],
                            "influence_strength": record["influence_strength"],
                            "mechanism": record["influence_mechanism"],
                            "conditionality": record["conditionality"],
                            "temporal_scope": record["temporal_scope"]
                        },
                        "organization": {
                            "id": record["organization_id"],
                            "name": record["organization_name"],
                            "type": record["organization_type"]
                        },
                        "additional_participants": record["additional_participants"]
                    })
                
                print(f"✓ Retrieved {len(network_data)} network relationships")
                return network_data
                
        except Exception as e:
            print(f"✗ Failed to retrieve network: {e}")
            return []
    
    def export_for_table_analysis(self) -> List[Dict[str, Any]]:
        """
        Export graph data in table format for cross-modal analysis
        Each row represents a complete n-ary relationship
        
        Returns:
            List of table rows preserving relationship semantics
        """
        
        network_data = self.get_stakeholder_network()
        table_rows = []
        
        for item in network_data:
            # Flatten n-ary relationship into table row
            row = {
                # Primary participants
                "stakeholder_id": item["stakeholder"]["id"],
                "stakeholder_name": item["stakeholder"]["name"],
                "stakeholder_type": item["stakeholder"]["type"],
                "organization_id": item["organization"]["id"],
                "organization_name": item["organization"]["name"],
                "organization_type": item["organization"]["type"],
                
                # Relationship properties
                "relationship_id": item["relationship"]["id"],
                "influence_strength": item["relationship"]["influence_strength"],
                "influence_mechanism": item["relationship"]["mechanism"],
                "conditionality": item["relationship"]["conditionality"],
                "temporal_scope": item["relationship"]["temporal_scope"],
                
                # Stakeholder dimensions
                "legitimacy": item["stakeholder"]["legitimacy"],
                "urgency": item["stakeholder"]["urgency"],
                "power": item["stakeholder"]["power"],
                "salience_score": item["stakeholder"]["salience_score"],
                "mitchell_category": item["stakeholder"]["mitchell_category"],
                
                # Additional participants (JSON string for table storage)
                "additional_participants": json.dumps(item["additional_participants"]),
                
                # Computed metrics (would be calculated)
                "network_centrality": None,  # To be computed
                "influence_reach": None,     # To be computed
                "coalition_potential": None  # To be computed
            }
            
            table_rows.append(row)
        
        print(f"✓ Exported {len(table_rows)} rows for table analysis")
        return table_rows
    
    def calculate_network_metrics(self) -> Dict[str, Any]:
        """
        Calculate network-level metrics using Cypher queries
        
        Returns:
            Dictionary of network metrics
        """
        
        if not self.driver:
            return {"error": "No Neo4j connection"}
        
        queries = {
            "total_stakeholders": "MATCH (s:Stakeholder) RETURN count(s) as count",
            "total_relationships": "MATCH (:Stakeholder)-[:INFLUENCES_VIA]->(:INFLUENCE_RELATION) RETURN count(*) as count",
            "high_salience_stakeholders": "MATCH (s:Stakeholder) WHERE s.salience_score >= 0.7 RETURN count(s) as count",
            "definitive_stakeholders": "MATCH (s:Stakeholder) WHERE s.mitchell_category = 'definitive' RETURN count(s) as count",
            "average_salience": "MATCH (s:Stakeholder) RETURN avg(s.salience_score) as average",
            "max_influence_strength": "MATCH (r:INFLUENCE_RELATION) RETURN max(r.influence_strength) as max_strength"
        }
        
        metrics = {}
        
        try:
            with self.driver.session() as session:
                for metric_name, query in queries.items():
                    result = session.run(query)
                    record = result.single()
                    if record:
                        key = list(record.keys())[0]
                        metrics[metric_name] = record[key]
                    else:
                        metrics[metric_name] = 0
                        
                print(f"✓ Calculated {len(metrics)} network metrics")
                return metrics
                
        except Exception as e:
            print(f"✗ Failed to calculate metrics: {e}")
            return {"error": str(e)}

def main():
    """Test Neo4j setup and operations"""
    
    print("Neo4j Setup for Stakeholder Analysis")
    print("=" * 50)
    
    # Initialize manager
    manager = StakeholderNeo4jManager()
    
    if not manager.driver:
        print("Cannot proceed without Neo4j connection")
        return
    
    # Setup schema
    manager.setup_schema()
    
    # Clear existing data for clean test
    manager.clear_database()
    
    # Test data creation
    print("\nCreating test data...")
    
    # Create organization
    org_data = {
        "id": "org_001",
        "canonical_name": "Federal Environmental Agency",
        "entity_type": "organization",
        "organization_type": "government_agency",
        "sector": "environmental_regulation",
        "size": "large",
        "confidence": 0.95,
        "quality_tier": "gold",
        "created_by": "test_system",
        "created_at": datetime.now().isoformat(),
        "workflow_id": "test_workflow_001",
        "description": "Federal agency responsible for environmental protection"
    }
    
    manager.create_organization(org_data)
    
    # Create stakeholder
    stakeholder_data = {
        "id": "stakeholder_001",
        "canonical_name": "Environmental Defense Coalition",
        "stakeholder_type": "group",
        "entity_type": "organization",
        "legitimacy": 0.8,
        "legitimacy_confidence": 0.9,
        "urgency": 0.9,
        "urgency_confidence": 0.85,
        "power": 0.6,
        "power_confidence": 0.75,
        "salience_score": 0.765,  # (0.8 * 0.9 * 0.6)^(1/3)
        "mitchell_category": "dependent",
        "priority_tier": "high",
        "confidence": 0.85,
        "quality_tier": "silver",
        "created_by": "test_system",
        "created_at": datetime.now().isoformat(),
        "workflow_id": "test_workflow_001",
        "description": "Coalition of environmental advocacy organizations",
        "surface_forms": json.dumps(["Environmental Defense Coalition", "EDC", "Environmental Coalition"]),
        "mention_count": 15
    }
    
    manager.create_stakeholder(stakeholder_data)
    
    # Create reified influence relationship
    relationship_data = {
        "id": "influence_001",
        "source_id": "stakeholder_001",
        "target_id": "org_001",
        "relationship_type": "INFLUENCES",
        "influence_strength": 0.7,
        "influence_mechanism": "legal",
        "conditionality": "during_regulatory_periods",
        "temporal_scope": "2024_policy_cycle",
        "confidence": 0.8,
        "quality_tier": "silver",
        "created_by": "test_system",
        "created_at": datetime.now().isoformat(),
        "workflow_id": "test_workflow_001",
        "weight": 0.7,
        "direction": "directed",
        "source_role_name": "advocacy_group",
        "target_role_name": "regulatory_agency",
        "additional_participants": {}
    }
    
    manager.create_reified_influence_relationship(relationship_data)
    
    # Test data retrieval
    print("\nTesting data retrieval...")
    
    network = manager.get_stakeholder_network()
    print(f"Network relationships: {len(network)}")
    
    table_data = manager.export_for_table_analysis()
    print(f"Table rows: {len(table_data)}")
    
    metrics = manager.calculate_network_metrics()
    print(f"Network metrics: {metrics}")
    
    # Cleanup
    manager.close()
    
    print("\n✓ Neo4j setup and testing completed")

if __name__ == "__main__":
    main()