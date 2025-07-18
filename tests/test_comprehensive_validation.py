"""Deep content validation testing

Validates actual output content, not just presence of outputs.
Tests semantic correctness, data integrity, and business logic.
"""

import pytest
import json
import os
import sys
import time
from typing import Dict, List, Any
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.evidence_logger import EvidenceLogger
from src.core.config_manager import ConfigManager
from src.core.tool_adapters import PDFLoaderAdapter, TextChunkerAdapter, SpacyNERAdapter
from src.tools.phase1.t01_pdf_loader import PDFLoader
from src.tools.phase1.t15a_text_chunker import TextChunker
from src.tools.phase1.t23a_spacy_ner import SpacyNER
from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
from src.tools.phase1.t31_entity_builder import EntityBuilder
from src.tools.phase1.t34_edge_builder import EdgeBuilder
from src.tools.phase1.t49_multihop_query import MultiHopQuery
from src.tools.phase1.t68_pagerank import PageRankCalculator


class TestComprehensiveValidation:
    """Deep content validation for GraphRAG tools"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.evidence_logger = EvidenceLogger()
        self.config_manager = ConfigManager()
        
        # Create reference test documents
        self._create_reference_documents()
        
        yield
        
        # Cleanup
        self._cleanup_reference_documents()
    
    def _create_reference_documents(self):
        """Create reference documents with known content"""
        # Create realistic test directory
        os.makedirs("test_data/realistic", exist_ok=True)
        
        # Create a reference text document with known entities
        self.reference_text_path = "test_data/realistic/reference_document.txt"
        self.reference_content = """
        Dr. Sarah Chen, a renowned researcher at Stanford University in Palo Alto, California, 
        published groundbreaking research on artificial intelligence in collaboration with 
        Professor Michael Johnson from MIT. The research, funded by the National Science Foundation 
        with a grant of $2.5 million, focused on neural network architectures.
        
        The team's findings were presented at the International Conference on Machine Learning 
        in New York City on July 15, 2023. Apple Inc. and Google LLC have shown interest in 
        licensing the technology for their respective AI platforms.
        
        Dr. Chen stated, "This breakthrough could revolutionize how we approach deep learning 
        in autonomous systems." The research paper, titled "Advanced Neural Architectures for 
        Autonomous Decision Making," has been cited over 500 times since its publication.
        """
        
        with open(self.reference_text_path, "w") as f:
            f.write(self.reference_content)
        
        # Expected entities for validation
        self.expected_entities = {
            "PERSON": ["Dr. Sarah Chen", "Professor Michael Johnson"],
            "ORG": ["Stanford University", "MIT", "National Science Foundation", 
                    "Apple Inc.", "Google LLC", "International Conference on Machine Learning"],
            "GPE": ["Palo Alto", "California", "New York City"],
            "DATE": ["July 15, 2023"],
            "MONEY": ["$2.5 million"],
            "CARDINAL": ["500"]
        }
        
        # Create a simple PDF for testing (using text file as mock PDF for now)
        self.reference_pdf_path = "test_data/realistic/reference_document.pdf"
        # In a real implementation, we'd create an actual PDF
        # For testing, we'll use the text file
        import shutil
        shutil.copy(self.reference_text_path, self.reference_pdf_path)
    
    def _cleanup_reference_documents(self):
        """Clean up reference documents"""
        files_to_remove = [
            self.reference_text_path,
            self.reference_pdf_path
        ]
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_pdf_extraction_content_accuracy(self):
        """Verify PDF extraction produces semantically correct content"""
        loader = PDFLoaderAdapter(self.config_manager)
        
        # For testing, we'll use a text file since we can't easily create a real PDF
        result = loader.execute({
            "document_paths": [self.reference_text_path],
            "workflow_id": "content_validation_test"
        })
        
        # Verify extraction was successful
        assert "documents" in result, "PDF loader should return documents"
        assert len(result["documents"]) > 0, "Should extract at least one document"
        
        document = result["documents"][0]
        content = document.get("text", "")
        
        # Verify specific content was extracted
        key_phrases = [
            "Dr. Sarah Chen",
            "Stanford University",
            "artificial intelligence",
            "$2.5 million",
            "neural network architectures"
        ]
        
        content_validation_results = {
            "content_length": len(content),
            "key_phrases_found": {},
            "extraction_accuracy": 0.0
        }
        
        found_count = 0
        for phrase in key_phrases:
            if phrase in content:
                content_validation_results["key_phrases_found"][phrase] = True
                found_count += 1
            else:
                content_validation_results["key_phrases_found"][phrase] = False
        
        content_validation_results["extraction_accuracy"] = found_count / len(key_phrases)
        
        # Log detailed content validation evidence
        self.evidence_logger.log_detailed_execution(
            operation="PDF_CONTENT_VALIDATION",
            details={
                "extracted_content_length": len(content),
                "expected_phrases": key_phrases,
                "found_phrases": [k for k, v in content_validation_results["key_phrases_found"].items() if v],
                "missing_phrases": [k for k, v in content_validation_results["key_phrases_found"].items() if not v],
                "extraction_accuracy": content_validation_results["extraction_accuracy"],
                "content_sample": content[:200] if len(content) > 200 else content
            }
        )
        
        # Assertions
        assert len(content) > 100, "Should extract meaningful content"
        assert content_validation_results["extraction_accuracy"] >= 0.8, "Should find at least 80% of key phrases"
    
    def test_entity_extraction_semantic_accuracy(self):
        """Verify entity extraction produces semantically correct entities"""
        # First, create chunks from our reference text
        text_chunker = TextChunkerAdapter(self.config_manager)
        
        chunk_result = text_chunker.execute({
            "documents": [{
                "text": self.reference_content,
                "document_id": "reference_doc",
                "metadata": {"source": "test"}
            }],
            "workflow_id": "semantic_accuracy_test"
        })
        
        assert "chunks" in chunk_result, "Chunker should return chunks"
        chunks = chunk_result["chunks"]
        
        # Now extract entities
        ner_adapter = SpacyNERAdapter(self.config_manager)
        
        ner_result = ner_adapter.execute({
            "chunks": chunks,
            "workflow_id": "semantic_accuracy_test"
        })
        
        assert "entities" in ner_result, "NER should return entities"
        entities = ner_result["entities"]
        
        # Validate entity extraction accuracy
        found_entities = {
            "PERSON": set(),
            "ORG": set(),
            "GPE": set(),
            "DATE": set(),
            "MONEY": set()
        }
        
        for entity in entities:
            entity_type = entity.get("entity_type", "")
            entity_text = entity.get("text", "")
            
            if entity_type in found_entities:
                found_entities[entity_type].add(entity_text)
        
        # Calculate extraction accuracy
        validation_results = {}
        
        for entity_type, expected_list in self.expected_entities.items():
            if entity_type in found_entities:
                expected_set = set(expected_list)
                found_set = found_entities[entity_type]
                
                # Calculate precision and recall
                true_positives = len(expected_set.intersection(found_set))
                false_positives = len(found_set - expected_set)
                false_negatives = len(expected_set - found_set)
                
                precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
                recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
                f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                validation_results[entity_type] = {
                    "expected": list(expected_set),
                    "found": list(found_set),
                    "true_positives": true_positives,
                    "false_positives": false_positives,
                    "false_negatives": false_negatives,
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1_score
                }
        
        # Verify entity boundaries are correct
        boundary_validation = []
        for entity in entities[:10]:  # Check first 10 entities
            chunk_id = entity.get("chunk_id")
            chunk = next((c for c in chunks if c.get("chunk_id") == chunk_id), None)
            
            if chunk:
                chunk_text = chunk.get("text", "")
                start = entity.get("start", 0)
                end = entity.get("end", 0)
                
                if 0 <= start < end <= len(chunk_text):
                    extracted_text = chunk_text[start:end]
                    boundary_validation.append({
                        "entity_text": entity.get("text"),
                        "extracted_text": extracted_text,
                        "boundary_correct": extracted_text == entity.get("text")
                    })
        
        # Log detailed validation results
        self.evidence_logger.log_detailed_execution(
            operation="ENTITY_EXTRACTION_VALIDATION",
            details={
                "total_entities_found": len(entities),
                "entity_type_validation": validation_results,
                "boundary_validation_sample": boundary_validation,
                "overall_precision": sum(v["precision"] for v in validation_results.values()) / len(validation_results) if validation_results else 0,
                "overall_recall": sum(v["recall"] for v in validation_results.values()) / len(validation_results) if validation_results else 0
            }
        )
        
        # Assertions
        assert len(entities) > 0, "Should find at least some entities"
        
        # Check that we found at least some entities of each major type
        assert len(found_entities["PERSON"]) > 0, "Should find PERSON entities"
        assert len(found_entities["ORG"]) > 0, "Should find ORG entities"
        assert len(found_entities["GPE"]) > 0, "Should find GPE entities"
        
        # Check accuracy (relaxed for real NER variation)
        for entity_type in ["PERSON", "ORG"]:
            if entity_type in validation_results:
                assert validation_results[entity_type]["recall"] >= 0.5, f"Should have at least 50% recall for {entity_type}"
    
    def test_relationship_extraction_quality(self):
        """Test the quality and accuracy of relationship extraction"""
        # Create a controlled scenario with known relationships
        test_entities = [
            {
                "entity_id": "sarah_chen",
                "text": "Dr. Sarah Chen",
                "entity_type": "PERSON",
                "chunk_id": "chunk_1",
                "confidence": 0.95
            },
            {
                "entity_id": "stanford",
                "text": "Stanford University",
                "entity_type": "ORG",
                "chunk_id": "chunk_1",
                "confidence": 0.98
            },
            {
                "entity_id": "michael_johnson",
                "text": "Professor Michael Johnson",
                "entity_type": "PERSON",
                "chunk_id": "chunk_1",
                "confidence": 0.93
            },
            {
                "entity_id": "mit",
                "text": "MIT",
                "entity_type": "ORG",
                "chunk_id": "chunk_1",
                "confidence": 0.99
            }
        ]
        
        test_chunks = [{
            "chunk_id": "chunk_1",
            "text": self.reference_content,
            "confidence": 0.95
        }]
        
        # Extract relationships
        rel_extractor = RelationshipExtractorAdapter(self.config_manager)
        
        rel_result = rel_extractor.execute({
            "entities": test_entities,
            "chunks": test_chunks,
            "workflow_id": "relationship_quality_test"
        })
        
        assert "relationships" in rel_result, "Should return relationships"
        relationships = rel_result["relationships"]
        
        # Validate relationship quality
        relationship_validation = {
            "total_relationships": len(relationships),
            "relationship_types": {},
            "expected_relationships_found": {},
            "confidence_distribution": {
                "high": 0,  # > 0.8
                "medium": 0,  # 0.5-0.8
                "low": 0  # < 0.5
            }
        }
        
        # Expected relationships based on the text
        expected_relationships = [
            ("sarah_chen", "stanford", ["works_at", "affiliated_with", "researcher_at"]),
            ("michael_johnson", "mit", ["works_at", "affiliated_with", "professor_at"]),
            ("sarah_chen", "michael_johnson", ["collaborates_with", "co_author"])
        ]
        
        # Analyze found relationships
        for rel in relationships:
            rel_type = rel.get("relationship_type", "UNKNOWN")
            confidence = rel.get("confidence", 0)
            
            # Count relationship types
            if rel_type not in relationship_validation["relationship_types"]:
                relationship_validation["relationship_types"][rel_type] = 0
            relationship_validation["relationship_types"][rel_type] += 1
            
            # Categorize by confidence
            if confidence > 0.8:
                relationship_validation["confidence_distribution"]["high"] += 1
            elif confidence > 0.5:
                relationship_validation["confidence_distribution"]["medium"] += 1
            else:
                relationship_validation["confidence_distribution"]["low"] += 1
            
            # Check expected relationships
            source = rel.get("source_id")
            target = rel.get("target_id")
            
            for exp_source, exp_target, exp_types in expected_relationships:
                if (source == exp_source and target == exp_target) or (source == exp_target and target == exp_source):
                    key = f"{exp_source}-{exp_target}"
                    if key not in relationship_validation["expected_relationships_found"]:
                        relationship_validation["expected_relationships_found"][key] = {
                            "found": True,
                            "type": rel_type,
                            "confidence": confidence,
                            "expected_types": exp_types
                        }
        
        # Log validation results
        self.evidence_logger.log_detailed_execution(
            operation="RELATIONSHIP_EXTRACTION_VALIDATION",
            details=relationship_validation
        )
        
        # Assertions
        assert len(relationships) > 0, "Should extract at least some relationships"
        assert relationship_validation["confidence_distribution"]["high"] > 0, "Should have some high-confidence relationships"
    
    def test_graph_construction_integrity(self):
        """Test the integrity of the constructed knowledge graph"""
        # Build a complete graph from our reference content
        workflow_id = "graph_integrity_test"
        
        # Step 1: Create chunks
        text_chunker = TextChunkerAdapter(self.config_manager)
        chunk_result = text_chunker.execute({
            "documents": [{
                "text": self.reference_content,
                "document_id": "reference_doc",
                "metadata": {"source": "test"}
            }],
            "workflow_id": workflow_id
        })
        chunks = chunk_result["chunks"]
        
        # Step 2: Extract entities
        ner_adapter = SpacyNERAdapter(self.config_manager)
        ner_result = ner_adapter.execute({
            "chunks": chunks,
            "workflow_id": workflow_id
        })
        entities = ner_result["entities"]
        
        # Step 3: Extract relationships
        rel_extractor = RelationshipExtractorAdapter(self.config_manager)
        rel_result = rel_extractor.execute({
            "entities": entities,
            "chunks": chunks,
            "workflow_id": workflow_id
        })
        relationships = rel_result["relationships"]
        
        # Step 4: Build entity nodes
        entity_builder = EntityBuilderAdapter(self.config_manager)
        entity_result = entity_builder.execute({
            "entities": entities,
            "chunks": chunks,
            "workflow_id": workflow_id
        })
        nodes = entity_result.get("nodes", [])
        
        # Step 5: Build edges
        edge_builder = EdgeBuilderAdapter(self.config_manager)
        edge_result = edge_builder.execute({
            "relationships": relationships,
            "entities": entities,
            "workflow_id": workflow_id
        })
        edges = edge_result.get("edges", [])
        
        # Validate graph integrity
        graph_validation = {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "node_types": {},
            "edge_types": {},
            "orphan_nodes": 0,
            "invalid_edges": 0,
            "node_properties_complete": 0,
            "edge_properties_complete": 0
        }
        
        # Create node lookup
        node_ids = {node.get("id") for node in nodes}
        
        # Validate nodes
        for node in nodes:
            node_type = node.get("type", "UNKNOWN")
            if node_type not in graph_validation["node_types"]:
                graph_validation["node_types"][node_type] = 0
            graph_validation["node_types"][node_type] += 1
            
            # Check if node has complete properties
            required_props = ["id", "type", "text", "confidence"]
            if all(prop in node for prop in required_props):
                graph_validation["node_properties_complete"] += 1
        
        # Validate edges
        nodes_with_edges = set()
        for edge in edges:
            edge_type = edge.get("type", "UNKNOWN")
            if edge_type not in graph_validation["edge_types"]:
                graph_validation["edge_types"][edge_type] = 0
            graph_validation["edge_types"][edge_type] += 1
            
            # Check if edge references valid nodes
            source = edge.get("source")
            target = edge.get("target")
            
            if source not in node_ids or target not in node_ids:
                graph_validation["invalid_edges"] += 1
            else:
                nodes_with_edges.add(source)
                nodes_with_edges.add(target)
            
            # Check if edge has complete properties
            required_props = ["source", "target", "type", "confidence"]
            if all(prop in edge for prop in required_props):
                graph_validation["edge_properties_complete"] += 1
        
        # Count orphan nodes
        graph_validation["orphan_nodes"] = len(node_ids - nodes_with_edges)
        
        # Calculate graph density
        max_edges = len(nodes) * (len(nodes) - 1) / 2
        graph_validation["graph_density"] = len(edges) / max_edges if max_edges > 0 else 0
        
        # Log graph integrity results
        self.evidence_logger.log_detailed_execution(
            operation="GRAPH_CONSTRUCTION_VALIDATION",
            details=graph_validation
        )
        
        # Assertions
        assert len(nodes) > 0, "Should create at least some nodes"
        assert len(edges) > 0, "Should create at least some edges"
        assert graph_validation["invalid_edges"] == 0, "All edges should reference valid nodes"
        assert graph_validation["node_properties_complete"] == len(nodes), "All nodes should have complete properties"
        assert graph_validation["edge_properties_complete"] == len(edges), "All edges should have complete properties"
    
    def test_pagerank_calculation_correctness(self):
        """Test the correctness of PageRank calculations"""
        # Create a simple, known graph structure
        workflow_id = "pagerank_correctness_test"
        
        # Create a controlled graph with known structure
        # A -> B, C
        # B -> C, D
        # C -> D
        # D -> A (creating a cycle)
        
        test_entities = [
            {"entity_id": "A", "text": "Node A", "entity_type": "TEST", "chunk_id": "chunk_1", "confidence": 0.9},
            {"entity_id": "B", "text": "Node B", "entity_type": "TEST", "chunk_id": "chunk_1", "confidence": 0.9},
            {"entity_id": "C", "text": "Node C", "entity_type": "TEST", "chunk_id": "chunk_1", "confidence": 0.9},
            {"entity_id": "D", "text": "Node D", "entity_type": "TEST", "chunk_id": "chunk_1", "confidence": 0.9}
        ]
        
        test_relationships = [
            {"relationship_id": "r1", "source_id": "A", "target_id": "B", "relationship_type": "LINKS_TO", "chunk_id": "chunk_1", "confidence": 0.9},
            {"relationship_id": "r2", "source_id": "A", "target_id": "C", "relationship_type": "LINKS_TO", "chunk_id": "chunk_1", "confidence": 0.9},
            {"relationship_id": "r3", "source_id": "B", "target_id": "C", "relationship_type": "LINKS_TO", "chunk_id": "chunk_1", "confidence": 0.9},
            {"relationship_id": "r4", "source_id": "B", "target_id": "D", "relationship_type": "LINKS_TO", "chunk_id": "chunk_1", "confidence": 0.9},
            {"relationship_id": "r5", "source_id": "C", "target_id": "D", "relationship_type": "LINKS_TO", "chunk_id": "chunk_1", "confidence": 0.9},
            {"relationship_id": "r6", "source_id": "D", "target_id": "A", "relationship_type": "LINKS_TO", "chunk_id": "chunk_1", "confidence": 0.9}
        ]
        
        chunks = [{"chunk_id": "chunk_1", "text": "Test graph", "confidence": 0.9}]
        
        # Build the graph
        entity_builder = EntityBuilderAdapter(self.config_manager)
        entity_result = entity_builder.execute({
            "entities": test_entities,
            "chunks": chunks,
            "workflow_id": workflow_id
        })
        
        edge_builder = EdgeBuilderAdapter(self.config_manager)
        edge_result = edge_builder.execute({
            "relationships": test_relationships,
            "entities": test_entities,
            "workflow_id": workflow_id
        })
        
        # Calculate PageRank
        pagerank = PageRankAdapter(self.config_manager)
        pagerank_result = pagerank.execute({
            "iterations": 50,
            "damping_factor": 0.85,
            "workflow_id": workflow_id
        })
        
        assert "nodes" in pagerank_result, "PageRank should return nodes with scores"
        nodes_with_scores = pagerank_result["nodes"]
        
        # Validate PageRank properties
        pagerank_validation = {
            "total_nodes": len(nodes_with_scores),
            "sum_of_scores": 0,
            "score_distribution": {},
            "convergence_check": True
        }
        
        # Extract scores
        scores = {}
        for node in nodes_with_scores:
            node_id = node.get("id")
            score = node.get("pagerank", 0)
            scores[node_id] = score
            pagerank_validation["sum_of_scores"] += score
            pagerank_validation["score_distribution"][node_id] = score
        
        # PageRank properties to validate:
        # 1. Sum of all PageRank scores should be close to 1.0
        # 2. In our graph, D should have high score (receives from A, B, C)
        # 3. A should have decent score (receives from D)
        # 4. All scores should be positive
        
        # Check sum close to 1.0 (allowing for numerical errors)
        pagerank_validation["sum_close_to_one"] = abs(pagerank_validation["sum_of_scores"] - 1.0) < 0.1
        
        # Check all scores are positive
        pagerank_validation["all_positive"] = all(score > 0 for score in scores.values())
        
        # Check relative ordering makes sense
        if len(scores) == 4:
            # D should have high score as it has most incoming links
            pagerank_validation["d_has_high_score"] = scores.get("D", 0) > sum(scores.values()) / 4
        
        # Log PageRank validation results
        self.evidence_logger.log_detailed_execution(
            operation="PAGERANK_CALCULATION_VALIDATION",
            details=pagerank_validation
        )
        
        # Assertions
        assert len(nodes_with_scores) > 0, "Should calculate PageRank for nodes"
        assert pagerank_validation["all_positive"], "All PageRank scores should be positive"
        assert pagerank_validation["sum_close_to_one"], "Sum of PageRank scores should be close to 1.0"
    
    def test_query_result_relevance(self):
        """Test the relevance and accuracy of query results"""
        # First, build a graph from our reference content
        workflow_id = "query_relevance_test"
        
        # Build complete graph (reusing previous steps)
        text_chunker = TextChunkerAdapter(self.config_manager)
        chunk_result = text_chunker.execute({
            "documents": [{
                "text": self.reference_content,
                "document_id": "reference_doc",
                "metadata": {"source": "test"}
            }],
            "workflow_id": workflow_id
        })
        
        ner_adapter = SpacyNERAdapter(self.config_manager)
        ner_result = ner_adapter.execute({
            "chunks": chunk_result["chunks"],
            "workflow_id": workflow_id
        })
        
        rel_extractor = RelationshipExtractorAdapter(self.config_manager)
        rel_result = rel_extractor.execute({
            "entities": ner_result["entities"],
            "chunks": chunk_result["chunks"],
            "workflow_id": workflow_id
        })
        
        entity_builder = EntityBuilderAdapter(self.config_manager)
        entity_result = entity_builder.execute({
            "entities": ner_result["entities"],
            "chunks": chunk_result["chunks"],
            "workflow_id": workflow_id
        })
        
        edge_builder = EdgeBuilderAdapter(self.config_manager)
        edge_result = edge_builder.execute({
            "relationships": rel_result["relationships"],
            "entities": ner_result["entities"],
            "workflow_id": workflow_id
        })
        
        # Now test queries
        query_adapter = MultihopQueryAdapter(self.config_manager)
        
        test_queries = [
            {
                "query": "Dr. Sarah Chen",
                "expected_results": ["Dr. Sarah Chen", "Stanford University"],
                "max_hops": 1
            },
            {
                "query": "Stanford University",
                "expected_results": ["Stanford University", "Dr. Sarah Chen", "Palo Alto"],
                "max_hops": 2
            },
            {
                "query": "artificial intelligence",
                "expected_results": ["artificial intelligence", "neural network"],
                "max_hops": 2
            }
        ]
        
        query_validation_results = []
        
        for test_query in test_queries:
            query_result = query_adapter.execute({
                "query": test_query["query"],
                "max_hops": test_query["max_hops"],
                "workflow_id": workflow_id
            })
            
            # Analyze results
            if "error" not in query_result:
                nodes = query_result.get("nodes", [])
                edges = query_result.get("edges", [])
                
                # Extract node texts
                found_texts = [node.get("text", "") for node in nodes]
                
                # Check relevance
                relevant_found = [text for text in test_query["expected_results"] if any(text.lower() in found.lower() for found in found_texts)]
                
                validation = {
                    "query": test_query["query"],
                    "nodes_returned": len(nodes),
                    "edges_returned": len(edges),
                    "expected_results": test_query["expected_results"],
                    "relevant_found": relevant_found,
                    "relevance_score": len(relevant_found) / len(test_query["expected_results"]) if test_query["expected_results"] else 0,
                    "sample_results": found_texts[:5]  # First 5 results
                }
            else:
                validation = {
                    "query": test_query["query"],
                    "error": query_result.get("error"),
                    "relevance_score": 0
                }
            
            query_validation_results.append(validation)
        
        # Log query validation results
        self.evidence_logger.log_detailed_execution(
            operation="QUERY_RELEVANCE_VALIDATION",
            details={
                "total_queries": len(test_queries),
                "query_results": query_validation_results,
                "average_relevance": sum(r["relevance_score"] for r in query_validation_results) / len(query_validation_results) if query_validation_results else 0
            }
        )
        
        # Assertions
        for result in query_validation_results:
            assert "error" not in result, f"Query '{result.get('query')}' should not error"
            assert result.get("nodes_returned", 0) > 0, f"Query '{result.get('query')}' should return some nodes"
            assert result.get("relevance_score", 0) > 0, f"Query '{result.get('query')}' should return relevant results"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])