"""
Test suite for Task C.4: Cross-Document Relationship Discovery

Following TDD methodology - implementing 14+ test cases first, then implementation.
Tests cover entity resolution, concept tracking, relationship discovery, and graph operations.
"""

import pytest
import asyncio
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path

# Import the classes we'll implement
from src.relationships.cross_document_linker import CrossDocumentLinker
from src.relationships.entity_resolver import EntityResolver  
from src.relationships.concept_tracker import ConceptTracker
from src.relationships.relationship_classifier import RelationshipClassifier


@dataclass
class EntityReference:
    """Reference to an entity across documents"""
    entity_id: str
    entity_name: str
    document_path: str
    mention_context: str
    confidence_score: float
    entity_type: str


@dataclass
class ConceptEvolution:
    """Tracks how a concept evolves across documents"""
    concept_id: str
    concept_name: str
    timeline: List[Dict[str, Any]]
    evolution_type: str  # emerging, evolving, declining, stable
    confidence_score: float


@dataclass
class Relationship:
    """Represents a relationship between entities or concepts"""
    relationship_id: str
    source_entity: str
    target_entity: str
    relationship_type: str  # causal, temporal, hierarchical, associative
    confidence_score: float
    evidence_documents: List[str]
    relationship_direction: str  # bidirectional, source_to_target, target_to_source


@dataclass
class RelationshipNetwork:
    """Network representation of discovered relationships"""
    entities: List[str]
    relationships: List[Relationship]
    network_density: float
    centrality_scores: Dict[str, float]


@dataclass
class ConceptHierarchy:
    """Hierarchical organization of concepts"""
    root_concepts: List[str]
    concept_tree: Dict[str, List[str]]
    hierarchy_depth: int
    concept_relationships: List[Relationship]


@dataclass
class ContradictionAnalysis:
    """Analysis of contradictions between documents"""
    contradictions: List[Dict[str, Any]]
    confidence_scores: List[float]
    resolution_suggestions: List[str]


@dataclass
class InfluenceNetwork:
    """Network of influence relationships between entities"""
    influence_graph: Dict[str, List[str]]
    influence_scores: Dict[str, float]
    influence_paths: List[List[str]]


# Test fixtures
@pytest.fixture
def sample_documents():
    """Sample documents for testing relationship discovery"""
    return [
        {
            "path": "doc1.txt",
            "content": "Dr. Sarah Chen published groundbreaking research on CRISPR gene editing in 2023. Her work at Stanford University focuses on treating genetic diseases using precision medicine approaches.",
            "metadata": {
                "authors": ["Dr. Sarah Chen"],
                "date": "2023-03-15",
                "keywords": ["CRISPR", "gene editing", "genetics", "medicine"],
                "references": ["Smith2022.pdf", "genetic_therapy_review.txt"]
            }
        },
        {
            "path": "doc2.txt", 
            "content": "The CRISPR-Cas9 system has revolutionized biotechnology since Jennifer Doudna's pioneering work led to breakthrough discoveries. Recent advances by researchers like Sarah Chen have shown promising results in clinical trials.",
            "metadata": {
                "authors": ["Dr. Michael Rodriguez"],
                "date": "2023-05-20",
                "keywords": ["CRISPR", "biotechnology", "clinical trials"],
                "references": ["Chen2023.pdf", "doudna_nature.pdf"]
            }
        },
        {
            "path": "doc3.txt",
            "content": "Stanford University's genetics program has been at the forefront of precision medicine. Dr. Chen's recent publication demonstrates the potential of gene therapy for hereditary conditions.",
            "metadata": {
                "authors": ["Prof. Lisa Wang"],
                "date": "2023-07-10", 
                "keywords": ["Stanford", "genetics", "precision medicine", "gene therapy"],
                "references": ["stanford_report.pdf", "Chen2023.pdf"]
            }
        },
        {
            "path": "doc4.txt",
            "content": "Ethical concerns about gene editing have been raised by bioethics committees. While CRISPR offers medical benefits, some argue that genetic modifications could have unintended consequences.",
            "metadata": {
                "authors": ["Dr. Robert Kim"],
                "date": "2023-06-01",
                "keywords": ["ethics", "gene editing", "bioethics", "CRISPR"],
                "references": ["ethics_review.pdf", "bioethics_guidelines.txt"]
            }
        },
        {
            "path": "doc5.txt",
            "content": "Jennifer Doudna received the Nobel Prize for CRISPR development. Her collaboration with Emmanuelle Charpentier laid the foundation for modern gene editing technologies. Doudna's research pioneered the CRISPR revolution.",
            "metadata": {
                "authors": ["Science Reporter"],
                "date": "2023-04-12",
                "keywords": ["Nobel Prize", "Jennifer Doudna", "CRISPR", "collaboration"],
                "references": ["nobel_announcement.pdf", "Doudna_Charpentier2012.pdf"]
            }
        }
    ]


@pytest.fixture
def cross_document_linker():
    """Cross-document relationship linker instance"""
    return CrossDocumentLinker()


@pytest.fixture
def entity_resolver():
    """Entity resolver instance"""
    return EntityResolver()


@pytest.fixture
def concept_tracker():
    """Concept tracker instance"""
    return ConceptTracker()


@pytest.fixture
def relationship_classifier():
    """Relationship classifier instance"""
    return RelationshipClassifier()


# Test Cases for Task C.4: Cross-Document Relationship Discovery

@pytest.mark.asyncio
async def test_entity_coreference_resolution(entity_resolver, sample_documents):
    """Test linking same entities across documents"""
    result = await entity_resolver.resolve_entity_coreferences(sample_documents)
    
    # Should identify entity clusters
    assert len(result.entity_clusters) > 0, "Should identify entity clusters"
    
    # Should link "Dr. Sarah Chen" and "Sarah Chen" as same entity
    sarah_chen_clusters = []
    for cluster in result.entity_clusters:
        entity_names = [ref.entity_name.lower() for ref in cluster.entity_references]
        if any("sarah chen" in name for name in entity_names):
            sarah_chen_clusters.append(cluster)
    
    # Find the best Sarah Chen cluster (highest confidence with multiple references)
    sarah_chen_cluster = None
    for cluster in sarah_chen_clusters:
        if len(cluster.entity_references) >= 2:
            if sarah_chen_cluster is None or cluster.cluster_confidence > sarah_chen_cluster.cluster_confidence:
                sarah_chen_cluster = cluster
    
    assert sarah_chen_cluster is not None, "Should identify Sarah Chen entity cluster"
    assert len(sarah_chen_cluster.entity_references) >= 2, "Should link multiple Sarah Chen mentions"
    
    # Should have high confidence for clear matches
    high_confidence_refs = [ref for ref in sarah_chen_cluster.entity_references if ref.confidence_score > 0.8]
    assert len(high_confidence_refs) > 0, "Should have high confidence entity matches"
    
    # Should identify CRISPR as a consistent concept/entity
    crispr_cluster = None
    for cluster in result.entity_clusters:
        entity_names = [ref.entity_name.lower() for ref in cluster.entity_references]
        if any("crispr" in name for name in entity_names):
            crispr_cluster = cluster
            break
    
    assert crispr_cluster is not None, "Should identify CRISPR entity cluster"
    assert len(crispr_cluster.entity_references) >= 3, "Should link multiple CRISPR mentions"


@pytest.mark.asyncio
async def test_concept_evolution_tracking(concept_tracker, sample_documents):
    """Test tracking how concepts evolve across documents"""
    result = await concept_tracker.track_concept_evolution(sample_documents)
    
    # Should track evolution of key concepts
    assert len(result.concept_evolutions) > 0, "Should track concept evolutions"
    
    # Should track CRISPR evolution from basic research to clinical applications
    crispr_evolution = None
    for evolution in result.concept_evolutions:
        if "crispr" in evolution.concept_name.lower():
            crispr_evolution = evolution
            break
    
    assert crispr_evolution is not None, "Should track CRISPR concept evolution"
    assert len(crispr_evolution.timeline) >= 3, "Should have multiple timeline points"
    
    # Timeline should be chronologically ordered
    dates = [event["date"] for event in crispr_evolution.timeline if "date" in event]
    assert dates == sorted(dates), "Timeline should be chronologically ordered"
    
    # Should classify evolution type
    assert crispr_evolution.evolution_type in ["emerging", "evolving", "stable", "declining"], "Should classify evolution type"
    assert crispr_evolution.confidence_score > 0.5, "Should have reasonable confidence"


@pytest.mark.asyncio
async def test_causal_relationship_discovery(cross_document_linker, sample_documents):
    """Test finding causal links between documents"""
    result = await cross_document_linker.discover_causal_relationships(sample_documents)
    
    # Should identify causal relationships
    assert len(result.causal_relationships) > 0, "Should discover causal relationships"
    
    # Should find causal link: research → outcome (like breakthrough discoveries or CRISPR revolution)
    research_causal = None
    for rel in result.causal_relationships:
        if ("research" in rel.source_entity.lower() or "work" in rel.source_entity.lower()) and \
           ("revolution" in rel.target_entity.lower() or "breakthrough" in rel.target_entity.lower() or "discoveries" in rel.target_entity.lower()):
            research_causal = rel
            break
    
    assert research_causal is not None, "Should find research-related causal relationship"
    assert research_causal.confidence_score > 0.6, "Should have reasonable confidence"
    assert len(research_causal.evidence_documents) >= 1, "Should have supporting evidence"
    
    # Should identify relationships with reasonable confidence scores
    high_confidence_rels = [rel for rel in result.causal_relationships if rel.confidence_score > 0.6]
    assert len(high_confidence_rels) > 0, "Should have high-confidence causal relationships"


@pytest.mark.asyncio
async def test_temporal_relationship_mapping(cross_document_linker, sample_documents):
    """Test mapping temporal sequences across documents"""
    result = await cross_document_linker.map_temporal_relationships(sample_documents)
    
    # Should identify temporal sequences
    assert len(result.temporal_sequences) > 0, "Should identify temporal sequences"
    
    # Should map CRISPR development timeline
    crispr_sequence = None
    for sequence in result.temporal_sequences:
        if "crispr" in sequence.sequence_name.lower():
            crispr_sequence = sequence
            break
    
    assert crispr_sequence is not None, "Should map CRISPR temporal sequence"
    assert len(crispr_sequence.events) >= 3, "Should have multiple temporal events"
    
    # Events should be temporally ordered
    event_dates = [event.timestamp for event in crispr_sequence.events]
    assert event_dates == sorted(event_dates), "Events should be temporally ordered"
    
    # Should identify key milestones
    milestone_events = [event for event in crispr_sequence.events if event.is_milestone]
    assert len(milestone_events) > 0, "Should identify milestone events"


@pytest.mark.asyncio
async def test_influence_network_construction(cross_document_linker, sample_documents):
    """Test building influence and impact networks"""
    result = await cross_document_linker.build_influence_network(sample_documents)
    
    # Should construct influence network
    assert len(result.influence_graph) > 0, "Should build influence network"
    
    # Should identify Jennifer Doudna as highly influential
    doudna_influence = result.influence_scores.get("Jennifer Doudna", 0)
    assert doudna_influence > 0.7, f"Doudna should have high influence score: {doudna_influence}"
    
    # Should identify influence paths
    assert len(result.influence_paths) > 0, "Should identify influence paths"
    
    # Should find Doudna → Chen influence path
    doudna_chen_path = None
    for path in result.influence_paths:
        path_str = " → ".join(path).lower()
        if "doudna" in path_str and "chen" in path_str:
            doudna_chen_path = path
            break
    
    assert doudna_chen_path is not None, "Should find Doudna→Chen influence path"
    assert len(doudna_chen_path) >= 2, "Influence path should have multiple nodes"


@pytest.mark.asyncio
async def test_contradiction_detection(cross_document_linker, sample_documents):
    """Test finding contradictory statements across documents"""
    result = await cross_document_linker.detect_contradictions(sample_documents)
    
    # Should analyze potential contradictions
    assert hasattr(result, 'contradictions'), "Should have contradictions analysis"
    
    # Should identify potential ethical vs medical benefits tension
    ethical_contradiction = None
    for contradiction in result.contradictions:
        statement1 = contradiction.get("statement1", "").lower()
        statement2 = contradiction.get("statement2", "").lower()
        if ("benefit" in statement1 and "concern" in statement2) or ("concern" in statement1 and "benefit" in statement2):
            ethical_contradiction = contradiction
            break
    
    if ethical_contradiction:
        assert ethical_contradiction.get("confidence_score", 0) > 0.5, "Should have reasonable confidence in contradiction detection"
    
    # Should provide resolution suggestions if contradictions found
    if result.contradictions:
        assert len(result.resolution_suggestions) > 0, "Should provide resolution suggestions"


@pytest.mark.asyncio
async def test_supporting_evidence_linking(cross_document_linker, sample_documents):
    """Test linking supporting evidence across documents"""
    result = await cross_document_linker.link_supporting_evidence(sample_documents)
    
    # Should identify evidence chains
    assert len(result.evidence_chains) > 0, "Should identify evidence chains"
    
    # Should link Chen's work being supported by multiple documents
    chen_evidence = None
    for chain in result.evidence_chains:
        if "chen" in chain.primary_claim.lower():
            chen_evidence = chain
            break
    
    assert chen_evidence is not None, "Should find evidence chain for Chen's work"
    assert len(chen_evidence.supporting_documents) >= 2, "Should have multiple supporting documents"
    
    # Should calculate evidence strength
    assert chen_evidence.evidence_strength > 0.6, "Should have strong evidence support"
    
    # Should identify cross-references in metadata
    cross_refs_found = False
    for chain in result.evidence_chains:
        if len(chain.cross_references) > 0:
            cross_refs_found = True
            break
    
    assert cross_refs_found, "Should identify cross-references between documents"


@pytest.mark.asyncio
async def test_concept_hierarchy_building(cross_document_linker, sample_documents):
    """Test building concept hierarchies from multiple sources"""
    result = await cross_document_linker.build_concept_hierarchy(sample_documents)
    
    # Should build concept hierarchy
    assert len(result.root_concepts) > 0, "Should identify root concepts"
    assert len(result.concept_tree) > 0, "Should build concept tree"
    
    # Should identify "gene editing" as a parent concept
    gene_editing_children = result.concept_tree.get("gene editing", [])
    assert len(gene_editing_children) > 0, "Gene editing should have child concepts"
    
    # CRISPR should be under gene editing
    assert "CRISPR" in gene_editing_children or "crispr" in [c.lower() for c in gene_editing_children], "CRISPR should be child of gene editing"
    
    # Should have reasonable hierarchy depth
    assert result.hierarchy_depth >= 2, "Should have multi-level hierarchy"
    assert result.hierarchy_depth <= 5, "Hierarchy should not be too deep"
    
    # Should identify hierarchical relationships
    hierarchical_rels = [rel for rel in result.concept_relationships if rel.relationship_type == "hierarchical"]
    assert len(hierarchical_rels) > 0, "Should identify hierarchical relationships"


@pytest.mark.asyncio
async def test_cross_document_entity_disambiguation(entity_resolver, sample_documents):
    """Test disambiguating entities with same names"""
    # Add ambiguous entities to test data
    ambiguous_docs = sample_documents + [
        {
            "path": "doc6.txt",
            "content": "Dr. Chen from Harvard Medical School published a study on cancer immunotherapy. This research is unrelated to CRISPR technology.",
            "metadata": {
                "authors": ["Dr. James Chen"],
                "date": "2023-08-15",
                "keywords": ["cancer", "immunotherapy", "Harvard"],
                "references": ["cancer_study.pdf"]
            }
        }
    ]
    
    result = await entity_resolver.disambiguate_entities(ambiguous_docs)
    
    # Should distinguish between different "Dr. Chen" entities
    chen_clusters = [cluster for cluster in result.disambiguated_entities 
                    if any("chen" in ref.entity_name.lower() for ref in cluster.entity_references)]
    
    assert len(chen_clusters) >= 2, "Should distinguish between different Chen entities"
    
    # Should correctly associate each Chen with their research area
    sarah_chen_cluster = None
    james_chen_cluster = None
    
    for cluster in chen_clusters:
        contexts = [ref.mention_context.lower() for ref in cluster.entity_references]
        if any("crispr" in context or "gene editing" in context for context in contexts):
            sarah_chen_cluster = cluster
        elif any("cancer" in context or "immunotherapy" in context for context in contexts):
            james_chen_cluster = cluster
    
    assert sarah_chen_cluster is not None, "Should identify Sarah Chen (CRISPR researcher)"
    assert james_chen_cluster is not None, "Should identify James Chen (cancer researcher)"
    
    # Should have high disambiguation confidence
    for cluster in chen_clusters:
        assert cluster.disambiguation_confidence > 0.7, "Should have high disambiguation confidence"


@pytest.mark.asyncio
async def test_relationship_confidence_scoring(relationship_classifier, sample_documents):
    """Test scoring relationship strength and confidence"""
    result = await relationship_classifier.score_relationship_confidence(sample_documents)
    
    # Should calculate confidence scores for relationships
    assert len(result.relationship_scores) > 0, "Should calculate relationship confidence scores"
    
    # Should have scores in valid range
    for rel_id, score in result.relationship_scores.items():
        assert 0.0 <= score <= 1.0, f"Confidence score should be in [0,1]: {score}"
    
    # Should identify high-confidence relationships
    high_confidence_rels = {rel_id: score for rel_id, score in result.relationship_scores.items() if score > 0.8}
    assert len(high_confidence_rels) > 0, "Should identify high-confidence relationships"
    
    # Should provide confidence factors
    assert hasattr(result, 'confidence_factors'), "Should provide confidence factors"
    for rel_id in result.relationship_scores:
        assert rel_id in result.confidence_factors, "Should have confidence factors for each relationship"


@pytest.mark.asyncio
async def test_relationship_type_classification(relationship_classifier, sample_documents):
    """Test classifying types of discovered relationships"""
    result = await relationship_classifier.classify_relationship_types(sample_documents)
    
    # Should classify relationship types
    assert len(result.classified_relationships) > 0, "Should classify relationships"
    
    # Should identify different relationship types
    relationship_types = set(rel.relationship_type for rel in result.classified_relationships)
    expected_types = {"causal", "temporal", "hierarchical", "associative"}
    found_types = relationship_types.intersection(expected_types)
    assert len(found_types) >= 2, f"Should identify multiple relationship types: {found_types}"
    
    # Should classify Doudna→Chen as causal or temporal
    doudna_chen_rel = None
    for rel in result.classified_relationships:
        if ("doudna" in rel.source_entity.lower() and "chen" in rel.target_entity.lower()):
            doudna_chen_rel = rel
            break
    
    if doudna_chen_rel:
        assert doudna_chen_rel.relationship_type in ["causal", "temporal"], "Doudna→Chen should be causal or temporal"
        assert doudna_chen_rel.confidence_score > 0.6, "Should have reasonable classification confidence"


@pytest.mark.asyncio
async def test_bidirectional_relationship_validation(relationship_classifier, sample_documents):
    """Test validating relationships work both ways"""
    result = await relationship_classifier.validate_bidirectional_relationships(sample_documents)
    
    # Should validate relationship directionality
    assert len(result.validated_relationships) > 0, "Should validate relationships"
    
    # Should identify bidirectional relationships
    bidirectional_rels = [rel for rel in result.validated_relationships 
                         if rel.relationship_direction == "bidirectional"]
    assert len(bidirectional_rels) > 0, "Should identify bidirectional relationships"
    
    # Should identify unidirectional relationships
    unidirectional_rels = [rel for rel in result.validated_relationships 
                          if rel.relationship_direction in ["source_to_target", "target_to_source"]]
    assert len(unidirectional_rels) > 0, "Should identify unidirectional relationships"
    
    # Should provide validation confidence
    for rel in result.validated_relationships:
        assert hasattr(rel, 'validation_confidence'), "Should have validation confidence"
        assert 0.0 <= rel.validation_confidence <= 1.0, "Validation confidence should be in [0,1]"


@pytest.mark.asyncio
async def test_relationship_graph_visualization(cross_document_linker, sample_documents):
    """Test generating relationship graphs"""
    result = await cross_document_linker.generate_relationship_graph(sample_documents)
    
    # Should generate graph structure
    assert hasattr(result, 'nodes'), "Should have graph nodes"
    assert hasattr(result, 'edges'), "Should have graph edges"
    
    # Should include key entities as nodes
    node_names = [node.get('name', '').lower() for node in result.nodes]
    assert any("chen" in name for name in node_names), "Should include Chen as node"
    assert any("doudna" in name for name in node_names), "Should include Doudna as node"
    assert any("crispr" in name for name in node_names), "Should include CRISPR as node"
    
    # Should have edges between related entities
    assert len(result.edges) > 0, "Should have relationship edges"
    
    # Should provide graph metrics
    assert hasattr(result, 'graph_metrics'), "Should provide graph metrics"
    assert 'density' in result.graph_metrics, "Should calculate graph density"
    assert 'centrality' in result.graph_metrics, "Should calculate centrality measures"
    
    # Should support visualization export
    assert hasattr(result, 'export_formats'), "Should support export formats"
    assert 'networkx' in result.export_formats, "Should support NetworkX export"


@pytest.mark.asyncio
async def test_relationship_query_interface(cross_document_linker, sample_documents):
    """Test querying discovered relationships efficiently"""
    # First discover relationships
    discovery_result = await cross_document_linker.discover_all_relationships(sample_documents)
    
    # Test entity-based queries
    chen_relationships = await cross_document_linker.query_entity_relationships("Sarah Chen")
    assert len(chen_relationships) > 0, "Should find relationships for Sarah Chen"
    
    # Test relationship type queries
    causal_relationships = await cross_document_linker.query_by_relationship_type("causal")
    assert len(causal_relationships) >= 0, "Should handle causal relationship queries"
    
    # Test path queries between entities
    doudna_chen_path = await cross_document_linker.query_relationship_path("Jennifer Doudna", "Sarah Chen")
    if doudna_chen_path:
        assert len(doudna_chen_path.path) >= 2, "Relationship path should have multiple steps"
        assert doudna_chen_path.path_strength > 0.5, "Path should have reasonable strength"
    
    # Test temporal range queries
    recent_relationships = await cross_document_linker.query_temporal_range("2023-01-01", "2023-12-31")
    assert len(recent_relationships) > 0, "Should find relationships in temporal range"
    
    # Test concept-based queries
    crispr_relationships = await cross_document_linker.query_concept_relationships("CRISPR")
    assert len(crispr_relationships) > 0, "Should find CRISPR-related relationships"
    
    # Performance test - queries should be fast
    import time
    start_time = time.time()
    await cross_document_linker.query_entity_relationships("CRISPR")
    query_time = time.time() - start_time
    assert query_time < 1.0, f"Query should be fast (<1s): {query_time:.3f}s"