"""Edge case tests for Super-Digimon tools."""

import pytest
from datetime import datetime

from src.utils.database import DatabaseManager
from tests.utils.builders import TestEntityBuilder, TestGraphBuilder, TestDataCleaner


class TestT68PageRankEdgeCases:
    """Edge case tests for PageRank analyzer."""
    
    @pytest.fixture
    def db(self):
        """Create test database manager."""
        db_manager = DatabaseManager()
        db_manager.initialize()
        
        # Clean up before test
        with db_manager.neo4j.driver.session() as session:
            TestDataCleaner.cleanup_all(session)
        
        yield db_manager
        
        # Clean up after test
        with db_manager.neo4j.driver.session() as session:
            TestDataCleaner.cleanup_all(session)
        
        db_manager.close()
    
    def test_empty_graph(self, db):
        """Test PageRank on empty graph."""
        from src.tools.phase5.t68_pagerank import PageRankAnalyzer
        
        analyzer = PageRankAnalyzer(db)
        result = analyzer.compute_pagerank()
        
        assert result["status"] == "success"
        assert result["scores"] == {}
        assert result["top_entities"] == []
        assert result["metadata"]["entity_count"] == 0
        assert len(result["warnings"]) > 0
        assert "No entities found" in result["warnings"][0]
    
    def test_single_node(self, db):
        """Test PageRank on single node (no edges)."""
        from src.tools.phase5.t68_pagerank import PageRankAnalyzer
        
        # Create single entity
        with db.neo4j.driver.session() as session:
            entity_id = TestEntityBuilder.create_entity(
                session,
                name="Lonely Node",
                entity_type="ISOLATED"
            )
        
        analyzer = PageRankAnalyzer(db)
        result = analyzer.compute_pagerank()
        
        assert result["status"] == "success"
        assert len(result["scores"]) == 1
        assert f"neo4j://entity/{entity_id}" in result["scores"]
        # Single node should have PageRank = 1.0
        assert result["scores"][f"neo4j://entity/{entity_id}"] == pytest.approx(1.0, rel=0.01)
    
    def test_disconnected_components(self, db):
        """Test PageRank on disconnected graph."""
        from src.tools.phase5.t68_pagerank import PageRankAnalyzer
        
        # Create disconnected components
        with db.neo4j.driver.session() as session:
            components = TestGraphBuilder.create_disconnected_components(
                session,
                component_count=3,
                size_per_component=3
            )
        
        analyzer = PageRankAnalyzer(db)
        result = analyzer.compute_pagerank()
        
        assert result["status"] == "success"
        assert result["metadata"]["entity_count"] == 9  # 3 components * 3 entities
        assert len(result["scores"]) == 9
        
        # Each component should have similar internal scores
        component_scores = []
        for component in components:
            scores = [result["scores"][f"neo4j://entity/{eid}"] for eid in component]
            component_scores.append(sum(scores))
        
        # Each component should have roughly 1/3 of total PageRank
        for score in component_scores:
            assert score == pytest.approx(1/3, rel=0.1)
    
    def test_self_loop(self, db):
        """Test PageRank with self-referencing entity."""
        from src.tools.phase5.t68_pagerank import PageRankAnalyzer
        
        with db.neo4j.driver.session() as session:
            # Create entity with self-loop
            entity_id = TestEntityBuilder.create_entity(
                session,
                name="Self Referencer",
                entity_type="LOOP"
            )
            
            # Create self-loop
            session.run("""
                MATCH (e:Entity {id: $id})
                CREATE (e)-[:RELATES {
                    id: 'self_loop',
                    relationship_type: 'REFERENCES_SELF',
                    created_at: datetime()
                }]->(e)
            """, id=entity_id)
        
        analyzer = PageRankAnalyzer(db)
        result = analyzer.compute_pagerank()
        
        assert result["status"] == "success"
        assert len(result["scores"]) == 1
        # Self-loop shouldn't crash the algorithm
        assert f"neo4j://entity/{entity_id}" in result["scores"]
    
    def test_circular_references(self, db):
        """Test PageRank with circular relationship pattern."""
        from src.tools.phase5.t68_pagerank import PageRankAnalyzer
        
        with db.neo4j.driver.session() as session:
            # Create circular pattern: A -> B -> C -> A
            entities = []
            for name in ["A", "B", "C"]:
                entities.append({
                    "name": name,
                    "entity_type": "CIRCULAR"
                })
            
            relationships = [
                {"source_name": "A", "target_name": "B", "relationship_type": "NEXT"},
                {"source_name": "B", "target_name": "C", "relationship_type": "NEXT"},
                {"source_name": "C", "target_name": "A", "relationship_type": "NEXT"}
            ]
            
            id_map = TestEntityBuilder.create_entities_with_relationships(
                session, entities, relationships
            )
        
        analyzer = PageRankAnalyzer(db)
        result = analyzer.compute_pagerank()
        
        assert result["status"] == "success"
        assert len(result["scores"]) == 3
        
        # In a perfect circle, all nodes should have equal PageRank
        scores = list(result["scores"].values())
        assert all(s == pytest.approx(scores[0], rel=0.01) for s in scores)
    
    def test_extreme_hub(self, db):
        """Test PageRank with extreme hub-and-spoke pattern."""
        from src.tools.phase5.t68_pagerank import PageRankAnalyzer
        
        with db.neo4j.driver.session() as session:
            # Create hub with many spokes
            id_map = TestGraphBuilder.create_hub_spoke(
                session,
                hub_name="MegaHub",
                spoke_count=100
            )
        
        analyzer = PageRankAnalyzer(db)
        result = analyzer.compute_pagerank()
        
        assert result["status"] == "success"
        assert result["metadata"]["entity_count"] == 101
        
        # Hub should have highest PageRank
        hub_ref = f"neo4j://entity/{id_map['MegaHub']}"
        hub_score = result["scores"][hub_ref]
        
        # Check hub is in top entities
        assert result["top_entities"][0]["entity_ref"] == hub_ref
        
        # Hub should have much higher score than spokes
        for i in range(100):
            spoke_ref = f"neo4j://entity/{id_map[f'Spoke_{i}']}"
            assert result["scores"][spoke_ref] < hub_score * 0.1


class TestT94NaturalLanguageQueryEdgeCases:
    """Edge case tests for Natural Language Query."""
    
    @pytest.fixture
    def db(self):
        """Create test database manager."""
        db_manager = DatabaseManager()
        db_manager.initialize()
        
        # Initialize FAISS index
        db_manager.faiss.initialize_index(dimension=384)  # all-MiniLM-L6-v2 dimension
        
        yield db_manager
        
        db_manager.close()
    
    def test_empty_query(self, db):
        """Test with empty query string."""
        from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery
        
        nlq = NaturalLanguageQuery(db)
        
        # Empty query should raise ValueError
        with pytest.raises(ValueError, match="Query text cannot be empty"):
            nlq.query("")
        
        # Whitespace-only query should also fail
        with pytest.raises(ValueError, match="Query text cannot be empty"):
            nlq.query("   \n\t  ")
    
    def test_no_embeddings_fallback(self, db):
        """Test fallback to graph search when no embeddings exist."""
        from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery
        
        # Create entities without embeddings
        with db.neo4j.driver.session() as session:
            TestEntityBuilder.create_entity(
                session,
                name="Apple Inc",
                entity_type="COMPANY"
            )
            TestEntityBuilder.create_entity(
                session,
                name="Microsoft Corporation",
                entity_type="COMPANY"
            )
        
        nlq = NaturalLanguageQuery(db)
        result = nlq.query("Tell me about Apple")
        
        assert result["status"] == "success"
        assert "graph_based" in result["metadata"].get("search_method", "")
        assert len(result["warnings"]) > 0
        assert "no embeddings available" in result["warnings"][0].lower()
    
    def test_very_long_query(self, db):
        """Test with extremely long query."""
        from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery
        
        # Create a very long query
        long_query = " ".join(["analyze"] * 1000)  # ~7000 characters
        
        nlq = NaturalLanguageQuery(db)
        result = nlq.query(long_query)
        
        # Should handle gracefully
        assert result["status"] == "success"
        assert result["metadata"]["query_length"] > 5000
    
    def test_special_characters_query(self, db):
        """Test query with special characters."""
        from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery
        
        queries = [
            "What about $AAPL stock?",
            "Email: test@example.com",
            "C++ vs Java",
            "Is 2+2=4?",
            "¿Cómo está? 你好",
            "🚀 To the moon!"
        ]
        
        nlq = NaturalLanguageQuery(db)
        
        for query in queries:
            result = nlq.query(query)
            # Should not crash
            assert result["status"] == "success"
            assert result["confidence"] >= 0.0


class TestT41EmbeddingGeneratorEdgeCases:
    """Edge case tests for Embedding Generator."""
    
    @pytest.fixture
    def db(self):
        """Create test database manager."""
        db_manager = DatabaseManager()
        db_manager.initialize()
        db_manager.faiss.initialize_index(dimension=384)
        
        yield db_manager
        
        db_manager.close()
    
    def test_empty_object_list(self, db):
        """Test with empty object list."""
        from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
        
        generator = EmbeddingGenerator(db)
        
        with pytest.raises(ValueError, match="No objects provided"):
            generator.generate_embeddings([])
    
    def test_invalid_references(self, db):
        """Test with invalid object references."""
        from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
        
        generator = EmbeddingGenerator(db)
        
        invalid_refs = [
            "invalid_format",
            "missing://type",
            "neo4j://",
            "://entity/123",
            "neo4j//entity/123",  # Single slash
            "neo4j://entity",  # Missing ID
        ]
        
        result = generator.generate_embeddings(invalid_refs)
        
        assert result["status"] == "success"
        assert result["embedding_count"] == 0
        assert len(result["warnings"]) == len(invalid_refs)
    
    def test_entity_without_text(self, db):
        """Test embedding generation for entity with no text content."""
        from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
        
        # Create entity with minimal fields
        with db.neo4j.driver.session() as session:
            entity_id = TestEntityBuilder.create_entity(
                session,
                name="",  # Empty name
                entity_type="UNKNOWN",
                canonical_name=""
            )
        
        generator = EmbeddingGenerator(db)
        result = generator.generate_embeddings([f"neo4j://entity/{entity_id}"])
        
        # Should use fallback text
        assert result["status"] == "success"
        assert result["embedding_count"] == 1
        # The fallback should include entity ID
        assert entity_id in str(result)
    
    def test_mixed_valid_invalid_objects(self, db):
        """Test with mix of valid and invalid objects."""
        from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
        
        # Create one valid entity
        with db.neo4j.driver.session() as session:
            entity_id = TestEntityBuilder.create_entity(
                session,
                name="Valid Entity",
                entity_type="TEST"
            )
        
        refs = [
            f"neo4j://entity/{entity_id}",  # Valid
            "invalid://format",  # Invalid
            "neo4j://entity/nonexistent",  # Valid format but doesn't exist
        ]
        
        generator = EmbeddingGenerator(db)
        result = generator.generate_embeddings(refs)
        
        assert result["status"] == "success"
        assert result["embedding_count"] == 1  # Only the valid one
        assert len(result["warnings"]) >= 2  # At least 2 failed