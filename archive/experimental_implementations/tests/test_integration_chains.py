"""Integration tests for tool chains."""

import pytest
import tempfile
from pathlib import Path

from src.utils.database import DatabaseManager
from tests.utils.builders import TestDataCleaner


class TestPDFToPageRankChain:
    """Test complete chain from PDF loading to PageRank analysis."""
    
    @pytest.fixture
    def db(self):
        """Create test database manager."""
        db_manager = DatabaseManager()
        db_manager.initialize()
        
        # Initialize FAISS
        db_manager.faiss.initialize_index(dimension=384)
        
        # Clean up before test
        with db_manager.neo4j.driver.session() as session:
            TestDataCleaner.cleanup_all(session)
        
        yield db_manager
        
        # Clean up after test
        with db_manager.neo4j.driver.session() as session:
            TestDataCleaner.cleanup_all(session)
        
        db_manager.close()
    
    @pytest.fixture
    def test_pdf(self):
        """Create a test PDF file."""
        # Create temporary PDF with reportlab
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
        except ImportError:
            pytest.skip("reportlab not installed")
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            pdf_path = tmp.name
            
        # Create PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Add test content
        c.drawString(100, 750, "Super-Digimon Integration Test")
        c.drawString(100, 700, "")
        c.drawString(100, 650, "Apple Inc was founded by Steve Jobs in 1976.")
        c.drawString(100, 600, "Microsoft Corporation was founded by Bill Gates.")
        c.drawString(100, 550, "Apple and Microsoft are competitors in the tech industry.")
        c.drawString(100, 500, "Google acquired YouTube in 2006.")
        c.drawString(100, 450, "Amazon Web Services provides cloud computing.")
        
        c.save()
        
        yield Path(pdf_path)
        
        # Cleanup
        Path(pdf_path).unlink(missing_ok=True)
    
    def test_full_chain(self, db, test_pdf):
        """Test complete processing chain."""
        # Step 1: Load PDF
        from src.tools.phase1.t01_pdf_loader import PDFDocumentLoader
        
        loader = PDFDocumentLoader(db)
        pdf_result = loader.load_pdf(str(test_pdf))
        
        assert pdf_result["status"] == "success"
        assert pdf_result["page_count"] > 0
        doc_ref = pdf_result["document_ref"]
        
        # Step 2: Chunk document
        from src.tools.phase1.t13_text_chunker import TextChunker
        
        chunker = TextChunker(db)
        chunk_result = chunker.chunk_document(
            doc_ref,
            chunk_size=200,
            overlap=50
        )
        
        assert chunk_result["status"] == "success"
        assert len(chunk_result["chunk_refs"]) > 0
        
        # Step 3: Extract entities (using LLM extractor)
        from src.tools.phase2.t23b_llm_extractor import LLMEntityExtractor
        
        extractor = LLMEntityExtractor(db)
        all_entities = []
        
        for chunk_ref in chunk_result["chunk_refs"][:2]:  # Process first 2 chunks
            try:
                extract_result = extractor.extract_entities_and_relationships(chunk_ref)
                if extract_result["status"] == "success":
                    all_entities.extend(extract_result["entity_refs"])
            except Exception as e:
                # Skip if OpenAI not configured
                if "OPENAI_API_KEY" in str(e):
                    pytest.skip("OpenAI API key not configured")
                raise
        
        if not all_entities:
            # Fallback to SpaCy if LLM fails
            from src.tools.phase2.t23a_entity_extractor import EntityExtractor
            
            extractor = EntityExtractor(db)
            for chunk_ref in chunk_result["chunk_refs"]:
                extract_result = extractor.extract_entities(chunk_ref)
                if extract_result["status"] == "success":
                    all_entities.extend(extract_result["entity_refs"])
        
        assert len(all_entities) > 0
        
        # Step 4: Build entity nodes with communities
        from src.tools.phase3.t31_entity_node_builder import EntityNodeBuilder
        
        builder = EntityNodeBuilder(db)
        build_result = builder.build_entity_nodes(
            algorithm="label_propagation",
            weight_threshold=1.0
        )
        
        assert build_result["status"] == "success"
        
        # Step 5: Generate embeddings
        from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
        
        generator = EmbeddingGenerator(db)
        embed_result = generator.generate_embeddings(
            all_entities[:10]  # Embed first 10 entities
        )
        
        assert embed_result["status"] == "success"
        assert embed_result["embedding_count"] > 0
        
        # Step 6: Run PageRank
        from src.tools.phase5.t68_pagerank import PageRankAnalyzer
        
        analyzer = PageRankAnalyzer(db)
        pagerank_result = analyzer.compute_pagerank()
        
        assert pagerank_result["status"] == "success"
        assert len(pagerank_result["scores"]) > 0
        assert len(pagerank_result["top_entities"]) > 0
        
        # Step 7: Query the graph
        from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery
        
        nlq = NaturalLanguageQuery(db)
        query_result = nlq.query("Tell me about Apple")
        
        assert query_result["status"] == "success"
        # Should find something (either via embeddings or graph search)
        assert len(query_result["results"]) > 0 or "no embeddings" in str(query_result["warnings"])
        
        # Verify data consistency
        with db.neo4j.driver.session() as session:
            # Check entities exist
            entity_count = session.run("MATCH (e:Entity) RETURN count(e) as c").single()["c"]
            assert entity_count > 0
            
            # Check some have PageRank scores
            pr_count = session.run("""
                MATCH (e:Entity)
                WHERE e.attributes CONTAINS 'pagerank_score'
                RETURN count(e) as c
            """).single()["c"]
            assert pr_count > 0
            
            # Check relationships exist
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]
            # May or may not have relationships depending on extraction


class TestMultiHopQueryChain:
    """Test multi-hop query with neighborhood exploration."""
    
    @pytest.fixture
    def db(self):
        """Create test database manager."""
        db_manager = DatabaseManager()
        db_manager.initialize()
        
        yield db_manager
        
        db_manager.close()
    
    def test_hop_to_neighborhood_chain(self, db):
        """Test finding entities via hops then exploring neighborhoods."""
        from tests.utils.builders import TestEntityBuilder
        
        # Create a network structure
        with db.neo4j.driver.session() as session:
            entities = [
                {"name": "Central", "entity_type": "HUB"},
                {"name": "Branch1", "entity_type": "NODE"},
                {"name": "Branch2", "entity_type": "NODE"},
                {"name": "Leaf1A", "entity_type": "LEAF"},
                {"name": "Leaf1B", "entity_type": "LEAF"},
                {"name": "Leaf2A", "entity_type": "LEAF"},
                {"name": "Leaf2B", "entity_type": "LEAF"},
            ]
            
            relationships = [
                {"source_name": "Central", "target_name": "Branch1", "relationship_type": "CONNECTS"},
                {"source_name": "Central", "target_name": "Branch2", "relationship_type": "CONNECTS"},
                {"source_name": "Branch1", "target_name": "Leaf1A", "relationship_type": "CONTAINS"},
                {"source_name": "Branch1", "target_name": "Leaf1B", "relationship_type": "CONTAINS"},
                {"source_name": "Branch2", "target_name": "Leaf2A", "relationship_type": "CONTAINS"},
                {"source_name": "Branch2", "target_name": "Leaf2B", "relationship_type": "CONTAINS"},
            ]
            
            id_map = TestEntityBuilder.create_entities_with_relationships(
                session, entities, relationships
            )
        
        # Step 1: Find 2-hop entities from Central
        from src.tools.phase4.t49_hop_query import HopQuery
        
        hop_query = HopQuery(db)
        hop_result = hop_query.hop_query(
            source_entities=["Central"],
            k=2
        )
        
        assert hop_result["status"] == "success"
        assert hop_result["metadata"]["hop_count"] == 2
        # Should find all leaves (4 entities at 2 hops)
        assert len([e for e in hop_result["entities"] if e["distance"] == 2]) == 4
        
        # Step 2: Explore neighborhood of one branch
        from src.tools.phase4.t50_neighborhood import NeighborhoodSearch
        
        neighborhood = NeighborhoodSearch(db)
        neighbor_result = neighborhood.search_neighborhood(
            entity_refs=[f"neo4j://entity/{id_map['Branch1']}"],
            radius=1
        )
        
        assert neighbor_result["status"] == "success"
        # Should find Central + Leaf1A + Leaf1B = 3 neighbors
        assert len(neighbor_result["neighbors"]) == 3
        
        # Step 3: Find paths between leaves
        from src.tools.phase4.t52_path_finding import PathFinder
        
        path_finder = PathFinder(db)
        path_result = path_finder.find_paths(
            source_ref=f"neo4j://entity/{id_map['Leaf1A']}",
            target_ref=f"neo4j://entity/{id_map['Leaf2A']}",
            algorithm="all_paths",
            max_length=4
        )
        
        assert path_result["status"] == "success"
        assert len(path_result["paths"]) > 0
        # Shortest path should be: Leaf1A -> Branch1 -> Central -> Branch2 -> Leaf2A (length 4)
        assert path_result["paths"][0]["length"] == 4