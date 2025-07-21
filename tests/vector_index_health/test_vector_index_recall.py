import pytest
import os
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "password")

RECALL_THRESHOLD = 0.8  # Placeholder until calibration

@pytest.fixture(scope="module")
def neo4j_driver():
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        # Quick connectivity check
        with driver.session() as session:
            session.run("RETURN 1").single()
        yield driver
    except Exception:
        pytest.skip("Neo4j not available – skipping vector index recall test")
    finally:
        if "driver" in locals():
            driver.close()


def test_vector_index_recall_at_k5(neo4j_driver):
    """Simple recall@5 test to detect staleness in the HNSW index."""
    from random import sample
    with neo4j_driver.session() as session:
        # Select 10 random entity IDs that have embeddings
        result = session.run(
            "MATCH (e:Entity) WHERE exists(e.embedding) RETURN e.id AS id LIMIT 1000"
        )
        ids = [record["id"] for record in result]
        if len(ids) < 10:
            pytest.skip("Not enough vectors to compute recall@5")
        test_ids = sample(ids, 10)

        # For each id, query the index for similar vectors
        hits = 0
        for eid in test_ids:
            vector_record = session.run(
                "MATCH (e:Entity {id: $id}) RETURN e.embedding AS vec", id=eid
            ).single()
            if not vector_record:
                continue
            vec = vector_record["vec"]
            # Query top 5
            res = session.run(
                "CALL db.index.vector.queryNodes('entity_embedding_index', $k, $v) YIELD node "
                "RETURN node.id AS id LIMIT $k",
                k=5,
                v=vec,
            )
            returned_ids = [rec["id"] for rec in res]
            if eid in returned_ids:
                hits += 1

        recall = hits / len(test_ids)
        assert recall >= RECALL_THRESHOLD, f"Recall@5 {recall:.2f} below threshold {RECALL_THRESHOLD}" 